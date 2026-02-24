# -*- coding: utf-8 -*-
"""
/***************************************************************************
 VectorToMap - QGIS Plugin
 ---------------------------------------------------------------------------
 This script initializes the plugin, making it known to QGIS.
 It defines the classFactory function which is called by the QGIS
 Plugin Manager to instantiate the plugin's main class.
 
 Author: Matheus Durso
 Date: 2026-02-20
 ***************************************************************************/
"""

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