# G2 eAT core recovery

The retained `platform\service\eAT\core\at_core.c` anchor expands from two
path-anchored Ghidra bodies / 302 bytes to five functions / 666 body bytes plus
a 58-byte pool, for 724 physical bytes at `[0x005412E0,0x005415B4)`. The
additional source-order registration helper and two pathless Ghidra bodies
complete initialization, incremental parsing, response output, command-table
matching, and four exact indirect callback sites. Eighty-five direct entries,
21 body calls, both adjacent boundaries, and the absence of stored or
strict-interior entries are pinned by the analyzer.

The 20 direct external calls close over 10 admitted EasyLogger diagnostics,
six bounded or source-owned IAR DLIB memory/string/format calls, and four
first-party/private eAT parser calls. A clean-room five-function C replacement
now preserves callback registration, initialization, bounded three-segment
parsing, formatted output routing, exact command matching, filter policy, and
direct/adapted handler dispatch. Both reviewed compiler profiles route all five
stock entries to strictly relocated compiled source; the 666 stock body bytes
are displaced while the 58-byte diagnostic literal pool remains explicitly
retained. Searches for the exact retained
`AT_CoreInit` and `AT_Handler` fingerprints found no indexed public source, so
there is no evidence that eAT is a third-party library and no upstream version
or commit can honestly be assigned. The object embeds no upstream definition,
adds no utility-version discriminator. Software production routing is closed.
End-to-end parser/callback behavior on physical glasses remains explicitly
blocked by unavailable authorized G2 trace evidence; no hardware operation was
performed or inferred.
