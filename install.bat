@echo off
echo Installing Myanmar Map Generator Plugin...

set PLUGIN_DIR=%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\myanmar_map_plugin

if not exist "%PLUGIN_DIR%" mkdir "%PLUGIN_DIR%"

xcopy /Y /E "%~dp0*" "%PLUGIN_DIR%\"

echo.
echo Plugin installed successfully!
echo.
echo To activate:
echo 1. Restart QGIS
echo 2. Go to Plugins menu - Manage and Install Plugins
echo 3. Find "Myanmar Map Generator" and enable it
echo.
pause
