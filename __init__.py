"""
Myanmar Map Generator QGIS Plugin
"""

def classFactory(iface):
    from .myanmar_map import MyanmarMapPlugin
    return MyanmarMapPlugin(iface)
