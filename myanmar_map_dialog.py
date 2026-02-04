"""
Myanmar Map Generator - Dialog with GUI
"""

from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QPushButton, QComboBox, QLineEdit, QCheckBox, QSpinBox,
    QDoubleSpinBox, QFileDialog, QColorDialog, QMessageBox,
    QRadioButton, QButtonGroup, QFrame, QProgressBar
)
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor
from qgis.core import (
    QgsProject, QgsVectorLayer, QgsField,
    QgsCategorizedSymbolRenderer, QgsSymbol, QgsRendererCategory,
    QgsPalLayerSettings, QgsTextFormat, QgsVectorLayerSimpleLabeling,
    QgsPrintLayout, QgsLayoutExporter, QgsLayoutItemMap,
    QgsLayoutItemLegend, QgsLayoutItemLabel, QgsLayoutSize,
    QgsUnitTypes, QgsLayoutPoint
)
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QFont
from pathlib import Path
import pandas as pd
import os


COLORS = [
    '#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6',
    '#1abc9c', '#34495e', '#e67e22', '#95a5a6', '#16a085',
    '#27ae60', '#2980b9', '#8e44ad', '#c0392b', '#d35400',
    '#7f8c8d', '#bdc3c7', '#ecf0f1', '#f1c40f', '#e8daef',
    '#d5f4e6', '#fdebd0', '#fadbd8', '#d6eaf8', '#ebf5fb'
]


