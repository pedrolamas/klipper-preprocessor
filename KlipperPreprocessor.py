# Copyright (c) 2022 Lasse Dalegaard
# Copyright (c) 2023 Pedro Lamas
# MIT licensed

from ..Script import Script
from tempfile import TemporaryDirectory
import subprocess
import shutil
import os

class KlipperPreprocessor(Script):
    """
    Prepare resulting gcode for Klipper.
    """

    def getSettingDataString(self):
        return """{
            "name": "Klipper Preprocessor",
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
                "klipper_estimator_config_file_path":
                {
                    "label": "Path to config file",
                    "description": "The full path for the klipper_estimator config file.",
                    "type": "str",
                    "default_value": "",
                    "enabled": "klipper_estimator_enabled and klipper_estimator_config_type != 'moonraker_url'"
                },
                "klipper_estimator_moonraker_url":
                {
                    "label": "Moonraker URL",
                    "description": "URL to Moonraker base",
                    "type": "str",
                    "default_value": "",
                    "enabled": "klipper_estimator_enabled and klipper_estimator_config_type == 'moonraker_url'"
                }
            }
        }"""

    def execute(self, data):
        add_set_print_stats_info = self.getSettingValueByKey("add_set_print_stats_info")

        with TemporaryDirectory() as work_dir:
            filename = os.path.join(work_dir, "work.gcode")
            with open(filename, 'w') as work_file:
                for layer in data:
                    lines = layer.split("\n")
                    for line in lines:
                        work_file.write(line + "\n")
                        if add_set_print_stats_info:
                            if (line.startswith(';LAYER:')):
                                work_file.write("SET_PRINT_STATS_INFO CURRENT_LAYER=%i\n" % (int(line[7:]) + 1,))
                            elif (line.startswith(';LAYER_COUNT:')):
                                work_file.write("SET_PRINT_STATS_INFO TOTAL_LAYERS=%s\n" % (line[13:],))

            if self.getSettingValueByKey("preprocess_cancellation_enabled"):
                args = [
                    self.getSettingValueByKey("preprocess_cancellation_path"),
                    filename,
                ]

                ret = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                if ret.returncode != 0:
                    raise RuntimeError("Failed to run preprocess_cancellation\n%s" % (ret.stdout,))

            if self.getSettingValueByKey("klipper_estimator_enabled"):
                klipper_estimator_config_type = self.getSettingValueByKey("klipper_estimator_config_type")
                klipper_estimator_config_arg = self.getSettingValueByKey("klipper_estimator_moonraker_url") if klipper_estimator_config_type == 'moonraker_url' else self.getSettingValueByKey("klipper_estimator_config_file_path")
                args = [
                    self.getSettingValueByKey("klipper_estimator_path"),
                    "--config_" + klipper_estimator_config_type,
                    klipper_estimator_config_arg,
                    "post-process",
                    filename,
                ]

                ret = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                if ret.returncode != 0:
                    raise RuntimeError("Failed to run klipper_estimator\n%s" % (ret.stdout,))

            with open(filename) as work_file:
                return work_file.readlines()
