import argparse
import json
import subprocess
import sys
import re
import platform
import shutil
import os
import ctypes
import csv
import webbrowser
from weasyprint import HTML, CSS
    

def get_local_smartctl_path():
    if getattr(sys, 'frozen', False):  # running from PyInstaller bundle
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    if platform.system() == "Windows":
        return os.path.join(base_dir, "bin", "smartctl.exe")
    else:
        return os.path.join(base_dir, "bin", "smartctl")
    

def resolve_smartctl_path():
    local = get_local_smartctl_path()
    
    if os.path.isfile(local):
        return local
    elif shutil.which("smartctl"):
        return "smartctl"
    raise RuntimeError("smartctl not found locally or system-wide.")


SMARTCTL = resolve_smartctl_path()
    
# ------------------------------
# Helper: Check for Admin on Windows
# ------------------------------

def is_admin():
    """Return True if running with administrative privileges on Windows."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def run_as_admin():
    """Re-launch the current script with admin privileges, hiding the console window."""
    params = " ".join([f'"{arg}"' for arg in sys.argv])
    SW_HIDE = 1  # Hide window
    ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, SW_HIDE)
    if ret <= 32:
        print("Failed to elevate privileges.")
        sys.exit(1)
    sys.exit(0)


def get_smart_data(device):
    """Run smartctl to retrieve SMART data for a given device."""
    try:
        result = subprocess.run(
            [SMARTCTL, '-a', device, '--json'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=True
        )
        stdout = result.stdout
        return get_smart_data2(stdout)
    except Exception as e:
        try:
            return get_smart_data2(e.stdout)
        except Exception as e2: 
            return f"Error retrieving SMART data: {e2}"


def get_smart_data2(stdout):
    # print(stdout)
    smart_json = json.loads(stdout)
    # print(f'smart_json: { smart_json}')
    # print(json.dumps(smart_json, indent=4))
    smart_info = {
        "Device": smart_json["device"]["name"],
        "Model": smart_json["model_name"],
        "Serial #": smart_json["serial_number"],
        "Capacity":'-1',
        "Temperature (°C)": f'{smart_json.get("temperature", {}).get("current")}',
        "Power On Hrs.": smart_json.get("power_on_time", {}).get("hours"),
        "Power Cycle Ct.": smart_json.get("power_cycle_count"),
    }
    
    if "user_capacity" in smart_json:
        smart_info["Capacity"] = format_capacity(smart_json["user_capacity"]["bytes"])
    elif "nvme_total_capacity" in smart_json:
        smart_info["Capacity"] = format_capacity(smart_json["nvme_total_capacity"])
    else:
        smart_info["Capacity"] = -1

    if "ata_smart_attributes" in smart_json:
        table = smart_json["ata_smart_attributes"]["table"]

        def get_attr(name, fallback) -> str:
            return next(
                iter([attr["raw"]["string"] for attr in table if attr["name"] == name]),
                fallback,
            )

        smart_info["Power On Hrs."] = smart_info["Power On Hrs."] or int(get_attr("Power_On_Hours", -1))
        smart_info["Power Cycle Ct."] = smart_info["Power Cycle Ct."] or int(get_attr("Power_Cycle_Count", -1))
        smart_info["Temperature (°C)"] = smart_info["Temperature (°C)"] or int(get_attr("Temperature_Celsius", -1))
    
    smart_info["SMART Status"] = (
        "OK"
        if "smart_status" in smart_json.keys() and smart_json["smart_status"]["passed"]
        else "POOR"
    )
    smart_info["Diagnosis"] = get_drive_diagnosis(smart_info)
    
    # print(f'smartInfo: {json.dumps(smart_info, indent=4)}')
    return smart_info

def get_drive_diagnosis(smart_info: dict) -> str:
    """Classify drive age based only on Power-On Hours."""
    
    # Extract power-on hours (default to 0 if missing)
    power_on_hours = int(smart_info.get("Power On Hrs.", 0))  # Drive age in hours

    # Adjusted classification thresholds
    HIGH_USAGE_THRESHOLD = 35040
    MID_USAGE_THRESHOLD = 500
    
     # 🚀 **Green - Healthy Condition**
    if power_on_hours == 'N/A' or power_on_hours <= 1:
        return "Lightly Used"  # lightly used condition
    
    # 🚀 **Green - Healthy Condition**
    if power_on_hours < MID_USAGE_THRESHOLD:
        return "New"  # Good condition

    # ⚠️ **Yellow - Warning Condition**
    elif MID_USAGE_THRESHOLD <= power_on_hours < HIGH_USAGE_THRESHOLD:
        return "Used"  # Some signs of aging

    # ❌ **Red - Critical Condition**
    else:
        return "Old"  # Drive is aging or near end-of-life
    
    # Default case (shouldn't happen)
    return "Unknown"


# ------------------------------
# Drive Scanning and Summary (Background Thread)
# ------------------------------

def scan_drives():
    """Return a list of device names using smartctl --scan."""
    drives = []
    try:
        result = subprocess.run(
            [SMARTCTL, '--scan'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=True
        )
        for line in result.stdout.splitlines():
            if line.strip():
                if line.startswith("/dev/csmi") or line.startswith("/dev/sr"):
                    continue
                parts = line.split()
                if parts:
                    device = parts[0]
                    drives.append(device)
    except subprocess.CalledProcessError as e:
        print("Error scanning drives:", e)
    return drives


def format_capacity(bytes_size):
    if bytes_size >= 1024**4:
        return f"{bytes_size / (1024**4):.2f} TB"
    elif bytes_size >= 1024**3:
        return f"{bytes_size / (1024**3):.2f} GB"
    elif bytes_size >= 1024**2:
        return f"{bytes_size / (1024**2):.2f} MB"
    elif bytes_size >= 1024:
        return f"{bytes_size / 1024:.2f} KB"
    else:
        return f"{bytes_size} Bytes"


def output_drive_check_info_text(smart_data):
    """Display drive information with colored diagnosis labels."""
    devices = list(smart_data)
    # print(f"DEBUG: Found {len(devices)} block devices.\n")

    if not devices:
        print("No drives found! Are you running with sufficient permissions?")
        return

    # ANSI Color Codes
    GREEN = "\033[92m"  # Green
    YELLOW = "\033[93m"  # Yellow
    ORANGE = "\033[38;5;214m"  # Yellow
    RED = "\033[91m"  # Red
    RESET = "\033[0m"  # Reset to default terminal color

    print("\nLEGEND:")
    print(f"{GREEN}Green{RESET}: means the drive is NEW (under 1 hour of usage time)")
    print(f"{YELLOW}Yellow{RESET}: means the drive is LIGHTLY USED (between 1 and 500 hours of usage time).")
    print(f"{ORANGE}Orange{RESET}: means the drive is USED (between 500 and 30,040 hours of usage time).")
    print(f"{RED}Red{RESET}: means the drive is OLD, with over 4 years of usage time.")
    print("     (Keep an eye on this one for errors, and consider replacing it with a new one.)\n")


    # Table Header
    print("{:<10} {:<28} {:<20} {:<18} {:<15} {:<10}".format(
        "Device", "Model", "Serial", "Capacity", "Hours", "Result"
    ))
    print("=" * 120)

    for device in devices:
        drive = device
        if isinstance(drive, dict) == False:
            print(drive)
            continue
            
        if drive:
            diagnosis = drive["Diagnosis"]

            # Assign color based on diagnosis
            if diagnosis == "New":
                color = GREEN
            elif diagnosis == "Lightly Used":
                color = YELLOW
            elif diagnosis == "Used":
                color = ORANGE
            elif diagnosis == "Old":
                color = RED
            else:
                color = RESET  # Default

            # Print drive details with color-coded diagnosis
            print("{:<10} {:<28} {:<20} {:<18} {:<15} {}{:<10}{}".format(
                drive["Device"],
                drive["Model"],
                drive["Serial #"],
                drive.get("Capacity", -1),
                drive.get("Power On Hrs.", -1),
                color, diagnosis, RESET  # Apply color and reset
            ))
            # print(f'drive: {drive}')



def output_drive_check_info_csv(smart_infos, filename="drive_info.csv"):
    """Write drive SMART info to a CSV file."""
    if not smart_infos:
        print("No drive data available to write.")
        return
    
    keys = smart_infos[0].keys()  # Extract headers from first drive entry
    
    with open(filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        writer.writerows(smart_infos)
    
    print(f"Drive info saved to {filename}")

def generate_drive_report_html(smart_infos):
    """Generate a well-structured and styled HTML string for the drive report."""
    if not smart_infos:
        return "<html><body><h2>No drive data available.</h2></body></html>"

    html_content = """
    <html>
    <head>
        <title>45Drives Disk Check-Up</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h3 { text-align: center; color: #b91c1c; }
            table { width: 100%; border-collapse: collapse; table-layout: fixed; word-wrap: normal; }
            th, td { border: 1px solid black; padding: 4px; text-align: left; }
            th { font-size: 10px; background-color: #475569; color: white; text-transform: uppercase; }
            td { font-size: 8px; word-wrap: break-word;}
            p { font-size: 10px; text-align: right; }
            
            /* Increase font size for HTML output */
            @media screen {
                th { font-size: 15px; }
                td { font-size: 13px; }
                p { font-size: 12px; }
            }

            /* Keep original font size for PDF output */
            @media print {
                th { font-size: 9px; }
                td { font-size: 7px; }
                p { font-size: 10px; }
            }

           /* Conditional styling for Diagnosis */
            .lightly-used { background-color: #ffa500; }   /* Light Green - Lightly Used */
            .new { background-color: #03d103; }   /* Green - New */
            .used { background-color: #ffff00;  } /* Yellow - Used */
            .old { background-color: #ff3f3f; }   /* Red - Old */
            .unknown { background-color: #D9D9D9;  }   /* Grey - Unknown */
        

        </style>
    </head>
    <body>
        <h3>45Drives Disk Check-Up</h3>
        <div>
            <p><span class="new"><b>Green</b></span> means the drive brand new right out of the package(under 1 hour of usage).</p>
            <p><span class="lightly-used"><b>Orange</b></span> means the drive is Lightly Used, with between 1 and 500 hours .</p>
            <p><span class="used"><b>Yellow</b></span> means the drive is Used, with between 500 and 30,040 hours (4 years) of usage.</p>
            <p><span class="old"><b>Red</b></span> means the drive is Old, with over 4 years of usage. Keep an eye on this one for errors, and consider replacing it with a new one.</p>
        </div>
        <table>
            <tr>
                <th>Device</th>
                <th>Model</th>
                <th>Serial #</th>
                <th>Capacity</th>
                <th>Temp (°C)</th>
                <th>Power On Hrs.</th>
                <th>Power Cycle Ct.</th>
                <th>SMART Status</th>
                <th>Result</th>
            </tr>
    """

    # **Process Each Drive's Data**
    for drive in smart_infos:
        diagnosis = drive.get("Diagnosis", "Unknown")

        # Assign a class based on diagnosis for conditional styling
        diagnosis_class = "unknown"
        if diagnosis == "New":
            diagnosis_class = "new"
        elif diagnosis == "Lightly Used":
            diagnosis_class = "lightly-used"
        elif diagnosis == "Used":
            diagnosis_class = "used"
        elif diagnosis == "Old":
            diagnosis_class = "old"

        html_content += f"""
            <tr>
                <td>{drive.get("Device", "N/A")}</td>
                <td>{drive.get("Model", "N/A")}</td>
                <td>{drive.get("Serial #", "N/A")}</td>
                <td>{drive.get("Capacity", "N/A")}</td>
                <td>{drive.get("Temperature (°C)", "N/A")}</td>
                <td>{drive.get("Power On Hrs.", "N/A")}</td>
                <td>{drive.get("Power Cycle Ct.", "N/A")}</td>
                <td>{drive.get("SMART Status", "N/A")}</td>
                <td class="{diagnosis_class}"><b>{diagnosis}</b></td>
            </tr>
        """

    html_content += """
        </table>
    </body>
    </html>
    """

    return html_content  # Return the HTML string


def output_drive_check_info_pdf(smart_infos, filename="drive_info.pdf", landscape=False):
    """Generate a PDF from an HTML report using WeasyPrint without creating an HTML file."""
    if not smart_infos:
        print("No drive data available to write.")
        return

    # Generate HTML content dynamically
    html_content = generate_drive_report_html(smart_infos)

    # Define CSS for landscape mode
    landscape_css = CSS(string='@page { size: A4 landscape; }') if landscape else None

    # Convert HTML to PDF directly from string
    if landscape:
        HTML(string=html_content).write_pdf(filename, stylesheets=[landscape_css])
    else:
        HTML(string=html_content).write_pdf(filename)

    print(f"Drive info saved as PDF: {filename}")

    # Open the generated PDF
    open_pdf(filename)
    
    
def output_drive_check_info_html(smart_infos, filename="drive_info.html"):
    """Generate an HTML file and open it in a browser."""
    html_content = generate_drive_report_html(smart_infos)

    with open(filename, "w") as f:
        f.write(html_content)

    print(f"Drive info saved to {filename}")

    open_html(filename)



def open_html(filename):
    """Open an HTML file using the best available web browser on any OS, ensuring proper handling for Linux with sudo."""
    file_path = os.path.abspath(filename)

    # Ensure the file exists before attempting to open
    if not os.path.exists(file_path):
        print(f"Error: The file {file_path} does not exist.")
        return

    # Linux-specific logic to open as the original user if script was run with sudo
    if platform.system() == "Linux":
        original_user = os.getenv("SUDO_USER")  # Get the original user running the script
        if original_user:
            home_dir = os.path.expanduser(f"~{original_user}")  # Get the user's home directory
            xauthority_path = os.path.join(home_dir, ".Xauthority")

            # Preferred browsers in order of priority
            linux_browsers = ["google-chrome", "firefox", "chromium", "brave", "xdg-open"]

            for browser in linux_browsers:
                if shutil.which(browser):
                    try:
                        subprocess.Popen(
                            ["sudo", "-u", original_user, "DISPLAY=:0", f"XAUTHORITY={xauthority_path}", browser, file_path],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True
                        )
                        print(f"Opening HTML in {browser} as the original user.")
                        return
                    except Exception as e:
                        print(f"Failed to open with {browser}: {e}")

    # Try opening in the default web browser
    try:
        if webbrowser.open("file://" + file_path):
            print("Opening HTML in the default web browser.")
            return
    except Exception as e:
        print(f"Failed to open in default browser: {e}")

    # Manual fallback: Check for specific browsers per OS
    browsers = {
        "Linux": ["google-chrome", "firefox", "chromium", "brave", "xdg-open"],
        "Darwin": ["open"],  # macOS uses 'open' command
        "Windows": ["cmd", "/c", "start", "", file_path]  # Windows uses 'start' command
    }

    os_type = platform.system()
    available_browsers = browsers.get(os_type, [])

    # Try the first available browser
    for browser in available_browsers:
        if shutil.which(browser) or browser == "cmd":  # Windows uses 'cmd'
            try:
                subprocess.Popen([browser, file_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
                print(f"Opening HTML with {browser}.")
                return
            except Exception as e:
                print(f"Failed to open with {browser}: {e}")

    print("No suitable web browser found. Please open the file manually:", file_path)
    
    
def open_pdf(filename):
    """Open a PDF file using the best available viewer based on OS and installed applications."""
    file_path = os.path.abspath(filename)
    original_user = os.getenv("SUDO_USER")  # Get original user if running with sudo

    # Define known PDF viewers per OS
    pdf_viewers = {
        "Linux": {
            "okular": [],    # KDE
            "evince": [],    # GNOME
            "google-chrome": ["--window-size=1200,800"],
            "firefox": ["--width=1200", "--height=800"],
            "xdg-open": []                 # Generic fallback
        },
        "Darwin": {  # macOS
            "open": []  # macOS default app launcher
        },
        "Windows": {
            "explorer": [],  # Windows default PDF viewer
            "chrome": ["--window-size=1200,800"],
            "firefox": ["--width=1200", "--height=800"],
            "AcroRd32.exe": []  # Adobe Acrobat
        }
    }

    os_type = platform.system()
    available_viewers = pdf_viewers.get(os_type, {})

    # Check if a viewer exists on the system
    viewer = next((v for v in available_viewers if shutil.which(v) is not None), None)

    if not viewer:
        print("No known PDF viewer found. Please install a PDF reader.")
        return

    try:
        command = [viewer, file_path]

        if os_type == "Linux" and original_user:
            # Run as the original user if script is run with sudo
            command = ["sudo", "-u", original_user, "DISPLAY=:0", "XAUTHORITY=/home/"+original_user+"/.Xauthority"] + command

        # Run the process detached from the terminal
        subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)

        print("PDF opened successfully. Returning to menu...")

    except Exception as e:
        print(f"Error opening PDF file: {e}")


def intro_text():
    print("With recent concerns about used drives being resold as new, it’s more important than ever to verify the condition of your storage devices.")
    print("This tool helps you quickly assess the health, usage, ensuring you get exactly what you paid for.")
    print("What This Tool Does:")
    print("\t✅ Health Status: Check for signs of wear, bad sectors, and overall lifespan.")
    print("\t✅ Usage History: See how many hours the drive has been used and how much data has been written.")
    print("\t✅ SMART Data Analysis: Review key health indicators reported by the drive itself.")
    print("\t✅ Peace of Mind: Confirm whether your drive is truly new or has been previously used.")
    
    input("Press Any Key to Continue\n")

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')
    
# ------------------------------
# Main Entry Point
# ------------------------------
def main():
    
    # Force admin elevation on Windows before showing UI.
    if platform.system() == "Windows" and not is_admin():
        run_as_admin()
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--quiet", action="store_true", help="Suppresses the intro text.")
    parser.add_argument("--json", action="store_true", help="Outputs JSON and exits.")
    args = parser.parse_args()
        
    drives = scan_drives()
    smart_infos = list(map(get_smart_data, drives))
    
    info = smart_infos
    
    # Print JSON and exit if --json flag is used
    if args.json:
        print(json.dumps(info, indent=4))
        return  # Exit early
    
    clear_terminal()
    # Skip intro text if --quiet is used
    if not args.quiet:
        intro_text()

    clear_terminal()
    while True:
        print("Welcome to the Drive Check!\n")
        print("Please choose output format:")
        print("1. text")
        print("2. csv")
        print("3. pdf")
        print("4. html")
        print("5. Exit the program")

        choice = input("Enter the number corresponding to your choice: ")

        if choice == "1":
            output_drive_check_info_text(smart_infos)
        elif choice == "2":
            output_drive_check_info_csv(smart_infos)
        elif choice == "3":
            output_drive_check_info_pdf(smart_infos)
        elif choice == "4":
            output_drive_check_info_html(smart_infos)
        elif choice == "5":
            print("Exiting the program. Goodbye!")
            break
        else:
            print("Invalid choice, please try again.")


if __name__ == "__main__":
    main()
