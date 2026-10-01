# Peripheral configuration writer at 9178

The120-byte code body [9178,91F0) is followed by ten offset literals through9218. Mode5 writes zero to peripheral3020, then five input words0..4 to3024..3034. Mode11 writes input words0..4 to3000..3010, word5 to3020, then words6..10 to3024..3034. Other modes write word0 to3020 and words1..5 to3024..3034. Return the input peripheral pointer unchanged and restore12-byte frame. No calls orinput-buffer writes occur.

Forty-eight original-instruction fixtures check exact ordered stores, distinct input words, all low modes, return andframe. MMIO is synthetic; physical behavior andpointervalidityremainunresolved. No canonical admission or C implementation.
