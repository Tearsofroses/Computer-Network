import os
import socket
import threading
import time
from typing import List, Dict
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, TransferSpeedColumn
import requests