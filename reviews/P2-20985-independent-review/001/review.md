# P2-20985 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh locked replay passed in isolated output; 158 bytes at 0x47E674..0x47E712, two entries. Fatal initializer failure attempts the observed invalid-address store/self-loop. Wrapper passes 44 and caller stack arguments; shifted POP aliases differ according to overwritten stack slots.

Instruction/reference evidence was replayed directly from the locked image. No external helper, pointer ownership, or broader completeness claim is made.
