# -*- coding: utf-8 -*-
# /***************************************************************************
#  VectorToMap - QGIS Plugin
#  Automates the generation of print layouts for vector features.
#  Author: Matheus Durso Neves Caetano
#
#  Copyright (C) 2026 Matheus Durso Neves Caetano
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#  ***************************************************************************/

# noinspection PyPep8Naming
def classFactory(iface):
    """
    Entry point for the QGIS Plugin Manager.

    :param iface: An interface instance (QgsInterface) that allows the
                  plugin to interact with the QGIS application.
    :return: An instance of the VectorToMap class.
    """

    # Import the main plugin class from the vector_to_map.py file
    from .vector_to_map import VectorToMap

    # Return the instantiated object to QGIS
    return VectorToMap(iface)