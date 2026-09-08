"""ROS-independent task validation and planar orientation conversion."""

from dataclasses import dataclass
import json
from math import cos, isfinite, sin
from typing import Any


MAX_REQUEST_LENGTH = 16_384
MAX_IDENTIFIER_LENGTH = 128


class InvalidRequestError(ValueError):
    """A warehouse task request cannot be safely interpreted."""


@dataclass(frozen=True)
class TaskRequest:
    """A validated warehouse request; DELIVER currently resolves a rack pose."""

    task_id: str
    sku: str
    action: str


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject duplicate JSON keys instead of silently changing a request."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise InvalidRequestError(f"Duplicate JSON field: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    """Reject Python JSON extensions such as NaN and Infinity."""
    raise InvalidRequestError(f"Nonstandard JSON constant: {value}")


def _request_field(payload: dict[str, Any], field: str) -> str:
    """Extract one required, nonempty string and normalize whitespace."""
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise InvalidRequestError(f"{field} must be a nonempty string")
    value = value.strip()
    if not value.isprintable():
        raise InvalidRequestError(f"{field} must not contain control characters")
    return value


def parse_task_request(raw: str) -> TaskRequest:
    """Parse a JSON object containing task_id, sku, and action strings.

    Requests are limited to 16,384 characters, and task/SKU identifiers to
    128 characters after trimming, with no embedded control characters.
    DELIVER is the only supported action.
    Extra fields are accepted for future warehouse metadata, but duplicate
    keys and nonstandard JSON constants anywhere in the object are rejected.
    """
    if not isinstance(raw, str) or not raw.strip():
        raise InvalidRequestError("Request must be a nonempty JSON string")
    if len(raw) > MAX_REQUEST_LENGTH:
        raise InvalidRequestError(
            f"Request exceeds {MAX_REQUEST_LENGTH} characters"
        )
    try:
        payload = json.loads(
            raw,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except InvalidRequestError:
        raise
    except (ValueError, RecursionError) as exc:
        raise InvalidRequestError(f"Malformed JSON request: {exc}") from exc
    if not isinstance(payload, dict):
        raise InvalidRequestError("Request must be a JSON object")

    task_id = _request_field(payload, "task_id")
    sku = _request_field(payload, "sku")
    action = _request_field(payload, "action")
    for field, value in (("task_id", task_id), ("sku", sku)):
        if len(value) > MAX_IDENTIFIER_LENGTH:
            raise InvalidRequestError(
                f"{field} exceeds {MAX_IDENTIFIER_LENGTH} characters"
            )
    if action != "DELIVER":
        raise InvalidRequestError(f"Unsupported action: {action}; expected DELIVER")
    return TaskRequest(task_id=task_id, sku=sku, action=action)


def yaw_to_quaternion(yaw: float) -> tuple[float, float, float, float]:
    """Return an (x, y, z, w) unit quaternion for finite yaw in radians."""
    if isinstance(yaw, bool) or not isinstance(yaw, (int, float)):
        raise ValueError("yaw must be a finite number")
    try:
        angle = float(yaw)
    except OverflowError as exc:
        raise ValueError("yaw must be a finite number") from exc
    if not isfinite(angle):
        raise ValueError("yaw must be a finite number")
    return (0.0, 0.0, sin(angle / 2.0), cos(angle / 2.0))
