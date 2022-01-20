# mdp2ora

This is a WIP tool to convert the mdp file format to the ora file format.

There are a couple of things which are lost in the conversion from MDP to PSD to ORA, so this is an attempt to both document the mdp format as well as propose new extensions to the ORA spec to assist with conversion.

The code is able to parse and decode individual layers into images (based on samples), but it's unable to create an equivalent ora file as of now.

A kaitai struct file is provided, but the code is currently using a custom binary parser due to limitations of both the Kaitai Struct spec and the Kaitai Struct Python Implementation.
