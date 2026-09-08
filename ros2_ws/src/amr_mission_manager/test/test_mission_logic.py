"""Validate JSON requests and yaw conversion with no ROS dependency."""

import json
from math import pi, sqrt

import pytest

from amr_mission_manager.mission_logic import (
    InvalidRequestError,
    MAX_IDENTIFIER_LENGTH,
    MAX_REQUEST_LENGTH,
    TaskRequest,
    parse_task_request,
    yaw_to_quaternion,
)


def test_valid_request() -> None:
    task = parse_task_request(
        '{"task_id":"TASK001", "sku":"SKU001", "action":"DELIVER"}'
    )
    assert task == TaskRequest("TASK001", "SKU001", "DELIVER")


def test_request_values_trimmed_and_metadata_allowed() -> None:
    task = parse_task_request(json.dumps({
        "task_id": " TASK001 ", "sku": " SKU001\n", "action": " DELIVER ",
        "priority": 2,
    }))
    assert task == TaskRequest("TASK001", "SKU001", "DELIVER")


@pytest.mark.parametrize("raw", ["", "  ", "not json", "{", "[]", "null",
                                     "42", '"request"', "true", "{}", None])
def test_malformed_or_nonobject_request(raw: object) -> None:
    with pytest.raises(InvalidRequestError):
        parse_task_request(raw)


@pytest.mark.parametrize("field", ["task_id", "sku", "action"])
def test_missing_required_field(field: str) -> None:
    request = {"task_id": "TASK001", "sku": "SKU001", "action": "DELIVER"}
    del request[field]
    with pytest.raises(InvalidRequestError, match=field):
        parse_task_request(json.dumps(request))


@pytest.mark.parametrize("field", ["task_id", "sku", "action"])
@pytest.mark.parametrize("value", ["", " \t\n ", None, 123, True, [], {}])
def test_invalid_required_field(field: str, value: object) -> None:
    request = {"task_id": "TASK001", "sku": "SKU001", "action": "DELIVER"}
    request[field] = value
    with pytest.raises(InvalidRequestError, match=field):
        parse_task_request(json.dumps(request))


@pytest.mark.parametrize("action", ["PICK", "CANCEL", "deliver"])
def test_unsupported_action(action: str) -> None:
    request = {"task_id": "TASK001", "sku": "SKU001", "action": action}
    with pytest.raises(InvalidRequestError, match="Unsupported action"):
        parse_task_request(json.dumps(request))


@pytest.mark.parametrize("field", ["task_id", "sku", "action"])
@pytest.mark.parametrize("value", ["A\nB", "A\tB", "A\x00B", "A\x1bB"])
def test_embedded_control_characters_rejected(field: str, value: str) -> None:
    request = {"task_id": "TASK001", "sku": "SKU001", "action": "DELIVER"}
    request[field] = value
    with pytest.raises(InvalidRequestError, match="control characters"):
        parse_task_request(json.dumps(request))


@pytest.mark.parametrize("constant", ["NaN", "Infinity", "-Infinity"])
def test_nonstandard_json_constant_rejected(constant: str) -> None:
    raw = ('{"task_id":"TASK001", "sku":"SKU001", "action":"DELIVER", '
           '"metadata":' + constant + '}')
    with pytest.raises(InvalidRequestError, match="Nonstandard JSON constant"):
        parse_task_request(raw)


def test_duplicate_json_key_rejected() -> None:
    raw = ('{"task_id":"TASK001", "sku":"SKU001", "sku":"SKU002", '
           '"action":"DELIVER"}')
    with pytest.raises(InvalidRequestError, match="Duplicate JSON field: sku"):
        parse_task_request(raw)


def test_request_size_guard() -> None:
    with pytest.raises(InvalidRequestError, match="Request exceeds"):
        parse_task_request("x" * (MAX_REQUEST_LENGTH + 1))


@pytest.mark.parametrize("field", ["task_id", "sku"])
def test_identifier_size_guard(field: str) -> None:
    request = {"task_id": "TASK001", "sku": "SKU001", "action": "DELIVER"}
    request[field] = "x" * (MAX_IDENTIFIER_LENGTH + 1)
    with pytest.raises(InvalidRequestError, match=f"{field} exceeds"):
        parse_task_request(json.dumps(request))


def test_deep_json_rejected_safely() -> None:
    raw = "[" * 2000 + "0" + "]" * 2000
    with pytest.raises(InvalidRequestError):
        parse_task_request(raw)


@pytest.mark.parametrize("yaw, expected", [
    (0.0, (0.0, 0.0, 0.0, 1.0)),
    (pi / 2, (0.0, 0.0, sqrt(0.5), sqrt(0.5))),
    (-pi / 2, (0.0, 0.0, -sqrt(0.5), sqrt(0.5))),
    (pi, (0.0, 0.0, 1.0, 0.0)),
])
def test_yaw_quaternion(yaw: float, expected: tuple[float, ...]) -> None:
    quaternion = yaw_to_quaternion(yaw)
    assert quaternion == pytest.approx(expected)
    assert sum(value * value for value in quaternion) == pytest.approx(1.0)


@pytest.mark.parametrize("yaw", [float("nan"), float("inf"), float("-inf"),
                                      True, "0", None, 10 ** 400])
def test_invalid_yaw_rejected(yaw: object) -> None:
    with pytest.raises(ValueError, match="finite number"):
        yaw_to_quaternion(yaw)
