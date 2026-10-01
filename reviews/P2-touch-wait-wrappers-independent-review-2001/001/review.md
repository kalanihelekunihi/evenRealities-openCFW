# Independent review 2001

**Result:** PASS_SCOPED.

- The exact source hash and every receipt file hash match. The two owned bodies are [0xA528,0xA582) and [0xA58C,0xA5F0); the 0xA582 alignment and literal words at 0xA584, 0xA588 and 0xA5F0 are outside ownership.
- Isolated replay regenerated all 64 original-instruction fixtures exactly. It covers both wrappers, initial selected flag, post-probe and post-leaf flag mutation, status 0/7, and initial PRIMASK 0/1.
- Decoded control flow supports the asymmetric failure paths: A528 notifies A444(index,2) on nonzero probe status regardless of the later flag, while A58C re-reads its selected word and only sends that notification if it remains nonzero. Success paths save/disable via original 4492, re-read the selected word, call the index-specific leaf, restore via original 449A, and conditionally notify again.

**Limits:** A444 and leaf effects are controlled; wrapper meaning, physical sleep behavior, mutation/concurrency outside these fixtures and callee semantics remain unresolved. No canonical admission is made.
