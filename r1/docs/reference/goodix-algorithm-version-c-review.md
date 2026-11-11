# R1 Goodix algorithm version dispatcher in C

`r1/src/application/goodix/native_algorithm_version.c` supplies `GH3X2X_AlgoVersion` and eight native version providers. The full license-free build now compiles 878 units, with 60 unresolved application symbols and 22 bootloader symbols. `GH3X2X_AlgoVersion` is removed from imports; no imports are added. No new writable state is introduced.

The [machine-readable receipt](goodix-algorithm-version-c-review.json) pins REA reads, source, objects, tests and the final build report. All 867 previous nongenerated source/object pairs remain unchanged. The tested object equals the normal build object. Existing generated startup and uecc objects differ. This remains a relocatable composition, not proof of a bootable image.

The admitted native entries are:

| Entry | C provider |
| --- | --- |
| `0x2a0f4` | `GH3X2X_AlgoVersion` |
| `0x2b4d8` | `GH3x2xAdtVersion` |
| `0x667e4` | `r1_goodix_dlcom_version` |
| `0x66840` | `r1_goodix_dsp_version` |
| `0x66890` | `r1_goodix_version_qualifier` |
| `0x6d424` | `goodix_hba_version` |
| `0x6df60` | `goodix_hrv_version` |
| `0x6e788` | `goodix_nadt_version` |
| `0x6ec90` | `goodix_spo2_version` |

These native buffer APIs supersede earlier portable capacity-taking symbol hints. The portable implementations remain available to their own consumers.

All 3,122 paired native/C comparisons pass, executing all 768 admitted native instruction bytes. Tests cover all 256 function IDs, null dispatcher outputs, three buffer seed patterns, both PRIMASK settings, each provider directly, and null qualifier output. Complete 512-byte caller buffers and guards match, including untouched bytes after the terminator. The longest version text is 126 bytes. Saved integer/FP registers, SP and masks are preserved. The ADT getter's returned text is compared; numeric read-only addresses depend on layout. DSP/DLCOM destination returns, qualifier return one and unterminated two-byte write, and builder return zero are checked.

No providers are modeled: stock executes its actual version and string routines; compiled C executes its complete graph with the existing C memclr4/memset providers. Source execution cannot enter stock. Private frames, caller scratch, APSR and the dispatcher's void return word are excluded.

Eight compiled defects are rejected: wrong default text, omitted NADT ID, missing qualifier separator, unwanted qualifier terminator, wrong HRV return, wrong SpO2 parenthesis, wrong DSP hash and wrong ADT identity.

The stock weights helper at `0x6a020` performs a raw requested-length copy. Its SpO2 caller requests 50 bytes from an 18-byte identity, copying the terminator, alignment padding and adjacent executable instructions into private scratch. Only terminated text reaches the caller's version output. The C caller supplies that text through a private helper without retaining executable data; the unused private scratch tail differs. **The unchecked weights helper is not exported, mapped or admitted as a native C replacement.** Its arbitrary-count ABI remains an analysis boundary. The initial standalone bounded-copy candidate was rejected and removed before admission.

No instruction or image identity is claimed. Final executable linking/startup, physical sensor operation, concurrency and boot remain open.
