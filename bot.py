from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class Meganet:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "*/*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Host": "api.meganet.app",
            "Origin": "https://meganet.app",
            "Referer": "https://meganet.app/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": FakeUserAgent().random
        }
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Ping {Fore.BLUE + Style.BRIGHT}Meganet - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    async def load_proxies(self, use_proxy_choice: bool):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = content.splitlines()
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = f.read().splitlines()
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def mask_account(self, account):
        mask_account = account[:6] + '*' * 6 + account[-6:]
        return mask_account
    
    def print_message(self, account, proxy, color, message):
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(account)} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
            f"{color + Style.BRIGHT} {message} {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
        )

    def print_question(self):
        while True:
            try:
                print("1. Run With Monosans Proxy")
                print("2. Run With Private Proxy")
                print("3. Run Without Proxy")
                choose = int(input("Choose [1/2/3] -> ").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "Run With Monosans Proxy" if choose == 1 else 
                        "Run With Private Proxy" if choose == 2 else 
                        "Run Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{proxy_type} Selected.{Style.RESET_ALL}")
                    return choose
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

    async def user_data(self, address: str, proxy=None, retries=5):
        url = f"https://api.meganet.app/wallets?address={address}&refcode=JQC59E"
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=self.headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue

                return self.print_message(address, proxy, Fore.RED, f"GET User Data Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")

    async def user_earning(self, address: str, point_id: str, proxy=None, retries=5):
        url = f"https://api.meganet.app/points/point-today/{point_id}"
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=self.headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue

                return self.print_message(address, proxy, Fore.RED, f"GET Earning Data Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
    
    async def task_lists(self, address: str, user_id: str, proxy=None, retries=5):
        url = f"https://api.meganet.app/wallets/task/{user_id}"
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=self.headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue

                return self.print_message(address, proxy, Fore.RED, f"GET Task Lists Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
    
    async def complete_tasks(self, address: str, user_id: str, task_id: str, proxy=None, retries=5):
        url = f"https://api.meganet.app/wallets/task/{user_id}/{task_id}"
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.patch(url=url, headers=self.headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue

                return self.print_message(address, proxy, Fore.WHITE, f"Task {task_id}{Fore.RED+Style.BRIGHT} Not Completed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")

    async def update_uptime(self, address: str, user_id: str, proxy=None, retries=5):
        url = f"https://api.meganet.app/wallets/uptime/{user_id}"
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.patch(url=url, headers=self.headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue

                return self.print_message(address, proxy, Fore.RED, f"Update Node Uptime Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")

    async def process_get_user_data(self, address: str, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(address) if use_proxy else None
        user = None
        while user is None:
            user = await self.user_data(address, proxy)
            if not user:
                proxy = self.rotate_proxy_for_account(address) if use_proxy else None
                continue
        
            user_id = user.get("_id")
            point_id = user.get("point", {}).get("_id")
            self.print_message(address, proxy, Fore.GREEN, "GET User Data Success")
            return user_id, point_id

    async def process_get_user_earning(self, address: str, point_id: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            point = "N/A"
            balance = await self.user_earning(address, point_id, proxy)
            if balance:
                point = balance.get("pointsFarmToday", 0)

            self.print_message(address, proxy, Fore.WHITE, f"Earning Today {point} PTS")
            await asyncio.sleep(10 * 60)

    async def process_complete_tasks(self, address: str, user_id: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            tasks = await self.task_lists(address, user_id, proxy)
            if tasks:
                for task_id, is_completed in tasks.items():
                    if task_id in ["_id", "__v"] or is_completed:
                        continue
                    else:
                        complete = await self.complete_tasks(address, user_id, task_id, proxy)
                        if complete:
                            self.print_message(address, proxy, Fore.WHITE, 
                                f"Task {task_id} "
                                f"{Fore.GREEN + Style.BRIGHT}Is Completed{Style.RESET_ALL}"
                            )
                self.print_message(address, proxy, Fore.GREEN, "All Available Tasks Is Completed"
                )
            await asyncio.sleep(24 * 60 * 60)

    async def process_update_node_uptime(self, address: str, user_id: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            update = await self.update_uptime(address, user_id, proxy)
            if update and update.get("message") == "Update uptime successful!":
                self.print_message(address, proxy, Fore.GREEN, "Update Node Uptime Success")
            
            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Wait For 2 Minutes For Next Update...{Style.RESET_ALL}",
                end="\r"
            )
            await asyncio.sleep(2 * 60)

    async def process_accounts(self, address: str, use_proxy: bool):
        user_id, point_id = await self.process_get_user_data(address, use_proxy)
        if user_id and point_id:
            tasks = []
            tasks.append(asyncio.create_task(self.process_get_user_earning(address, point_id, use_proxy)))
            tasks.append(asyncio.create_task(self.process_complete_tasks(address, user_id, use_proxy)))
            tasks.append(asyncio.create_task(self.process_update_node_uptime(address, user_id, use_proxy)))
            await asyncio.gather(*tasks)

    async def main(self):
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]
            
            use_proxy_choice = self.print_question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
            )

            if use_proxy:
                await self.load_proxies(use_proxy_choice)

            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)

            while True:
                tasks = []
                for address in accounts:
                    if address:
                        tasks.append(asyncio.create_task(self.process_accounts(address, use_proxy)))

                await asyncio.gather(*tasks)
                await asyncio.sleep(10)

        except FileNotFoundError as e:
            self.log(f"{Fore.RED+Style.BRIGHT}File 'accounts.txt' Not Found.{Style.RESET_ALL}")
            return
        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        bot = Meganet()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Meganet - BOT{Style.RESET_ALL}                                       "                              
        )