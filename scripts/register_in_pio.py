# Copyright (c) 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import subprocess
from os.path import dirname, join, realpath

root_dir = realpath(join(dirname(realpath(__file__)), ".."))

for current_dir, _, files in os.walk(os.path.join(root_dir, "configs")):
    for filename in files:
        if not filename.endswith(".json"):
            continue
        print current_dir, filename
        raw_url = ("https://raw.githubusercontent.com/platformio/"
                   "platformio-libmirror/master%s/%s" %
                   (current_dir.replace(root_dir, ""), filename))
        subprocess.call(["platformio", "lib", "register", raw_url])
