"""A library to interface with Kenwood's FleetSync"""

import logging

from ksync.kmessage import KMessage
from ksync.ksync import KSync

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

__version__ = "0.3.0"
