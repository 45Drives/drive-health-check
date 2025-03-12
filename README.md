# drive-health-check
A tool to check the health of your drives and ensure they are as old or new as you think they are.

With recent concerns about used drives being resold as new, it’s more important than ever to verify the condition of your storage devices. This tool helps you quickly assess the health, usage, ensuring you get exactly what you paid for.
<br/>
  What This Tool Does:
    - Health Status: Check for signs of wear, bad sectors, and overall lifespan.<br/>
    - Usage History: See how many hours the drive has been used and how much data has been written.<br/>
    - SMART Data Analysis: Review key health indicators reported by the drive itself.<br/>
    - Peace of Mind: Confirm whether your drive is truly new or has been previously used.<br/>


There is a python script (drive-checker.py) and an executable file.

The script can be run as follows:

pip install WeasyPrint==52.5 pyinstaller
pyinstaller --onefile drive-checker.py --add-data "bin/smartctl:bin"
pyinstaller --onefile drive-checker.py --add-data "bin/smartctl.exe;bin"

rename smartctl_mac to smartctl

sudo python3 drive-checker.py --drive-check


The executable is "main_with_drive-check.exe" and can be run.
