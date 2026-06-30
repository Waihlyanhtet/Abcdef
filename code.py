# ========== KEY APPROVED SYSTEM WITH .SO LOGO REPLACEMENT (RUIJIE ASYNC EXTREME -> BYPASS LOGO) ==========
import os
import sys
import time
import json
import requests
import re
import random
import string
import threading
import subprocess
import importlib.util
import builtins
from datetime import datetime, timedelta

# ========== CONFIG ==========
RAW_KEY_LINK = "https://raw.githubusercontent.com/Waihlyanhtet/my-python-project/main/keys.txt"
DEVICE_ID_FILE = ".device_id"
ACCESS_KEY_FILE = ".access_key"
LAST_SEEN_FILE = ".last_seen"
SO_FILE_PATH = "code.cpython-314-aarch64-linux-gnu.so"

# ========== BYPASS1.PY ORIGINAL LOGO ==========
BYPASS_LOGO = r"""
 _    _                               _               
| |  | |                             | |              
| |  | | __ _ _   _ _ __ ___   __ _  | |  _  ___ _ __ 
| |/\| |/ _` | | | | '_ ` _ \ / _` | | |/ // _ \ '__|
\  /\  / (_| | |_| | | | | | | (_| | |   <|  __/ |   
 \/  \/ \__,_|\__, |_| |_| |_|\__,_| |_|\_\\___|_|   
               __/ |                                  
              |___/                                   
"""

# ========== DEVICE ID ==========
def get_device_id():
    if os.path.exists(DEVICE_ID_FILE):
        try:
            with open(DEVICE_ID_FILE, "r") as f:
                return f.read().strip()
        except:
            pass
    try:
        result = subprocess.check_output("whoami", shell=True, encoding='utf-8')
        device_id = result.strip()
        if device_id:
            clean_id = re.sub(r'[^A-Za-z0-9]', '', device_id).upper()
            if len(clean_id) >= 6:
                final_id = clean_id[:6]
            else:
                final_id = clean_id.ljust(6, 'X')
            new_id = f"RUI-{final_id}"
            with open(DEVICE_ID_FILE, "w") as f:
                f.write(new_id)
            return new_id
    except:
        pass
    random_id = "RUI-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    with open(DEVICE_ID_FILE, "w") as f:
        f.write(random_id)
    return random_id

# ========== NETWORK TIME ==========
def get_network_time():
    try:
        res = requests.get("https://www.google.com", timeout=5)
        gmt_str = res.headers.get('Date')
        gmt_dt = datetime.strptime(gmt_str, '%a, %d %b %Y %H:%M:%S %Z')
        mm_time = gmt_dt + timedelta(hours=6, minutes=30)
        return mm_time
    except:
        return None

# ========== DURATION PARSE ==========
def parse_duration(duration_str):
    days = re.search(r'(\d+)\s*(d|day|days)', duration_str, re.I)
    hours = re.search(r'(\d+)\s*(h|hour|hours)', duration_str, re.I)
    minutes = re.search(r'(\d+)\s*(m|min|minute|minutes)', duration_str, re.I)
    d = int(days.group(1)) if days else 0
    h = int(hours.group(1)) if hours else 0
    m = int(minutes.group(1)) if minutes else 0
    return timedelta(days=d, hours=h, minutes=m)

