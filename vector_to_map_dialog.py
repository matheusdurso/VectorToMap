# -*- coding: utf-8 -*-
"""
/***************************************************************************
 VectorToMapDialog - QGIS Plugin
 ---------------------------------------------------------------------------
 This script manages the dialog window for the VectorToMap plugin.
 It uses uic to dynamically load the UI design from the .ui file.

 Author: Matheus Durso
 Date: 2026-02-20
 ***************************************************************************/
"""

import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

# Load the .ui file dynamically so PyQt can populate the plugin with 
# the elements designed in Qt Designer.
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'vector_to_map_dialog_base.ui'))


class VectorToMapDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """
        Constructor for the dialog.
        
        :param parent: The parent widget (usually the QGIS main window).
        """
        super(VectorToMapDialog, self).__init__(parent)
        
        # Set up the user interface from the .ui file through FORM_CLASS.
        # After setupUi(), all widgets defined in the UI (like chk_preview_auto) 
        # become available as self.<objectname>.
        self.setupUi(self)