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
first-party/private eAT parser calls. Searches for the exact retained
`AT_CoreInit` and `AT_Handler` fingerprints found no indexed public source, so
there is no evidence that eAT is a third-party library and no upstream version
or commit can honestly be assigned. The object embeds no upstream definition,
adds no utility-version discriminator, and is not yet production-routed.
