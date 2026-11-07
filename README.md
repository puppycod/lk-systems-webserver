# LK Systems Webserver

A local Home Assistant custom integration for LK Webserver and LK ICS.2 floor heating. The protocol was investigated on firmware 3.1.850. Home Assistant communicates with the Webserver using its local HTTP interface.

This project started after we found a Home Assistant setup for LK ICS.2 over Modbus RTU and couldn't find an integration that used the LK Webserver's local interface. We wanted to use the Webserver already connected to the heating system, so we mapped its local HTTP requests. The existing Modbus work was the starting point for that search. [Modbus setup by astrandb](https://github.com/astrandb/lk-systems-floor) · [Home Assistant Community discussion](https://community.home-assistant.io/t/lk-systems-floor-heating-ongoing-help-wouldn-t-hurt/292646)

This independent integration and its author are not affiliated with, endorsed by, or supported by LK Systems. Use it at your own risk.

For hardware setup and troubleshooting, see the manufacturer's documentation. [LK Systems ICS.2 support](https://www.lksystems.se/sv/produktsystem/golvvarme/support-for-golvvarmesystem/support-for-lk-ics.2/) · [LK Webserver installation manual (English)](https://www.lksystems.se/download/75166/en.33.c.190_lk-webserver.pdf?1750570618281=)

## Install with Home Assistant Marketplace

Home Assistant 2026.11 includes the Marketplace, which replaces HACS. [Home Assistant Marketplace documentation](https://www.home-assistant.io/integrations/marketplace/)

1. Open **Settings → Marketplace → Add from link**.
2. Enter `https://github.com/puppycod/lk-systems-webserver` and select **Add**. Connect GitHub if prompted. If asked for the type, select **Integration**.
3. Open **LK Systems Webserver** in the Marketplace and select **Install**.
4. Restart Home Assistant to load the installed integration.
5. For a new setup, open **Settings → Devices & services → Add integration → LK Systems Webserver** and enter the local Webserver address and credentials.

If you previously installed the integration manually, the Marketplace installs it to the same directory. After restarting Home Assistant, use the existing integration entry. Future releases appear under **Settings → Updates**.

## Install manually

1. Copy `custom_components/lk_systems_webserver` into the Home Assistant configuration directory. The manifest should end up at `/config/custom_components/lk_systems_webserver/manifest.json`.
2. Restart Home Assistant.
3. Go to **Settings → Devices & services → Add integration → LK Systems Webserver**.
4. Enter the Webserver's local hostname or IP address and the local Webserver username and password.
5. Open **Floor Heating** from the sidebar as a Home Assistant administrator.

Minimum Home Assistant Core version: **2026.11.0**.

The panel and integration are available in English, Finnish, Swedish and Norwegian Bokmål. The panel content follows the Home Assistant profile language. Home Assistant uses a shared sidebar label for custom panels, so this label follows the system language.

To upgrade an existing installation, replace the contents of its `custom_components/lk_systems_webserver` directory and restart Home Assistant. The existing climate entity IDs and settings are retained.

## Change the Webserver password

Change the password on the LK Webserver first. In Home Assistant, open **Settings → Devices & services → LK Systems Webserver**, then choose **Reconfigure** from the hub's menu and enter the new password. If Home Assistant prompts for reauthentication, you can enter it there instead. Home Assistant verifies the password and device identity, then reloads the existing entry.

## Home Assistant entities

Each thermostat device has a climate entity, battery and radio link diagnostics, switches for the weekly program, adaptive start, backlight and key lock, and number entities for Comfort, Economy, Holiday and Setback temperatures. The radio value uses the LK scale.

Each thermostat also exposes read-only room temperature, target temperature and heating demand entities for dashboards and automations. Use the climate entity to change the target.

The LK Systems Webserver device has connection status, the time of the last successful read, effective system mode, reported pump and boiler relay states, and a clock sync button. Thermostat devices are linked to this hub in the device registry. The panel provides the week editor, extended room settings and system mode controls.

The hub also exposes **System mode control** (Normal, Holiday or Setback) and **Planned holiday end date** for dashboards and automations. Set the date first, then select Holiday. Home Assistant saves the planned date locally and sends it to LK when Holiday is selected. The date must be 1–99 days ahead of the Webserver's current date. The separate **System mode** sensor reports the effective mode from LK.

**Estimated holiday end date** is a read-only date sensor calculated from the LK clock and its remaining whole-hour counter while Webserver Holiday mode is selected. It also reflects holidays configured on the LK Webserver. The estimate can be off by a day around midnight. Use **System mode** to trigger an automation when Holiday actually ends.

## What it controls

- Discover active thermostats and create climate entities identified by Webserver MAC and thermostat number. Room names in the panel are read from LK.
- Show current temperature, target temperature and heating demand. Poll the Webserver every minute. The panel shows the latest successful read and flags persistent connection failures.
- Read battery and radio link quality at startup and hourly. Opening room settings also refreshes that room's detailed data.
- Set room targets, weekly schedules, Comfort and Economy temperatures, adaptive start, backlight, key lock, room target limits, holiday and setback temperatures, fireplace duration and output, and bypass mode.
- Show the system mode and reported pump and boiler relays. Set Holiday or Setback mode and synchronize the LK clock from Home Assistant's configured timezone.

The room card uses the LK native weekly program. A manual target during an active program requests the same temporary override as the Webserver interface. An empty schedule slot is represented on the device by two equal time values.

Writes use the local `update.cgi` endpoint and verify the result by reading it back. Where LK requires multiple writes, the integration serializes them. If a multi-step write fails, refresh the settings and retry the intended change. The device protocol does not provide an atomic transaction.

Floor sensor control and LK WSS are outside this preview. The connection indicator measures the Home Assistant to Webserver connection.

## Verify after installation

1. Check that the expected room names appear and that the reported values match the LK Webserver.
2. Change one room target by 0.5 °C in Home Assistant. Verify it on the LK Webserver and restore the original target.
3. Change one economy interval and restore it after checking both interfaces.
4. Make a reversible change on the LK Webserver and check that the Home Assistant reading updates.
5. Check the connection indicator and both panel languages.

The local HTTP login should be used on a trusted network. Keep the Webserver credentials in the Home Assistant setup form and out of repository files.


