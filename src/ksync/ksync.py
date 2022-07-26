import logging

logger = logging.getLogger('KSync')


class KSync:
    """
    Provides methods to work with FleetSync.
    """

    def __init__(self, serial_port: object) -> None:
        """
        :param serial_port: A serial port object, object must have a
        write() and flush() method.
        """
        self.serial_port = serial_port
        self.sequence = 0

    @staticmethod
    def _length_code(message: str) -> bytes:
        """
        :param message: The message to be transmitted.
        :return: Hex codes to indicate the length of the message to be sent to the serial port.

        If the message length is greater than 4096 characters an exception is thrown.

        <length_code> - indicates max possible message length, though the plain text message is not padded to that length
        46 hex (ascii F) - corresponds to 'S' (Short - 48 characters)
        47 hex (ascii G) - corresponds to both 'L' (Long - 1024 characters) and 'X' (Extra-long - 4096 characters)
        if you send COM port data with message body longer than that limit, the mobile will not transmit
        """

        length_of_message = len(message)

        if length_of_message <= 48:
            return '\x46'

        elif length_of_message <= 4096:
            return '\x47'

        else:
            raise Exception(f'Length of message is {length_of_message}, > 4096 characters and cannot be transmitted.')

    def send_text(self, message: str, fleet: str = '000', device: str = '0000', broadcast: bool = False) -> int:
        """
        :param message: The text of the message to be sent.
        :param fleet: The fleet code to be used as a string.
        :param device: The device code to be used as a string.
        :param broadcast: Is the message intended to be a broadcast.
        :return: The number of characters transmitted.

        Send a  message to a given radio, or broadcast a  message to all radios.
        """

        if fleet == '000' and device == '0000' and broadcast is False:
            raise Exception(f'Fleet number {fleet} and device number {device} can not be set to 000 '
                            'and 0000 respectively unless broadcast is desired, please set a fleet '
                            'number and device number or enable broadcast.')

        text = f'\x02{self._length_code(message)}{fleet}{device}{message}' + \
               f'{str(self.sequence)}\x03'

        return_length = self.serial_port.write(text.encode())
        self.sequence += 1

        # No assumption is made that this is used within a qthread, hence it is flushed.
        self.serial_port.flush()

        return return_length

    def poll_gnss(self, fleet: str, device: str) -> int:
        """
        :param fleet: The fleet number as a string.
        :param device: The device number as a string.
        :return: The number of characters transmitted.

        Request a radio to return the current position using the
        Global Navigation Satellite Systems (commonly referred to as GPS).
        """
        message = f'\x02\x52\x33{fleet}{device}\x03'

        return_length = self.serial_port.write(message.encode())
        self.sequence += 1

        self.serial_port.flush()

        return return_length
