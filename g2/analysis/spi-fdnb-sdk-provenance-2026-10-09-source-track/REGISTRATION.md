# Registered public IOM reference

The reference proposed in `REPORT.md` is now registered at `third-party/reference/ambiqhal-iom-fdnb`, pinned to official Ambiq commit `ef488e3b1fb1d612d61862595edd203ee9f6ca37`. `.gitmodules` uses `update = none` and `shallow = true`. Its current sparse checkout materializes only `mcu/apollo510/hal/mcu/am_hal_iom.c` and `.h`; blob-filtered acquisition avoids downloading unrelated SDK binaries. Both files retain their BSD-3-Clause notices. No downloaded code was executed.

An offline object check found this commit absent from both initialized older Ambiq repositories. Those remain at `5efc0228528a8adce5eae0d226fac85d2551eb3b`. No existing pin was changed. A separate reference was therefore necessary for this public source revision; no duplicate full SDK checkout was created.

Important source-version qualification: the newer public **C file** contains the TX-DMA/RX-IRQ FDNB implementation, but its public **header remains byte-identical to the older 5efc header** (SHA-256 `86135b68a11e12dccf041515bb09a22103c8ec26270d40d042fb65928b99c621`). It lacks both the new API prototype and selectable `eFdnbMode` field. This is a public source reference, not a complete newly published API/header release. Supplied SDK 5.2 C/H provide the selectable-direction variant and its public API declaration; their source hashes and finite discriminators remain in the original report.

Only the new gitlink and appended `.gitmodules` stanza were staged. Verified preservation: 31448 prior index entries, 31449 afterward, no removed entries, `.gitmodules` the only changed baseline path, and `third-party/reference/ambiqhal-iom-fdnb` the only added path. All preexisting `.gitmodules` content was preserved exactly. `REGISTRATION-PRESERVATION.json` records heads, hashes and these assertions.

No commit or push was made. This registration establishes licensed public provenance and availability, not linked stock inclusion, producing SDK identity, or equivalence to the supplied 5.2 implementation. Owner/auditor should use the registered C file for the one-direction lineage comparator and retain the SDK's separate source contract.
