from unittest.mock import MagicMock

import random
import string
import pytest

from ksync.ksync import KSync

# A number of constants to be used throughout the tests
device_id = "1234"
fleet_id = "123"
short_message = "".join(random.choices(string.ascii_uppercase + string.digits, k=47))
long_message = "".join(random.choices(string.ascii_uppercase + string.digits, k=49))
too_long_message = "".join(
    random.choices(string.ascii_uppercase + string.digits, k=4097)
)


@pytest.fixture
def k():
    """
    Instantiate KSync with a MagicMocked serial port object.
    """

    def len_message(message):
        return len(message)

    mock_port = MagicMock(spec=["flush", "write"])
    mock_port.flush.return_value = True
    mock_port.write.side_effect = len_message

    return KSync(mock_port)


def test_length_code_short_message():
    """
    Test the return is correct when the length of the message is 47 characters.
    """
    expected = "\x46"

    output = KSync._length_code(message=short_message)

    assert output == expected


def test_length_code_long_message():
    """
    Test the return is correct when the length of the message is 49 characters.
    """
    expected = "\x47"

    output = KSync._length_code(message=long_message)

    assert output == expected


def test_length_code_too_long_message():
    """
    Test that an exception is thrown when the length of the message is 4097 characters.
    """

    with pytest.raises(Exception):
        assert KSync._length_code(too_long_message)


def test_send_short_text_broadcast(k):
    """
    Test a basic broadcast message is formatted correctly.
    """
    # Arrange
    expected = len(b"\x02\x460000000" + short_message.encode() + b"\x03")

    # Act
    output = k.send_text(short_message, broadcast=True)

    # Assert
    assert output == expected


def test_send_short_text_single_device(k):
    expected = len(
        b"\x02\x46"
        + fleet_id.encode()
        + device_id.encode()
        + short_message.encode()
        + b"\x03"
    )

    output = k.send_text(message=short_message, fleet_id=fleet_id, device_id=device_id)

    assert output == expected


def test_poll_gnss(k):
    expected = len(b"\x02\x52\x33" + fleet_id.encode() + device_id.encode() + b"\x03")

    output = k.poll_gnss(fleet_id=fleet_id, device_id=device_id)

    assert output == expected
