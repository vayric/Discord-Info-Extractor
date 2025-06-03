import requests
import json
from datetime import datetime
from time import sleep
import colorama
from colorama import Fore, Back, Style
import os

# Initialize colorama
colorama.init()

class Colors:
    RESET = Style.RESET_ALL
    TITLE = Fore.LIGHTBLUE_EX + Style.BRIGHT  
    SECTION = Fore.LIGHTBLUE_EX + Style.BRIGHT
    ITEM = Fore.LIGHTBLUE_EX + Style.BRIGHT   
    ERROR = Fore.WHITE + Style.BRIGHT  
    SUCCESS = Fore.WHITE + Style.BRIGHT   
    WARNING = Fore.WHITE + Style.BRIGHT  
    HIGHLIGHT = Fore.WHITE + Style.BRIGHT   
    DIM = Style.DIM

def animated_loading(message, duration=3.0, steps=20):   
    print(f"\n{Colors.ITEM}{message}", end='', flush=True)
    delay = duration/steps
    for i in range(steps):
        progress = (i + 1)/steps
        bar_length = 50   
        filled_length = int(bar_length * progress)
        bar = '=' * filled_length + '-' * (bar_length - filled_length)
        percentage = int(progress * 100)
        print(f"\r{Colors.ITEM}{message} [{bar}] {Colors.HIGHLIGHT}{percentage}%{Colors.RESET}", end='', flush=True)
        sleep(delay)
    print(f"\n{Colors.ITEM}Done!{Colors.RESET}")

def main():
    while True:
        print(f"\n{Colors.TITLE}┌─────────────────────────────────────────────┐")
        print(f"│           {Colors.HIGHLIGHT}DISCORD INFO EXTRACTOR{Colors.TITLE}            │")
        print(f"└─────────────────────────────────────────────┘{Colors.RESET}")
        
        token = input(f"\n{Colors.ITEM}🔑 Enter your Discord token: {Colors.RESET}").strip()
        
        if token.lower() == 'exit':
            break
            
        if not token:
            print(f"{Colors.ERROR}❌ No token provided{Colors.RESET}")
            continue
            
        try:
            animated_loading("Connecting to Discord API", 1.2)
            extractor = DiscordInfoExtractor(token)
            info = extractor.get_all_info()
            display_info(info)
        except Exception as e:
            print(f"{Colors.ERROR}❌ Error: {str(e)}{Colors.RESET}")
        
        choice = input(f"\n{Colors.ITEM}🔄 Do you want to perform another search? ({Colors.SUCCESS}y{Colors.ITEM}/{Colors.ERROR}n{Colors.ITEM}): {Colors.RESET}").strip().lower()
        if choice != 'y':
            print(f"\n{Colors.SUCCESS}✨ Operation completed!{Colors.RESET}")
            break

class DiscordInfoExtractor:
    def __init__(self, token):
        self.token = token
        self.headers = {
            'Authorization': token,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.base_url = 'https://discord.com/api/v9'
    


    def fetch_data(self, endpoint):
        try:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                timeout=15
            )
            
            if response.status_code == 401:
                raise ValueError(f"{Colors.ERROR}Invalid or expired token{Colors.RESET}")
            return response.json() if response.status_code == 200 else None
            
        except requests.exceptions.RequestException as e:
            print(f"{Colors.ERROR}⚠️ Connection error: {str(e)}{Colors.RESET}")
            return None

    def get_all_info(self):
        info = {}
        total_steps = 4   
        current_step = 0
        
        def update_progress():
            nonlocal current_step
            current_step += 1
            progress = current_step / total_steps
            bar_length = 20
            filled_length = int(bar_length * progress)
            bar = '=' * filled_length + '-' * (bar_length - filled_length)
            print(f"\r{Colors.ITEM}[{bar}]", end='', flush=True)
            if current_step == total_steps:
                print()

        user_data = self.fetch_data('/users/@me')
        if not user_data:
            raise ValueError(f"{Colors.ERROR}Failed to retrieve user data{Colors.RESET}")
        info['basic_info'] = {
            'username': f"{user_data.get('username')}#{user_data.get('discriminator')}",
            'global_name': user_data.get('global_name'),
            'user_id': user_data.get('id'),
            'avatar_url': f"https://cdn.discordapp.com/avatars/{user_data.get('id')}/{user_data.get('avatar')}.png?size=1024" if user_data.get('avatar') else None,
            'banner_url': f"https://cdn.discordapp.com/banners/{user_data.get('id')}/{user_data.get('banner')}.png?size=1024" if user_data.get('banner') else None,
            'banner_color': user_data.get('banner_color'),
            'accent_color': user_data.get('accent_color'),
            'bio': user_data.get('bio'),
            'creation_date': datetime.fromtimestamp(((int(user_data.get('id')) >> 22) + 1420070400000) / 1000).strftime('%Y-%m-%d %H:%M:%S'),
            'flags': self.parse_user_flags(user_data.get('flags', 0)),
            'public_flags': self.parse_user_flags(user_data.get('public_flags', 0)),
            'locale': user_data.get('locale'),
            'nsfw_allowed': user_data.get('nsfw_allowed'),
            'mfa_enabled': user_data.get('mfa_enabled'),
            'email': user_data.get('email'),
            'verified': user_data.get('verified'),
            'phone': user_data.get('phone'),
            'premium_type': self.parse_nitro(user_data.get('premium_type', 0))
        }
        update_progress()

        guilds = self.fetch_data('/users/@me/guilds')
        if guilds:
            info['guilds'] = []
            for guild in guilds:
                perms = int(guild.get('permissions', 0))
                info['guilds'].append({
                    'id': guild.get('id'),
                    'name': guild.get('name'),
                    'icon_url': f"https://cdn.discordapp.com/icons/{guild.get('id')}/{guild.get('icon')}.png" if guild.get('icon') else None,
                    'owner': (perms & 0x8) == 0x8,
                    'permissions': perms
                })
        update_progress()

        relationships = self.fetch_data('/users/@me/relationships')
        if relationships:
            info['relationships'] = {
                'friends': [r for r in relationships if r.get('type') == 1],
                'blocked': [r for r in relationships if r.get('type') == 2]
            }
        update_progress()

        connections = self.fetch_data('/users/@me/connections')
        if connections:
            info['connections'] = connections
        update_progress()

        return info

    @staticmethod
    def parse_nitro(premium_type):
        nitro_map = {
            0: 'No Nitro',
            1: 'Nitro Classic',
            2: 'Nitro',
            3: 'Nitro Basic'
        }
        return nitro_map.get(premium_type, 'Unknown')

    @staticmethod
    def parse_user_flags(flags):
        flags_map = {
            1 << 0: 'Staff',
            1 << 1: 'Partner',
            1 << 3: 'Bug Hunter',
            1 << 6: 'HypeSquad Bravery',
            1 << 7: 'HypeSquad Brilliance',
            1 << 8: 'HypeSquad Balance',
            1 << 14: 'Bug Hunter Level 2',
            1 << 18: 'Certified Moderator'
        }
        return [desc for bit, desc in flags_map.items() if flags & bit]

