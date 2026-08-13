OpenCFW Lorelei Cordio wstr.c bounded structural matrix

Scope and provenance
--------------------
Only proven-linked WStrReverseCpy and WStrReverse are compared. AmbiqSuite 2.5.1 wstr.c is authenticated by SHA-256 7b226d9ebdbab4d305da843c4fd865c64f408f4376551499f94fcd0451dd6452. Their textual bodies are exact in official Apache-2.0 Packetcraft Cordio r19.02 commit 86372d84ef0386d8834ed036e613c8f2ded1ff16, supplying a license-safe source route. WstrnCpy compiles and its section size is inventoried, but it is excluded from comparison and address assignment because independent stock evidence is absent.

Stock closure
-------------
WStrReverseCpy [0x0056D8C4,0x0056D8F0) is 44 bytes, SHA-256 249d9f2b812108c61c554f67936ae7cd01ac1029b475f21deb49f55cf27e6b94, with 39 direct BL callers and no stored entry pointer. WStrReverse [0x0056D8F0,0x0056D93A) is 74 bytes, SHA-256 dd319dbd967e39a1da26a2e1393cc42aed30fcc0a96b4e43c326490b801e20a7, with two callers and no stored entry pointer. They are contiguous in exact source order.

Matrix
------
Thirteen established GCC profiles x two functions produced 26 rows in 2152592560 ns. Summed compile time was 924864101 ns and link time 183226346 ns. Every closure link has zero undefined symbols. Best aggregate lane is ambiq_exact__O1, absolute size delta 10 bytes with 0/2 exact-size functions. Raw matches total 0; strict normalized matches total 0.

Artifact policy
---------------
Proprietary Ambiq source, stock firmware/function bytes, objects, linked ELFs, and disassembly are excluded. The artifact retains identities, exact public commit/tree/blob route, clean-room closure input, flags, full comparison/build ledgers, caller closure, timing, and checksums.
