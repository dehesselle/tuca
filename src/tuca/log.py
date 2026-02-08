# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import logging
import os


def setup_logging() -> None:
    level = os.environ.get("TUCA_LOGLEVEL", "ERROR").upper()

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    stream_handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
    logging.basicConfig(
        level=level,
        handlers=[
            stream_handler,
        ],
    )