class MyanmarMapDialog(QDialog):
    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.setWindowTitle('Myanmar Map Generator')
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)

        self.excel_df = None
        self.data_color = '#1abc9c'
        self.no_data_color = '#f0f0f0'

        self.setup_ui()

    def setup_ui(self):
        """Create the dialog UI"""
        layout = QVBoxLayout()

        # ===== DATA FILES =====
        data_group = QGroupBox('Data Files')
        data_layout = QVBoxLayout()

        # State shapefile
        state_layout = QHBoxLayout()
        state_layout.addWidget(QLabel('State Shapefile:'))
        self.state_path = QLineEdit()
        self.state_path.setPlaceholderText('Select state boundary shapefile...')
        state_layout.addWidget(self.state_path)
        state_btn = QPushButton('Browse')
        state_btn.clicked.connect(lambda: self.browse_file(self.state_path, 'shp'))
        state_layout.addWidget(state_btn)
        data_layout.addLayout(state_layout)

        # Township shapefile
        township_layout = QHBoxLayout()
        township_layout.addWidget(QLabel('Township Shapefile:'))
        self.township_path = QLineEdit()
        self.township_path.setPlaceholderText('Select township shapefile...')
        township_layout.addWidget(self.township_path)
        township_btn = QPushButton('Browse')
        township_btn.clicked.connect(lambda: self.browse_file(self.township_path, 'shp'))
        township_layout.addWidget(township_btn)
        data_layout.addLayout(township_layout)

        # Excel file
        excel_layout = QHBoxLayout()
        excel_layout.addWidget(QLabel('Excel Data:'))
        self.excel_path = QLineEdit()
        self.excel_path.setPlaceholderText('Select Excel file...')
        self.excel_path.textChanged.connect(self.load_excel_columns)
        excel_layout.addWidget(self.excel_path)
        excel_btn = QPushButton('Browse')
        excel_btn.clicked.connect(lambda: self.browse_file(self.excel_path, 'xlsx'))
        excel_layout.addWidget(excel_btn)
        data_layout.addLayout(excel_layout)

        data_group.setLayout(data_layout)
        layout.addWidget(data_group)

        # ===== COLUMN MAPPING =====
        column_group = QGroupBox('Column Mapping')
        column_layout = QVBoxLayout()

        # P_Code shapefile
        pcode_shp_layout = QHBoxLayout()
        pcode_shp_layout.addWidget(QLabel('P_Code (Shapefile):'))
        self.pcode_shp = QLineEdit('TS_PCODE')
        pcode_shp_layout.addWidget(self.pcode_shp)
        column_layout.addLayout(pcode_shp_layout)

        # P_Code Excel
        pcode_excel_layout = QHBoxLayout()
        pcode_excel_layout.addWidget(QLabel('P_Code (Excel):'))
        self.pcode_excel = QComboBox()
        pcode_excel_layout.addWidget(self.pcode_excel)
        column_layout.addLayout(pcode_excel_layout)

        # Category column
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel('Category Column:'))
        self.category_col = QComboBox()
        category_layout.addWidget(self.category_col)
        column_layout.addLayout(category_layout)

        # Township column
        township_col_layout = QHBoxLayout()
        township_col_layout.addWidget(QLabel('Township Column:'))
        self.township_col = QComboBox()
        township_col_layout.addWidget(self.township_col)
        column_layout.addLayout(township_col_layout)

        # Label column
        label_layout = QHBoxLayout()
        label_layout.addWidget(QLabel('Label Column:'))
        self.label_col = QComboBox()
        label_layout.addWidget(self.label_col)
        column_layout.addLayout(label_layout)

        column_group.setLayout(column_layout)
        layout.addWidget(column_group)

        # ===== COLOR MODE =====
        color_group = QGroupBox('Color Mode')
        color_layout = QVBoxLayout()

        self.color_mode_group = QButtonGroup()
        self.multi_color_radio = QRadioButton('Multi-color (by category)')
        self.multi_color_radio.setChecked(True)
        self.single_color_radio = QRadioButton('Single color (binary)')
        self.color_mode_group.addButton(self.multi_color_radio)
        self.color_mode_group.addButton(self.single_color_radio)
        color_layout.addWidget(self.multi_color_radio)
        color_layout.addWidget(self.single_color_radio)

        # Color pickers
        color_picker_layout = QHBoxLayout()

        self.data_color_btn = QPushButton('Data Color')
        self.data_color_btn.setStyleSheet(f'background-color: {self.data_color}')
        self.data_color_btn.clicked.connect(lambda: self.pick_color('data'))
        color_picker_layout.addWidget(self.data_color_btn)

        self.no_data_color_btn = QPushButton('No Data Color')
        self.no_data_color_btn.setStyleSheet(f'background-color: {self.no_data_color}')
        self.no_data_color_btn.clicked.connect(lambda: self.pick_color('no_data'))
        color_picker_layout.addWidget(self.no_data_color_btn)

        color_layout.addLayout(color_picker_layout)
        color_group.setLayout(color_layout)
        layout.addWidget(color_group)

        # ===== MAP SETTINGS =====
        map_group = QGroupBox('Map Settings')
        map_layout = QVBoxLayout()

        # Title
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel('Map Title:'))
        self.title_edit = QLineEdit('Myanmar Coverage Map 2025')
        title_layout.addWidget(self.title_edit)
        map_layout.addLayout(title_layout)

        # Labels
        label_settings_layout = QHBoxLayout()
        self.show_labels = QCheckBox('Show Labels')
        self.show_labels.setChecked(True)
        label_settings_layout.addWidget(self.show_labels)
        label_settings_layout.addWidget(QLabel('Label Size:'))
        self.label_size = QSpinBox()
        self.label_size.setRange(4, 14)
        self.label_size.setValue(7)
        label_settings_layout.addWidget(self.label_size)
        map_layout.addLayout(label_settings_layout)

        # Page size
        page_layout = QHBoxLayout()
        page_layout.addWidget(QLabel('Page Size:'))
        self.page_size = QComboBox()
        self.page_size.addItems(['A4', 'A3'])
        page_layout.addWidget(self.page_size)
        page_layout.addWidget(QLabel('DPI:'))
        self.dpi = QSpinBox()
        self.dpi.setRange(100, 600)
        self.dpi.setValue(300)
        page_layout.addWidget(self.dpi)
        map_layout.addLayout(page_layout)

        map_group.setLayout(map_layout)
        layout.addWidget(map_group)

        # ===== OUTPUT =====
        output_group = QGroupBox('Output')
        output_layout = QVBoxLayout()

        output_path_layout = QHBoxLayout()
        output_path_layout.addWidget(QLabel('Output Folder:'))
        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText('Select output folder...')
        output_path_layout.addWidget(self.output_path)
        output_btn = QPushButton('Browse')
        output_btn.clicked.connect(self.browse_output_folder)
        output_path_layout.addWidget(output_btn)
        output_layout.addLayout(output_path_layout)

        export_layout = QHBoxLayout()
        self.export_png = QCheckBox('Export PNG')
        self.export_png.setChecked(True)
        self.export_pdf = QCheckBox('Export PDF')
        self.export_pdf.setChecked(True)
        export_layout.addWidget(self.export_png)
        export_layout.addWidget(self.export_pdf)
        output_layout.addLayout(export_layout)

        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        # ===== BUTTONS =====
        button_layout = QHBoxLayout()

        self.preview_btn = QPushButton('Preview Map')
        self.preview_btn.clicked.connect(self.preview_map)
        button_layout.addWidget(self.preview_btn)

        self.generate_btn = QPushButton('Generate && Export')
        self.generate_btn.clicked.connect(self.generate_map)
        self.generate_btn.setStyleSheet('background-color: #27ae60; color: white; font-weight: bold;')
        button_layout.addWidget(self.generate_btn)

        self.close_btn = QPushButton('Close')
        self.close_btn.clicked.connect(self.close)
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Set default paths
        self.set_default_paths()

    def set_default_paths(self):
        """Set default file paths"""
        base_dir = Path(__file__).parent.parent

        state_path = base_dir / 'State' / 'mmr_polbnda2_adm1_250k_mimu_1.shp'
        township_path = base_dir / 'Township' / 'mmr_polbnda_adm3_250k_mimu_1.shp'
        excel_path = base_dir / 'Coverage_PQ.xlsx'
        output_path = base_dir / 'Output'

        if state_path.exists():
            self.state_path.setText(str(state_path))
        if township_path.exists():
            self.township_path.setText(str(township_path))
        if excel_path.exists():
            self.excel_path.setText(str(excel_path))
        if output_path.exists():
            self.output_path.setText(str(output_path))

    def browse_file(self, line_edit, file_type):
        """Browse for a file"""
        if file_type == 'shp':
            path, _ = QFileDialog.getOpenFileName(self, 'Select Shapefile', '', 'Shapefiles (*.shp)')
        else:
            path, _ = QFileDialog.getOpenFileName(self, 'Select Excel File', '', 'Excel Files (*.xlsx *.xls)')
        if path:
            line_edit.setText(path)

    def browse_output_folder(self):
        """Browse for output folder"""
        path = QFileDialog.getExistingDirectory(self, 'Select Output Folder')
        if path:
            self.output_path.setText(path)

    def load_excel_columns(self):
        """Load columns from Excel file"""
        excel_path = self.excel_path.text()
        if not excel_path or not Path(excel_path).exists():
            return

        try:
            self.excel_df = pd.read_excel(excel_path)
            columns = list(self.excel_df.columns)

            # Update combo boxes
            for combo in [self.pcode_excel, self.category_col, self.township_col, self.label_col]:
                combo.clear()
                combo.addItems(columns)

            # Set defaults if available
            if 'TS_Pcode' in columns:
                self.pcode_excel.setCurrentText('TS_Pcode')
            if 'Thematic25' in columns:
                self.category_col.setCurrentText('Thematic25')
            if 'Township' in columns:
                self.township_col.setCurrentText('Township')
            if 'IP_25' in columns:
                self.label_col.setCurrentText('IP_25')

        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to load Excel: {e}')

    def pick_color(self, color_type):
        """Open color picker dialog"""
        current_color = self.data_color if color_type == 'data' else self.no_data_color
        color = QColorDialog.getColor(QColor(current_color), self, 'Select Color')
        if color.isValid():
            hex_color = color.name()
            if color_type == 'data':
                self.data_color = hex_color
                self.data_color_btn.setStyleSheet(f'background-color: {hex_color}')
            else:
                self.no_data_color = hex_color
                self.no_data_color_btn.setStyleSheet(f'background-color: {hex_color}')

    def preview_map(self):
        """Generate map preview in QGIS canvas"""
        try:
            self.create_map(export=False)
            QMessageBox.information(self, 'Success', 'Map preview generated! Check the QGIS canvas.')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to generate preview: {e}')

    def generate_map(self):
        """Generate map and export"""
        try:
            self.create_map(export=True)
            QMessageBox.information(self, 'Success', 'Map generated and exported successfully!')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to generate map: {e}')

    def create_map(self, export=False):
        """Create the map"""
        project = QgsProject.instance()
        project.clear()

        # Load Excel
        df = pd.read_excel(self.excel_path.text())
        pcode_excel = self.pcode_excel.currentText()
        df[pcode_excel] = df[pcode_excel].astype(str).str.strip().str.upper()

        excel_fields = [c for c in df.columns if c != pcode_excel]
        lookup = df.set_index(pcode_excel).to_dict('index')

        # Load shapefiles
        state_layer = QgsVectorLayer(self.state_path.text(), 'States', 'ogr')
        township_layer = QgsVectorLayer(self.township_path.text(), 'Townships', 'ogr')

        pcode_shp = self.pcode_shp.text()

        # Add fields and join
        township_layer.startEditing()
        existing = [f.name() for f in township_layer.fields()]
        for field in excel_fields:
            if field not in existing:
                township_layer.addAttribute(QgsField(field, QVariant.String))
        township_layer.updateFields()

        for feature in township_layer.getFeatures():
            pcode = str(feature[pcode_shp]).strip().upper()
            if pcode in lookup:
                for field in excel_fields:
                    val = lookup[pcode].get(field, '')
                    feature[field] = str(val) if pd.notna(val) else ''
                township_layer.updateFeature(feature)
        township_layer.commitChanges()

        # Style state layer BEFORE adding to project
        state_symbol = QgsSymbol.defaultSymbol(state_layer.geometryType())
        state_symbol.setColor(QColor(255, 255, 255, 0))
        state_symbol.symbolLayer(0).setStrokeColor(QColor('#a8a5a5'))
        state_symbol.symbolLayer(0).setStrokeWidth(0.5)
        state_layer.renderer().setSymbol(state_symbol)
        state_layer.triggerRepaint()

        # Add layers: States first (bottom), Townships second (top)
        project.addMapLayer(state_layer)
        project.addMapLayer(township_layer)

        # Apply colors
        category_col = self.category_col.currentText()
        is_multi_color = self.multi_color_radio.isChecked()

        if is_multi_color:
            categories = set()
            for f in township_layer.getFeatures():
                val = f[category_col]
                categories.add(str(val) if val else 'NA')

            cat_list = []
            for i, cat in enumerate(sorted(categories)):
                symbol = QgsSymbol.defaultSymbol(township_layer.geometryType())
                symbol.setColor(QColor(COLORS[i % len(COLORS)]))
                symbol.setOpacity(0.8)
                symbol.symbolLayer(0).setStrokeColor(QColor('#ffffff'))
                symbol.symbolLayer(0).setStrokeWidth(0.3)
                cat_list.append(QgsRendererCategory(cat, symbol, cat))

            township_layer.setRenderer(QgsCategorizedSymbolRenderer(category_col, cat_list))
        else:
            # Binary mode
            cat_list = []
            for cat_type in ['Has Data', 'No Data']:
                symbol = QgsSymbol.defaultSymbol(township_layer.geometryType())
                color = self.data_color if cat_type == 'Has Data' else self.no_data_color
                symbol.setColor(QColor(color))
                symbol.setOpacity(0.8)
                symbol.symbolLayer(0).setStrokeColor(QColor('#ffffff'))
                symbol.symbolLayer(0).setStrokeWidth(0.3)
                cat_list.append(QgsRendererCategory(cat_type, symbol, cat_type))

            # Update category field for binary
            township_layer.startEditing()
            for feature in township_layer.getFeatures():
                val = feature[category_col]
                binary_val = 'Has Data' if val and str(val) != 'NA' and str(val).strip() else 'No Data'
                feature[category_col] = binary_val
                township_layer.updateFeature(feature)
            township_layer.commitChanges()

            township_layer.setRenderer(QgsCategorizedSymbolRenderer(category_col, cat_list))

        # Apply labels
        if self.show_labels.isChecked():
            settings = QgsPalLayerSettings()
            fmt = QgsTextFormat()
            fmt.setFont(QFont('Arial', self.label_size.value()))
            fmt.setSize(self.label_size.value())
            fmt.buffer().setEnabled(True)
            fmt.buffer().setSize(0.5)
            settings.setFormat(fmt)

            township_col = self.township_col.currentText()
            label_col = self.label_col.currentText()
            settings.fieldName = f'"{township_col}" || \' - \' || "{label_col}"'
            settings.isExpression = True
            settings.enabled = True
            township_layer.setLabeling(QgsVectorLayerSimpleLabeling(settings))
            township_layer.setLabelsEnabled(True)

        # Refresh canvas
        self.iface.mapCanvas().setExtent(township_layer.extent())
        self.iface.mapCanvas().refresh()

        # Export
        if export and (self.export_png.isChecked() or self.export_pdf.isChecked()):
            self.export_map(project, township_layer, state_layer)

    def export_map(self, project, township_layer, state_layer):
        """Export map to PNG/PDF"""
        output_folder = Path(self.output_path.text())
        output_folder.mkdir(exist_ok=True)

        # Create layout
        layout = QgsPrintLayout(project)
        layout.initializeDefaults()
        layout.setName(self.title_edit.text())

        # Page size
        page_sizes = {
            'A3': QgsLayoutSize(297, 420, QgsUnitTypes.LayoutMillimeters),
            'A4': QgsLayoutSize(210, 297, QgsUnitTypes.LayoutMillimeters),
        }
        page = layout.pageCollection().page(0)
        page.setPageSize(page_sizes.get(self.page_size.currentText(), page_sizes['A4']))

        pw = page.pageSize().width()
        ph = page.pageSize().height()
        margin = 10

        # Title
        title = QgsLayoutItemLabel(layout)
        title.setText(self.title_edit.text())
        title.setFont(QFont('Arial', 18, QFont.Bold))
        title.attemptMove(QgsLayoutPoint(margin, margin, QgsUnitTypes.LayoutMillimeters))
        title.attemptResize(QgsLayoutSize(pw - 2*margin, 12, QgsUnitTypes.LayoutMillimeters))
        layout.addLayoutItem(title)

        # Map
        legend_height = 60
        map_height = ph - 25 - legend_height - margin
        map_width = pw - 2*margin

        map_item = QgsLayoutItemMap(layout)
        map_item.attemptMove(QgsLayoutPoint(margin, 25, QgsUnitTypes.LayoutMillimeters))
        map_item.attemptResize(QgsLayoutSize(map_width, map_height, QgsUnitTypes.LayoutMillimeters))
        map_item.setExtent(township_layer.extent())
        map_item.setLayers([township_layer, state_layer])
        map_item.refresh()
        layout.addLayoutItem(map_item)

        # Legend
        legend = QgsLayoutItemLegend(layout)
        legend.setLinkedMap(map_item)
        legend.setTitle('Legend')
        legend.attemptMove(QgsLayoutPoint(margin, ph - legend_height - margin, QgsUnitTypes.LayoutMillimeters))
        legend.attemptResize(QgsLayoutSize(pw - 2*margin, legend_height, QgsUnitTypes.LayoutMillimeters))
        legend.updateLegend()
        layout.addLayoutItem(legend)

        project.layoutManager().addLayout(layout)

        # Export
        filename = self.title_edit.text().replace(' ', '_')
        exporter = QgsLayoutExporter(layout)
        dpi = self.dpi.value()

        if self.export_png.isChecked():
            png_path = str(output_folder / f'{filename}.png')
            settings = QgsLayoutExporter.ImageExportSettings()
            settings.dpi = dpi
            exporter.exportToImage(png_path, settings)

        if self.export_pdf.isChecked():
            pdf_path = str(output_folder / f'{filename}.pdf')
            settings = QgsLayoutExporter.PdfExportSettings()
            settings.dpi = dpi
            exporter.exportToPdf(pdf_path, settings)
