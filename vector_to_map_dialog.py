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