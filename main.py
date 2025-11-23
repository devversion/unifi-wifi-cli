"""Control UniFi devices."""

import asyncio
import os
import aiohttp
from aiounifi.controller import Controller
from aiounifi.models.configuration import Configuration
from aiounifi.models.device import DeviceRestartRequest
import typer
from typing import Annotated
from rich import print
from dotenv import load_dotenv

from disable_radio import SetDisabledDevice

load_dotenv()

# --- Configuration ---
# Replace with your UniFi Controller's details
CONTROLLER_IP = os.getenv("CONTROLLER_IP")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
PORT = int(os.getenv("PORT", 443))
SITE = os.getenv("SITE", "default")

app = typer.Typer()

async def set_all_devices_disabled_status(disabled: bool):
    """Connect to the UniFi controller and set the disabled status of all APs."""
    if not all([CONTROLLER_IP, USERNAME, PASSWORD]):
        print("Please set CONTROLLER_IP, USERNAME, and PASSWORD environment variables.")
        return

    async with aiohttp.ClientSession(
        cookie_jar=aiohttp.CookieJar(unsafe=True),
    ) as session:
        try:
            unifi_controller = Controller(
                config=Configuration(
                    host=CONTROLLER_IP,
                    username=USERNAME,
                    password=PASSWORD,
                    port=PORT,
                    site=SITE,
                    session=session,
                    ssl_context=False
                )
            )

            await unifi_controller.login()

            await unifi_controller.devices.update()

            aps = unifi_controller.devices.values()

            print(f"Setting disabled state for all APs to [bold red]{disabled}[/bold red]")

            for ap in aps:
                if ap.raw.get('type') == 'uap':
                    print(f"- Setting device {ap.name} ({ap.mac}): disabled={disabled}")
                    await unifi_controller.request(SetDisabledDevice(id=ap.id, disabled=disabled))

            print("Finished setting disabled state for all APs.")

        except Exception as e:
            print(f"An error occurred: {e}")


@app.command()
def control_wifi(
    disabled: Annotated[
        bool,
        typer.Option(
            writable=True,
            help="Disable the device. Use --no-disabled to enable it.", rich_help_panel="Wifi Control"
        ),
    ],
):
    """Set the disabled state of all devices."""
    print(
        f"Setting disabled state for all devices to [bold red]{disabled}[/bold red]"
    )
    asyncio.run(set_all_devices_disabled_status(disabled))


if __name__ == "__main__":
    app()
