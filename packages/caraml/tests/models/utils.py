# Copyright 2020 The Merlin Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import caraml.models as merlin
from caraml.models.endpoint import Status


def undeploy_all_version():
    for v in merlin.active_model().list_version():
        ve = v.endpoint
        if ve is not None and (ve.status == Status.RUNNING or ve.status == Status.PENDING):
            merlin.undeploy(v)