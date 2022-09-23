"""
Parse and hold messages received from FleetSync devices.
"""
import datetime
import logging

from pynmeagps import NMEAReader, NMEAMessage

logger = logging.getLogger(__name__)


class KMessage:
    """
    Holds a FleetSync message.

    Args:
        raw_message: The raw fleetsync message as bytes.
    """

    def __init__(self, raw_message: bytes = None):
        """
        Initialize the Kmessage class.

        Examples:

            Note: The blank space before D and at the end are unprintable ASCII
            characters STX and ETX, represented as \\x02 and \\x03 respectively.
            Check an ASCII table for STX and ETX.

            >>> k = KMessage(b"\x02D2001814\x03")
            >>> k.device_id
            1814
            >>> k.fleet_id
            200
            >>> k.ack
            False

            Note: As with the above example ASCII STX and ETX are present here.

            >>> k = KMessage(b"\x02I020018142001814\x03")
            >>> k.device_id
            1814
            >>> k.fleet_id
            200

        Args:
            raw_message: The raw fleetsync message as bytes.

        """

        self.ack: bool = False
        self.fleet_id: int = 0
        self.message: str = ""
        self.device_id: int = 0
        self.nmea_message: NMEAMessage = None
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

        Raises:
            Exception: Message does not start with STX control character or
                       does not end with ETX control character.
            Exception: Unknown message type.
        """

        # ASCII control characters.
        stx = b"\x02"
        etx = b"\x03"

        logger.debug("Beginning parse of message.")

        # Test that this is a real message
        if self.raw_message.startswith(stx) and self.raw_message.endswith(etx):
            logger.debug("Message is well formatted data from a device.")
            self.message = self.raw_message.strip(stx).strip(etx).decode("utf-8")

        elif self.raw_message.startswith(b"$PK"):
            logger.debug("Message is a proprietary Kenwood NMEA sentence.")
            self.message = self.raw_message.decode("utf-8")

        else:
            raise Exception(
                "Message does not start with $ (NMEA sentence) or does not start"
                "with ASCII STX."
            )

        # Identification message.
        if self.message.startswith("D"):
            logger.info("Message is an Identification.")

            self.device_id = int(self.message[4:])
            self.fleet_id = int(self.message[1:4])
            return

        # Identification message.
        if self.message.startswith("I"):
            logger.info("Message is an identification.")

            self.fleet_id = int(self.message[2:5])
            self.device_id = int(self.message[5:9])
            return

        if self.message.startswith("$PK"):
            logger.info(
                "Message is a proprietary Kenwood NMEA sentence, parsing via pynmeagps."
            )
            self.nmea_message = NMEAReader.parse(self.message)
            self.device_id = int(self.nmea_message.deviceId)
            self.fleet_id = int(self.nmea_message.fleetId)
            return

        # Acknowledgement message.
        if self.message[0] == "0":
            logger.info("Message is an acknowledgement.")

            self.ack = True
            return

        raise Exception(f"Unknown message type for message: {self.raw_message}")
