# Auto-dither and mode7: full software composition

Independent source `g2/components/touch/auto_dither_offline/dither.c` closes0x68ec and supplies a mode7 dependency binding. **240 fresh original-instruction comparisons passed**:48 direct auto-dither,144 mode7 transitions and48 generated-base composition cases. Both sides execute full all-slot, per-sensor, CDAC, masks, divider, CPU setup and software delay helpers. The independent side uses public pinned PDL Configure. There are **no function-entry stubs or executable donor dependencies on the independent side**.

Comparisons include return values, both slot arrays, full base frame, internal context, driver context, final MMIO and ordered MMIO/SFLASH accesses. Source composition builds under Arm GNU13.3 -Og. Public Configure remains behaviorally validated rather than byte-exact (24-byte loop-layout difference, prior report). Inputs are synthetic coherent ARM32 contexts and trim/MMIO values.

## Concrete call chain and error ownership

0x68ec: GenerateAllSensorConfig(type0) -> GenerateAllSensorConfig(type1) -> Cy_MSCLP_Configure(hw, base, key2, driverContext) -> SetupCpuOperatingMode -> return configureFailure?0x40:0.

Both slot generations discard per-sensor errors, so malformed methods can leave partially written frames while mask overlays continue. PDL key errors can reject before configuration writes; unsupported IMO selector7 can reject after writes. **CPU setup always follows**, even when Configure fails. With static MRSS bit0 clear, the315-iteration wait exhausts, its status is discarded and CPU setup continues. Test instrumentation observes317 MRSS reads including the preliminary check and final budget check, not317 time units. Physical timing is unverified.

Mode switch0x6ac0 calls auto-dither at0x6bb0 and discards its return. For example prior mode0, driver lock255, selector7 and exhausted MRSS wait still return0 and install current mode7. Invalid prior mode3 instead returns1 without calling auto-dither; already-current7 returns0 without regenerating frames or clearing repeat. These are synthetic instruction-grounded software facts, not a claim that a hardware failure occurs or a patch is safe.

## Composition boundary

`touch_prepare_auto_dither` generates a base then executes auto-dither, comparing original0x5378 followed by0x68ec. This is an explicit offline helper sequence, not a claim that every stock caller invokes it. Static caller evidence separately shows stock0x71c8 calls0x5378 at0x7200 then both all-slot generations0x720a/0x7212; it first calls unresolved0x6384 and continues through0x5d70. The larger stock preparation function is not yet closed.

For CFW development, preserve slot layouts and partial-write semantics; treat mode7's zero return as mode assignment, not proof of successful PDL configuration or readiness. An improved error API would be a deliberate firmware behavior change and is not implemented here.

## Reproduction and next leads

build_offline.py takes an explicit ARM compiler, public PDL object and scratch output directory. Pinned PDL35f1714623cfea682d5e285af80d50416b4c7bbc; CapSense semantic reference247a9a0f79eb976f144f5fbeb29488c1c2606517. Prior submodule proposal remains intact; no index/gitlink changes were made. Source/constants/ELF provenance is recorded in reproduction-receipt.json and provenance.json.

Actionable next stock dependencies:0x6384 and0x5d70 in preparation0x71c8, and the dither/calibration selection caller ending0x7192..0x71c4. Analog responses, real factory trim bytes and physical timing need hardware evidence or a validated peripheral model. These software leads are not exhausted.
