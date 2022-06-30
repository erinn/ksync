import pytest
import random
import string

from ksync import ksync

def test_length_code_47():
  '''
  Test the return is correct when the length of the message is 47 characters.
  '''

  string_47 = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 47))

  assert ksync._length_code(message = string_47) == '\x46'

def test_length_code_49():
  '''
  Test the return is correct when the length of the message is 49 characters.
  '''

  string_49 = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 49))

  assert ksync._length_code(message = string_49) == '\x47'

def test_length_code_4097():
  '''
  Test that an exception is thrown when the length of the message is 4097 characters.
  '''

  string_4097 = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 4097))

  with pytest.raises(Exception):
    assert ksync._length_code(string_4097)

def test_send_text_broadcast():
  message = 'foo'
  k = ksync()

  assert k.send_text(message, broadcast=True) == '\x02\x460000000foo0\x03'

def test_send_text_single_device():
  message = 'foo'
  fleet = '123'
  device = '1234'

  k = ksync()
  assert k.send_text(message=message, fleet=fleet, device=device) == '\x02\x461231234foo0\x03'

def test_send_text_broadcast_false_exception():
  message = 'foo'
  k = ksync()

  with pytest.raises(Exception):
    assert k.send_text(message)