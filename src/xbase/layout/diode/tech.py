# SPDX-License-Identifier: Apache-2.0
# Copyright 2019 Blue Cheetah Analog Design Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This module defines diode technology class.
"""

from __future__ import annotations

from typing import Any, Mapping

import abc

from bag.layout.tech import TechInfo

from ..array.tech import ArrayTech


class DiodeTech(ArrayTech, abc.ABC):
    def __init__(self, tech_info: TechInfo, dio_type: str = '') -> None:
        ArrayTech.__init__(self, tech_info, 'diode', dio_type=dio_type)

        self._dio_config = tech_info.config['diode']
        # fill config dictionary
        self._dio_config = {}
        for k, v in tech_info.config['diode'].items():
            if isinstance(v, dict):
                val = v.get(dio_type, None)
                if val is None:
                    self._dio_config[k] = v
                else:
                    self._dio_config[k] = val
            else:
                self._dio_config[k] = v

    @property
    def dio_config(self) -> Mapping[str, Any]:
        return self._dio_config

    @property
    def conn_layer(self) -> int:
        return self._dio_config['conn_layer']
