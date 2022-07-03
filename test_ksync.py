import pytest
import random
import string

from ksync import KSync

# A number of constants to be used throughout the tests
device_id = '1234'
fleet_id = '123'
short_message = ''.join(random.choices(string.ascii_uppercase + string.digits, k=47))
long_message = ''.join(random.choices(string.ascii_uppercase + string.digits, k=49))
too_long_message = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4097))


@pytest.fixture
def k():
  """
  Although initializing ksync is not currently a heavy operation, there is no reason to keep doing it.
  """

  return KSync()


def test_length_code_short_message():
  """
  Test the return is correct when the length of the message is 47 characters.
  """

  assert KSync._length_code(message=short_message) == '\x46'


def test_length_code_long_message():
  """
  Test the return is correct when the length of the message is 49 characters.
  """

  assert KSync._length_code(message=long_message) == '\x47'


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

  assert k.send_text(short_message, broadcast=True) == f'\x02\x460000000{short_message}0\x03'


def test_send_short_text_single_device(k):
  assert k.send_text(message=short_message,
                     fleet=fleet_id,
                     device=device_id) == f'\x02\x46{fleet_id}{device_id}{short_message}0\x03'


def test_send_text_broadcast_false_exception(k):
  with pytest.raises(Exception):
      assert k.send_text(short_message)
