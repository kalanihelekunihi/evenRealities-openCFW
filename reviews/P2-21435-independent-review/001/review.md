# Independent review — P2-21435

Status: partial; accepted: false.

Fresh replay passed for the 114-byte range. Regenerated instruction and reference files match the candidate exactly, including tiling and PC-relative references.

The preferred parent-owner search is gated by the fresh parent+72 pointer, parent+80 byte, and parent+68 word checks. It scans nodes and tests byte+4, word+80, and the context field at node+84+28 against the parent; a match stores the flag at node+80, keeps R6 zero, and returns through the recorded child. If that route is not selected, the global callback traversal passes parent, node, and a fresh node+12 callback pointer, does not null-check the callback pointer, compares its R0 result with one (so FFFFFFFF is not the sentinel), and loads next after callback. The return wrapper restores saved R7 into R0, overriding the helper result.

External callback and helper contracts remain unknown; review remains partial/unaccepted.