# ========== CORE LICENSE CHECK ==========
def check_online_license(user_key):
    dev_id = get_device_id()
    net_time = get_network_time()
    curr_sys_time = datetime.now()
    
    if os.path.exists(LAST_SEEN_FILE):
        try:
            last_ts = float(open(LAST_SEEN_FILE, "r").read().strip())
            if curr_sys_time.timestamp() < last_ts:
                return False, "Time Travel Detected! Fix your date."
        except:
            pass
    current_working_time = net_time if net_time else curr_sys_time
    with open(LAST_SEEN_FILE, "w") as f:
        f.write(str(current_working_time.timestamp()))
    
    try:
        res = requests.get(RAW_KEY_LINK, timeout=10)
        if res.status_code == 200:
            lines = res.text.splitlines()
            for line in lines:
                if "|" in line:
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) >= 3:
                        if parts[0] == dev_id and parts[1] == user_key:
                            raw_duration = parts[2]
                            if os.path.exists(ACCESS_KEY_FILE):
                                saved_data = open(ACCESS_KEY_FILE, "r").read().strip().split("|")
                                expiry_dt = datetime.fromtimestamp(float(saved_data[1]))
                            else:
                                if not net_time:
                                    return None, "Activation requires internet!"
                                delta = parse_duration(raw_duration)
                                if delta.total_seconds() == 0:
                                    return False, "Invalid Duration!"
                                expiry_dt = net_time + delta
                                with open(ACCESS_KEY_FILE, "w") as f:
                                    f.write(f"{user_key}|{expiry_dt.timestamp()}")
                            if current_working_time < expiry_dt:
                                return True, expiry_dt
                            else:
                                if os.path.exists(ACCESS_KEY_FILE):
                                    os.remove(ACCESS_KEY_FILE)
                                return False, "Key Expired!"
            return False, "Key not found on Server!"
    except Exception as e:
        if os.path.exists(ACCESS_KEY_FILE):
            try:
                s_key, s_exp_ts = open(ACCESS_KEY_FILE, "r").read().strip().split("|")
                expiry_dt = datetime.fromtimestamp(float(s_exp_ts))
                if curr_sys_time < expiry_dt:
                    return True, expiry_dt
                else:
                    return False, "Expired (Offline)"
            except:
                pass
        return None, f"Connection Error: {e}"
    return False, "Access Denied"

# ========== CHECK REALTIME ==========
def check_github_key_realtime():
    if os.path.exists(ACCESS_KEY_FILE):
        try:
            saved_key = open(ACCESS_KEY_FILE, "r").read().strip().split("|")[0]
            status, info = check_online_license(saved_key)
            if status is True:
                days_left = (info - datetime.now()).days
                expiry_str = info.strftime('%Y-%m-%d')
                return (expiry_str, days_left)
            else:
                return False
        except:
            return False
    return False

# ========== SAVE KEY ==========
def save_user_key(key):
    try:
        if os.path.exists(ACCESS_KEY_FILE):
            content = open(ACCESS_KEY_FILE, "r").read().strip()
            if "|" in content:
                old_exp = content.split("|")[1]
                with open(ACCESS_KEY_FILE, "w") as f:
                    f.write(f"{key}|{old_exp}")
            else:
                with open(ACCESS_KEY_FILE, "w") as f:
                    f.write(key)
        else:
            with open(ACCESS_KEY_FILE, "w") as f:
                f.write(key)
        return True
    except:
        return False

# ========== ACTIVATE ==========
def activate_key(user_key):
    status, info = check_online_license(user_key)
    if status is True:
        save_user_key(user_key)
        return True, info
    return False, info

# ========== LOGO OVERRIDE SYSTEM ==========
original_print = builtins.print
original_input = builtins.input
_logo_printed = False

def patched_print(*args, **kwargs):
    global _logo_printed
    # Combine all args into a single string for checking
    combined = ''.join(str(arg) for arg in args)
    
    # Detect original RUIJIE ASYNC EXTREME logo or Telegram@SIRZIPP
    if 'RUIJIE' in combined or 'ASYNC' in combined or 'Telegram@SIRZIPP' in combined or 'SIRZIPP' in combined:
        # Print bypass logo instead
        if not _logo_printed:
            original_print(BYPASS_LOGO, **kwargs)
            _logo_printed = True
        return
    
    # Also detect the ASCII art from screenshot (ESC / - HOME ij END PGUP etc)
    if 'ESC' in combined and 'HOME' in combined and 'PGUP' in combined:
        original_print(BYPASS_LOGO, **kwargs)
        _logo_printed = True
        return
    
    # Detect "Select Mode:" prompt - print bypass logo before it
    if 'Select Mode:' in combined:
        if not _logo_printed:
            original_print(BYPASS_LOGO, **kwargs)
            _logo_printed = True
        return
    
    # Normal print
    original_print(*args, **kwargs)

def patched_input(*args, **kwargs):
    global _logo_printed
    # If input prompt contains the original logo text
    if args:
        combined = ''.join(str(arg) for arg in args)
        if 'RUIJIE' in combined or 'ASYNC' in combined or 'Telegram@SIRZIPP' in combined:
            if not _logo_printed:
                original_print(BYPASS_LOGO)
                _logo_printed = True
            # Return empty to let original input proceed
    return original_input(*args, **kwargs)

