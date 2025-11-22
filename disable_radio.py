from aiounifi.models.api import ApiRequest

class SetDisabledDevice(ApiRequest):
    """Data class to disable the radio on an access point."""

    def __init__(self, id: str, disabled: bool) -> None:
        """Initialize DisableRadioRequest."""
        path = f"/rest/device/{id}"
        data = {
           "disabled": disabled
        }
        super().__init__(method="PUT", path=path, data=data)