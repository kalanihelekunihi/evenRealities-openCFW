# Public Infineon MSCLP source: exact attribution and behavior

Pinned public PDL `35f1714623cfea682d5e285af80d50416b4c7bbc`, built with Arm GNU 13.3 `-Og` for `CY8C4046FNI_T412`, reproduces two unique stock sections exactly:

| Public function | Stock address | Bytes |
|---|---|---:|
|Cy_MSCLP_Capture|0x8fa0|48|
|Cy_MSCLP_ConfigureScan|0x9178|160|

This is **208 bytes of compiled-source attribution**, not 208 newly discovered executable bytes. Reproduction asserts byte equality including literals, and records compiler/source/header/object/ELF hashes. These sections have no relocations. No uniqueness claim about the producer compiler/release and no whole-image source-completeness claim follows.

`Cy_MSCLP_Configure` has the same 424-byte extent at `0x8fd0`, but GCC 13.3 `-Og` differs in 24 bytes confined to one loop layout. Four optimization levels and three targeted loop/branch flags did not yield equality. **180 original/public instruction comparisons passed**, including key/lock failures and supported/unsupported IMO selectors, ordered MMIO and factory-trim reads. This is bounded behavioral equivalence. Synthetic trim values cannot establish physical oscillator frequency.

No function-entry stubs or original executable dependency occur on the public comparator side. Full regular-mode composition and initialization/capture use these public functions in separate validation reports.

## Pinned sources and submodule references

The existing PDL gitlink already points to the tested pin. The CapSense gitlink is `25fa1cd...`, whose pinned RELEASE identifies version **3.0.1**; its tree lacks the LP sensing source. The useful semantic comparator is **6.10.0** at `247a9a0...`. It is a separate reference, not justification to globally re-pin authenticated work.

Newly downloaded official sources include LP sensing headers, structure generation, LP generator source/header and release metadata. Downloads and hashes live in receipts; vendor EULA source remains in `/tmp`, with independent reconstructed C in the versioned repository. Both registered submodule directories lack local `.git`, so parent-repository HEAD must not be mistaken for their version. No gitlink/index changes were performed.

`submodule-proposals.json` records the additional pinned 6.10 reference. Proper installation requires a gitlink/index update, outside this task's explicit no-index constraint; the usable downloaded comparator and receipts are already present.

## Next source lead

Official LP generator source identifies `GenerateAllSensorConfig` at `0x56a4`, invoking the now-recovered per-sensor generator `0x5548`, CDAC generator `0x51bc`, mask helper `0x5188` and divider helper `0x5528`. The all-slot orchestration and auto-dither lifecycle remain open. Exact producer configuration requires generated `cycfg_capsense.h` or defensible reconstruction of its selected macros; semantic matching alone does not establish that build configuration.
