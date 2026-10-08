# Bootloader ADC context and calibration initialization

Locked bootloader f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5, load0x410000. Candidate shared image8ec1fa00cae0c882dae79282e43736418537a942645ba185d7a6d6026f5618fb. New readable C/header: `g2/components/bootloader/initializer_callbacks/adc_context.c`/`.h`. Bodies: initializer42e8d0..42ea32 (354 bytes), metadata reset42ea32..42ea68 (54 bytes). The existing INFO selector421548, dispatch4213e6 and ROM thunk41d28a are reused native source. Exact disassembly/body hashes and pinned SDK evidence hashes are in provenance.json/original-disassembly.txt.

## Context and publication

Only module0 is accepted; other values (including256) return5 before output validation. Null output returns6; already-claimed bit24 returns7 without changing state/output. The context is a source-owned static72-byte object at20026df0, not heap allocation. Its prefix is flags at+0/module at+4; the other64 bytes are retained unchanged by these two bodies.

Success first sets claimed bit24 in a separate store, preserves the upper flag byte while replacing low24 magic with0xafafaf, sets module0, zeros2002702c, then publishes the output pointer. Calibration happens **after publication**. Calibration failure does not roll back claim or report failure: the initializer returns0 after choosing defaults/validity markers. Direct ROM fixtures observe the published output and claimed prefix before every INFO read.

There is no critical section around claim/publication/reset; caller serialization and real scheduling remain unproved.

Reset validates masked prefix01afafaf, separately clears claim and low24 magic, resets module+4 and returns0. Invalid handle returns2. It does not clear calibration fields, free memory, disable the ADC peripheral, mask IRQs, drain callbacks or establish task quiescence. A successful reset permits reclaim; repeated initialization without reset returns7.

## Calibration fields and actual reads

| INFO1 word offset | MRAM route address | Pinned Apollo510 field | Destination |
|---|---|---|---|
|0x240|42003300|TEMP_CAL_ATE|20026fc0|
|0x241|42003304|TEMP_CAL_MEASURED|20026fc4|
|0x242|42003308|TEMP_CAL_ADC_OFFSET|20026fc8|
|0x24a|42003328|ADC_GAIN_ERR|20026fe4|
|0x24b|4200332c|ADC_OFFSET_ERR|20026fe0|

These offsets/counts are **32-bit words**, corroborated by SDK INFO declarations and the native dispatch. CURRENT_INFO1 selector1 chooses MRAM or OTP using400201bc bit3. MRAM adds0x280 words for input offsets>=0x200; OTP uses42006000+4*offset and requires40021008 bit27, otherwise returns9. The resident reader atROM48 is absent from the official payload and remains an explicit external dependency. Its return is discarded by the thunk/dispatch; a nonzero resident status alone does not cause calibration fallback if it supplies nonzero words.

If cached structure200267f8 starts with1f01600d, the first group copies cached+38/+3c/+40 and bypasses INFO reads. Otherwise the three INFO statuses are ORed. All three raw words must be nonzero and combined status0. Failure substitutes4395c000/3f839874/bb8c47a1 and clears byte20026fcc; success sets that byte1. This is a nonzero-bit-pattern test, not a finite/range check: direct NaN and signed-zero-word fixtures can pass it.

For the second group the function **rereads** cached magic. Valid cache copies+48 to gain and+4c to offset; otherwise it reads0x24a then0x24b, ORing statuses. It clears bit0 of4002010c, and sets byte20027199 only when gain/offset raw words are nonzero and status0. On failure it does not replace/clear the existing pair: stale words can remain with validity0. The meaning of4002010c bit0 is not assigned without separately tracing that peripheral definition.

A synthetic mutation sets cached magic during the first INFO callback. The first group still makes three reads, but the second uses the new cache and makes none. This proves static reread order in the fixture, not a physical race.

## SDK corroboration and practical meaning

Downloaded Apollo510 HAL headers are pinned at5efc0228528a8adce5eae0d226fac85d2551eb3b, release_sdk5p1p0-366b80e084, under the bootloader upstream-worker directory. `am_hal_adc.h` explicitly states that initialization success does not imply valid temperature calibration and that INFO OTP must be powered beforehand. Its TEMP_TRIMS_GET contract exposes a measured/default indication. Its CORRECTION_TRIMS_GET request describes offset/gain used by samples. `am_mcu_apollo510_mraminfo1.h` names the five addresses above. These are corroborating contracts; no Apollo3 implementation or unverified physical units are substituted.

Apps/CFW must not treat init return0 as evidence of measured calibration. Preserve the measured/default marker and independently trace the correction getter/sample consumer before applying a second correction in an app. Reset metadata is not an ownership-release or safe shutdown primitive. No firmware patch is implemented here.

## Validation and remaining limits

135 fresh-CPU stock/source comparisons PASS: cached/current-MRAM/OTP ready/not-ready routes, resident statuses0/9/ffffffff, each calibration word zero/nonzero/NaN/signed-zero pattern, module/null/already-claimed guard precedence, flag preservation, reset/reclaim and synthetic cache switching. Ordered prefix/global/MMIO writes, ROM addresses/outputs/publication snapshots, statuses, retained context bytes and markers compare. Original selector, dispatch and thunk instructions execute; **only unavailable ROM48** is modeled with explicit word/status callbacks.

Seven-case integration additionally uses zero-valued synthetic INFO words for the five exact requests, causing defaults/invalid correction markers while preserving the native instruction chain. Its final context/calibration fields and native call counts are compared along with prior system observables. No actual factory calibration, OTP power/read, analog sampling, hardware IRQ/scheduling or shutdown proof is claimed. Prior GPIO higher-bank callback and direct zero-fill-model limits remain recorded; CMDQ termination remains a separately retained test module.

Remaining ADC initializer dependencies include control/getters42ec0c, context configuration42eb74, profile/channel/activation/read/reset-lifecycle APIs and their real peripheral/sampling behavior. This checkpoint closes context claim/calibration/reset metadata only, not all ADC behavior, complete source build or byte equality. No unrelated app work, commits, flashes or IAR login.

Next [control/getter finding](../adc-control-next.md): request3 copies offset/gain without reading correction-valid marker; request2 returns measured/default as rawword0/1. These are static findings only, not integrated source behavior at this checkpoint.
