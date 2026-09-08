# GX8002 audio reset source

The reconstructed C routine at `0x10203c88` / package `0xd214` uses 240 of
its original 320 bytes. The original section exactly matches authenticated
NationalChip `.text._ain_reset` at commit
`8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`, without relocations. SDK object
bytes are identification evidence only: the candidate links only the new C
object. Its compiler flags and source/target hashes are pinned in the report.

The function preserves individually ordered volatile 32-bit accesses to the
audio registers at `0xa0a00000`. Each field change performs a fresh read and
write, even for consecutive updates to the same register. After writing
`0x200` to offset `0x104`, it repeatedly reads that register until bit8 is set.
It then performs the remaining reset sequence and returns zero, using no
stack. The original indefinite hardware wait remains intact.

Stock and compiled instructions match an independent ordered-register oracle
in 2,070 completed cases. Initial values include all single-bit and inverted
single-bit patterns, zero, all ones and mixed patterns. Read responses use
three models: constant values, prior writes retained, and changing values at
every read. Selected completion delays run from zero through 1,023 polls.
Another 621 comparisons check never-ready prefixes of 1, 2 and 32 reads.
Ten regression tests check fresh reads, delayed/absent completion, reset bits,
register offsets, polling bit/branch, return value, and preserved registers.

These are decoded instruction/MMIO comparisons, not physical register or
timing validation. The prefix checks are finite observations of the retained
wait loop. They do not claim a hardware completion guarantee. The hardware
register semantics and whole audio subsystem remain unqualified.

```sh
python3 g2/tools/verify_gx8002_audio_reset.py
python3 -m unittest discover -s g2/tests -p test_gx8002_audio_reset.py
```

Evidence: [gx8002-audio-reset-verification.json](gx8002-audio-reset-verification.json)
and [gx8002-audio-reset-identification.json](gx8002-audio-reset-identification.json).
