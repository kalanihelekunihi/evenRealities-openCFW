# Independent review 2481

**Result:** PASS_SCOPED.

Candidate `analysis/touch-mode-three-original-port-chain-2480/001` has receipt SHA-256 `590401ceb163a15bf97284a365521c99e780556b51d8591ea4cae1e22a61c3cd`. Its declared artifacts and all ten source spans match their hashes against the pinned image. The isolated replay passes all 48 fixtures.

Original 6AC0, port-list wrappers, paired setup, and pin configuration execute without firmware interception. The fixtures exercise request 3 from six non-equal permitted prior modes, nonempty lists, PRIMASK 0/1, and descriptor flags zero/all-set. Ordered pin calls/direction writes, parameter byte21 clear, unchanged descriptor word8, mode3 commit, no loader entry, pin configuration words, status, and register/frame assertions agree with the code path. The loader span is pinned as a non-entered dependency, not counted as executed coverage.

**Limits:** Factory/config values are not consumed on this request-3 route. MMIO is modeled; physical ports, pointer/count mutation, and invalid-pin behavior are not established. Accepted:false; private scoped evidence only, no canonical admission.
