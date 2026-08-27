# G2 bootloader EasyLogger output source closure

The complete authenticated `elog_output` entry `[0x004176CE,0x00417AD0)` is now production source-owned. Its 1,026 stock bytes have SHA-256 `97645514643e4e4e3e5e04a8d14a08c5c714df3cfd64e764b7b73ab95860e021` and 115 exact whole-image `BL` callers.

`runtime_easylogger_output_4176ce.c` is a bounded MIT adaptation of EasyLogger commit `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`. It preserves the recovered G2 interrupt-context early return, assertion path, enable/global/tag/tag-level filters, post-format keyword filter, lock/unlock discipline, all enabled prefix fields, ANSI colors, the 1,024-byte line buffer, truncation capacity for the CSI terminator and newline, and the three-argument channel sink that retains the log level.

The Apple reference leaf is 1,060 bytes at overlay offset 7,780 (`0x004362DC`) with SHA-256 `b64c49b0615fd3cb4d5aba393ea929024fc05a7e884eea41019777b6b667d4ce` and zero relocations. The Linux leaf is 1,064 bytes at offset 7,760 with SHA-256 `370bc7eb08f68f3115660612356c7190df6609711c2d2347f069e4400362c7fa`. Eight host/target tests cover the interrupt gate, filters, formatting, keyword path, truncation, source identity, stock identity, and all callers.

The four bytes `[0x00417AD0,0x00417AD4)` are authenticated CSI-start literal/alignment data and remain explicitly retained, not misclassified as executable code.

No physical hardware was accessed. Live UART/channel timing, scheduler concurrency, exception logging, and rendered-output evidence remains blocked by unavailable authorized responsive G2 hardware.
