# Eight-byte flag-clear lineage check

## Result

No accessible exact implementation or patch evidence attributes the stock `flags &= ~0x20` block to a named release, build configuration, or local patch. The discriminator remains valid, but its lineage is unresolved. Stop at this boundary; do not label the block a 1.4.15 fix.

## Evidence checked

- Authenticated supplied AmbiqSuite 5.2.0 ZIP: no `nema_cmdlist.c` member in ThinkSi; extracted header declares NemaGFX 1.4.12, implementation 2024-10. The supplied changelog extends through 1.4.17 and lists a circular-flag handling change under 1.4.15 (2025-05). Member hashes and ZIP paths are in `LINEAGE-MEMBER-PROVENANCE.json`.
- Existing public Ambiq exact subtree pin `b853fded7e545f005727e13bf2ce83018c7e242d`: complete, untruncated tree has public command-list headers and changelogs, but no `nema_cmdlist.c`. Its changelog stops at 1.4.12 and does not name the later circular-flag change. Downloaded documentation SHA-256 `09c01747a286ae77699c1eff0daf904715a9a1ec568811cf21446651c6294c10`; pinned URL in `LINEAGE-AMBIQ-PROVENANCE.json`.
- Official ST x-cube-image-processing changelog pinned to its most recent file-changing commit `f415e9bcce92a532096a62f6d1e9764895bec95f`: NEMAP 1.4.15 release, 2025-05-08, reports that circular-flag setting moved from unbind to bind. Download SHA-256 `f01484f3275a51b712548d455c258fe5fca104aca2cd5302cd0783ae4c17a59d`. Complete public tree contains `nema_cmdlist.h` but no implementation C; receipts in `LINEAGE-ST-PROVENANCE.json` and `LINEAGE-PUBLIC-TREE-CHECK.json`.
- Existing LVGL public header declares 1.4.11/2024-06. Existing locked-reference command-list header describes `flags` at the expected structure location but does not publicly define bit 0x20 as the circular flag.
- Exact public searches for the named function with `flags` or `nema_cmdlist.c` found API/use-site material and changelog descriptions, not a code-level attribution of this block.

## Interpretation limits

The public 1.4.15 note concerns setting a circular flag. Stock's observed block clears bit 0x20 in an existing command list before the unbind-related path. Neither the available public headers nor release note proves that these are the same operation. Supplied 5.2.0 header/archive packaging is also not a reliable release mapping: a 1.4.12 header coexists with documentation describing later versions. No build-configuration conditional or local patch implementing the clear was found.

This follow-up acquired documentation only. No proprietary binary was newly downloaded, publicly registered, or redistributed; no new agreement was accepted. The license uncertainty documented in `FINAL-STATIC-RESULT.md` remains. Root index, canonical ledgers, firmware sources and reference seals were untouched.
