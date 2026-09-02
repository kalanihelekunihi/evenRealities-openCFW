# G2 bootloader CLKGEN configuration source closure

The authenticated bootloader entry at `[0x00426CCC,0x00426D1E)` is an
82-byte CLKGEN configuration service. A null configuration returns status 6
without touching hardware. A non-null configuration:

1. sets bits 2:0 of control register `0x40004020`;
2. replaces mode-register `0x4000404C` bit 29 with configuration byte 0 bit 0;
3. replaces divider-register `0x40004048` bits 1:0 with configuration byte 1
   bits 1:0 and performs the authenticated first divider write;
4. reads the divider register again, replaces bits 30:2 with the low 29 bits
   of the configuration word at offset 4, preserves bit 31 and bits 1:0, and
   performs the authenticated second divider write;
5. sets mode-register bit 0 and returns success.

`runtime_clkgen_config_426ccc.c` expresses that contract as freestanding
clean-room MIT C. The host fixture covers null rejection, set and clear cases,
out-of-range input masking, control/mode/divider preservation, and final
register values. Its target bitfield layout is not assumed silently: both
reviewed target compilers are pinned by their emitted object body. Apple clang
21.0.0 and Homebrew clang 22.1.8 emit the same 84-byte Thumb body with no
relocations:

- source size/SHA-256: 2,674 bytes /
  `b93014f4591b61ee1accbf673f272a2e9d4321bf918f7adf863212ff3a4e3261`;
- emitted and unrelocated body SHA-256:
  `eca58d33f0d33fdefcc0b3f30c8988a2986c6ed4d713b4a081cacf9f9f7fc2d9`;
- authenticated stock body SHA-256:
  `c9ec02c292145c709613ed59045b804cbe0e697d86c83ed579bd2e3075a49b62`.

The compiled body is two bytes larger than the authenticated stock entry, so
production routes it through `[0x00415BFC,0x00415C50)`, an 84-byte,
word-aligned slice of authenticated generated NOP fill inside the existing
`replace_bootloader_format_core` patch site. The replaced fill SHA-256 is
`78680bf9577c12058eebdcfd3143188ebe75c9159a69de6bbc1f7c1e6af675a4`.
The stock entry becomes one bounded `B.W` followed by NOP fill; firmware and
partition sizes do not grow. The two direct stock call sites remain
`0x00421928` and `0x00421FC6`, and no stock interior halfword has direct or
stored ingress.

The exhaustive post-MSPI ledger now admits eight production spans totaling
1,932 stock bytes. Its remaining typed-unresolved executable queue is 118
spans / 19,316 bytes, with zero unclassified bytes. Canonical provider
accounting is:

- Apple: 163,840 bytes, SHA-256
  `930f5886a6116cbfa2ceb456ff83a7a12ce891bf5bd4679df6e2ff458bb9b9e4`;
- Linux: 163,824 bytes, SHA-256
  `bbd9bfa4b0db6d7fe1fc7448649d6ea9bd153f0a8f30850cc2f6cf76fa6cc97a`;
- 34,641/34,623 production-source bytes, 588 cave-source bytes,
  16,462 generated patch-site bytes, and 112,721 retained official bytes.

The complete Apple/Linux packages are 4,749,540/4,749,524 bytes with SHA-256
`22f6bd25615853983a485f929f5c7bf1ae1ecd148d7ef7d4f62e57ff98f804ea`
and
`97de01d80549ec7eec19c5b30615e42ee57b105d202b938c214b099a40d3b26d`.
Both have zero unresolved flash regions.

No MMIO, clock, reset, signing, transmission, erase, or flash operation was
performed. Live clock selection, divider stability, oscillator transition,
timing, and cold-boot qualification is **blocked by unavailable physical
evidence**. Firmware-wide functional completeness is not claimed; the next
executable software frontier begins at `0x00426D1E`.
