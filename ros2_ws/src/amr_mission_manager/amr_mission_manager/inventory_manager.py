"""Load and query a validated warehouse inventory without requiring ROS."""

from dataclasses import dataclass
from math import isfinite
from pathlib import Path
from typing import Any

import yaml


class InventoryError(ValueError):
    """Base class for inventory configuration and lookup errors."""


class InvalidInventoryError(InventoryError):
    """The inventory file cannot be read or does not match the schema."""


class UnknownSKUError(InventoryError):
    """A requested SKU does not exist in the inventory."""


class UnknownRackError(InventoryError):
    """A requested rack does not exist in the inventory."""


@dataclass(frozen=True)
class InventoryItem:
    """A warehouse item and the rack where it is stored."""

    sku: str
    name: str
    rack: str


@dataclass(frozen=True)
class RackLocation:
    """A rack approach pose in map coordinates, with yaw in radians."""

    rack_id: str
    x: float
    y: float
    yaw: float


def _mapping(value: Any, context: str) -> dict:
    """Require a YAML mapping and retain context in validation errors."""
    if not isinstance(value, dict):
        raise InvalidInventoryError(f"{context} must be a mapping")
    return value


def _text(value: Any, context: str, *, identifier: bool = False) -> str:
    """Validate text, rejecting ambiguous whitespace around identifiers."""
    if not isinstance(value, str) or not value.strip():
        raise InvalidInventoryError(f"{context} must be a nonempty string")
    if identifier and value != value.strip():
        raise InvalidInventoryError(
            f"{context} must not have leading or trailing whitespace"
        )
    if identifier and not value.isprintable():
        raise InvalidInventoryError(f"{context} must not contain control characters")
    return value.strip()


def _coordinate(value: Any, context: str) -> float:
    """Require a finite real number; YAML booleans are not coordinates."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InvalidInventoryError(f"{context} must be a finite number")
    try:
        coordinate = float(value)
    except OverflowError as exc:
        raise InvalidInventoryError(f"{context} must be a finite number") from exc
    if not isfinite(coordinate):
        raise InvalidInventoryError(f"{context} must be a finite number")
    return coordinate


class InventoryManager:
    """Read a YAML inventory once and expose immutable validated records.

    Every item must reference an existing rack. Inventory identifiers are
    case-sensitive and must not contain surrounding whitespace. Coordinates
    are meters and yaw is radians in the shared map frame.
    """

    def __init__(self, path: str | Path) -> None:
        """Load the file safely and validate it before accepting any tasks."""
        inventory_path = Path(path)
        try:
            with inventory_path.open("r", encoding="utf-8") as stream:
                raw = yaml.safe_load(stream)
        except (OSError, UnicodeError, ValueError, RecursionError, yaml.YAMLError) as exc:
            raise InvalidInventoryError(
                f"Cannot load inventory {inventory_path}: {exc}"
            ) from exc

        document = _mapping(raw, "Inventory")
        raw_items = _mapping(document.get("items"), "items")
        raw_racks = _mapping(document.get("racks"), "racks")
        self._racks = self._load_racks(raw_racks)
        self._items = self._load_items(raw_items)

    @staticmethod
    def _load_racks(raw_racks: dict) -> dict[str, RackLocation]:
        """Validate rack IDs and all three planar pose coordinates."""
        racks: dict[str, RackLocation] = {}
        for raw_id, raw_record in raw_racks.items():
            rack_id = _text(raw_id, "Rack ID", identifier=True)
            record = _mapping(raw_record, f"Rack {rack_id}")
            racks[rack_id] = RackLocation(
                rack_id=rack_id,
                x=_coordinate(record.get("x"), f"Rack {rack_id}.x"),
                y=_coordinate(record.get("y"), f"Rack {rack_id}.y"),
                yaw=_coordinate(record.get("yaw"), f"Rack {rack_id}.yaw"),
            )
        return racks

    def _load_items(self, raw_items: dict) -> dict[str, InventoryItem]:
        """Validate item records and reject unresolved rack references."""
        items: dict[str, InventoryItem] = {}
        for raw_sku, raw_record in raw_items.items():
            sku = _text(raw_sku, "SKU", identifier=True)
            record = _mapping(raw_record, f"Item {sku}")
            name = _text(record.get("name"), f"Item {sku}.name")
            rack = _text(record.get("rack"), f"Item {sku}.rack", identifier=True)
            if rack not in self._racks:
                raise InvalidInventoryError(
                    f"Item {sku} references missing rack {rack}"
                )
            items[sku] = InventoryItem(sku=sku, name=name, rack=rack)
        return items

    @property
    def item_count(self) -> int:
        """Return the number of catalogued SKUs."""
        return len(self._items)

    @property
    def rack_count(self) -> int:
        """Return the number of configured rack poses."""
        return len(self._racks)

    def get_item(self, sku: str) -> InventoryItem:
        """Look up a case-sensitive SKU or raise UnknownSKUError."""
        if not isinstance(sku, str) or sku not in self._items:
            raise UnknownSKUError(f"Unknown SKU: {sku!r}")
        return self._items[sku]

    def get_rack(self, rack_id: str) -> RackLocation:
        """Look up a case-sensitive rack ID or raise UnknownRackError."""
        if not isinstance(rack_id, str) or rack_id not in self._racks:
            raise UnknownRackError(f"Unknown rack: {rack_id!r}")
        return self._racks[rack_id]

    def resolve_sku(self, sku: str) -> RackLocation:
        """Resolve an SKU to its configured rack approach coordinates."""
        return self.get_rack(self.get_item(sku).rack)
