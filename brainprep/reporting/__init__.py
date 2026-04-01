##########################################################################
# NSAp - Copyright (C) CEA, 2022 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Module that implements reporting tools.
"""


from .html_reporting import generate_qc_report
from .rst_reporting import (
    RSTReport,
    trace_module_calls,
)

__all__ = [
    "RSTReport",
    "generate_qc_report",
    "trace_module_calls",
]
