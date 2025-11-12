##########################################################################
# NSAp - Copyright (C) CEA, 2022 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Module that implements tools.
"""

from .bunch import Bunch
from .color import (
    print_command,
    print_deprecated,
    print_error,
    print_info,
    print_result,
    print_subtitle,
    print_title,
    print_warn,
)
from .utils import (
    bids,
    coerceparams,
    find_stack_level,
    outputdir,
    parse_bids_keys,
    sidecar_from_file,
)

__all__ = []
