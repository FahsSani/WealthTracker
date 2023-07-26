# Wealth Tracker

The Wealth Tracker is a simple Python application that allows users to track their financial assets and liabilities. It provides a graphical user interface (GUI) built with Tkinter to display and manage the financial data. The application saves the data in a JSON file, which can be loaded later for comparison and historical tracking.


## Requirements

Python 3.x

json module (included with Python)

requests module (install via pip install requests)

tkinter module (included with Python)

locale module (included with Python)

time module (included with Python)

schedule module (install via pip install schedule)

os module (included with Python)

re module (included with Python)

## Getting Started

Install the required Python modules if you haven't already. You can do this via pip:
pip install requests schedule

Download the code and save it in a .py file (e.g., wealth_tracker.py).

Run the Python script using the following command in your terminal or command prompt:
python wealth_tracker.py

The Wealth Tracker GUI will open, and you can start using the application.

## How to Use the Application

The application displays your financial assets and liabilities, which you can modify and track over time.

To add a new sub-account (asset or liability):

Click on "File" in the menu.
Choose "Add Sub Account."
Enter 'A' for Assets or 'L' for Liabilities when prompted.
Enter the name of the sub-account.
The new sub-account will be added to the list.
To modify the value of a sub-account:

Click on "File" in the menu.
Choose "Modify Values."
Enter 'A' for Assets or 'L' for Liabilities when prompted.
Enter the name of the sub-account you want to modify.
Enter the new value for the sub-account.
To modify the name of a sub-account:

Click on "File" in the menu.
Choose "Modify Sub Account Name."
Enter 'A' for Assets or 'L' for Liabilities when prompted.
Enter the current name of the sub-account you want to modify.
Enter the new name for the sub-account.
To remove a sub-account:

Click on "File" in the menu.
Choose "Remove Sub Account."
Enter 'A' for Assets or 'L' for Liabilities when prompted.
Enter the name of the sub-account you want to remove.
To save the current data to a JSON file:

Click on "File" in the menu.
Choose "Save Data."
The data will be saved in a new JSON file with a timestamp as the filename. The file will be stored in the "HistoricalData" folder in the application's directory.
To compare historical data from multiple JSON files:

Click on "File" in the menu.
Choose "Compare Historical Data."
Select the JSON files you want to compare when prompted. The files should be located in the "HistoricalData" folder within the application's directory.
A new window will display a comparison of the financial data from the selected files.

## Note
The application fetches the current Bitcoin price from an external API (CoinGecko). It is recommended to have an internet connection for accurate Bitcoin value updates.
The Bitcoin price is also stored locally in the bitcoin_data.json file, so the application can display the last fetched price when there's a connection issue.
Contributing
Contributions to the Wealth Tracker are welcome! Please feel free to open issues for bug reports, suggestions, or new features.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.






