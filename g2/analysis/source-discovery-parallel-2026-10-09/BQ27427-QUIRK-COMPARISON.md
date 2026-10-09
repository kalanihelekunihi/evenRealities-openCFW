# Zephyr BQ27427 CC Gain reference

New isolated official source acquisition: Zephyr main pinned87a40fa6068d12d14a7a3521c3d12925da2cc37e, fetched2026-10-09. https://github.com/zephyrproject-rtos/zephyr/tree/87a40fa6068d12d14a7a3521c3d12925da2cc37e/drivers/sensor/ti/bq274xx . Acquired bq274xx.c, bq274xx.h and rootLICENSE; per-file URLs/SHA256 in acquisitions/zephyr-bq27427-reference/provenance.json. Driver SPDXApache-2.0. No code executed. Existing third-party search found no Zephyr fuel-gauge checkout; prefer a pinned reference-file addition for owner review, not wholeSDK download. No .gitmodules/index mutation.

## Applicable device evidence

Consolidated docs/hardware/components/bq27427.md and g2-glasses.md identify BQ27427 on charger-family2 boards, I2Cbus7 address55; firmware contains both chargerfamilies, so no universal fitted-board assertion. Current authenticated symbol index binds37 driverfunctions. Fresh byte hashes agree for updateDM53B6F0..53B8BA (ffa13effca5ff6bfbc0f8400917e362a63f02ed8334ba11e1d711ca4c2a688f7) and configure53BB8C..53BCDA (aa1a85372d9952b3cba9ec540200536d9e832d0a5c072819e84f246344c0ddb4). Image identity is inBQ27427-QUIRK-RECEIPT.json. Historical detailed recovery paths cited by hardwaredocs are absent locally.

## Pinned source contract

bq274xx.c266–326: select subclass105, block0; read BlockData byte5 (register45); if bit7 alreadyclear return; otherwise read checksum60, XOR80 into both byte5 andchecksum, write both, delay. This selectively clears the sign bit while preserving other bits. Configurator invokes it only for BQ27427 inside the block_modified branch (around475), so it is not an unconditional startup action. GenericDM fields and checksum helpers are relatedprotocol references, not stocksource fingerprints. Source cites TI E2E thread1215460; direct verification was blocked403, so the manufacturer erratum rationale is presently source-reported, not independently fetched.

## Stock comparison and bounded stop

Stock configure53BB8C builds fiveDMbuffers from a sevenentrydescriptor root. Literal53C1CC contains RAMpointer200006EC. Genericupdate53B6FC..53B708 indexes descriptors at stride8 and reads fieldoffset; the bufferupdate paths store caller-supplied values. Configure's visible calls use descriptorindices0/1/4/2/3/6 and commit fourbuffers; index5 contributes an additional readbuffer. This does not expose descriptorclass/fieldvalues without resolving initializedRAM bytes. A simple rawliteral-table search found no uncompressed82/6/8 pattern and is not an absenceproof; IARinitializeddata decoding/mapping is still required.

No explicit Zephyr-like signbit/checksumXOR sequence was established in these two boundedfunctions. The genericupdate path may implement a related effect through initializeddescriptor/value semantics; no stockabsenceclaim is made. Next finite comparison: authenticate sevendescriptorbytes at200006EC, resolve subclass105/offset5/type/value, then trace any containingbuffer read/dirtyupdate/checksumcommit. Avoid extrapolating from sharedDMprotocol or namedfunctions.

## Emulator implication

At pinned emulatorf30527c0b7e6fa6e9be06e7067e49468197fa258, G2BQ27427.cs498–513 initializes subclass105/block0 byte5 to00. This is already signclear under the Zephyrpredicate; its default fixture cannot exercise the ROMsignbit-set branch. Generic32byteDM/checksum support is relevant, but no modelrun or physicalgaugegainaccuracy was tested. The model's default is not an authenticated ROMdump and cannot prove stockworkaroundpresence or necessity on fittedhardware.

Outcome: genuinelynew publicprotocolreference, acquired/pinned/licensed; stockworkaroundbinding remains unresolved at a precise initializeddescriptorboundary. No newdevice/emulator/canonical/index changes.
