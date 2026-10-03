# Independent review 2515

**Result:** PASS_SCOPED.

Reviewed `g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-shared-primitive-call-candidates-2514/001`. Candidate receipt SHA-256 is `524f49ff95de3e7229b62561ca9fa7d71bd9737eea84b43de0171c4f2dbffc33`; all declared artifact hashes match: `candidates.json` `3d841c9049f5ed847528814ed952772bce07e685bf42543ea305bcc3a21d46f3`, `verify.py` `7726516a7064d926626f82179d760e1454faf27942c8551951075a4400b4100e`, and `notes.md` `dc5e02ad8b082e92c74e27b8994656e0c7359e5601dfae25dc345a0dcaefd6b9`.

The inventory SHA-256 is `f2795f712ed64d147a3fe94d570bf85ea43175cae0f2e89ab01e96fe9a3a5aaa`. Both source images match their pinned hashes: main flash `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` and bootloader flash `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`. The script derives its image mappings from the pinned inventory, scans halfword-aligned offsets, applies a Thumb BL encoding prefilter, and accepts a hit only when Capstone decodes the four-byte candidate as `bl`/`blx` with one of the image’s four selected loaded targets.

I reran the verifier from a copy directed to a fresh output directory. It reproduces all 293 records: 156 in the main image and 137 in the bootloader. Per-target counts are main `0x4807A0: 116`, `0x4807FC: 15`, `0x480826: 24`, `0x48086A: 1`; bootloader `0x41D1C0: 103`, `0x41D21C: 15`, `0x41D246: 18`, `0x41D28A: 1`. Each retained record’s four original bytes, file offset, loaded address, target, mnemonic and operands are generated from the pinned source bytes and decode. The totals agree with the candidate receipt.

**Limits:** These are syntactic direct-call candidates in two flash images, not a recovered caller set. The records explicitly set `caller_ownership_verified` to false. The scan does not establish whether each byte sequence is executable, reachable, correctly bounded by preceding instructions, or invoked after ITCM installation. It does not search indirect calls, veneers, or alternate mappings; it makes no absence or completeness claim. Private evidence only; accepted:false and no canonical admission.
