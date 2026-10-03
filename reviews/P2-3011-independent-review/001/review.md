# Independent review 3011

**Result:** REVISE_PINS; `accepted: false`.

Candidate `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-boot-command-queue-init-original-3010/001` passes an isolated replay of 3,264 cases using the actual authenticated descriptor records, and the source image hash matches. However, its receipt's body and table digests are both SHA256(empty): the script slices runtime addresses directly as file offsets. With load base `0x410000`, the body file span is `[0x17794,0x17878)` and hashes to `ad7e3d6257b791855a8cd7fe90389313dfb9496262724777900d6a4193c09b52`; the 12-record descriptor table span is `[0x20880,0x20A60)` and hashes to `1ed1fa3682f9c16c403ee0e6cee7761b70ca610656a2b6e56de3f0b05cee7fea`. The receipt therefore does not authenticate these claimed evidence extents.

The successful write ledger has 18 entries because it includes final output-handle publication after the 17 preceding state/descriptor writes. The bounded behavior otherwise matches the replay assertions, but the pin defect needs an append-only correction before this packet can pass review.

The fixtures use stable nonalias memory and do not establish physical hardware, asynchronous behavior, global ownership, or canonical admission.
