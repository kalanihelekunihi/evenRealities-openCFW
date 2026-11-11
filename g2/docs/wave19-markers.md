# Wave 19 markers

Stock images: apollo /tmp/apm.bin (base 0x438000); em9305 g2/blobs/official/g2-2.2.6.10/firmware_ble_em9305.bin.

## (1) em9305 relink
g2/build/g2c-w19-final-em9305 was relinked from g2c-w18-em9305/g2/g2-em9305/g2-em9305.o against the current .ld. 0 undefined; the myapp pins ASSERT passes.

## (2) NAN / FPSCR carriers in g2c_nema_vg_path.c
- NAN( dropped 158 -> 0 code uses, and the macro is removed.
- g2c_fpscr_* dropped 43 -> 0, and the helpers are removed.
- Each site now has a stock vcmp/vmrs citation next to it. Flag semantics: GE is ordered; LT includes unordered; EQ is ordered.
- vector_shape_draw (0x5202ec):
  - 0x520676/684, 0x520736/740, 0x52086a, 0x520884, 0x520a84, 0x520ac2..af4, 0x520b00..b6a
  - 14 eps sites, 0x520ede..0x5214de
  - 0x521546, 0x521864, 0x52187a, 0x521e26, 0x522190/19e, 0x52220e/228/236, 0x522312/31c
- arc_draw:
  - GE chain 0x5653ec..0x565480 (bge 0x565558)
  - LT chain 0x5654a4..0x565518 and 0x5654c8
- path_inner:
  - GE chain 0x5662ec..0x56635c (bge 0x566418)
  - LT triples 0x566388/3a2/3aa, 0x5663b4/3be/3c6, 0x5663d0/3da/3e2 (blt 0x566408)
- Z-only EQ pairs, each cited at its site:
  - bezier_subdiv 0x51b158/16a, 0x51b17e/190
  - arc_seg 0x51b91e/930, 0x51b942/954
  - arc_seg2 0x51bfaa/fbc, 0x51bfce/fe0
  - arc_seg3 0x51c61a/62c, 0x51c640/652
  - The NZCV stand-in word is replaced by its masked base. Later reads only use `& 0xfffffff` or RMode, so this is value-preserving.

## (3) stroke_path / fill_path
The 4 order-matched citations are now address-verified: decompiler label = stock fallthrough of bl 0x516b34.

## (4) em9305 myapp_ao / queue
- The W18 claim "code is not plain ARC" was wrong. The bin has 2626 middle-endian limm words pointing into 0x800000..0x820000.
- 0x801970 appears at file offset 0xca2e (after halfword 0x40c3) and 0x80f97c at 0xcb0e (after 0x42c3). Hand-decoded as mov_s r0/r2,limm; there is no ARC disassembler on the host.
- The addresses are now stock-backed. The 36/16-byte sizes are not, so the comment is marked UNVERIFIED (sizes). That is the +1 to em9305 unverified.
