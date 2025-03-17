# drive-health-check
<h2>Windows</h2>
<h3>Getting Started</h3>
<b>Prerequisites</b><br/>
You will need Python 3 installed on your system.<br/>
<!-- 
<b>Install Python 3 (Windows)</b>
- Download the latest Python 3 installer from python.org.<br/>
- Run the installer and check the box for "Add Python to PATH".<br/>
- Click Install Now and follow the prompts.<br/> -->
<b>Install Python 3 (Windows)</b>
<br/>

- Download the latest Python 3 version from the Windows Store App.<br/>
- Wait for the installation to complete<br/>

Verify the installation by opening Command Prompt (cmd) and running:
<br/>

```python --version```

<br/>

<h3>**Recommended**: Using the Prebuilt Executable</h3>
An executable version of the tool is available in the <i>builds</i> folder.<br/>

Right-click → <i>Run as Administrator</i><br/>



<br/>
<h3>Running the Script</h3>

<b>Install Dependencies</b><br/>
Make sure you have pip installed:<br/>
```pip --version```
<br/>
If it isn't, run:
```python -m pip install --upgrade pip```<br/>

Run the following command to install the required dependencies:<br/>

```pip install WeasyPrint==52.5 pycairo PyGObject```
<br/>

Download smartctl and place it in the same directory as drive-checker.py:<br/>

```bin/smartctl.exe```<br/>

Run the script with administrator privileges:<br/>
```sudo python3 drive-checker.py```
<br/>


<br/>
<h3>Building the Executable Yourself</h3>
If you want to generate the executable manually, use pyinstaller:
<br/>
<b>Install dependencies:</b><br/>

```pip install WeasyPrint==52.5 pyinstaller```
Get GTK-for-Windows-Runtime-Environment-Installer. I think just installing will work but we downloaded the zip and added dlls manually to build. See Build below.
<br/>

<b>Build the executable:</b><br/>
make sure to add the GTK runtime binaries
```cd app```
```pyinstaller --onefile drive-checker.py --add-data "bin/smartctl.exe;bin" --add-binary "bin/*.dll;."```
<br/>

<b>Additional Notes</b><br/>
WeasyPrint relies on pycairo and PyGObject, which require GTK and Cairo.<br/>
If you encounter any issues, ensure the necessary system packages are installed.<br/>
