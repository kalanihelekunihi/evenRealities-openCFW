# Independent review: P2-19173

Status: partial / unaccepted. No source or gate changes.

Fresh replay of `0x46A12C..0x46A18C` (96 bytes) matches candidate instruction and reference records. The full-word selector tree tests 77, 78, then 64; other values take the default route. The 64 route uses separate fresh diagnostic mask reads, including the distant literal at `0x46AE6C`. Every recorded route assigns R0=1 before the shared POP. Diagnostic stores may overwrite saved incoming R1-R3 slots, and the POP restores those slots while R0 remains the explicit result.
