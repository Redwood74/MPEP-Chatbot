import os
import logging
import shutil
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.common.exceptions import WebDriverException
from pathlib import Path
from datetime import datetime


def configure_environment():
    # Use absolute path for driver cache
    cache_path = os.path.join(os.path.expanduser("~"), ".wdm")
    os.makedirs(cache_path, exist_ok=True)

    # Set environment variables
    os.environ["WDM_LOCAL"] = "1"
    os.environ["WDM_CACHE_PATH"] = cache_path

    # Load other environment variables
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    load_dotenv(env_path)

    logging.debug(f"WDM_LOCAL: {os.environ['WDM_LOCAL']}")
    logging.debug(f"WDM_CACHE_PATH: {os.environ['WDM_CACHE_PATH']}")

    return cache_path


def setup_logging():
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_level = log_level.upper()
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logging.info(f"Logging is set to {log_level} level")


def get_driver_options():
    options = webdriver.EdgeOptions()
    options.add_argument("--start-maximized")

    # Add headless mode if specified in environment
    if os.getenv("HEADLESS_MODE", "False").lower() == "true":
        options.add_argument("--headless")

    return options


def setup_edge_driver():
    setup_logging()
    configure_environment()

    try:
        # Create WebDriver Manager instance
        driver_path = EdgeChromiumDriverManager().install()

        # Set up the service and driver
        service = Service(driver_path)
        options = get_driver_options()
        driver = webdriver.Edge(service=service, options=options)
        driver.set_page_load_timeout(30)

        logging.info("EdgeDriver successfully initialized")
        return driver

    except WebDriverException as we:
        logging.error(
            f"WebDriverException occurred while setting up EdgeDriver: {str(we)}",
            exc_info=True,
        )
        raise
    except Exception as e:
        logging.error(
            f"Unexpected error while setting up EdgeDriver: {str(e)}", exc_info=True
        )
        raise


def inject_custom_overlay(driver):
    """Inject custom overlay for user interactions."""
    driver.execute_script(
        """
        var style = document.createElement('style');
        style.innerHTML = `
            #lms-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.5);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 9999;
            }
            #lms-message {
                background-color: white;
                padding: 20px;
                border-radius: 5px;
                text-align: center;
            }
        `;
        document.head.appendChild(style);

        var overlay = document.createElement('div');
        overlay.id = 'lms-overlay';
        overlay.innerHTML = '<div id="lms-message"></div>';
        overlay.style.display = 'none';
        document.body.appendChild(overlay);

        window.showLmsMessage = function(message) {
            document.getElementById('lms-message').innerText = message;
            document.getElementById('lms-overlay').style.display = 'flex';
        };

        window.hideLmsMessage = function() {
            document.getElementById('lms-overlay').style.display = 'none';
        };
    """
    )


def backup_current_data(source_dir, backup_dir):
    """
    Backup all CSV, XLS, and other important files from source_dir to a new backup folder.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.getenv("BACKUP_DIR", backup_dir)
    backup_folder = Path(backup_dir) / f"LMS_Data_Backup_{timestamp}"

    try:
        backup_folder.mkdir(parents=True, exist_ok=True)
        logging.info(f"Created backup folder: {backup_folder}")

        for filename in os.listdir(source_dir):
            if filename.endswith(
                (".csv", ".xls", ".xlsx")
            ):  # Add other extensions if needed
                source_file = Path(source_dir) / filename
                dest_file = backup_folder / filename
                shutil.copy2(str(source_file), str(dest_file))
                logging.info(f"Backed up file: {filename}")

        logging.info("Backup process completed successfully")
        return True
    except Exception as e:
        logging.error(f"Error during backup process: {str(e)}")
        return False
