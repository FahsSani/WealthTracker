import json
import requests
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import locale
import time
import schedule
import os
import re

# Set the locale to the user's default for displaying numbers with thousand separator
locale.setlocale(locale.LC_ALL, '')

# Define the data file name
DATA_FILE = "accounting_data.json"
BITCOIN_FILE = "bitcoin_data.json"  # New file for storing Bitcoin price

# Function to load data from the JSON file
def load_data():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "assets": {
                "Cash": 0,
                "Stocks": 0,
                "Bank": 0,
                "Crypto": 0
            },
            "liabilities": {
                "Credit Card Debt": 0,
                "Student Loans": 0,
                "Mortgage": 0
            }
        }

# Function to save data to the JSON file
def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)


# Function to retrieve Bitcoin value from an external API (for example, CoinGecko)
def get_bitcoin_value():
    try:
        response = requests.get("https://api.coingecko.com/api/v3/simple/price",
                                params={"ids": "bitcoin", "vs_currencies": "usd"})
        response.raise_for_status()
        return response.json()["bitcoin"]["usd"]
    except requests.RequestException:
        return None  # Return None when there's a connection issue

# New function to retrieve and store Bitcoin price locally
def update_bitcoin_data():
    bitcoin_data = {
        "timestamp": int(time.time()),
        "price_usd": get_bitcoin_value()
    }
    with open(BITCOIN_FILE, "w") as file:
        json.dump(bitcoin_data, file)

def manual_update_bitcoin_price():
    global bitcoin_price_usd
    bitcoin_price_usd = get_bitcoin_value()
    if bitcoin_price_usd is not None:
        bitcoin_label.config(text=f"Bitcoin Price per USD: {locale.format_string('%.2f', bitcoin_price_usd, grouping=True)}")
    else:
        # If no current price is available, check if there's a stored price in bitcoin_data
        try:
            with open(BITCOIN_FILE, "r") as file:
                bitcoin_data = json.load(file)
                bitcoin_price_usd = bitcoin_data["price_usd"]
                bitcoin_label.config(text=f"Bitcoin Price per USD: {locale.format_string('%.2f', bitcoin_price_usd, grouping=True)}")
        except (FileNotFoundError, json.JSONDecodeError):
            bitcoin_price_usd = None
            bitcoin_label.config(text="Bitcoin Price per USD: N/A")  # Display "N/A" if no stored price is available


def update_and_reschedule(root):
    update_bitcoin_data()
    display_data()
    root.after(10000, update_and_reschedule, root)  # Reschedule the function after 10000 milliseconds (10 seconds)


# Function to handle adding a new sub-account
def add_sub_account():
    category_input = simpledialog.askstring("Add Sub Account", "Enter 'A' for Assets or 'L' for Liabilities:")
    category_input = category_input.lower()  # Convert input to lowercase
    if category_input == 'a':
        category = "assets"
    elif category_input == 'l':
        category = "liabilities"
    else:
        messagebox.showerror("Error", "Invalid input. Please enter 'A' for Assets or 'L' for Liabilities.")
        return
    sub_account_name = simpledialog.askstring("Add Sub Account", "Enter the sub account name:")
    if category and sub_account_name:
        data = load_data()
        data[category][sub_account_name] = 0
        save_data(data)
        display_data()

# Function to handle modifying sub-account values
def modify_values():
    category_input = simpledialog.askstring("Modify Values", "Enter 'A' for Assets or 'L' for Liabilities:")
    category_input = category_input.lower()  # Convert input to lowercase
    if category_input == 'a':
        category = "assets"
    elif category_input == 'l':
        category = "liabilities"
    else:
        messagebox.showerror("Error", "Invalid input. Please enter 'A' for Assets or 'L' for Liabilities.")
        return
    sub_account_name = simpledialog.askstring("Modify Values", "Enter the sub account name:")
    new_value = simpledialog.askfloat("Modify Values", "Enter the new value:")
    if category and sub_account_name and new_value is not None:
        data = load_data()
        data[category][sub_account_name] = new_value
        save_data(data)
        display_data()

# Function to handle modifying sub-account names
def modify_sub_account_name():
    category_input = simpledialog.askstring("Modify Sub Account Name", "Enter 'A' for Assets or 'L' for Liabilities:")
    category_input = category_input.lower()  # Convert input to lowercase
    if category_input == 'a':
        category = "assets"
    elif category_input == 'l':
        category = "liabilities"
    else:
        messagebox.showerror("Error", "Invalid input. Please enter 'A' for Assets or 'L' for Liabilities.")
        return
    old_sub_account_name = simpledialog.askstring("Modify Sub Account Name", "Enter the current sub account name:")
    new_sub_account_name = simpledialog.askstring("Modify Sub Account Name", "Enter the new sub account name:")
    if category and old_sub_account_name and new_sub_account_name:
        data = load_data()
        value = data[category].pop(old_sub_account_name, None)
        if value is not None:
            data[category][new_sub_account_name] = value
            save_data(data)
            display_data()
        else:
            messagebox.showwarning("Modify Sub Account Name", f"No sub account named '{old_sub_account_name}' found.")

