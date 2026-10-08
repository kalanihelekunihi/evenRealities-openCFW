# Independent review — P2-21457

Status: partial; accepted: false.

Fresh replay passed for the 86-byte range. Regenerated instruction and reference files match the candidate exactly, including tiling and PC-relative references.

The owner-head traversal follows next pointers until the target is found, then rewrites only the predecessor's +76 link using a fresh target+76 read. There is no head-equal special case or post-unlink revisit in this slice. The outer callback word at +692 is read for the null test and freshly reread for the indirect call; its result is ignored before target release. Auxiliary cleanup conditionally releases aux+28 when byte+84 bit 0 is set, then clears the field. The child resource pointer is freshly reloaded for release before child release. The common POP restores saved entry R2/R3 into R0/R1, except if the earlier diagnostic wrote SP0.

Free and callback contracts are not inferred; review remains partial/unaccepted.
