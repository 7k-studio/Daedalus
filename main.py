'''

Copyright (C) 2025-2026 Jakub Kamyk

This file is part of DAEDALUS.

DAEDALUS is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

DAEDALUS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with DAEDALUS.  If not, see <http://www.gnu.org/licenses/>.

'''
# Library import
import logging
import sys
import os
import datetime

# Module-level logger so exception hook can always access a logger
logger = logging.getLogger(__name__)

# PyQt import 
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from src.widgets.splash_screen import SplashScreen
from src.program.main_window import MainWindow

def log_uncaught_exceptions(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        # To allow clean exit
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    sys.exit()

def main():
    from src.program.program import Program
    DAEDALUS = Program()

    log_file = 'toolout.log'

    if os.path.exists(log_file):
        os.remove(log_file)

    with open(log_file, "w") as file:
        header(DAEDALUS.version, file)
    
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(name)s: %(funcName)s: %(message)s", handlers=[logging.FileHandler("toolout.log"), logging.StreamHandler()])

    sys.excepthook = log_uncaught_exceptions

    DAEDALUS.APP = QApplication(sys.argv)
    icon = QIcon("src/assets/logo.png")
    DAEDALUS.APP.setWindowIcon(icon)

    DAEDALUS.buildStyleSheet()
    DAEDALUS.APP.setStyleSheet(DAEDALUS.buildStyleSheet())

    # Show splash screen or main window
    DAEDALUS.SPLASHSCREEN = SplashScreen(DAEDALUS)
    DAEDALUS.SPLASHSCREEN.show()
    
    # Create the main window (single window for all modules)
    DAEDALUS.MAIN_WINDOW = MainWindow(program=DAEDALUS, project=None)
    
    # Show the main window
    DAEDALUS.SPLASHSCREEN.close()
    DAEDALUS.MAIN_WINDOW.showMaximized()
    
    sys.exit(DAEDALUS.APP.exec())

def header(version, file):
    file.write("       _______        ___________    _________    _______        ___________    ___           ___     ___    __________  \n")
    file.write("      /  ___  \      /  _____   /\  /  ______/\  /  ___  \      /  _____   /\  /  /\         /  /\   /  /\  /  _______/\ \n")
    file.write("     /  /\__\  \    /  /\___/  / / /  /\_____\/ /  /\__\  \    /  /\___/  / / /  / /        /  / /  /  / / /  /\______\/ \n")
    file.write("    /  / /  /  /\  /  /_/__/  / / /  /_/___    /  / /  /  /\  /  /_/__/  / / /  / /        /  / /  /  / / /  /_/_____    \n")
    file.write("   /  / /  /  / / /  _____   / / /  ______/\  /  / /  /  / / /  _____   / / /  / /        /  / /  /  / / /_______   /\   \n")
    file.write("  /  / /  /  / / /  /\___/  / / /  /\_____\/ /  / /  /  / / /  /\___/  / / /  / /        /  / /  /  / /  \______/  / /   \n")
    file.write(" /  /_/__/  / / /  / /  /  / / /  /_/____   /  /_/__/  / / /  / /  /  / / /  /_/_____   /  /_/__/  / / ________/  / /    \n")
    file.write("/__________/ / /__/ /  /__/ / /_________/\ /__________/ / /__/ /  /__/ / /__________/\ /__________/ / /__________/ /     \n")
    file.write("\__________\/  \__\/   \__\/  \_________\/ \__________\/  \__\/   \__\/  \__________\/ \__________\/  \__________\/      \n")
    file.write("\n")
    file.write("|/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\//\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\|\n")
    file.write(f"Program version: {version}\n")
    file.write(f"Program opened on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    

if __name__ == "__main__":

    main()