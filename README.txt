Myanmar Map Generator - QGIS Plugin
====================================

INSTALLATION
------------
Option 1: Run install.bat (Windows)
   Double-click install.bat

Option 2: Manual Installation
   1. Copy the entire "myanmar_map_plugin" folder to:
      Windows: %APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\
      Linux: ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
      Mac: ~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/

   2. Restart QGIS

   3. Go to: Plugins menu -> Manage and Install Plugins

   4. Find "Myanmar Map Generator" and check the box to enable it

USAGE
-----
1. Click the Myanmar Map Generator button in toolbar (or Plugins menu)
2. Select your data files:
   - State shapefile (boundaries)
   - Township shapefile
   - Excel data file
3. Map the columns:
   - P_Code fields for joining
   - Category column for colors
   - Township and Label columns for labels
4. Choose color mode:
   - Multi-color: each category gets different color
   - Single color: data vs no-data
5. Set map title and options
6. Click "Preview Map" to see in QGIS canvas
7. Click "Generate & Export" to export PNG/PDF

FEATURES
--------
- Multi-color mode (by category)
- Single color mode (binary)
- Custom color picker
- Label settings
- A3/A4 page sizes
- PNG and PDF export
- Auto column detection from Excel

REQUIREMENTS
------------
- QGIS 3.x
- pandas library (usually included with QGIS)
