# P2-21183 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x481574..0x4815F2 (126 bytes); instruction and literal-reference outputs match. The pointer/index validations accept only unsigned indices 56..62 and 125..131, with the recorded two-bank normalization and offset calculation. The helper receives the base pointer, bank, computed offset, and live R3; its full result is staged at SP0. The output receives a mask word first (fresh target or all ones), then the output word is reloaded before a fresh query-target read and AND/store. This preserves two writes and their alias-sensitive order. SP0 is reloaded for PRIMASK; the 32-byte unwind returns status zero on success and preserves the stated saved-slot behavior on validation errors.
