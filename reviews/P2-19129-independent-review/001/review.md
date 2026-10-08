# P2-19129 independent review

Status: partial, unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x469A76–0x469AE2 (108 bytes; 44 instructions); candidate instruction/reference records match exactly. Locked image SHA-256: `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`.

Verified the FULL selector-5 comparison, fresh byte guard, ordered two action calls on the nonzero route, and two explicit global flag clears before the BX LR leaf. The leaf retains R0, but the wrapper explicitly sets R0=0 before its shared ADD SP16/POP16 epilogue, discarding the original argument slots and any diagnostic overwrites. The next PUSH at 0x469AE2 is outside the map.
