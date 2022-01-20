from PIL import Image

def decodeThumbnail(mdp):
    thumb_xml = mdp.xml_data.find("./Thumb")
    item_name = thumb_xml.get('bin')

    thumb_bin = next(filter(lambda i: i.name == item_name, mdp.items))

    thumb_width = int(thumb_xml.get('width'))
    thumb_height = int(thumb_xml.get('height'))

    thumb_img = Image.frombytes('RGBA', (thumb_width, thumb_height), thumb_bin.data, 'raw', 'BGRA')

    return thumb_img

def decodeLayer(mdp, item_name):
    layer_xml = mdp.xml_data.find(f"./Layers/Layer[@bin='{item_name}']")

    item_bin = next(filter(lambda i: i.name == item_name, mdp.items))
    tile_dim, tiles = item_bin.get_layer_tiles()

    layer_type = layer_xml.get('type')

    layer_width = int(layer_xml.get('width'))
    layer_height = int(layer_xml.get('height'))

    layer_color = None
    layer_palette = []
    if layer_type in ('8bpp', '1bpp',):
        c = layer_xml.get('color')
        a, r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), int(c[6:8], 16)
        layer_color = (r, g, b, a,)
        for i in range(256):
            layer_palette.extend([r, g, b, i])

    layer_img = None

    if layer_type == '32bpp':
        layer_img = Image.new('RGBA', (layer_width, layer_height))
    elif layer_type == '8bpp':
        # TODO: Get Color Palettes working
        layer_img = Image.new('RGBA', (layer_width, layer_height))
    else:
        # TODO: Get Color Palettes working
        layer_img = Image.new('RGBA', (layer_width, layer_height))

    tile_img = None
    for patch in tiles:
        print(patch.col, patch.row)
        if layer_type == '32bpp':
            tile_img = Image.frombytes('RGBA', (tile_dim, tile_dim), patch.data, 'raw', 'BGRA')
        elif layer_type == '8bpp':
            tile_img = Image.new('RGB', (tile_dim, tile_dim), layer_color)
            mask_img = Image.frombytes('L', (tile_dim, tile_dim), patch.data, 'raw')
            tile_img.putalpha(mask_img)
        elif layer_type == '1bpp':
            tile_img = Image.new('RGB', (tile_dim, tile_dim), layer_color)
            mask_img = Image.frombytes('1', (tile_dim, tile_dim), patch.data, 'raw')
            tile_img.putalpha(mask_img)

        layer_img.paste(tile_img, (patch.col * tile_dim, patch.row * tile_dim))

    return layer_img
