# OctoPrint-PSUControl-Tradfri

Adds Ikea Tradfri support to OctoPrint-PSUControl as a sub-plugin

## Setup

Install libcoap using [this script](https://github.com/home-assistant-libs/pytradfri/blob/master/script/install-coap-client.sh)

Install via the bundled [Plugin Manager](https://docs.octoprint.org/en/master/bundledplugins/pluginmanager.html)
or manually using this URL:

    https://github.com/Piets/OctoPrint-PSUControl-Tradfri/archive/master.zip



## Configuration

Enter the Address of the Ikea Tradfri Gateway in the settings.

Enter the Security Key of the Gateway (can be found on the label at the  back of the Gateway) in the settings.

Enter the name of the smart Plug exactly as in the Ikea Home Smart 1 application (case sensitive).

Select this plugin as a Switching and/or Sensing method in [PSU Control](https://github.com/kantlivelong/OctoPrint-PSUControl)
