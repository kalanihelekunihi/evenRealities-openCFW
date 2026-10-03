# Independent review 5029/001

**PASS_SCOPED**; `accepted` remains false.

The packet’s 32-byte table at `[0x00433440, 0x00433460)` matches the locked image byte for byte and parses into the four recorded callback/key pairs. All literal values (table bounds, destination, comparator) agree with the pinned instruction consumers, and the candidate receipt’s source, dependencies, and file hashes validate. An isolated replay regenerated the records.

This verifies raw table evidence only. The callback functions’ behavior and the semantic meaning of their keys remain outside scope; this is not a closure or corpus-admission claim.

Candidate receipt SHA-256: `f9720c4adfe5a74b883bdc278153387ad41fb7b1288dbccaf1c5ccf0cf5f2aa2`.
