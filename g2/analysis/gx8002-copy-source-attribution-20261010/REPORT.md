# GX8002 `csky_copy_q15` source attribution

This bounded search followed the one concrete C mismatch from the prior GCC 6.3 comparison. `receipt.json` pins the searched files, hashes and search classes. It changes no source or canonical evidence.

## Result

The pinned NationalChip SDK has both `utility/libdsp/Source/SupportFunctions/csky_copy_q15.c` and `utility/libdsp/Source.asm/SupportFunctions/csky_copy_q15.S`. The SDK Makefile comments out the C object at line 263 and selects the assembly object at line 340. Under the fixed authenticated C-SKY GCC 6.3 recipe, the unchanged C source compiled to an 84-byte selected text section while the authenticated stock section is 44 bytes. The prior exact assembly rebuild already covers this stock section. This is an attributable source selection, not a missing C file or a reason to tune C flags until bytes happen to match.

The pinned SDK's local Git history contains only the checked revision for the C file. The retained NationalChip `lvp-aiot` acquisition contains an alternate `grus_gx8002b_dev_1v` board header and sources but no `csky_copy_q15` C or assembly alternative. Its board header differs in hash from the pinned SDK header, so the common board name does not authenticate either one as the G2 product configuration. The exact `grus_gx8002b_dev_1v` board string in the locked image identifies a family; no source-owned G2-specific `.config`, link map or private application definition was found in these retained leads. The codec symbol ledger adds no direct `csky_copy_q15` name/address entry; the existing object-section match is the bounded provenance basis.

## Finite local frontier

No new C revision or product configuration was found in the pinned SDK, its local history, or the retained `lvp-aiot` comparison tree. The matched assembly source is already compiled and byte-checked, so this pass admits **zero** new source units and **zero** new original/source execution cases. Repeating the same C build or copying the stock section would not advance source ownership. A new attributable product configuration/private source, exact compiler recipe for a distinct C body, or a qualified C-SKY numerical oracle would open a new task; none is present in the searched local corpus. The local attribution search for this unit is complete.
