# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from pydantic import Field

from .resource import SERIALIZE_ALWAYS, NamedResource


class Keypair(NamedResource):
    fingerprint: str = Field(json_schema_extra=SERIALIZE_ALWAYS)
    hasPrivateKey: bool
    publicKey: str
