# Copyright (c) 2019 Hibotronix
# Author: Hibotronix
# Web: hibotronix.co.uk
# Twitter: @HiboTronix
#
# Based on work by:
# Jacob Kittley-Davies https://github.com/jkittley/RFM69
# Eric Trombly https://github.com/etrombly/RFM69
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import json
from datetime import datetime

class Packet(object):
    """Object to represent received packet. Created internally and returned by radio when getPackets() is called.

    Args:
        receiver (int): Node ID of receiver
        sender (int): Node ID of sender
        RSSI (int): Received Signal Strength Indicator i.e. the power present in a received radio signal
        data (list): Raw transmitted data

    """
    
    # Declare slots to reduce memory
    __slots__ = 'received', 'receiver', 'sender', 'RSSI', 'data'
    
    def __init__(self, receiver, sender, RSSI, data):
        self.received = datetime.utcnow()
        self.receiver = receiver
        self.sender = sender
        self.RSSI = RSSI
        self.data = data
    
    def to_dict(self, dateFormat=None):
        """Returns a dictionary representation of the class data"""
        if dateFormat is None:
            return_date = self.received
        else:
            return_date = datetime.strftime(self.received, dateFormat)
        return dict(received=return_date, receiver=self.receiver, sender=self.sender, rssi=self.RSSI, data=self.data)

    @property
    def data_string(self):
        return "".join([chr(letter) for letter in self.data])

    def __str__(self):
        return json.dumps(self.to_dict('%c'))

    def __repr__(self):
        return "Radio({}, {}, {}, [data])".format(self.receiver, self.sender, self.RSSI)

