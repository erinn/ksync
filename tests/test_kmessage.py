import pytest

from ksync.kmessage import KMessage


def test_ack_message():
    """
    Test an acknowledgement message.
    """
    # Expected
    ack = True

    output = KMessage(b"\x020\x03")

    assert output.ack == ack


def test_identification_message():
    """
    Test a caller ID message
    """
    # Expected
    device_id = 1814
    fleet_id = 200

    output = KMessage(b"\x02D2001814\x03")

    assert output.device_id == device_id
    assert output.fleet_id == fleet_id


def test_malformed_message():
    """
    Test that an exception is raised from a malformed message.
    """
    with pytest.raises(Exception):
        KMessage(b"\x02D2001814")


def test_unknown_message():
    """
    Test a properly formatted, but unknown message raises an exception.
    """
    with pytest.raises(Exception):
        KMessage(b"\x02FOO\x03")
