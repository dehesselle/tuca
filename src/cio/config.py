# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from dataclasses import dataclass


@dataclass
class Config:
    be_verbose: bool = False


config = Config()
