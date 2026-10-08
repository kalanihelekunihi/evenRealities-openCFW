# P2-21037 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x47F0A0..0x47F11C; fresh instruction/reference outputs match candidate. Mode validation accepts LOW8 values 1 or 2; mode 2 applies its fresh word precheck before comparing the fresh observed byte. Equality bypasses the helper and later field test. On mismatch, the helper receives LOW8(mode); its full nonzero result returns unchanged. Only helper zero triggers a fresh field word comparison. The separate frameless getter returns 6 for null, otherwise writes a fresh byte to the output word and returns 0. No observed-hardware equivalence or external helper contract inferred.
