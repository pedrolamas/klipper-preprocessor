# Klipper Preprocessor script for Cura
# Version: 1.4.1
#
# Copyright (c) 2022 Lasse Dalegaard
# Copyright (c) 2023 Pedro Lamas
# MIT licensed

from ..Script import Script
from UM.Logger import Logger
from UM.Message import Message
from tempfile import TemporaryDirectory
from typing import List, Tuple
import sys
import subprocess
import shutil
import os

class KlipperPreprocessor(Script):
    """
    Prepare resulting gcode for Klipper.
    """

    def getSettingDataString(self) -> str:
        return """{
            "name": "Klipper Preprocessor v1.4.1",
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
                    "description": "URL to Moonraker base.",
                    "type": "str",
                    "default_value": "",
                    "enabled": "klipper_estimator_enabled and klipper_estimator_config_type == 'moonraker_url'"
                },
                "klipper_estimator_moonraker_api_key":
                {
                    "label": "Moonraker API Key",
                    "description": "Optional Moonraker API Key.",
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

    def execute(self, data: List[str]) -> List[str]:
        try:
            with TemporaryDirectory() as work_dir:
                filename, total_layers = self.prepare_temp_file(data, work_dir)

                self.execute_preprocess_cancellation(filename)

                self.execute_klipper_estimator(filename, work_dir)

                return self.return_processed_data(filename, total_layers)
        except Exception as e:
            self.showWarningMessage("Unhandled exception:\n%s" % (str(e),))
            return data

    def prepare_temp_file(self, data: List[str], work_dir: str) -> Tuple[str, int]:
        Logger.log("d", "Initial run...")

        add_timelapse_take_frame: bool = self.getSettingValueByKey("add_timelapse_take_frame")

        filename = os.path.join(work_dir, "work.gcode")
        total_layers = 0

        with open(filename, 'w') as work_file:
            for index, layer in enumerate(data):
                if index:
                    work_file.write(";CURA_DATA_SPLIT_HERE\n")

                lines = layer.split("\n")

                for line in lines:
                    if line.startswith(';LAYER:'):
                        total_layers += 1
                        if add_timelapse_take_frame:
                            work_file.write("TIMELAPSE_TAKE_FRAME\n")
                    work_file.write(line + "\n")

        Logger.log("d", "Total layers found: %d", total_layers)

        return filename, total_layers

    def return_processed_data(self, filename: str, total_layers: int) -> List[str]:
        Logger.log("d", "Return output...")

        add_set_print_stats_info: bool = self.getSettingValueByKey("add_set_print_stats_info")

        data: List[str] = []
        current_layer = 0

        with open(filename) as work_file:
            layer: List[str] = []

            for line in work_file:
                line = line.strip()

                if line == ";CURA_DATA_SPLIT_HERE":
                    data.append("\n".join(layer))
                    layer = []
                else:
                    layer.append(line)

                    if add_set_print_stats_info:
                        if line.startswith(';LAYER:'):
                            current_layer += 1
                            layer.append("SET_PRINT_STATS_INFO CURRENT_LAYER=%s" % (current_layer,))
                        elif line.startswith(';LAYER_COUNT:'):
                            layer.append("SET_PRINT_STATS_INFO TOTAL_LAYER=%s" % (total_layers,))
            data.append("\n".join(layer))

        return data

    def execute_preprocess_cancellation(self, filename: str) -> None:
        preprocess_cancellation_enabled: bool = self.getSettingValueByKey("preprocess_cancellation_enabled")

        if preprocess_cancellation_enabled:
            Logger.log("d", "Running preprocess_cancellation...")

            preprocess_cancellation_path: str = self.getSettingValueByKey("preprocess_cancellation_path")

            args = [
                preprocess_cancellation_path,
                filename,
            ]
            timeout: int = self.getSettingValueByKey("preprocess_cancellation_timeout")

            try:
                ret = subprocess.run(args, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, startupinfo = self.getSubprocessStartupinfo(), timeout = timeout)
                if ret.returncode != 0:
                    raise Exception(ret.stdout.decode().strip())
            except subprocess.TimeoutExpired:
                self.showWarningMessage("Timeout while running preprocess_cancellation")
            except Exception as e:
                self.showWarningMessage("Failed to run preprocess_cancellation\n%s" % (str(e),))

    def execute_klipper_estimator(self, filename: str, work_dir: str) -> None:
        klipper_estimator_enabled: bool = self.getSettingValueByKey("klipper_estimator_enabled")

        if klipper_estimator_enabled:
            klipper_estimator_config_type: str = self.getSettingValueByKey("klipper_estimator_config_type")
            klipper_estimator_moonraker_url: str = self.getSettingValueByKey("klipper_estimator_moonraker_url")
            klipper_estimator_moonraker_api_key: str = self.getSettingValueByKey("klipper_estimator_moonraker_api_key")
            klipper_estimator_config_file_path: str = self.getSettingValueByKey("klipper_estimator_config_file_path")
            klipper_estimator_path: str = self.getSettingValueByKey("klipper_estimator_path")

            if klipper_estimator_config_type == 'moonraker_url' and self.getSettingValueByKey("klipper_estimator_config_cache"):
                Logger.log("d", "Running klipper_estimator to get config from Moonraker...")

                klipper_estimator_config_type = 'file'

                args = [
                    klipper_estimator_path,
                    "--config_moonraker_url",
                    klipper_estimator_moonraker_url,
                    "--config_moonraker_api_key",
                    klipper_estimator_moonraker_api_key,
                    "dump-config"
                ]

                config_filename = os.path.join(work_dir, "config.json")

                with open(config_filename, 'w') as config_file:
                    try:
                        ret = subprocess.run(args, stdout = config_file, stderr = subprocess.PIPE, startupinfo = self.getSubprocessStartupinfo(), timeout = 5)
                        if ret.returncode == 0:
                            shutil.copy(config_filename, klipper_estimator_config_file_path)
                        else:
                            self.showWarningMessage("Failed to run klipper_estimator\n%s" % (ret.stderr.decode().strip(),))
                    except subprocess.TimeoutExpired:
                        pass

            Logger.log("d", "Running klipper_estimator...")

            klipper_estimator_config_arg: str = klipper_estimator_moonraker_url if klipper_estimator_config_type == 'moonraker_url' else klipper_estimator_config_file_path

            args = [
                klipper_estimator_path,
                "--config_" + klipper_estimator_config_type,
                klipper_estimator_config_arg,
                "--config_moonraker_api_key",
                klipper_estimator_moonraker_api_key,
                "post-process",
                filename,
            ]

            timeout: int = self.getSettingValueByKey("klipper_estimator_timeout")

            try:
                ret = subprocess.run(args, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, startupinfo = self.getSubprocessStartupinfo(), timeout = timeout)
                if ret.returncode != 0:
                    raise Exception(ret.stdout.decode().strip())
            except subprocess.TimeoutExpired:
                self.showWarningMessage("Timeout while running klipper_estimator")
            except Exception as e:
                self.showWarningMessage("Failed to run klipper_estimator\n%s" % (str(e),))

    def getSubprocessStartupinfo(self):
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            return startupinfo
        return None

    def showWarningMessage(self, text) -> None:
        Logger.logException("w", text)

        message = Message(text, title = "Klipper Preprocessor", message_type = Message.MessageType.WARNING)
        message.show()
