# -*- coding: utf-8 -*-
"""
/***************************************************************************
 facialRecognition
                                 A QGIS plugin
 facial recognition plugin
                             -------------------
        begin                : 2014-12-06
        copyright            : (C) 2014 by ASAHI Kosuke
        email                : waigania13@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load facialRecognition class from file facialRecognition.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .facialRecognition import facialRecognition
    return facialRecognition(iface)
