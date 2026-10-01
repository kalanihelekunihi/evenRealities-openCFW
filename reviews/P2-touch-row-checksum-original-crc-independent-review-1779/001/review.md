# Independent review 1779: scoped pass

The three original bodies match their pinned extents: 7F6C (12 bytes/5 instructions), 7F78 (4/2), 7F7C (32/14), with 7F9C data excluded. All 30 isolated fixtures reproduce the full-word equality/error result and preserved SP. The fixture generator independently computes the 0x31 CRC over row+1 through row+width−4; it sets the stored word’s upper bytes to zero before computing because bytes +1..+3 are inside that CRC window, then stores the resulting checksum in the low byte. This is consistent with the reader/adapter/wrapper instruction path.

The CRC proof is bounded to these lengths and rows; no physical storage claim follows. No canonical acceptance or coverage change is made.
