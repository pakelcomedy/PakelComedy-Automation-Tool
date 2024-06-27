import subprocess

# Define the path to the Brave browser executable
brave_path = '/usr/bin/brave-browser'  # Update this path based on your system

# Define the URL you want to open
url = 'https://www.instagram.com/accounts/emailsignup/'

# Command to open the URL in a new Brave window
subprocess.run([brave_path, '--new-window', url])