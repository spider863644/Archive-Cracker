import colorama
import os
from colorama import *
import zipfile
import rarfile
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import sys
import argparse
import urllib.request
colorama.init(autoreset=True)

def info():
    os.system('clear' if os.name != 'nt' else 'cls')
    header = """
 █████  ██████   ██████ ██   ██ ██ ██    ██ ███████ ███████        ██████ ██████   █████   ██████ ██   ██ ███████ ██████  
██   ██ ██   ██ ██      ██   ██ ██ ██    ██ ██      ██            ██      ██   ██ ██   ██ ██      ██  ██  ██      ██   ██ 
███████ ██████  ██      ███████ ██ ██    ██ █████   ███████ █████ ██      ██████  ███████ ██      █████   █████   ██████  
██   ██ ██   ██ ██      ██   ██ ██  ██  ██  ██           ██       ██      ██   ██ ██   ██ ██      ██  ██  ██      ██   ██ 
██   ██ ██   ██  ██████ ██   ██ ██   ████   ███████ ███████        ██████ ██   ██ ██   ██  ██████ ██   ██ ███████ ██   ██ 
    """
    print(f"{Fore.YELLOW}{header}")
    print(f"{Fore.RED}Version 1.0".center(90))
    print(f"{Fore.YELLOW}ARCHIVE-CRACKER\n".center(75))
    print(f"{Fore.GREEN}+++ Developer: {Fore.CYAN}Spider Anongreyhat {Fore.GREEN}+++")
    print(f"{Fore.GREEN}Github: spider863644\nTelegram: Anonspideyy\nCommunity: TermuxHackz Society")

def try_zip_password(zf, password, verbose=False):
    try:
        if verbose:
            print(f"[*] Trying: {password}")
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
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            bar = tqdm(total=len(password_list), desc="Cracking ZIP", disable=silent or verbose)
            futures = {executor.submit(try_zip_password, zf, pwd, verbose): pwd for pwd in password_list}
            for future in futures:
                result = future.result()
                bar.update(1)
                if result:
                    if not silent:
                        print(f"{Fore.GREEN}\n[+] Password found for ZIP: {Fore.YELLOW}{result}")
                    found = result
                    break
            bar.close()
        if not found and not silent:
            print(f"{Fore.RED}\n[-] Password not found for ZIP.")
        return found

def try_rar_password(rf, password, verbose=False):
    try:
        if verbose:
            print(f"[*] Trying: {password}")
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
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            bar = tqdm(total=len(password_list), desc="Cracking RAR", disable=silent or verbose)
            futures = {executor.submit(try_rar_password, rf, pwd, verbose): pwd for pwd in password_list}
            for future in futures:
                result = future.result()
                bar.update(1)
                if result:
                    if not silent:
                        print(f"{Fore.GREEN}\n[+] Password found for RAR: {Fore.CYAN}{result}")
                    found = result
                    break
            bar.close()
        if not found and not silent:
            print(f"{Fore.RED}\n[-] Password not found for RAR.")
        return found

def load_passwords(path_or_url):
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        try:
            print(f"{Fore.YELLOW}[+] Downloading wordlist from URL: {path_or_url}")
            response = urllib.request.urlopen(path_or_url)
            data = response.read().decode('utf-8', errors='ignore')
            return [line.strip() for line in data.splitlines() if line.strip()]
        except Exception as e:
            print(f"{Fore.RED}[!] Failed to download wordlist: {e}")
            sys.exit(1)
    else:
        if not os.path.exists(path_or_url):
            print(f"{Fore.RED}[!] Wordlist file not found: {path_or_url}")
            sys.exit(1)
        with open(path_or_url, 'r', encoding='utf-8', errors='ignore') as f:
            return [line.strip() for line in f if line.strip()]
if __name__ == "__main__":
    info()
    print("\n\n")

    parser = argparse.ArgumentParser(
        description="Archive-Cracker | Crack password-protected ZIP or RAR files using a wordlist.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  python3 archive_cracker.py zip secrets.zip rockyou.txt
  python3 archive_cracker.py rar secret.rar wordlist.txt --verbose
  python3 archive_cracker.py zip file.zip list.txt --silent
  python3 archive_cracker.py rar file.rar list.txt --threads 50

Flags:
  --verbose      Show each password being tried
  --silent       Hide all output except result
  --threads NUM  Number of threads to use (default: 100)
        """
    )

    parser.add_argument("type", help="Archive type: 'zip' or 'rar'")
    parser.add_argument("archive", help="Path to the archive file to be cracked")
    parser.add_argument("wordlist", help="Path to the wordlist containing possible passwords")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose mode (prints each attempt)")
    parser.add_argument("--silent", action="store_true", help="Silent mode (suppress output except result)")
    parser.add_argument("--threads", type=int, default=100, help="Number of threads to use (default: 100)")

    args = parser.parse_args()

    if args.verbose and args.silent:
        print(f"{Fore.RED}[!] Cannot use --verbose and --silent together.")
        sys.exit(1)

    archive_type = args.type.strip().lower()
    archive_path = args.archive.strip()
    wordlist_path = args.wordlist.strip()
    threads = args.threads

    passwords = load_passwords(wordlist_path)

    if archive_type == "zip":
        crack_zip(archive_path, passwords, max_workers=threads, verbose=args.verbose, silent=args.silent)
    elif archive_type == "rar":
        crack_rar(archive_path, passwords, max_workers=threads, verbose=args.verbose, silent=args.silent)
    else:
        print(f"{Fore.RED}[!] Unsupported archive type. Use 'zip' or 'rar'.")