# Function to handle removing a sub-account
def remove_sub_account():
    category_input = simpledialog.askstring("Remove Sub-Account", "Enter 'A' for Assets or 'L' for Liabilities:")
    category_input = category_input.lower()  # Convert input to lowercase
    if category_input == 'a':
        category = "assets"
    elif category_input == 'l':
        category = "liabilities"
    else:
        messagebox.showerror("Error", "Invalid input. Please enter 'A' for Assets or 'L' for Liabilities.")
        return
    sub_account_name = simpledialog.askstring("Remove Sub Account", "Enter the sub account name:")
    if category and sub_account_name:
        data = load_data()
        value = data[category].pop(sub_account_name, None)
        if value is not None:
            save_data(data)
            display_data()
        else:
            messagebox.showwarning("Remove Sub Account", f"No sub account named '{sub_account_name}' found.")


def save_current_data():
    data = load_data()
    json_file = save_data_to_json(data)
    messagebox.showinfo("Data Saved", f"Data saved to {json_file}")

def save_data_to_json(data):
    # Separate assets and liabilities into two dictionaries
    assets_dict = {}
    liabilities_dict = {}

    # Save asset data
    total_assets_usd = 0
    total_assets_btc = 0
    for account, value in data["assets"].items():
        total_assets_usd += value
        assets_dict[account] = {
            "USD": locale.format_string('%.2f', value, grouping=True),
            "BTC": f"{value / bitcoin_price_usd:.8f}" if bitcoin_price_usd and bitcoin_price_usd != 0 else "N/A"
        }
        if bitcoin_price_usd and bitcoin_price_usd != 0:
            total_assets_btc += value / bitcoin_price_usd

    # Save liabilities data
    total_liabilities_usd = 0
    total_liabilities_btc = 0
    for account, value in data["liabilities"].items():
        total_liabilities_usd += value
        liabilities_dict[account] = {
            "USD": locale.format_string('%.2f', value, grouping=True),
            "BTC": f"{value / bitcoin_price_usd:.8f}" if bitcoin_price_usd and bitcoin_price_usd != 0 else "N/A"
        }
        if bitcoin_price_usd and bitcoin_price_usd != 0:
            total_liabilities_btc += value / bitcoin_price_usd

    # Create a final dictionary with both assets and liabilities data
    final_data = {
        "Assets": assets_dict,
        "Assets Total": {
            "USD": locale.format_string('%.2f', total_assets_usd, grouping=True),
            "BTC": f"{total_assets_btc:.8f}" if bitcoin_price_usd and bitcoin_price_usd != 0 else "N/A"
        },
        "Liabilities": liabilities_dict,
        "Liabilities Total": {
            "USD": locale.format_string('%.2f', total_liabilities_usd, grouping=True),
            "BTC": f"{total_liabilities_btc:.8f}" if bitcoin_price_usd and bitcoin_price_usd != 0 else "N/A"
        }
    }

    # Save the data to a JSON file with a timestamp as the filename
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    folder_name = "HistoricalData"
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)

    json_file = f"{folder_name}/Data_{timestamp}.json"
    with open(json_file, "w") as file:
        json.dump(final_data, file, indent=4)

    return json_file

