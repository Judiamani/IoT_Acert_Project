'''
SCHC compressor, Copyright (c) <2017><IMT Atlantique and Philippe Clavier>
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>
'''

# from network import LoRa
import socket
#import pycom
import struct
from CBOR import CBOR
import time
import binascii
import sys
import pycom



CON = 0
"""Confirmable message type."""

NON = 1
"""Non-confirmable message type."""

ACK = 2
"""Acknowledgement message type."""

RST = 3
"""Reset message type"""

types = {0: 'CON',
         1: 'NON',
         2: 'ACK',
         3: 'RST'}

EMPTY = 0
GET = 1
POST = 2
PUT = 3
DELETE = 4

codes = {
0: "EMPTY",
1: "GET",
2: "POST",
3: "PUT",
4: "DELETE",
65: "CREATED",
66: "DELETED",
67: "VALID",
68: "CHANGED",
69: "CONTENT",
95: "CONTINUE",
128: "BAD_REQUEST",
129: "UNAUTHORIZED",
130: "BAD_OPTION",
131: "FORBIDDEN",
132: "NOT_FOUND",
133: "METHOD_NOT_ALLOWED",
134: "NOT_ACCEPTABLE",
136: "REQUEST_ENTITY_INCOMPLETE",
140: "PRECONDITION_FAILED",
141: "REQUEST_ENTITY_TOO_LARGE",
143: "UNSUPPORTED_CONTENT_FORMAT",
160: "INTERNAL_SERVER_ERROR",
161: "NOT_IMPLEMENTED",
162: "BAD_GATEWAY",
163: "SERVICE_UNAVAILABLE",
164: "GATEWAY_TIMEOUT",
165: "PROXYING_NOT_SUPPORTED"
}

# requests = {1: 'GET',
#             2: 'POST',
#             3: 'PUT',
#             4: 'DELETE'}

# requests_rev = {v:k for k, v in requests.items()}
#
# IF_MATCH = 1
# URI_HOST = 3
# ETAG = 4
# IF_NONE_MATCH = 5
# OBSERVE = 6
# URI_PORT = 7
# LOCATION_PATH = 8
# URI_PATH = 11
# CONTENT_FORMAT = 12
# MAX_AGE = 14
# URI_QUERY = 15
# ACCEPT = 17
# LOCATION_QUERY = 20
# BLOCK2 = 23
# BLOCK1 = 27
# SIZE2 = 28
# PROXY_URI = 35
# PROXY_SCHEME = 39
# SIZE1 = 60
#
options = {1: ['If-Match','hex'],
           3: ['Uri-Host','str'],
           4: ['ETag','hex'],
           5: ['If-None-Match','hex'],
           6: ['Observe','hex'],
           7: ['Uri-Port','hex'],
           8: ['Location-Path','str'],
           11: ['Uri-Path','str'],
           12: ['Content-Format','hex'],
           14: ['Max-Age','hex'],
           15: ['Uri-Query','str'],
           17: ['Accept','hex'],
           20: ['Location-Query','str'],
           23: ['Block2','hex'],
           27: ['Block1','hex'],
           28: ['Size2','hex'],
           35: ['Proxy-Uri','str'],
           39: ['Proxy-Scheme','str'],
           60: ['Size1','hex'],
           232: ['No Response', 'hex']}
#
# options_rev = {v:k for k, v in options.items()}

CONTENT_TEXT =  0
CONTENT_JSON = 50
CONTENT_CBOR = 60

NO_2 = 0b00000010
NO_4 = 0b00001000
NO_5 = 0b00010000

mid = 1

class MsgInWait:

    def __init__( self, s, m, p ):

        self.msg = m
        self.period = p
        self.timeout = p + time.time()
        self.DR = 5  # Data rate = 5 Best Perf
        self.attempts = 0
        self.socket = s

