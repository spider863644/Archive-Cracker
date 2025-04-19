import colorama
import os
from colorama import *
import zipfile
import rarfile
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import sys
import requests
import tempfile

colorama.init(autoreset=True)

def info():
    os.system('cls' if os.name == 'nt' else 'clear')
    header = """
 █████  ██████   ██████ ██   ██ ██ ██    ██ ███████ ███████        ██████ ██████   █████   ██████ ██   ██ ███████ ██████  
██   ██ ██   ██ ██      ██   ██ ██ ██    ██ ██      ██            ██      ██   ██ ██   ██ ██      ██  ██  ██      ██   ██ 
███████ ██████  ██      ███████ ██ ██    ██ █████   ███████ █████ ██      ██████  ███████ ██      █████   █████   ██████  
██   ██ ██   ██ ██      ██   ██ ██  ██  ██  ██           ██       ██      ██   ██ ██   ██ ██      ██  ██  ██      ██   ██ 
██   ██ ██   ██  ██████ ██   ██ ██   ████   ███████ ███████        ██████ ██   ██ ██   ██  ██████ ██   ██ ███████ ██   ██ 
    """
    print(f"{Fore.YELLOW}{header}")
    print(f"{Fore.RED}Version 1.1".center(90))
    print(f"{Fore.YELLOW}ARCHIVE-CRACKER\n".center(75))
    print(f"{Fore.GREEN}+++ Developer: {Fore.CYAN}Spider Anongreyhat {Fore.GREEN}+++")
    print(f"{Fore.GREEN}Github: spider863644\nTelegram: Anonspideyy\nCommunity: TermuxHackz Society")

def help_message():
    print(f"""{Fore.CYAN}
Usage:
  python3 archive_cracker.py <zip|rar> <archive_path> <wordlist_path_or_url> [--verbose] [--silent]

Arguments:
  zip/rar           Type of archive to crack (zip or rar)
  archive_path      Path to the password-protected archive
  wordlist_path     Path to the wordlist file or URL

Options:
  --verbose         Print each password being tried
  --silent          Suppress progress bar and verbose output
  -h, --help        Show this help message and exit

Examples:
  python3 archive_cracker.py zip secrets.zip wordlist.txt --verbose
  python3 archive_cracker.py rar protected.rar https://example.com/rockyou.txt --silent
    """)

def try_zip_password(zf, password):
    try:
        zf.extractall(pwd=password.encode('utf-8'))
        return password
    except:
        return None

def crack_zip(zip_path, password_list, max_workers=100, verbose=False, silent=False):
    with zipfile.ZipFile(zip_path) as zf:
        if not any(info.flag_bits & 0x1 for info in zf.infolist()):
            if not silent:
                print(f"{Fore.YELLOW}[!] The ZIP archive is not password-protected.")
            return None

        found = None
        with ThreadPoolExecutor(max_workers=max_workers) as executor, tqdm(total=len(password_list), desc="Cracking ZIP", disable=silent) as pbar:
            futures = {executor.submit(try_zip_password, zf, pwd): pwd for pwd in password_list}
            for future in futures:
                result = future.result()
                pwd = futures[future]
                if verbose and not silent:
                    print(f"{Fore.CYAN}[Trying] {pwd}")
                pbar.update(1)
                if result:
                    if not silent:
                        print(f"{Fore.GREEN}\n[+] Password found for {os.path.basename(zip_path)}: {Fore.YELLOW}{result}")
                    found = result
                    break
        if not found and not silent:
            print(f"{Fore.RED}\n[-] Password not found for {os.path.basename(zip_path)}.")
        return found

def try_rar_password(rf, password):
    try:
        rf.extractall(pwd=password.encode('utf-8'))
        return password
    except:
        return None

def crack_rar(rar_path, password_list, max_workers=100, verbose=False, silent=False):
    with rarfile.RarFile(rar_path) as rf:
        if not rf.needs_password():
            if not silent:
                print(f"{Fore.YELLOW}[!] The RAR archive is not password-protected.")
            return None

        found = None
        with ThreadPoolExecutor(max_workers=max_workers) as executor, tqdm(total=len(password_list), desc="Cracking RAR", disable=silent) as pbar:
            futures = {executor.submit(try_rar_password, rf, pwd): pwd for pwd in password_list}
            for future in futures:
                result = future.result()
                pwd = futures[future]
                if verbose and not silent:
                    print(f"{Fore.CYAN}[Trying] {pwd}")
                pbar.update(1)
                if result:
                    if not silent:
                        print(f"{Fore.GREEN}\n[+] Password found for {os.path.basename(rar_path)}: {Fore.YELLOW}{result}")
                    found = result
                    break
        if not found and not silent:
            print(f"{Fore.RED}\n[-] Password not found for {os.path.basename(rar_path)}.")
        return found

def load_passwords(path_or_url):
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        print(f"{Fore.YELLOW}[!] Downloading wordlist from {path_or_url} ...")
        try:
            response = requests.get(path_or_url, timeout=10)
            response.raise_for_status()
            temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w+', encoding='utf-8')
            temp_file.write(response.text)
            temp_file.close()
            with open(temp_file.name, 'r', encoding='utf-8', errors='ignore') as f:
                return [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"{Fore.RED}[Error] Failed to download wordlist: {e}")
            sys.exit(1)
    else:
        with open(path_or_url, 'r', encoding='utf-8', errors='ignore') as f:
            return [line.strip() for line in f if line.strip()]

if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        help_message()
        sys.exit(0)

    info()
    print("\n\n")

    if len(sys.argv) < 4:
        help_message()
        sys.exit(1)

    archive_type = sys.argv[1].strip().lower()
    archive_path = sys.argv[2].strip()
    wordlist_path = sys.argv[3].strip()

    verbose = "--verbose" in sys.argv
    silent = "--silent" in sys.argv

    passwords = load_passwords(wordlist_path)

    if archive_type == "zip":
        crack_zip(archive_path, passwords, verbose=verbose, silent=silent)
    elif archive_type == "rar":
        crack_rar(archive_path, passwords, verbose=verbose, silent=silent)
    else:
        print(f"{Fore.RED}Unsupported archive type. Use 'zip' or 'rar'.")