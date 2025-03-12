# drive-health-check
A tool to check the health of your drives and ensure they are as old or new as you think they are.
<br/><br/>
With recent concerns about used drives being resold as new, it’s more important than ever to verify the condition of your storage devices. This tool helps you quickly assess the health, usage, ensuring you get exactly what you paid for.
<br/><br/>
  What This Tool Does:<br/>
    - Health Status: Check for signs of wear, bad sectors, and overall lifespan.<br/>
    - Usage History: See how many hours the drive has been used and how much data has been written.<br/>
    - SMART Data Analysis: Review key health indicators reported by the drive itself.<br/>
    - Peace of Mind: Confirm whether your drive is truly new or has been previously used.<br/>


There is a python script (drive-checker.py) and an executable file.
<br/>
The script can be run as follows:
<br/>
Depending on what operating system you are running on, get the appropriate file from the <i>bin</i> folder<br/> and place it next to drive-checker.py in the same directory.<br/>
Windows: smartctl.exe<br/>
Linux: smartctl<br/>
Mac: smartctl_mac<br/>
<br/>
Next, run 'pip install WeasyPrint==52.5' and then run script with 'sudo python3 drive-checker.py'
<br/>
<br/>

To build yourself:
<br/>
pip install WeasyPrint==52.5 pyinstaller<br/>
pyinstaller --onefile drive-checker.py --add-data "bin/smartctl:bin"<br/>
pyinstaller --onefile drive-checker.py --add-data "bin/smartctl.exe;bin"<br/>
<br/>
rename smartctl_mac to smartctl<br/>