class CoAPClient:

    def __init__ (self, sock):
        self.socket = sock
        self.toBeAcked = []


    def send(self,  msg,  timeout=0):
        print ("TIME= ", time.time(),  end =" ")
        print ("ADD ",  msg.mid,  end=' ')
        print ('IN ',  timeout)

        self.toBeAcked.append( MsgInWait( self.socket, msg, timeout ) )

    def acked ( self, a ):
        for m in self.toBeAcked:
            if ( m.msg.mid() == a.mid() ):
                self.toBeAcked.remove( m )

    def sleep( self, duration ):

        finishIn = time.time() + duration

        print( 'managing retransmission until TIME =', finishIn )
        print ( len( self.toBeAcked ), " waiting in Queue" )

        while ( time.time() + 30 < finishIn ):
            if ( len( self.toBeAcked ) > 0 ):
            # find the next message to be acked
                when = duration;
                element = self.toBeAcked[0]
                for m in self.toBeAcked:
                    print ( 'time=', time.time(), end = ' ' )
                    print ( "when =", when, end = " " )
                    print ( "Mid = ", m.msg.mid(), end = " " )
                    print ( 'timeout = ', m.timeout, " diff = ", m.timeout - time.time() )

                    if ( m.timeout < element.timeout ): element = m

                print ( "process ", element.timeout )

                if ( element.msg.type() == NON ):
                    # No ack remove from the list
                    self.acked( element.msg )

                element.socket.setblocking(True)
                element.socket.settimeout(10)

                print( "sending: ", end = "" )
                element.msg.dump()
                print( ' DR = ', element.DR, 'attempt =', element.attempts )

                if ( element.attempts == 2 ): element.DR = 4
                if ( element.attempts == 4 ): element.DR = 2

                try:  # works only for LoRa, Sigfox generates error
                    element.socket.setsockopt( socket.SOL_LORA, socket.SO_DR, element.DR )
                    element.socket.setblocking( True )
                    element.socket.settimeout( 10 )
                except:
                    pass

                pycom.rgbled( 0xFF0000 )  # LED sending
#
                element.socket.send(element.msg.to_coap())

                try:
                    element.socket.send( bytes( element.msg ) )
                except:
                    print ( "TIMEOUT in sending" )

                element.attempts += 1

                pycom.rgbled( 0x0000FF )  # LED blue wait for ACK

                try:
                    data = element.socket.recv( 64 )
                    dataRcv = True
                    pycom.rgbled( 0x00FF00 )  # LED green ACK received
                except:
                    print ( 'timeout in receive' )
                    dataRcv = False
                    pycom.rgbled( 0x000000 )


                element.socket.setblocking( False )


                if ( dataRcv ):

                    ack = CoAP(data)
                    print(ack)
                    ack.dump()

                    if ( ack.type() == ACK ):
                        self.acked( ack )

            else:  # Queue empty
                pass

            time.sleep( 20 )

        # end while

        lastTime = finishIn - time.time()
        if ( lastTime > 0 ): time.sleep ( finishIn - time.time() )


class CoAP:

    """
    class CoAP for client and server
    """

    def __init__( self, buf = b'' ):
        self.buffer = buf
        self.option = 0

    def __dump_buffer( self ):
        for bytes in self.buffer:
            print ( hex( bytes ), end = '-' )

    def new_header ( self, Type = CON, Code = GET, MID = None, Token = None):

        global mid


        self.buffer = bytearray()

        # print ("token = ", token)
        # print (type(token))
        if Token == None:
            tkl = 0
        elif type(Token) is int:
            idx = 31
            while idx > 0:
                if Token & (0x01 << idx) != 0: break
                idx -= 1

            tkl = idx//8 +1

            tkv = []
            for i in range (0, tkl):
                tkv.append (Token & 0xFF)
                Token >>= 8

        else:
            raise ValueError ("Unknwon format {} for token".format(type(Token)))

        # First 32 bit word
        byte = ( 0x01 << 6 ) | ( Type << 4 ) | tkl  # need to compute token length
