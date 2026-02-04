"""
Myanmar Map Generator - Main Plugin Class
"""

from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.PyQt.QtGui import QIcon
from pathlib import Path
import os

from .myanmar_map_dialog import MyanmarMapDialog


class MyanmarMapPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = Path(__file__).parent
        self.action = None
        self.dialog = None

    def initGui(self):
        """Initialize plugin GUI"""
        icon_path = str(self.plugin_dir / 'icon.png')

        self.action = QAction(
            QIcon(icon_path) if os.path.exists(icon_path) else QIcon(),
            'Myanmar Map Generator',
            self.iface.mainWindow()
        )
        self.action.triggered.connect(self.run)

        # Add to menu and toolbar
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu('Myanmar Map Generator', self.action)

    def unload(self):
        """Remove plugin from QGIS"""
        self.iface.removePluginMenu('Myanmar Map Generator', self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        """Run the plugin dialog"""
        self.dialog = MyanmarMapDialog(self.iface)
        self.dialog.show()
