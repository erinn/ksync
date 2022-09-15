"""
Provides a simplified interface for working with FleetSync devices.
"""

import logging

logger = logging.getLogger(__name__)


class KSync:
    """
    Provides methods to work with FleetSync.
    """

    # ASCII Start of transmission (stx) and end of transmission (etx).
    stx = "\x02"
    etx = "\x03"

    def __init__(self, serial_port: object) -> None:
        """
        Args:
            serial_port: A serial port object, object must have a
            write() and flush() method.
        """
        self.serial_port = serial_port
        # Though the sequence number is unused it is held for completeness with
        # the understood protocol.
        self.sequence = 0

    @staticmethod
    def _length_code(message: str) -> str:
        """
        Calculate the length code to use for a given message.

        Args:
            message: The message to be transmitted.
        Returns:
            A string that indicates the length of message to be sent.
        Raises:
            Exception: Length of message is greater than 4096 characters.
        Notes:
            46 hex (ascii F) - corresponds to 'S' (Short - 48 characters)
            47 hex (ascii G) - corresponds to both 'L' (Long - 1024 characters)
            and 'X' (Extra-long - 4096 characters)
        """

        length_of_message = len(message)

        logger.info("Calculating length code for message.")
        logger.info("Length of message is %d", length_of_message)

        if length_of_message <= 48:
            return "\x46"

        if length_of_message <= 4096:
            return "\x47"

        raise Exception(
            f"Length of message is {length_of_message}, > 4096 characters and "
            "cannot be transmitted."
        )

    def send_text(
        self,
        message: str,
        fleet_id: int = None,
        device_id: int = None,
        broadcast: bool = False,
    ) -> int:
        """
        Send a message to a device or broadcast to all devices.

        Examples:
            >>> k = KSync(serial_port=port)
            >>> k.send_text(message="The vogon fleet has landed", fleet_id=100, device_id=1000)
        Args:
            message: The text of the message to be sent.
            fleet_id: The Fleet ID to be used.
            device_id: The Device ID to be used.
            broadcast: Is the message intended to be a broadcast?
        Returns:
            The number of characters transmitted.
        """

        logger.info("Fleet ID is: %s and Device ID is: %s", fleet_id, device_id)
        logger.info("Broadcast: %s", broadcast)

        if broadcast:
            # Int makes more sense to take in, but a broadcast requires a string.
            fleet_id = "000"
            device_id = "0000"

        text = f"{self.stx}{self._length_code(message)}{fleet_id}{device_id}{message}{self.etx}"

        return_length = self.serial_port.write(text.encode())
        self.sequence += 1

        # No assumption is made that this is used within a qthread, hence it is flushed.
        self.serial_port.flush()

        return return_length

    def poll_gnss(self, fleet_id: int, device_id: int) -> int:
        """
        Request a radio to return the current position using the
        Global Navigation Satellite Systems (commonly referred to as GPS).

        Args:
            fleet_id: The Fleet ID.
            device_id: The Device ID.
        Returns:
            The number of characters transmitted.
        """
        logger.info(
            "Polling Device ID: %s in Fleet ID: %s for location.", device_id, fleet_id
        )

        message = f"{self.stx}R3{fleet_id}{device_id}{self.etx}"

        return_length = self.serial_port.write(message.encode())
        self.sequence += 1

        self.serial_port.flush()

        logger.info("Polling command flushed to serial port.")

        return return_length
