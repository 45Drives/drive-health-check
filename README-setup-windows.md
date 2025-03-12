# drive-health-check
<h2>Windows</h2>
<h3>Getting Started</h3>
<b>Prerequisites</b><br/>
You need Python 3 installed on your system.<br/>

<b>Install Python 3 (Windows)</b>
<!-- - Download the latest Python 3 installer from python.org.<br/>
- Run the installer and check the box for "Add Python to PATH".<br/> -->
<br/>
Click Install Now and follow the prompts.<br/>
- Download the latest Python 3 version from the Windows Store App.<br/>
- Wait for the installation to complete<br/>

Verify the installation by opening Command Prompt (cmd) and running:
<br/>

```python --version```

<br/>
If that command doesn't work, try:<br/>

```py --version```

<b>Install Dependencies</b><br/>
Run the following command to install the required dependencies:<br/>

```pip install WeasyPrint==52.5 pycairo PyGObject```
<br/>

<h3>Running the Script</h3>
Download smartctl and place it in the same directory as drive-checker.py:<br/>

```bin/smartctl.exe```<br/>

Run the script with administrator privileges:<br/>
```sudo python3 drive-checker.py```
<br/>

<b>Using the Prebuilt Executable</b><br/>
An executable version of the tool is available in the <i>builds</i> folder.<br/>

Right-click → <i>Run as Administrator</i><br/>

<h3>Building the Executable Yourself</h3>
If you want to generate the executable manually, use pyinstaller:
<br/>
<b>Install dependencies:</b><br/>

```pip install WeasyPrint==52.5 pyinstaller```
<br/>

<b>Build the executable:</b><br/>

```pyinstaller --onefile drive-checker.py --add-data "bin/smartctl.exe;bin"```
<br/>

<b>Additional Notes</b><br/>
WeasyPrint relies on pycairo and PyGObject, which require GTK and Cairo.<br/>
If you encounter any issues, ensure the necessary system packages are installed.<br/>