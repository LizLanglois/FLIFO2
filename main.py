import subprocess
import time
##from datetime import date
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Load the Excel file
df = pd.read_excel('flights2.xlsx')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}


def get_flight_status(url):
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Locating the div by its class name
        status_div = soup.find('div', class_='ticket__StatusContainer-sc-1rrbl5o-17')

        if status_div:
            return status_div.get_text(separator=" ", strip=True)
        else:
            return None
    else:
        print(f"Error {response.status_code}: Unable to fetch the webpage.")
        return None


def scrape_status():
    for index, row in df.iterrows():
        url = row['check']
        flight_status = get_flight_status(url)
        if flight_status:
            print(f"Flight Status for {url}: {flight_status}")
            df.at[index, 'Status'] = flight_status
        else:
            print(f"Could not fetch the flight status for {url}.")
            df.at[index, 'updated'] = "Error or No Data"


# Save the updated DataFrame back to the same Excel file
    df.to_excel('flights2.xlsx', index=False)

def display_status_and_save_to_file(file_path):
    df_app = pd.read_excel('flights2.xlsx')
    columns_to_display = ["alinedesc", "fltno", "origin", "destinat", "deptime", "arrtime", "Status"]
    df_display = df_app[columns_to_display].copy()

    def format_status(status):
        if isinstance(status, str) and ('delayed' in status.lower() or 'diverted' in status.lower() or 'cancelled' in status.lower()):
            return f'<span style="color:red">{status}</span>'
        return status

    df_display['Status'] = df_display['Status'].apply(format_status)

    # Create an HTML table with formatting for the 'Status' column
    html_table = '<table border="1"><tr>'
    for column in df_display.columns:
        html_table += f'<th>{column}</th>'
    html_table += '</tr>'

    for _, row in df_display.iterrows():
        html_table += '<tr>'
        for column in df_display.columns:
            value = row[column]
            if column == 'Status':
                value = format_status(value)
            html_table += f'<td>{value}</td>'
        html_table += '</tr>'
    html_table += '</table>'

    # Write the HTML table to the specified file (overwriting the previous content)
    with open(file_path, 'w') as file:
        file.write(html_table)

def main():
    count = 0
    max_count = 100

    while count < max_count:
        print(f"Refreshing data - Count: {count + 1}")
        scrape_status()
        display_status_and_save_to_file('output.md')  # Use the file name 'output.md'
        commit_and_push_changes()  # Commit and push changes to GitHub
        count += 1
        time.sleep(600)

    print("Reached the maximum count of 100. Program complete.")

def commit_and_push_changes():
    try:
        # Add all changes to the Git staging area
        subprocess.run(['git', 'add', '.'])

        # Commit the changes
        display_status_and_save_to_file('output.md')  # Use the file name 'output.md'

        # Push the changes to the remote GitHub repository
        subprocess.run(['git', 'push'])

        print("Changes committed and pushed to GitHub.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()