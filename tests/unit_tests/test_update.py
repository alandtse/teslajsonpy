"""Test controller updates."""

import copy
import time

import pytest

from teslajsonpy.controller import Controller

from tests.tesla_mock import CAR_ID, TeslaMock, VIN


@pytest.mark.asyncio
async def test_update_handles_vehicle_data_without_drive_state(monkeypatch):
    """Test update handles vehicle data payloads missing drive_state."""
    original_update = Controller.update
    mock = TeslaMock(monkeypatch)
    monkeypatch.setattr(Controller, "update", original_update)

    controller = Controller(None)
    await controller.connect()
    await controller.generate_car_objects()

    cached_data = controller.cars[VIN]._vehicle_data
    cached_data["climate_state"]["is_climate_on"] = True

    mock._vehicle_data = copy.deepcopy(cached_data)
    mock._vehicle_data["charge_state"]["battery_level"] = 55
    mock._vehicle_data.pop("drive_state")

    before_update = int(time.time())

    await controller.update(car_id=CAR_ID, force=True)

    assert controller.get_last_update_time(vin=VIN) >= before_update
    assert controller.get_last_park_time(vin=VIN) >= before_update
    assert controller.cars[VIN].battery_level == 55
