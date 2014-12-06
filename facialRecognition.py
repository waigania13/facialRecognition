# -*- coding: utf-8 -*-
"""
/***************************************************************************
 facialRecognition
                                 A QGIS plugin
 facial recognition plugin
                              -------------------
        begin                : 2014-12-06
        git sha              : $Format:%H$
        copyright            : (C) 2014 by ASAHI Kosuke
        email                : waigania13@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from PyQt4.QtGui import QAction, QIcon, QColor
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from facialRecognition_dialog import facialRecognitionDialog
import os.path


class facialRecognition:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'facialRecognition_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = facialRecognitionDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&facialRecognition')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'facialRecognition')
        self.toolbar.setObjectName(u'facialRecognition')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('facialRecognition', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/facialRecognition/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'facialRecognition'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&facialRecognition'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        
        # set raster layer name to combobox
        self.dlg.layerList.clear()
        layers = QgsProject.instance().layerTreeRoot().findLayers()
        for layer in layers:
            if layer.layer().type() == QgsMapLayer.RasterLayer:
                self.dlg.layerList.addItem(layer.layer().name())
        
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            self._facialRecognition()
        
    def _facialRecognition(self):
        import cv2
        
        if self.dlg.layerList.count() == 0:
            return
        
        layer_name = self.dlg.layerList.currentText()
        raster_layer = QgsMapLayerRegistry.instance().mapLayersByName(layer_name)[0]
        
        width = raster_layer.width()
        height = raster_layer.height()
        extent = raster_layer.extent()
        
        # convert to gray image
        image = cv2.imread(raster_layer.dataProvider().dataSourceUri())
        image_gray = cv2.cvtColor(image, cv2.cv.CV_BGR2GRAY)
        
        # run facial recognition
        file = os.path.join(
            self.plugin_dir,
            'xml',
            'haarcascade_frontalface_alt.xml')
        cascade = cv2.CascadeClassifier(file)
        facerect = cascade.detectMultiScale(image_gray, scaleFactor=1.1, minNeighbors=1, minSize=(1, 1))
        
        # create memory layer
        memory_layer = QgsVectorLayer("Polygon?crs=epsg:4326", "face", "memory")
        memory_provider = memory_layer.dataProvider()
        
        polygons = []
        for rect in facerect:
            polygon = QgsFeature()
            polygon.setGeometry(QgsGeometry.fromRect( 
                QgsRectangle(
                    extent.xMinimum() + extent.width() * rect[0] / width,
                    extent.yMinimum() + extent.height() * (height - rect[1]) / height,
                    extent.xMinimum() + extent.width() * (rect[0] + rect[2]) / width,
                    extent.yMinimum() + extent.height() * (height - (rect[1] + rect[3])) / height
                )
            ))
            polygons.append(polygon)
        
        memory_provider.addFeatures(polygons)
        memory_layer.updateExtents()
        QgsMapLayerRegistry.instance().addMapLayer(memory_layer)
        
        # set fill style to memory layer
        symbol = QgsSymbolV2.defaultSymbol(QGis.Polygon)
        fillLayer = QgsSimpleFillSymbolLayerV2(QColor(255, 0, 0),Qt.NoBrush)
        symbol.appendSymbolLayer(fillLayer)
        symbol.deleteSymbolLayer(0)
        renderer = QgsSingleSymbolRendererV2(symbol)
        memory_layer.setRendererV2(renderer)
        self.iface.mapCanvas().refresh()