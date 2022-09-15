import datetime
import logging

logger = logging.getLogger(__name__)


class KMessage:
    """
    Holds FleetSync message output.
    """

    def __init__(self, raw_message: bytes = None):
        """
        :param raw_message: The raw message received from the serial port.
        """

        self.ack: bool = False
        self.fleet_id: int = None
        self.message: str = None
        self.device_id: int = None
        self.raw_message = raw_message
        self.time_stamp = datetime.datetime.now(datetime.timezone.utc)

        logger.debug(
            "Object initialized with raw message: '%s' at time: %s",
            self.raw_message,
            self.time_stamp,
        )

        self._parse()

    def _parse(self):
        """
        Parse the raw message and populate what can be populated.
        """

        # ASCII control characters.
        stx = b"\x02"
        etx = b"\x03"

        logger.debug("Beginning parse of message.")

        # Test that this is a real message
        if self.raw_message.startswith(stx) and self.raw_message.endswith(etx):
            logger.debug("Message appears well formatted.")
            self.message = self.raw_message.strip(stx).strip(etx).decode("utf-8")
        else:
            raise Exception(
                "Message does not start with STX control character or does not end with ETX control character."
            )

        # Identification message.
        if self.message.startswith("D"):
            logger.info("Message is an Identification.")

            self.device_id = int(self.message[4:])
            self.fleet_id = int(self.message[1:4])
            return
        # Acknowledgement message.
        elif self.message[0] == "0":
            logger.info("Message is an acknowledgement.")

            self.ack = True
            return
        else:
            raise Exception("Unknown message type for message: %s.", self.raw_message)
