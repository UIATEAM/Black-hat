import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
import time

# Function to run the tool after entering inputs
def run_tool():
    chat_name = entry_chat_name.get()
    
    if not chat_name:
        messagebox.showerror("Error", "Please enter the chat name.")
        return

    try:
        # Set up GeckoDriver for Firefox
        firefox_options = Options()
        firefox_profile_path = "/home/kali/.mozilla/firefox/your_profile.default"  # Replace with the correct path to your Firefox profile
        firefox_options.set_preference("profile", firefox_profile_path)
        service = Service(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=firefox_options)

        # Navigate to Telegram Web
        driver.get('https://web.telegram.org/')
        wait = WebDriverWait(driver, 60)

        # Ensure login
        def wait_for_login():
            try:
                # Wait until the search element is loaded to confirm successful login
                wait.until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Search"]')))
                print("Logged in successfully")
            except Exception as e:
                print(f"Error during login: {e}")
                driver.quit()

        wait_for_login()

        # Search for the chat
        def search_for_chat(chat_name):
            search_box = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Search"]')))
            search_box.send_keys(chat_name)
            time.sleep(2)  # Wait for search results to appear

            try:
                chat_element = wait.until(EC.presence_of_element_located((By.XPATH, f'//div[contains(@class, "chat-item") and .//span[contains(text(), "{chat_name}")]]')))
                chat_element.click()
                print("Chat found")
            except Exception as e:
                print(f"Error during chat search: {e}")
                driver.quit()

        # Collect messages from the chat
        def collect_messages():
            messages = []
            last_height = driver.execute_script("return document.body.scrollHeight")

            while True:
                # Collect messages from the visible elements
                message_elements = driver.find_elements(By.XPATH, '//div[@class="message-text"]')  # Ensure the XPath is correct
                for message in message_elements:
                    text = message.text
                    if text and text not in messages:  # Add non-empty and non-duplicate messages
                        messages.append(text)
                
                # Attempt to scroll down to load more messages
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # Wait for new messages to load
                
                # Check if more messages have been loaded
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            return messages

        # Save messages to a text file
        def save_messages_to_file(messages):
            with open('messages.txt', 'w', encoding='utf-8') as file:
                for message in messages:
                    file.write(message + '\n')

        # Execute the steps
        search_for_chat(chat_name)
        messages = collect_messages()
        save_messages_to_file(messages)

        # Close the browser
        driver.quit()
        messagebox.showinfo("Success", "Messages have been collected and saved successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Set up the application window
app = tk.Tk()
app.title("UIA TEAM")

# Set up the user interface
tk.Label(app, text="Chat name or ID:").pack(pady=5)
entry_chat_name = tk.Entry(app, width=50)
entry_chat_name.pack(pady=5)
tk.Button(app, text="Run Tool", command=run_tool).pack(pady=10)

# Start the application
app.mainloop()
