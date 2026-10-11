# EM9305 QP/C queue initializer candidate

`qequeue_init.c` isolates the official QP/C v6.5.1 `QEQueue_init` source body,
with the retained QP/C source and license attribution in the C file. The
32-bit layout assertions match the authenticated stock ARC body at
`0x310f5c..0x310f74`. This is a candidate for an ARC port, not a production
provider. The queue counter is one byte as observed. An ARCv2 EM/EM7D
product QP port/config and stock/source execution oracle are still needed
before admission into a complete image. The pinned ARC GNU compiler now builds
this unit for ARC EM; its existence does not identify the producing EM7D
compiler profile. The optional scheduler candidate adds recovered control flow
with two explicit vendor port imports.
