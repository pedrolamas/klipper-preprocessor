# Klipper Preprocessor script for Cura
# Version: 1.3.0
#
# Copyright (c) 2022 Lasse Dalegaard
# Copyright (c) 2023 Pedro Lamas
# MIT licensed

from ..Script import Script
from UM.Logger import Logger
from UM.Message import Message
from tempfile import TemporaryDirectory
import sys
import subprocess
import shutil
import os

class KlipperPreprocessor(Script):
    """
    Prepare resulting gcode for Klipper.
    """

    def getSettingDataString(self):
        return """{
            "name": "Klipper Preprocessor v1.3.0",
            "key": "KlipperPreprocessor",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "add_set_print_stats_info":
                {
                    "label": "Add SET_PRINT_STATS_INFO",
                    "description": "Enable this to allow the slicer to add Klipper's SET_PRINT_STATS_INFO macro to the resulting G-Code. This allows Klipper to know what is the exact total layer count, and the current layer number in real-time.",
                    "type": "bool",
                    "default_value": true
                },
                "add_timelapse_take_frame":
                {
                    "label": "Add TIMELAPSE_TAKE_FRAME",
                    "description": "Enable this to allow the slicer to add moonraker-timelapse's TIMELAPSE_TAKE_FRAME macro to the resulting G-Code. This allows Klipper to take snapshots on each layer change to make timelapse videos.",
                    "type": "bool",
                    "default_value": true
                },
                "preprocess_cancellation_enabled": {
                    "label": "Use preprocess_cancellation",
                    "description": "Enable this to will allow the slicer to add object cancellation data to the resulting G-Code, enabling Klipper to cancel any specific single object while printing.",
                    "type": "bool",
                    "default_value": false
                },
                "preprocess_cancellation_path":
                {
                    "label": "Path to preprocess_cancellation",
                    "description": "The path to the preprocess_cancellation binary (including file name).",
                    "type": "str",
                    "default_value": "",
                    "enabled": "preprocess_cancellation_enabled"
                },
                "preprocess_cancellation_timeout":
                {
                    "label": "preprocess_cancellation timeout",
                    "description": "The maximum time to allow preprocess_cancellation to run.",
                    "unit": "s",
                    "type": "int",
                    "default_value": 600,
                    "minimum_value": "1",
                    "minimum_value_warning": "10",
                    "maximum_value_warning": "900",
                    "enabled": "preprocess_cancellation_enabled"
                },
                "klipper_estimator_enabled": {
                    "label": "Use klipper_estimator",
                    "description": "Enable this to allow the slicer to add a more accurate time estimation to the resulting G-Code.",
                    "type": "bool",
                    "default_value": false
                },
                "klipper_estimator_path":
                {
                    "label": "Path to klipper_estimator",
                    "description": "The path to the klipper_estimator binary (including file name).",
                    "type": "str",
                    "default_value": "",
                    "enabled": "klipper_estimator_enabled"
                },
                "klipper_estimator_timeout":
                {
                    "label": "klipper_estimator timeout",
                    "description": "The maximum time to allow klipper_estimator to run.",
                    "unit": "s",
                    "type": "int",
                    "default_value": 600,
                    "minimum_value": "1",
                    "minimum_value_warning": "10",
                    "maximum_value_warning": "900",
                    "enabled": "klipper_estimator_enabled"
                },
                "klipper_estimator_config_type":
                {
                    "label": "Config source type",
                    "description": "",
                    "type": "enum",
                    "options": {
                        "file": "Config File",
                        "moonraker_url": "Moonraker URL"
                    },
                    "default_value": "file",
                    "enabled": "klipper_estimator_enabled"
                },
                "klipper_estimator_moonraker_url":
                {
                    "label": "Moonraker URL",
                    "description": "URL to Moonraker base",
                    "type": "str",
                    "default_value": "",
                    "enabled": "klipper_estimator_enabled and klipper_estimator_config_type == 'moonraker_url'"
                },
                "klipper_estimator_config_cache": {
                    "label": "Cache config from Moonraker",
                    "description": "Enable this to cache a copy of the config from Moonraker.",
                    "type": "bool",
                    "default_value": false,
                    "enabled": "klipper_estimator_enabled and klipper_estimator_config_type == 'moonraker_url'"
                },
                "klipper_estimator_config_file_path":
                {
                    "label": "Path to config file",
                    "description": "The full path for the klipper_estimator config file.",
                    "type": "str",
                    "default_value": "",
                    "enabled": "klipper_estimator_enabled and (klipper_estimator_config_type != 'moonraker_url' or klipper_estimator_config_cache)"
                }
            }
        }"""

    def execute(self, data):
        add_set_print_stats_info = self.getSettingValueByKey("add_set_print_stats_info")
        add_timelapse_take_frame = self.getSettingValueByKey("add_timelapse_take_frame")

        with TemporaryDirectory() as work_dir:
            Logger.log("d", "Initial run...")

            total_layers = 0

            filename = os.path.join(work_dir, "work.gcode")
            with open(filename, 'w') as work_file:
                first_layer_done = False
                for layer in data:
                    if first_layer_done:
                        work_file.write(";CURA_DATA_SPLIT_HERE\n")
                    else:
                        first_layer_done = True
                    lines = layer.split("\n")
                    for line in lines:
                        if (line.startswith(';LAYER:')):
                            total_layers += 1
                            if add_timelapse_take_frame:
                                work_file.write("TIMELAPSE_TAKE_FRAME\n")
                        work_file.write(line + "\n")

            Logger.log("d", "Total layers found: %d", total_layers)

            self.execute_preprocess_cancellation(filename)

            self.execute_klipper_estimator(filename, work_dir)

            Logger.log("d", "Return output...")

            data = []
            current_layer = 0
            with open(filename) as work_file:
                layer = []
                for line in work_file:
                    line = line.strip()
                    if line == ";CURA_DATA_SPLIT_HERE":
                        data.append("\n".join(layer))
                        layer = []
                    else:
                        layer.append(line)

                        if add_set_print_stats_info:
                            if (line.startswith(';LAYER:')):
                                current_layer += 1
                                layer.append("SET_PRINT_STATS_INFO CURRENT_LAYER=%s" % (current_layer,))
                            elif (line.startswith(';LAYER_COUNT:')):
                                layer.append("SET_PRINT_STATS_INFO TOTAL_LAYER=%s" % (total_layers,))
                data.append("\n".join(layer))

            return data

    def execute_preprocess_cancellation(self, filename):
        if self.getSettingValueByKey("preprocess_cancellation_enabled"):
            Logger.log("d", "Running preprocess_cancellation...")

            args = [
                self.getSettingValueByKey("preprocess_cancellation_path"),
                filename,
            ]
            timeout = self.getSettingValueByKey("preprocess_cancellation_timeout")

            try:
                ret = subprocess.run(args, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, startupinfo = self.getSubprocessStartupinfo(), timeout = timeout)
                if ret.returncode != 0:
                    self.showWarningMessage("Failed to run preprocess_cancellation\n%s" % (ret.stdout,))
            except subprocess.TimeoutExpired:
                self.showWarningMessage("Timeout while running preprocess_cancellation")

    def execute_klipper_estimator(self, filename, work_dir):
        if self.getSettingValueByKey("klipper_estimator_enabled"):
            klipper_estimator_config_type = self.getSettingValueByKey("klipper_estimator_config_type")
            klipper_estimator_moonraker_url = self.getSettingValueByKey("klipper_estimator_moonraker_url")
            klipper_estimator_config_file_path = self.getSettingValueByKey("klipper_estimator_config_file_path")

            if klipper_estimator_config_type == 'moonraker_url' and self.getSettingValueByKey("klipper_estimator_config_cache"):
                Logger.log("d", "Running klipper_estimator to get config from Moonraker...")

                klipper_estimator_config_type = 'file'

                args = [
                    self.getSettingValueByKey("klipper_estimator_path"),
                    "--config_moonraker_url",
                    klipper_estimator_moonraker_url,
                    "dump-config"
                ]

                config_filename = os.path.join(work_dir, "config.json")
                with open(config_filename, 'w') as config_file:
                    try:
                        ret = subprocess.run(args, stdout = config_file, startupinfo = self.getSubprocessStartupinfo(), timeout = 5)
                        if ret.returncode == 0:
                            shutil.copy(config_filename, klipper_estimator_config_file_path)
                    except subprocess.TimeoutExpired:
                        pass

            Logger.log("d", "Running klipper_estimator...")

            klipper_estimator_config_arg = klipper_estimator_moonraker_url if klipper_estimator_config_type == 'moonraker_url' else klipper_estimator_config_file_path

            args = [
                self.getSettingValueByKey("klipper_estimator_path"),
                "--config_" + klipper_estimator_config_type,
                klipper_estimator_config_arg,
                "post-process",
                filename,
            ]
            timeout = self.getSettingValueByKey("klipper_estimator_timeout")

            try:
                ret = subprocess.run(args, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, startupinfo = self.getSubprocessStartupinfo(), timeout = timeout)
                if ret.returncode != 0:
                    self.showWarningMessage("Failed to run klipper_estimator\n%s" % (ret.stdout,))
            except subprocess.TimeoutExpired:
                self.showWarningMessage("Timeout while running klipper_estimator")

    def getSubprocessStartupinfo(self):
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            return startupinfo
        return None

    def showWarningMessage(self, text):
        Logger.logException("w", text)

        message = Message(text, title = "Klipper Preprocessor", message_type = Message.MessageType.WARNING)
        message.show()
