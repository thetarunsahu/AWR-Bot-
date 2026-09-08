"""Exercise inventory validation and SKU-to-rack resolution without ROS."""

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest
import yaml

from amr_mission_manager.inventory_manager import (
    InvalidInventoryError,
    InventoryManager,
    UnknownRackError,
    UnknownSKUError,
)


@pytest.fixture
def catalog() -> dict:
    """Provide a small independent inventory with distinct approach poses."""
    return {
        "items": {
            "SKU001": {"name": "Laptop", "rack": "RACK_A1"},
            "SKU002": {"name": "Keyboard", "rack": "RACK_B2"},
        },
        "racks": {
            "RACK_A1": {"x": 2.0, "y": 4.0, "yaw": 0.0},
            "RACK_B2": {"x": 6.5, "y": 1.5, "yaw": 1.57},
        },
    }


def load_catalog(tmp_path: Path, catalog: dict) -> InventoryManager:
    """Write an isolated YAML inventory and load it through the public API."""
    path = tmp_path / "inventory.yaml"
    path.write_text(yaml.safe_dump(catalog), encoding="utf-8")
    return InventoryManager(path)


def test_valid_sku_and_coordinate_lookup(tmp_path: Path, catalog: dict) -> None:
    inventory = load_catalog(tmp_path, catalog)

    item = inventory.get_item("SKU001")
    assert (item.sku, item.name, item.rack) == ("SKU001", "Laptop", "RACK_A1")
    first = inventory.resolve_sku("SKU001")
    assert (first.rack_id, first.x, first.y, first.yaw) == (
        "RACK_A1", 2.0, 4.0, 0.0
    )
    second = inventory.get_rack("RACK_B2")
    assert (second.x, second.y, second.yaw) == (6.5, 1.5, 1.57)
    assert inventory.resolve_sku("SKU002") == second
    assert inventory.item_count == 2
    assert inventory.rack_count == 2


def test_catalog_records_cannot_be_mutated(tmp_path: Path, catalog: dict) -> None:
    inventory = load_catalog(tmp_path, catalog)
    with pytest.raises(FrozenInstanceError):
        inventory.get_item("SKU001").rack = "RACK_B2"
    with pytest.raises(FrozenInstanceError):
        inventory.get_rack("RACK_A1").x = 100.0


@pytest.mark.parametrize("sku", ["UNKNOWN", "sku001", "", None, []])
def test_unknown_sku(tmp_path: Path, catalog: dict, sku: object) -> None:
    inventory = load_catalog(tmp_path, catalog)
    with pytest.raises(UnknownSKUError, match="Unknown SKU"):
        inventory.resolve_sku(sku)


def test_unknown_rack(tmp_path: Path, catalog: dict) -> None:
    inventory = load_catalog(tmp_path, catalog)
    with pytest.raises(UnknownRackError, match="Unknown rack"):
        inventory.get_rack("RACK_MISSING")


def test_missing_rack_rejected_at_load(tmp_path: Path, catalog: dict) -> None:
    del catalog["racks"]["RACK_A1"]
    with pytest.raises(InvalidInventoryError, match="SKU001.*missing rack RACK_A1"):
        load_catalog(tmp_path, catalog)


@pytest.mark.parametrize("field", ["x", "y", "yaw"])
@pytest.mark.parametrize("value", [True, "2.0", None, float("nan"), float("inf"),
                                       float("-inf"), 10 ** 400])
def test_invalid_coordinate_rejected(
    tmp_path: Path, catalog: dict, field: str, value: object
) -> None:
    catalog["racks"]["RACK_A1"][field] = value
    with pytest.raises(InvalidInventoryError, match=f"RACK_A1.{field}.*finite number"):
        load_catalog(tmp_path, catalog)


@pytest.mark.parametrize("field", ["x", "y", "yaw"])
def test_missing_coordinate_rejected(
    tmp_path: Path, catalog: dict, field: str
) -> None:
    del catalog["racks"]["RACK_A1"][field]
    with pytest.raises(InvalidInventoryError, match="finite number"):
        load_catalog(tmp_path, catalog)


@pytest.mark.parametrize("field", ["name", "rack"])
@pytest.mark.parametrize("value", [None, "", "   ", 123, True, []])
def test_invalid_item_field(
    tmp_path: Path, catalog: dict, field: str, value: object
) -> None:
    catalog["items"]["SKU001"][field] = value
    with pytest.raises(InvalidInventoryError, match="nonempty string"):
        load_catalog(tmp_path, catalog)


@pytest.mark.parametrize("section", ["items", "racks"])
@pytest.mark.parametrize("identifier", [123, True, "", "  ", " PADDED ", "A\nB"])
def test_invalid_identifiers(
    tmp_path: Path, catalog: dict, section: str, identifier: object
) -> None:
    record = next(iter(catalog[section].values()))
    catalog[section][identifier] = record
    with pytest.raises(InvalidInventoryError):
        load_catalog(tmp_path, catalog)


@pytest.mark.parametrize("section", ["items", "racks"])
@pytest.mark.parametrize("value", [None, [], "invalid", 1])
def test_invalid_section(
    tmp_path: Path, catalog: dict, section: str, value: object
) -> None:
    catalog[section] = value
    with pytest.raises(InvalidInventoryError, match="must be a mapping"):
        load_catalog(tmp_path, catalog)


@pytest.mark.parametrize("raw", ["", "[1, 2]", "items: [unclosed", "items: {}",
                                     "!!python/object/apply:os.system ['echo unsafe']"])
def test_malformed_yaml_or_schema(tmp_path: Path, raw: str) -> None:
    path = tmp_path / "invalid.yaml"
    path.write_text(raw, encoding="utf-8")
    with pytest.raises(InvalidInventoryError):
        InventoryManager(path)


def test_missing_file(tmp_path: Path) -> None:
    with pytest.raises(InvalidInventoryError, match="Cannot load inventory"):
        InventoryManager(tmp_path / "missing.yaml")


def test_deep_yaml_rejected_safely(tmp_path: Path) -> None:
    path = tmp_path / "deep.yaml"
    path.write_text("[" * 2000 + "0" + "]" * 2000, encoding="utf-8")
    with pytest.raises(InvalidInventoryError):
        InventoryManager(path)


def test_inventory_requires_utf8(tmp_path: Path) -> None:
    path = tmp_path / "invalid.yaml"
    path.write_bytes(b"\xff\xfe\x00")
    with pytest.raises(InvalidInventoryError, match="Cannot load inventory"):
        InventoryManager(path)
