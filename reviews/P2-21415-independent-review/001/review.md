# Independent review — P2-21415

Status: partial; accepted: false.

Fresh extraction passed for the three disjoint flash-record intervals, totaling 60 bytes and 15 words; regenerated `bytes.json` matches the candidate. The three source pointers in map 21796 resolve to the same addresses and interval boundaries listed here. Its first record copy reads the three words into SP slots 0/4/8 before the configuration helper; the two later records are copied as 24-byte spans into SP+36 and SP+12 before their respective helper calls.

This confirms exact source bytes, pointer references, and observed copy ranges only. Field semantics and destination RAM contents are not inferred; helper contracts and image-wide ownership remain outside scope. Review remains partial/unaccepted.