def compare_historical_data():
    # Open a file dialog to select multiple files for comparison
    folder_name = "HistoricalData"
    files = filedialog.askopenfilenames(initialdir=folder_name, title="Select files for comparison", filetypes=[("JSON files", "*.json")])

    if not files:
        # No files selected
        return

    # Create a new Toplevel window for comparison
    comparison_window = tk.Toplevel()
    comparison_window.title("Historical Data Comparison")

    comparison_text = tk.Text(comparison_window, wrap="word", font=("Courier New", 10))
    comparison_text.pack(fill="both", expand=True)

    comparison_text.insert(tk.END, "Comparison of Historical Data\n\n")

    # Regular expression pattern to match the timestamp in the filename
    timestamp_pattern = r"Data_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})"

    # Load and display data from selected files
    for file in files:
        with open(file, "r") as file_data:
            data = json.load(file_data)

            # Extract the timestamp from the file path using regular expression
            match = re.search(timestamp_pattern, file)
            if match:
                timestamp = match.group(1)
            else:
                timestamp = "Unknown Timestamp"

            # Insert the bold date with a tag
            comparison_text.insert(tk.END, f"Date: ", "bold")
            comparison_text.insert(tk.END, f"{timestamp}\n", "bold")

            if "Assets" in data:
                comparison_text.insert(tk.END, "Assets\n", "bold")
                total_assets_usd = 0
                total_assets_btc = 0
                for account, values in data["Assets"].items():
                    usd_value = float(values["USD"].replace(",", ""))
                    btc_value = float(values["BTC"]) if values["BTC"] != "N/A" else None
                    total_assets_usd += usd_value
                    total_assets_btc += btc_value if btc_value is not None else 0

                    comparison_text.insert(tk.END, f"{account}: {values['USD']} USD / {values['BTC']} BTC\n")

                comparison_text.insert(tk.END, f"Total Assets: {locale.format_string('%.2f', total_assets_usd, grouping=True)} USD / {total_assets_btc:.8f} BTC\n")
                comparison_text.insert(tk.END, "\n")

            if "Liabilities" in data:
                comparison_text.insert(tk.END, "Liabilities\n", "bold")
                total_liabilities_usd = 0
                total_liabilities_btc = 0
                for account, values in data["Liabilities"].items():
                    usd_value = float(values["USD"].replace(",", ""))
                    btc_value = float(values["BTC"]) if values["BTC"] != "N/A" else None
                    total_liabilities_usd += usd_value
                    total_liabilities_btc += btc_value if btc_value is not None else 0

                    comparison_text.insert(tk.END, f"{account}: {values['USD']} USD / {values['BTC']} BTC\n")

                comparison_text.insert(tk.END, f"Total Liabilities: {locale.format_string('%.2f', total_liabilities_usd, grouping=True)} USD / {total_liabilities_btc:.8f} BTC\n")
                comparison_text.insert(tk.END, "\n\n\n")

    # Configure the bold tag
    comparison_text.tag_configure("bold", font=("Courier New", 10, "bold"))

    comparison_text.config(state=tk.DISABLED)  # Disable text editing
    
def display_data():
    data = load_data()

    # Get the Bitcoin price
    try:
        bitcoin_price_usd = get_bitcoin_value()
    except:
        # Handle error fetching Bitcoin price (you can customize this based on your preference)
        bitcoin_price_usd = None

    # Format and display the asset values
    assets_formatted = []
    for asset, value in data["assets"].items():
        if bitcoin_price_usd and bitcoin_price_usd != 0:
            bitcoin_equivalent = value / bitcoin_price_usd
        else:
            bitcoin_equivalent = None

        if bitcoin_equivalent is not None:
            assets_formatted.append(f"{asset:<15}: {locale.format_string('%.2f', value, grouping=True)} USD ({bitcoin_equivalent:.8f} BTC)")
        else:
            assets_formatted.append(f"{asset:<15}: {locale.format_string('%.2f', value, grouping=True)} USD (N/A BTC)")

    # Determine the maximum number of rows between assets and liabilities
    max_rows = max(len(assets_formatted), len(data["liabilities"]))

    # Add blank entries to assets for missing rows
    assets_formatted += [""] * (max_rows - len(assets_formatted))

    assets_text.set("\n".join(assets_formatted))

    # Format and display the liability values
    liabilities_formatted = []
    for liability, value in data["liabilities"].items():
        if bitcoin_price_usd and bitcoin_price_usd != 0:
            bitcoin_equivalent = value / bitcoin_price_usd
        else:
            bitcoin_equivalent = None

        if bitcoin_equivalent is not None:
            liabilities_formatted.append(f"{liability:<20}: {locale.format_string('%.2f', value, grouping=True)} USD ({bitcoin_equivalent:.8f} BTC)")
        else:
            liabilities_formatted.append(f"{liability:<20}: {locale.format_string('%.2f', value, grouping=True)} USD (N/A BTC)")

    # Add blank entries to liabilities for missing rows
    liabilities_formatted += [""] * (max_rows - len(liabilities_formatted))

    liabilities_text.set("\n".join(liabilities_formatted))

    # Calculate and display total assets and liabilities
    total_assets_usd = sum(data["assets"].values())
    total_liabilities_usd = sum(data["liabilities"].values())

    if bitcoin_price_usd and bitcoin_price_usd != 0:
        total_assets_btc = total_assets_usd / bitcoin_price_usd
        total_liabilities_btc = total_liabilities_usd / bitcoin_price_usd
    else:
        total_assets_btc = None
        total_liabilities_btc = None

    if total_assets_btc is not None:
        assets_text.set(assets_text.get() + f"\n{'-' * 40}\nTotal Assets: {locale.format_string('%.2f', total_assets_usd, grouping=True)} USD ({total_assets_btc:.8f} BTC)")
    else:
        assets_text.set(assets_text.get() + f"\n{'-' * 40}\nTotal Assets: {locale.format_string('%.2f', total_assets_usd, grouping=True)} USD (N/A BTC)")

    if total_liabilities_btc is not None:
        liabilities_text.set(liabilities_text.get() + f"\n{'-' * 40}\nTotal Liabilities: {locale.format_string('%.2f', total_liabilities_usd, grouping=True)} USD ({total_liabilities_btc:.8f} BTC)")
    else:
        liabilities_text.set(liabilities_text.get() + f"\n{'-' * 40}\nTotal Liabilities: {locale.format_string('%.2f', total_liabilities_usd, grouping=True)} USD (N/A BTC)")

