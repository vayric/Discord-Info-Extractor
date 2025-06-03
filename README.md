# Discord Info Extractor

A Python script to extract and display information from a Discord account using its token. The script provides a clean console interface and allows saving the extracted information to text files.

## Features

- Retrieves basic account information (username, ID, creation date, email, etc.)
- Displays server membership with owner/member status
- Shows account badges and Nitro status
- Colorful console output for better readability
- Option to save extracted information to text files

## Requirements

- Python 3.x
- Required packages (install via `pip install -r requirements.txt`):
  - `requests`
  - `colorama`

## Usage

1. Clone or download the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the script:
   ```bash
   python main.py
   ```
4. Enter your Discord token when prompted
5. View the extracted information in the console
6. Choose to save the information to a file (saved in the `results` folder)

## File Naming

Saved files are named in the format:
```
results/[username]_[date].txt
```
Example: `results/JohnDoe_1234_2023-11-15.txt`

## Notes

- The script requires a valid Discord account token
- Tokens are sensitive - never share them or commit them to version control
- Saved files contain the same information displayed in the console

## Example Output

```
=== DISCORD ACCOUNT INFORMATION ===

● Basic Information
👤 Username: JohnDoe#1234
🆔 ID: 123456789012345678
📅 Created: 2021-05-15 14:30:22
📧 Email: johndoe@example.com
📞 Phone: None
🛡️ 2FA: ✅ Active
💎 Nitro: Nitro Classic
🎖️ Badges: HypeSquad Bravery, Bug Hunter

● Servers (5):
👑 Owner → My Cool Server
🔹 Member → Gaming Community
... 
