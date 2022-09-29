# coding=utf-8
from __future__ import absolute_import

import uuid
import octoprint.plugin

from pytradfri import Gateway
from pytradfri.api.libcoap_api import APIFactory
from pytradfri.device import Device

class Psucontrol_tradfriPlugin(
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.RestartNeedingPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.SettingsPlugin
):
    def __init__(self):
        self.config = {}
        self.api_factory = None
        self.device = None
        self.state = False

    ##~~ PSUControl Methods

    def turn_psu_on(self):
        if self.device is not None:
            api = self.api_factory.request
            socket_command = self.device.socket_control.set_state(True)
            api(socket_command)
        else:
            self._logger.info("Device is not set")

    def turn_psu_off(self):
        if self.device is not None:
            api = self.api_factory.request
            socket_command = self.device.socket_control.set_state(False)
            api(socket_command)
        else:
            self._logger.info("Device is not set")

    def get_psu_state(self):
        if self.device is not None:
            self.find_tradfri_device()
        return self.state

    ##~~ StartupPlugin mixin

    def on_startup(self, host, port):
        psucontrol_helpers = self._plugin_manager.get_helpers("psucontrol")
        if not psucontrol_helpers or 'register_plugin' not in psucontrol_helpers.keys():
            self._logger.warning("The version of PSUControl that is installed does not support plugin registration.")
            return

        self._logger.debug("Registering plugin with PSUControl")
        psucontrol_helpers['register_plugin'](self)

    ##~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return {
            "address": '',
            "plug": '',
            "security_key": '',
            "psk": '',
            "identity": ''
        }

    def on_settings_initialized(self):
        self.reload_settings()

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        self.reload_settings()

    def get_settings_version(self):
        return 1

    def on_settings_migrate(self, target, current=None):
        pass

    def reload_settings(self):
        for k, _v in self.get_settings_defaults().items():
            v = self._settings.get([k])
            self.config[k] = v
            self._logger.debug("{}: {}".format(k, v))
        self.init_tradfri()

    ##~~ Tradfri methods
    def init_tradfri(self):
        if self.api_factory is not None:
            self._logger.info("API Factory already exists")
            self.find_tradfri_device()
            return

        if self.config.get("address") is "" or self.config.get("plug") is "" or self.config.get("security_key") is "":
            self._logger.info("Address, Plug or Security Key not set")
            return

        host = self.config.get("address")
        security_key = self.config.get("security_key")

        identity = uuid.uuid4().hex
        if self.config.get("identity") is not "":
            identity = self.config.get("identity")

        if self.config.get("psk") is not "":
            psk = self.config.get("psk")
            self.api_factory = APIFactory(host=host, psk_id=identity, psk=psk, timeout=20)
        else:
            self.api_factory = APIFactory(host=host, psk_id=identity, timeout=20)
            psk = self.api_factory.generate_psk(security_key)
            self._settings.set(["identity"], identity)
            self._settings.set(["psk"], psk)
            self._settings.save(force=True)

        if self.api_factory is not None:
            self.find_tradfri_device()
        else:
            self._logger.info("API Factory still not set")

    def find_tradfri_device(self):
        api = self.api_factory.request
        gateway = Gateway()
        devices_command = gateway.get_devices()
        devices_commands = api(devices_command)
        devices = api(devices_commands)

        for dev in devices:
            if dev.name == self.config.get("plug"):
                self.device = dev
                self.state = dev.socket_control.sockets[0].state

    ##~~ TemplatePlugin hook

    def get_template_configs(self):
        return [
            dict(type="settings", custom_bindings=False)
        ]

    ##~~ Softwareupdate hook

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return {
            "psucontrol_tradfri": {
                "displayName": "PSU Control - Tradfri",
                "displayVersion": self._plugin_version,

                # version check: github repository
                "type": "github_release",
                "user": "Piets",
                "repo": "OctoPrint-PSUControl-Tradfri",
                "current": self._plugin_version,

                # update method: pip
                "pip": "https://github.com/Piets/OctoPrint-PSUControl-Tradfri/archive/{target_version}.zip",
            }
        }


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "PSU Control - Tradfri"


# Set the Python version your plugin is compatible with below. Recommended is Python 3 only for all new plugins.
# OctoPrint 1.4.0 - 1.7.x run under both Python 3 and the end-of-life Python 2.
# OctoPrint 1.8.0 onwards only supports Python 3.
__plugin_pythoncompat__ = ">=3,<4"  # Only Python 3

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = Psucontrol_tradfriPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
