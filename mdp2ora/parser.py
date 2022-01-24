import struct
from io import BytesIO
from enum import Enum
import xml.etree.ElementTree as ET

import zlib
#import snappy


def parseMdpFile(filename):
    mdp = MdpFileRaw.from_file(filename)
    return mdp


class BinaryStruct:
    @classmethod
    def from_io(cls, io):
        return None

    @classmethod
    def from_file(cls, filename):
        with open(filename, 'rb') as f:
            return cls.from_io(f)

    @classmethod
    def from_bytes(cls, buf):
        return cls.from_io(BytesIO(buf))

    
class MdpTile(BinaryStruct):
    def __init__(self, col, row, unk, data):
        self.col = col
        self.row = row
        self.data = data

    @classmethod
    def from_io(cls, io):
        col = struct.unpack('<I', io.read(4))[0]
        row = struct.unpack('<I', io.read(4))[0]
        ctype = struct.unpack('<I', io.read(4))[0]
        size = struct.unpack('<I', io.read(4))[0]
        raw_data = io.read(size)
        io.seek((4 - size) % 4, 1)
        if ctype == 0: # zlib
            data = zlib.decompress(raw_data)
        elif ctype == 1: # snappy
            #data = snappy.uncompress(raw_data)
            data = raw_data
        elif ctype == 2:
            # TODO: fastlz decompression
            #data = fastlz.decompress(raw_data)
            data = raw_data
        return cls(col, row, unk, data)


class MdpItemRaw(BinaryStruct):
    def __init__(self, name, item_type, data, compressed_size, expanded_size):
        self.name = name
        self.item_type = item_type
        self.data = data
        self.compressed_size = compressed_size
        self.expanded_size = expanded_size

    def get_layer_tiles(self):
        io = BytesIO(self.data)
        tileNum = struct.unpack('<I', io.read(4))[0]
        tileSize = struct.unpack('<I', io.read(4))[0]

        tiles = [None] * tileNum
        for i in range(tileNum):
            tiles[i] = MdpTile.from_io(io)

        return (tileSize, tiles,)

    @classmethod
    def from_io(cls, io):
        pack_header_bytes = io.read(132)
        if len(pack_header_bytes) != 132:
            return None
        pack_header_io = BytesIO(pack_header_bytes)

        # First thing we do is check the magic header
        magic_header = pack_header_io.read(4).decode('ascii', errors='ignore')
        assert magic_header == 'PAC '

        item_size = struct.unpack('<I', pack_header_io.read(4))[0]
        item_type = struct.unpack('<I', pack_header_io.read(4))[0]

        compressed_size = struct.unpack('<I', pack_header_io.read(4))[0]
        expanded_size = struct.unpack('<I', pack_header_io.read(4))[0]

        # 48 bytes of padding
        pack_header_io.seek(48, 1)

        item_name = pack_header_io.read(64).decode('ascii').rstrip('\0')

        raw_data_len = expanded_size
        if item_type == 1: # ZLIB
            raw_data_len = compressed_size
        elif item_type == 0: # NONE
            raw_data_len = expanded_size

        assert raw_data_len == (item_size - 132)

        raw_data = io.read(raw_data_len)

        if item_type == 1: # ZLIB
            raw_data = zlib.decompress(raw_data)
        
        return cls(item_name, item_type, raw_data, compressed_size, expanded_size)


class MdpFileRaw(BinaryStruct):
    """
    The mdiapp file format doesn't appear to have any publically available
    documentation. This format is used by mdiapp, FireAlpaca, MediBang Paint,
    LayerPaintHD, and probably more.

    This is my attempt to document it.

    Thanks to Um6ra1, Bowserinator, and 42aruaour for the assistance.
    """

    def __init__(self, xml_data, items):
        self.xml_data = xml_data
        self.items = items

    @classmethod
    def from_io(cls, io):
        # First thing we do is check the magic header
        magic_header = io.read(7).decode('ascii', errors='ignore')
        assert magic_header == 'mdipack'

        # 5 bytes of padding
        io.seek(5, 1)

        # xml strict and total pack size
        xml_len = struct.unpack('<I', io.read(4))[0]
        pack_size = struct.unpack('<I', io.read(4))[0]
        xml_str = io.read(xml_len).decode('utf8')

        # TODO: Research Zero Copy Solution
        pack_io = BytesIO(io.read(pack_size))
        items = []

        while True:
            item = MdpItemRaw.from_io(pack_io)
            if item is None:
                break
            items.append(item)

        return cls(ET.fromstring(xml_str), items)
