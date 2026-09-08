# GX8002 IDLE source recovery

The IDLE mode implementation is adapted from NationalChip/lvp_kws commit
`8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`, using its actual `LVP_MODE_INFO`
header. The pinned source has Git blob `c61693132c382e25f780d31a9679216c5b621846`.

All four compiled callback payloads equal the stock executable bytes: an empty
tick (2 bytes), successful buffer initialization (4 bytes), shutdown logging
(16 bytes), and initialization logging followed by return zero (16 bytes).
The tick's remaining 2-byte envelope is generated unreachable fill. The empty
and zero-return functions are original upstream and stock behaviors, not
substitutes for unknown functionality.

The C initializer for the 20-byte mode object names its callback symbols and
uses upstream field types. Static assertions cover every field offset and
total size. The two 22-byte messages are source string literals. All three
compiled data objects match stock exactly; no binary object generates their
source definitions. The callback object links to the recovered code itself.

Decoded source and stock executions pass 336 cases with initial mode values,
caller register patterns and printf return values varied independently. The
init path always returns zero regardless of logging result, while the void
callbacks have no invented return contract. Logging uses the previously
recovered printf entry. Six regression checks exercise wrong helper, message,
return, outstanding frame and the original empty tick behavior.

The mode list, loop/index BSS, TWS callbacks and the rest of firmware remain
separate recovery work. These checks establish IDLE source provenance and
local behavior; they do not establish whole-device runnability or timing.

Full integration passed 298 tests. The native macOS package rebuilt and passed
artifact verification with the IDLE notice included. Codec and EVENOTA hashes
are unchanged because this recovery exactly reproduces the former retained
bytes. Source ownership increased by 104 bytes across seven regions. Current
codec ownership is 8,622 C bytes, 120 assembly, 2,280 source data, 80 metadata,
336 generated fill and 314,654 retained bytes. The full goal remains active.
