# drive-health-check
<h2>Linux</h2>
<h3>Getting Started</h3>
<b>Prerequisites</b><br/>
You need Python 3 installed on your system.<br/>

<b>Install Python 3 (Linux - Debian/Ubuntu)</b>

```sudo apt update```
```sudo apt install python3```

<br/>

Verify the installation:
```python3 --version```

<b>Install Dependencies</b><br/>
Run the following command to install the required dependencies:<br/>

```pip install WeasyPrint==52.5 pycairo PyGObject```
<br/>

<b>Note:</b> You may need additional system dependencies:<br/>

```sudo apt install libgtk-3-dev libpango1.0-0 libcairo2-dev```
<br/>

<h3>Running the Script</h3>
Download smartctl and place it in the same directory as drive-checker.py:<br/>

```bin/smartctl```

Run the script with administrator privileges:<br/>
```sudo python3 drive-checker.py```
<br/>

<b>Using the Prebuilt Executable</b><br/>
An executable version of the tool is available in the <i>builds</i> folder.<br/>

<h3>Building the Executable Yourself</h3>
If you want to generate the executable manually, use pyinstaller:
<br/>
<b>Install dependencies:</b><br/>

```pip install WeasyPrint==52.5 pyinstaller```
<br/>

<b>Build the executable:</b><br/>

```cd app```
```pyinstaller --onefile drive-checker.py --add-data "bin/smartctl:bin"```
<br/>

<b>Additional Notes</b><br/>
WeasyPrint relies on pycairo and PyGObject, which require GTK and Cairo.<br/>
If you encounter any issues, ensure the necessary system packages are installed.<br/>