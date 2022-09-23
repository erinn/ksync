"""
Test KMessage
"""
import pytest

from ksync.kmessage import KMessage

binary_ack = b"\x020\x03"
binary_identification_d = b"\x02D2001814\x03"
binary_identification_i = b"\x02I020018142001814\x03"
binary_pklsh = b"$PKLSH,3851.3330,N,09447.9417,W,012212,V,100,1202,*24"
string_pklsh = "$PKLSH,3851.3330,N,09447.9417,W,012212,V,100,1202,*24"


def test_ack_binary_message():
    """
    Test a binary acknowledgement message.
    """
    # Expected
    ack = True

    output = KMessage(binary_ack)

    assert output.ack == ack


def test_identification_d_binary_message():
    """
    Test a binary caller ID (D) message.
    """
    # Expected
    device_id = 1814
    fleet_id = 200

    output = KMessage(binary_identification_d)

    assert output.device_id == device_id
    assert output.fleet_id == fleet_id


def test_identification_i_binary_message():
    """
    Test a binary caller ID (I) message.
    """
    # Expected
    device_id = 1814
    fleet_id = 200

    output = KMessage(binary_identification_i)

    assert output.device_id == device_id
    assert output.fleet_id == fleet_id


def test_malformed_binary_message():
    """
    Test that an exception is raised from a binary malformed message.
    """
    with pytest.raises(Exception):
        KMessage(b"\x02D2001814")


def test_pklsh_binary_message():
    """
    Test a PKLSH binary message.
    """
    # Expected:
    device_id = 1202
    fleet_id = 100
    lat = 38.85555
    lon = -94.7990283333
    nmea_message = "<NMEA(PKLSH, lat=38.85555, NS=N, lon=-94.7990283333, EW=W, time=01:22:12, status=V, fleetId=100, deviceId=1202)>"

    output = KMessage(binary_pklsh)

    assert output.device_id == device_id
    assert output.fleet_id == fleet_id
    assert output.nmea_message.lat == lat
    assert output.nmea_message.lon == lon
    assert str(output.nmea_message) == nmea_message


def test_pklsh_string_message():
    """
    Test a PKLSH message sent as a string, an exception should be raised.
    """
    with pytest.raises(TypeError):
        KMessage(string_pklsh)


def test_unknown_message():
    """
    Test a properly formatted, but unknown message raises an exception.
    """
    with pytest.raises(Exception):
        KMessage(b"\x02FOO\x03")
