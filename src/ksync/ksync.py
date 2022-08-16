import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler)


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
        # Though the sequence number is unused it is held for completeness with
        # the understood protocol.
        self.sequence = 0

    @staticmethod
    def _length_code(message: str) -> str:
        """
        :param message: The message to be transmitted.
        :return: String that indicates the length of the message to be sent to the serial port.

        If the message length is greater than 4096 characters an exception is thrown.

        <length_code> - indicates max possible message length, though the plain text message is not padded to that length
        46 hex (ascii F) - corresponds to 'S' (Short - 48 characters)
        47 hex (ascii G) - corresponds to both 'L' (Long - 1024 characters) and 'X' (Extra-long - 4096 characters)
        """

        length_of_message = len(message)

        logger.info("Calculating length code for message.")
        logger.info("Length of message is %d", length_of_message)

        if length_of_message <= 48:
            return "\x46"

        elif length_of_message <= 4096:
            return "\x47"

        else:
            raise Exception(
                f"Length of message is {length_of_message}, > 4096 characters and cannot be transmitted."
            )

    def send_text(
        self,
        message: str,
        fleet_id: int = None,
        device_id: int = None,
        broadcast: bool = False,
    ) -> int:
        """
        :param message: The text of the message to be sent.
        :param fleet_id: The Fleet ID to be used.
        :param device_id: The Device ID to be usedg.
        :param broadcast: Is the message intended to be a broadcast?
        :return: The number of characters transmitted.

        Send a  message to a given radio, or broadcast a  message to all radios.
        """

        logger.info("Fleet ID is: %s and Device ID is: %s", fleet_id, device_id)
        logger.info("Broadcast? %s", broadcast)

        if broadcast:
            # Int makes more sense to take in, but a broadcast requires a string.
            fleet_id = "000"
            device_id = "0000"

        text = f"\x02{self._length_code(message)}{fleet_id}{device_id}{message}\x03"

        return_length = self.serial_port.write(text.encode())
        self.sequence += 1

        # No assumption is made that this is used within a qthread, hence it is flushed.
        self.serial_port.flush()

        return return_length

    def poll_gnss(self, fleet_id: int, device_id: int) -> int:
        """
        :param fleet_id: The Fleet ID.
        :param device_id: The Device IDg.
        :return: The number of characters transmitted.

        Request a radio to return the current position using the
        Global Navigation Satellite Systems (commonly referred to as GPS).
        """
        logger.info(
            "Polling Device ID: %s in Fleet ID: %s for location.", device_id, fleet_id
        )

        message = f"\x02\x52\x33{fleet_id}{device_id}\x03"

        return_length = self.serial_port.write(message.encode())
        self.sequence += 1

        self.serial_port.flush()

        logger.info("Polling command flushed to serial port.")

        return return_length
