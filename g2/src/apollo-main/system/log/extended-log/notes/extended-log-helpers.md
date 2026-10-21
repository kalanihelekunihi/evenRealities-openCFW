# Extended-log critical guard helpers

`guard.c` source-defines two complete lower helper bodies called by the extended logger: 0x43d416..0x43d438 and 0x43d438..0x43d45a. They read control byte base 0x20070be8 +242. When enabled, they call explicit lower enter/exit providers and update byte +244. Otherwise they set/clear byte +243. They do not implement the lower lock primitives at 0x44aa98/0x44aaa0 or the 1,026-byte extended-log body.

The original/helper comparison and remaining logger branch frontier are in `pre-consolidation:g2/analysis/extended-log-frontier-20261010/REPORT.md`.
