# Prepared connected packet dispatcher

`init_child_3191dc_connected.c` and `init_packet_switch_known.c` reduce native
`0x3191dc..0x319712` as one C call graph. The native 43-word handler table
at `0x334d0c` contains 35 distinct basic-block targets. The C switch has
every opcode `0..42` exactly once and no numeric executable pointers.
`init_child_3191dc.c` is the earlier wrapper-only investigation and must
**not** be built together with the connected candidate.

Provenance: `g2/build/c-firmware/20261011/em-inspection-full.arcem.txt`,
decoded from `em-activation-round/em-inspection.bin` at base `0x302400`,
SHA-256 `0de6e945a56ec886a92e44d4eaefe02fbca6db11f8747876e30bffb45cffce03`.
The stock table values were decoded from that image, then translated into
named C cases. The native `AW` pre-update load and `AB` post-update store
used by opcode 41 are described in the [ARC ISA address write-back table](https://me.bios.io/images/d/dd/ARCompactISA_ProgrammersReference.pdf).
The opcode 0 `MPYWHUL` operation is the low 32-bit result of a full-word
times low-halfword unsigned multiply according to the [ARC EM ISA manual](https://docs.alexrp.com/arc/arc_em.pdf).

The original 270-case fixture and its admission inference were superseded
after native review found missing child `R1`/`R2`, signed extension errors,
and premature context-state reads. The corrected candidate passes 280 bounded
state, gate, child-ABI, mutation, and zero-extension boundary cases. All 13
packet child calls now receive the live payload in `R1` and the native mode
or freshly read flag in `R2`; the stub consumes the payload byte and records
the full call identity. The source units compile with ARC
GNU 2026.03, `-mcpu=arcem -mcode-density -O2 -Werror`. The connected object
has no interior-entry imports. It retains 13 genuine packet child source
contracts and binds two existing selected providers:
`opencfw_em9305_ll_mask_count_30c414` and
`opencfw_em9305_short_header_decode_32dedc`.

Admission still requires independent native execution comparison for
representative numeric, flag, packet, aliasing, and child-effect paths.
The host fixture exercises typed child arguments and one child-driven state
mutation but does not prove the actual child bodies or hardware behavior.
Final data/placement remain separate obligations.

Three short packet decoders are separately prepared in
`init_packet_leaf_children.c`: `0x32de6c`, `0x32deac`, and `0x32e1f4`.
They preserve native field widths, payload byte order, store order, and
return lengths `12`, `9`, and `6`. Their separate 768-case host fixture
passes and the ARC target object compiles. Seven further prepared units cover
the remaining ten child bodies: `init_packet_mask_children.c`,
`init_packet_word_children.c`, `init_packet_accum_child.c`,
`init_packet_32dc40.c`, `init_packet_32dfe8.c`, `init_packet_32de08.c`,
and `init_packet_32dffc_e068.c`. The combined ten-unit ARC relocatable
graph has all thirteen packet child bodies defined and only four unresolved
symbols, each a selected source provider: `controller_pack_address`,
`ll_mask_count_30c414`, `ll_pack64_304648`, and
`short_header_decode_32dedc`. This graph has not been integrated into
selected EM source or compared against native execution with overlapping
buffers. The DSP accumulator and ARC loop/bitfield interpretations are
source-backed; runtime equivalence remains a qualification gate.
The `verify_connected_packet_real_children.c` fixture links the actual
prepared child implementations with the switch and exercises one enabled
route per distinct child (13 host routes); all pass. Its four selected
provider stand-ins are bounded host models, not replacements for selected
target source.