# /!\ Token is one byte long, should be changed to allow different sizes
        if MID == None:
            self.buffer = struct.pack ( '!BBH', byte, Code, mid )
        else:
            self.buffer = struct.pack ( '!BBH', byte, Code, MID )


# add token
        for i in range(0, tkl):
            self.buffer += struct.pack ("!B", tkv[i])

        mid = mid + 1

    def __add_option_TL ( self, T, L ):
        delta = T - self.option

        if (delta < 0):
            raise ValueError ("Option order not respected")

        self.option = T

        if delta >= 13 and delta < 269:
            delta_value = delta-13
            delta=13
        elif delta > 269:
            raise ValueError ('Delta {} more than 1 byte Not implemented'.format(delta))

        if L > 13:
            raise ValueError( 'Length after TLV byte Not Done' )

        self.buffer += struct.pack( 'B', ( delta << 4 ) | L)

        if delta == 13:
            self.buffer += struct.pack( 'B', delta_value)

    def add_option_URI_path( self, path = '' ):
        if path.find("/") != -1:
            raise ValueError("/ in URI-path")
        self.__add_option_TL( 11, len( path ) )
        self.buffer += bytes(path, 'utf-8')

    def add_option_URI_query( self, query = '' ):
        self.__add_option_TL( 15, len( query ) )
        self.buffer += query


    def add_option_content (self, value):
            self.__add_option_TL(12, 1)
            self.buffer += struct.pack('B', value)

    def add_option_noResponse (self, bitmap=None):
        if bitmap == None:
            self.__add_option_TL(258, 0)
        else:
            if type (bitmap) is int and bitmap < 256:
                self.__add_option_TL(258, 1)
                self.buffer += struct.pack("!B", bitmap)
            else:
                raise ValueError("Illegal No Response bitmap")


    def end_option( self ):
        self.buffer += struct.pack( 'B', 0xFF )

    def add_value( self, m = '' ):
        if ( type( m ) ) == type( str() ):
            self.buffer == m
        elif ( type( m ) == CBOR ):
            for char in m.buffer:
                self.buffer += struct.pack( 'B', char )

    def to_coap( self ):
        return self.buffer

    def type ( self ):
        return( ( self.buffer[0] & 0x30 ) >> 4 )

    def mid( self ):
        return self.buffer[2] << 8 | self.buffer[3]

    def __str__(self):
        return "CoAP message: Len {} Value {}".format(len(self.buffer), binascii.hexlify(self.buffer))

    def dump(self):
        if len(self.buffer) == 0:
            print("empty CoAP message")
            return

        if len (self.buffer) < 4:
            raise ValueError("CoAP length too small")

        (b1, Code, MID) = struct.unpack ("!BBH", self.buffer)

        Type = (b1 & 0x30) >> 4
        TLK = b1 & 0x0F

        if len (self.buffer) < 4+TLK:
            raise ValueError("Token too large")

        print ("{} 0x{:04x} [{}]".format(types[Type], MID, binascii.hexlify(self.buffer[4:4+TLK])))
        print ("{}.{:02d} ({})".format(Code >> 5, Code & 31, codes[Code]))

        idx = 4+TLK
        deltaT = 0
        while idx < len(self.buffer) and self.buffer[idx] != 0xff:
            d = self.buffer[idx]>>4
            l = self.buffer[idx] & 0x0F

            if d > 13:
                print ("deltaT not done")

            if l >= 13:
                print ("length not done")

            idx += 1

            if d == 13:
                d = self.buffer[idx] - 13
                idx += 1

            deltaT += d

            if deltaT in options:
                print (options[deltaT][0], end=":")
                option_type = options[deltaT][1]
            else:
                print (hex(deltaT), end=":")
                option_type = "hex"


            for i in range (0, l):
                if option_type == "hex":
                    print (hex(self.buffer[idx]), end=" ")
                elif option_type == "str":
                    print (chr(self.buffer[idx]), end="")
                else:
                    print (".")

                idx += 1
            print()
