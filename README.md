# drive-health-check
A tool to verify the health and authenticity of your hard drives.
<br/><br/>
With concerns about used drives being resold as new, it's crucial to check your storage devices before trusting them. This tool helps you quickly assess a drive’s condition, usage history, and overall health to ensure you get exactly what you paid for.
<br/><br/>
  What This Tool Does:<br/>
 - Health Status – Detect signs of wear, bad sectors, and lifespan indicators.<br/>
 - Usage History – Check power-on hours and total data written.<br/>
 - SMART Data Analysis – Review key attributes reported by the drive.<br/>
 - Peace of Mind – Confirm whether your drive is genuinely new or previously used.<br/>

<h3>Getting Started</h3><br/>
<b>Prerequisites</b><br/>
You need Python 3 installed on your system.<br/>
<br/>
<b>Install Dependencies</b><br/>
Run the following command to install the required dependencies:<br/>

```pip install WeasyPrint==52.5 pycairo PyGObject```
<br/>

<b>Note:</b> On some Linux distributions, you may need additional system dependencies:<br/>

<b>Debian/Ubuntu:</b><br/>
```sudo apt install libgtk-3-dev libpango1.0-dev libcairo2-dev```
<br/>

<b>Fedora:</b><br/>
```sudo dnf install gtk3-devel pango-devel cairo-devel```
<br/>

<b>MacOS:</b> Ensure you have brew installed, then run:<br/>
```brew install gtk+3 pango cairo```
<br/>


<h3>Running the Script</h3><br/>
Download smartctl (depends on your OS) and place it in the same directory as drive-checker.py:<br/>

<b>Windows:</b> Use bin/smartctl.exe<br/>
<b>Linux:</b> Use bin/smartctl<br/>
<b>Mac:</b> Use bin/smartctl_mac (rename it to smartctl)<br/>

Run the script with administrator privileges:<br/>
```sudo python3 drive-checker.py```
<br/>

<b>Using the Prebuilt Executable</b><br/>
An executable version of the tool is available in the <i>builds</i> folder.<br/>

On Windows: Right-click → <i>Run as Administrator</i><br/>


<h3>Building the Executable Yourself</h3><br/>
If you want to generate the executable manually, use pyinstaller:
<br/>
<b>Install dependencies:</b><br/>

```pip install WeasyPrint==52.5 pyinstaller```
<br/>

<b>Build the executable:</b><br/>

<b>Linux/macOS:</b><br/>
```pyinstaller --onefile drive-checker.py --add-data "bin/smartctl:bin"```
<br/>

<b>Windows:</b><br/>
```pyinstaller --onefile drive-checker.py --add-data "bin/smartctl.exe;bin"```
<br/>

If using macOS, rename smartctl_mac to smartctl before running the script.<br/>

<b>Additional Notes</b><br/>
WeasyPrint relies on pycairo and PyGObject, which require GTK and Cairo.<br/>
If you encounter any issues, ensure the necessary system packages are installed.<br/>