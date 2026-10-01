# Private P2 recovery 1482: C-SKY bit-clear wait leaf

Scope: candidate `0x10000B4C`, runtime `[0x10000B4C,0x10000B5C)`, conditional BINH-A source range `[0xB64,0xB74)`. All six direct call sites from an image-wide C-SKY objdump sweep are recorded.

Run `python3 verify.py` in this directory. Static traces control each fresh MMIO word; they do not claim physical-device behavior. No firmware source or canonical mapping is changed.
