# P2-21071 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x47FB78..0x47FC14 (156-byte middle fragment); instruction/reference outputs match candidate. Continuation from 21468 uses full-word comparison against the literal value; unequal flow performs two ordered fallback fetches with full-result error exits, while equality bypasses them. Later helper returns are ignored. The unsigned index guard is retained; its byte store uses the literal 480130 value as pointer. The 48013C operand contributes its literal value directly, not a dereference. Ordered word updates proceed and the fragment ends at FC14 with the 24-byte frame active; no rollback or cleanup is inferred.