def display_info(info):
    print(f"\n{Fore.CYAN + Style.BRIGHT}=== DISCORD ACCOUNT INFORMATION ==={Colors.RESET}")
    basic = info.get('basic_info', {})
    
    print(f"\n{Colors.SECTION}● Basic Information{Colors.RESET}")
    print(f"{Colors.ITEM}👤 Username: {Colors.HIGHLIGHT}{basic.get('username')}{Colors.RESET}")
    print(f"{Colors.ITEM}🆔 ID: {Colors.HIGHLIGHT}{basic.get('user_id')}{Colors.RESET}")
    print(f"{Colors.ITEM}📅 Created: {Colors.HIGHLIGHT}{basic.get('creation_date')}{Colors.RESET}")
    print(f"{Colors.ITEM}📧 Email: {Colors.HIGHLIGHT}{basic.get('email') or 'None'}{Colors.RESET}")
    print(f"{Colors.ITEM}📞 Phone: {Colors.HIGHLIGHT}{basic.get('phone') or 'None'}{Colors.RESET}")
    print(f"{Colors.ITEM}🛡️ 2FA: {Colors.HIGHLIGHT}{'✅ Active' if basic.get('mfa_enabled') else '❌ Inactive'}{Colors.RESET}")
    print(f"{Colors.ITEM}💎 Nitro: {Colors.HIGHLIGHT}{basic.get('premium_type')}{Colors.RESET}")
    print(f"{Colors.ITEM}🎖️ Badges: {Colors.HIGHLIGHT}{', '.join(basic.get('flags', ['None']))}{Colors.RESET}")

    if 'guilds' in info:
        print(f"\n{Colors.SECTION}● Servers ({len(info['guilds'])}):{Colors.RESET}")
        for guild in info['guilds']:
            status = f"{Fore.YELLOW}👑 Owner" if guild['owner'] else f"{Colors.ITEM}🔹 Member"
            print(f"{status}{Colors.RESET} → {Colors.HIGHLIGHT}{guild['name']}{Colors.RESET}")

    save_choice = input(f"\n{Colors.ITEM}💾 Do you want to save this information to a file? ({Colors.SUCCESS}y{Colors.ITEM}/{Colors.ERROR}n{Colors.ITEM}): {Colors.RESET}").strip().lower()
    if save_choice == 'y':
        if not os.path.exists('results'):
            os.makedirs('results')
        username = info.get('basic_info', {}).get('username', 'unknown').replace('#', '_')
        date = datetime.now().strftime('%Y-%m-%d')
        filename = f"results/{username}_{date}.txt"
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(f"=== DISCORD ACCOUNT INFORMATION ===\n\n")
            file.write(f"● Basic Information\n")
            basic = info.get('basic_info', {})
            file.write(f"👤 Username: {basic.get('username')}\n")
            file.write(f"🆔 ID: {basic.get('user_id')}\n")
            file.write(f"📅 Created: {basic.get('creation_date')}\n")
            file.write(f"📧 Email: {basic.get('email') or 'None'}\n")
            file.write(f"📞 Phone: {basic.get('phone') or 'None'}\n")
            file.write(f"🛡️ 2FA: {'✅ Active' if basic.get('mfa_enabled') else '❌ Inactive'}\n")
            file.write(f"💎 Nitro: {basic.get('premium_type')}\n")
            file.write(f"🎖️ Badges: {', '.join(basic.get('flags', ['None']))}\n\n")
            if 'guilds' in info:
                file.write(f"● Servers ({len(info['guilds'])}):\n")
                for guild in info['guilds']:
                    status = "👑 Owner" if guild['owner'] else "🔹 Member"
                    file.write(f"{status} → {guild['name']}\n")
        print(f"{Colors.SUCCESS}📁 Information saved to {filename}{Colors.RESET}")

if __name__ == "__main__":
    main()

