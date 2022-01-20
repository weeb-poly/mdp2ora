#!/usr/bin/env python3

from . import parser
from . import decoder

def main():
    mdp = parser.parseMdpFile('./samples/yohaku_370x320.mdp')
    #img = decoder.decodeLayer(mdp, 'layer0img')
    img = decoder.decodeThumbnail(mdp)
    img.show()

if __name__ == '__main__':
    main()