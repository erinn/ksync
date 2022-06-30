import pytest
import random
import string

from ksync import ksync

def test_length_code_47():
  '''
  Test the return is correct when the length of the message is 47 characters.
  '''

  string_47 = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 47))

  k = ksync()
  assert k._length_code(message = string_47) == '\x46'

def test_length_code_49():
  '''
  Test the return is correct when the length of the message is 49 characters.
  '''

  string_49 = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 49))

  k = ksync()
  assert k._length_code(message = string_49) == '\x47'

def test_length_code_4097():
  '''
  Test that an exception is thrown when the length of the message is 4097 characters.
  '''
  
  string_4097 = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 4097))

  k = ksync()

  with pytest.raises(Exception):
    assert k._length_code(string_4097)