# P2-20781 independent review

Status: **partial / unaccepted**.

Fresh locked-image replay passed; image SHA-256 and source/fresh receipt hashes verified.

156B inherited 72-byte frame: logger2004 and mask path use count10; later logger2005 reads the word through literal address 47C558, while mask route freshly reloads that word independently. SP0/4/8 are locals, separate status queries retained.

The literal’s target semantics are not inferred. No whole-firmware coverage or source/gate changes.