def apply_logo_override():
    """Apply monkey-patch to replace RUIJIE ASYNC EXTREME logo with bypass logo"""
    builtins.print = patched_print
    builtins.input = patched_input
    print("[+] Logo override active: RUIJIE ASYNC EXTREME -> BYPASS LOGO")
    
    # Also clear any terminal logo artifacts
    os.system('clear' if os.name != 'nt' else 'cls')

def restore_print():
    """Restore original print function"""
    builtins.print = original_print
    builtins.input = original_input

# ========== RUN .SO FILE ==========
def run_so_module():
    try:
        if not os.path.exists(SO_FILE_PATH):
            print(f"[!] .so file not found: {SO_FILE_PATH}")
            return False
        
        # Apply logo override BEFORE importing .so
        apply_logo_override()
        
        module_name = os.path.splitext(os.path.basename(SO_FILE_PATH))[0].split('.')[0]
        
        # Try direct import
        try:
            import importlib
            module = importlib.import_module(module_name)
            print(f"[+] Imported .so module: {module_name}")
            
            # Try entry points
            entry_functions = ['main', 'run', 'start', 'execute', 'init']
            for func_name in entry_functions:
                if hasattr(module, func_name):
                    func = getattr(module, func_name)
                    if callable(func):
                        print(f"[+] Calling {func_name}() from .so")
                        result = func()
                        restore_print()
                        return True
            
            print(f"[+] Available attributes: {dir(module)}")
            restore_print()
            return True
            
        except ImportError as e:
            print(f"[!] Direct import failed: {e}")
            
            # Try importlib.util
            try:
                spec = importlib.util.spec_from_file_location(module_name, SO_FILE_PATH)
                if spec is None:
                    print("[!] spec_from_file_location returned None")
                    restore_print()
                    return False
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                print(f"[+] Loaded .so using importlib: {module_name}")
                
                entry_functions = ['main', 'run', 'start', 'execute', 'init']
                for func_name in entry_functions:
                    if hasattr(module, func_name):
                        func = getattr(module, func_name)
                        if callable(func):
                            print(f"[+] Calling {func_name}() from .so")
                            result = func()
                            restore_print()
                            return True
                restore_print()
                return True
                
            except Exception as e:
                print(f"[!] importlib loading failed: {e}")
        
        # ctypes fallback
        try:
            import ctypes
            lib = ctypes.CDLL(SO_FILE_PATH)
            print(f"[+] Loaded .so with ctypes")
            
            func_names = ['main', 'run', 'start', 'execute', 'init']
            for name in func_names:
                try:
                    func = getattr(lib, name)
                    result = func()
                    print("[+] Called via ctypes")
                    restore_print()
                    return True
                except AttributeError:
                    continue
                except Exception:
                    continue
            restore_print()
            return True
            
        except Exception as e:
            print(f"[!] ctypes loading failed: {e}")
        
        restore_print()
        return False
        
    except Exception as e:
        print(f"[!] .so execution error: {e}")
        restore_print()
        return False

# ========== MONITOR THREAD ==========
def license_monitor():
    while True:
        time.sleep(30)
        result = check_github_key_realtime()
        if result is False:
            print("\n[!] License expired or revoked during runtime!")
            os._exit(0)

# ========== MAIN ==========
def main():
    # Print bypass logo first
    print(BYPASS_LOGO)
    
    dev_id = get_device_id()
    print(f"Device ID: {dev_id}")
    
    existing = check_github_key_realtime()
    if existing is False:
        print("No valid license found.")
        user_key = input("Enter Access Key: ").strip()
        if not user_key:
            print("No key entered. Exiting.")
            sys.exit(0)
        status, info = activate_key(user_key)
        if status:
            print("Key Activated Successfully!")
            if isinstance(info, datetime):
                days_left = (info - datetime.now()).days
                print(f"Expires in: {days_left} days")
        else:
            print(f"Activation Failed: {info}")
            sys.exit(0)
    else:
        expiry_str, days_left = existing
        print(f"License Active - {days_left} days left (expires {expiry_str})")
    
    monitor_thread = threading.Thread(target=license_monitor, daemon=True)
    monitor_thread.start()
    
    print("\n[+] Key Approved. Loading .so with logo override...")
    time.sleep(1)
    
    success = run_so_module()
    if not success:
        print("[!] Failed to execute .so module")
        sys.exit(1)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Interrupted")
        sys.exit(0)

if __name__ == "__main__":
    main()
