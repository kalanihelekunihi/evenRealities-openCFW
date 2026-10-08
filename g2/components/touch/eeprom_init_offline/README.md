# Touch EEPROM initialization — offline reconstruction

Independent initialized-data declaration, provider-table setup, configuration validation/geometry, EEPROM initialization and application readiness wrapper. Source-defined factory configuration is256bytes, extended mode,wear2, redundantcopy1,blocking1; application patchesbase0xe400. See `PROVENANCE.json` and `g2/analysis/touch-init-closure-2026-10-08/REPORT.md` for original addresses, hashes, tests and limits.

Depends on the preserved `../eeprom_offline` module. This additive module is not linked into production firmware or acceptedbootloader checkpoints. It deliberately retains raw stock arithmetic/truncation, errorcodes and ignored scanstatus. It is not a defensive newstorageAPI or physicalflashdurability promise.

Build with the analysis `build.py --gcc <ArmGNU13.3gcc> --output <scratch>`, then `verify.py <scratch>/provider.elf`. The public Apache2 provider input is retained separately in `third-party/upstream/infineon-block-storage-1.3.0`; selectedSDKbyte attribution does not identify auniqueproducingrevision.
