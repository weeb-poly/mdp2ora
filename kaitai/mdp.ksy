meta:
  id: mdp
  title: mdipack file format
  file-extension: mdp
  endian: le
doc: |
  The mdiapp file format doesn't appear to have any publically available
  documentation. This format is used by mdiapp, FireAlpaca, MediBang Paint,
  LayerPaintHD, and probably more.
  This is my attempt to document it.

  Zlib compressed blobs are still a work in progress as Kaitai
  Structs don't have any method of handling those yet.

  Thanks to Um6ra1, Bowserinator, and 42aruaour for the assistance.
seq:
  - id: header
    type: header
  - id: pack
    type: pack
    size: header.pack_size
types:
  header:
    seq:
      - id: magic
        contents: 'mdipack'
      - id: padding
        size: 5
      - id: xml_len
        type: u4
      - id: pack_size
        type: u4
      - id: xml_str
        type: str
        size: xml_len
        encoding: utf8
  pack:
    seq:
      - id: items
        type: item
        repeat: eos
  item:
    seq:
      - id: magic
        contents: 'PAC '
      - id: item_size
        type: u4
      - id: item_type
        type: u4
      - id: compressed_size
        type: u4
      - id: expanded_size
        type: u4
      - id: padding
        size: 48
      - id: section_name
        type: str
        size: 64
        encoding: ascii
      - id: data
        size: item_size - 132
#  layer:
#    seq:
#      - id: tile_count
#        type: u4
#      - id: dim
#        type: u4
#      - id: tiles
#        type: tile
#        repeat: expr
#        repeat-expr: tile_count
#  tile:
#    seq:
#      - id: col
#        type: u4
#      - id: row
#        type: u4
#      - id: unk
#        type: u4
#      - id: size
#        type: u4
#      - id: raw_data
#        size: size
#        doc: compressed using DEFLATE
#      - id: padding
#        size: (4 - _io.pos) % 4
