# Independent review 2021

**Result:** PASS_SCOPED.

- The immutable source pin and both consolidated output hashes match. Independently extracted [0xA444,0xA516) is 210 bytes with the recorded SHA; its 105-line listing is contiguous and each encoded instruction byte matches the source span.
- All four dependency receipt hashes and every dependency artifact hash match their exact paths. Their fixture counts sum to 736 (256 + 64 + 384 + 32), as stated.
- The merged pseudocode is consistent with the original branch structure: index/mode BKPT boundaries, exact modes 1/2/4/8, low-byte validation followed by full-width comparisons, callback argument copying, post-callback link reloads, mode-1 sentinel stop/failure pointer, reverse traversal and unchanged globals for wide modes.
- The null-head reverse path is accurately bounded at the word read from address 20; no null-head safe return or hardware fault behavior is claimed.

**Limits:** The six wide aliases are representative, not exhaustive. BKPT continuation, null-head memory-fault outcome, callbacks, arbitrary/cyclic topology, and external behavior remain unresolved. This is a private evidence consolidation, not canonical admission or a claim of full firmware coverage. No canonical admission is made.