def main():
    global assets_text, liabilities_text, bitcoin_label, bitcoin_price_usd

    root = tk.Tk()
    root.title("Wealth Tracker")

    # Set the window width (height will be adjusted automatically)
    #root.geometry("1100x400")  # Set your desired width here, height will adjust automatically


    # Create a button to manually update the Bitcoin price
    manual_update_button = tk.Button(root, text="Update", command=manual_update_bitcoin_price)
    manual_update_button.grid(row=0, column=4, padx=10, pady=5, sticky="w")

    # Define StringVar variables
    assets_text = tk.StringVar()
    liabilities_text = tk.StringVar()

    # Schedule periodic updates for Bitcoin price
    schedule.every(5).minutes.do(update_bitcoin_data)

    # Load Bitcoin price data if available
    try:
        with open(BITCOIN_FILE, "r") as file:
            bitcoin_data = json.load(file)
            # Check if the stored data is not older than 5 minutes
            if int(time.time()) - bitcoin_data["timestamp"] < 5 * 60:
                bitcoin_price_usd = bitcoin_data["price_usd"]
            else:
                bitcoin_price_usd = get_bitcoin_value()
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file doesn't exist or has invalid data, fetch Bitcoin price
        bitcoin_price_usd = get_bitcoin_value()

    # Update Bitcoin value display in the GUI
    if bitcoin_price_usd is not None:
        bitcoin_label = tk.Label(root, text=f"Bitcoin Price per USD: {locale.format_string('%.2f', bitcoin_price_usd, grouping=True)}", font=("Arial", 10))
    else:
        bitcoin_label = tk.Label(root, text="Bitcoin Price per USD: N/A", font=("Arial", 10))
    bitcoin_label.grid(row=0, column=2, padx=10, pady=5, sticky="e", columnspan=2)  # Span the last two columns

    assets_label = tk.Label(root, text="ASSETS", font=("Arial", 12, "bold"))
    assets_label.grid(row=1, column=0, padx=10, pady=5, sticky="n")

    # Add an empty label for the empty column
    empty_label = tk.Label(root, text="", font=("Arial", 12, "bold"))
    empty_label.grid(row=1, column=1, padx=10, pady=5, sticky="n")

    liabilities_label = tk.Label(root, text="LIABILITIES", font=("Arial", 12, "bold"))
    liabilities_label.grid(row=1, column=2, padx=10, pady=5, sticky="n")

    assets_display = tk.Label(root, textvariable=assets_text, font=("Courier New", 10), justify="left", anchor="w")
    assets_display.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

    # Add an empty label for the empty column
    empty_label = tk.Label(root, text="", font=("Courier New", 10))
    empty_label.grid(row=2, column=1, padx=10, pady=5, sticky="nsew")

    liabilities_display = tk.Label(root, textvariable=liabilities_text, font=("Courier New", 10), justify="left", anchor="w")
    liabilities_display.grid(row=2, column=2, padx=10, pady=5, sticky="nsew")

    # Set the grid configuration to make rows and columns expandable
    root.grid_rowconfigure(2, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=0)  # Make the empty column non-expandable
    root.grid_columnconfigure(2, weight=1)
    root.grid_columnconfigure(3, weight=1)

    # Create the top menu
    top_menu = tk.Menu(root)
    root.config(menu=top_menu)

    # Create the "File" menu and its options
    file_menu = tk.Menu(top_menu, tearoff=0)
    top_menu.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Add Sub Account", command=add_sub_account)
    file_menu.add_command(label="Modify Values", command=modify_values)
    file_menu.add_command(label="Modify Sub Account Name", command=modify_sub_account_name)
    file_menu.add_command(label="Remove Sub Account", command=remove_sub_account)
    file_menu.add_command(label="Save Data", command=save_current_data)
    file_menu.add_command(label="Compare Historical Data", command=compare_historical_data)

    # Display the initial data
    display_data()

    # Schedule periodic updates for Bitcoin price
    root.after(10000, update_and_reschedule, root)  # Initial scheduling after 10 seconds

    root.mainloop()  # Start the Tkinter event loop

if __name__ == "__main__":
    main()
