# Independent review 1815: scoped trace pass

The exact body is 82E0..854C (620 bytes/291 decoded instructions). All 15 isolated traces execute original instructions and reached helpers without interception. The candidate recomputes CRC values after writing all row payload/sequence data, then corrupts only primary row zero; its corresponding mirror is valid. The traces reproduce requested bytes, A5 destination suffix, SP and returns: 0x093E0004 when the request includes recovery from primary row zero, otherwise zero. At primary-limit crossing after fallback, original 810C/812A pointer helpers wrap to primary base, so the model correctly repeats row-zero payload rather than advancing into primary row one. This is a bounded trace observation, not complete pseudocode recovery.

This records only bounded trace behavior for the stated synthetic mirror layout. No canonical acceptance or complete-recovery claim is made.
