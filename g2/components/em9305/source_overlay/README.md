# G2 EM9305 source overlay

SPDX-License-Identifier: MIT

This component production-routes the 21 mechanically reconstructible residual
tail spans in the authenticated EM9305 ARCv2-EM application. Twenty-three
four-byte C tail branches replace the callable entries, deterministic ARC NOP
fill replaces their remaining stock allocations, and the C implementations
occupy the previously unused end of the same flash sector. Four no-op spans
are regenerated directly from their authenticated semantics.

The builder preserves the first three records byte-for-byte, extends only the
application record, rebuilds the record table, and performs no hardware
operation. The 980-byte MetaWare runtime and the 260-byte reconstructible-tail
frontier are both production-routed through maintained ARCv2-EM C and checked
entry veneers. The remaining 210,584 provider bytes are an authenticated,
typed retained controller boundary, so whole-component source completion is
still false. Live boot/radio validation is blocked by unavailable physical
evidence.
