# Private P2 recovery: C-SKY controller-to-buffer transfer 1465

This packet recovers candidate `0x10000BBC` from the authenticated conditional BINH-A bytes and caller sites in 1428/001. No firmware source or canonical record is changed.

Run `python3 verify.py` from this directory. It verifies the original byte span, tool output, exact callsite arguments, helper edges, and five bounded input/status traces. B4C and physical controller behavior remain unresolved.

Status: `ready_for_review`; preserve the 1309/1352/1408 inherited findings.
