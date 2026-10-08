# Actual touch flash provider and discarded errors

Independent reconstructed `flash.c`, `providers.c` and `provider.h` now execute the locked-image flash/provider control flow in a standalone ELF: `b400fe9e1004ec83c205ee82cf3dcf3274fb20f0f704d803bfebdb77880bbaf7`. Public CM0+ critical-section assembly is linked from the existing pinned PDL closure. No accepted firmware checkpoint, production payload or index changed.

## Installed provider and ownership

Initializer0x486c populates provider20000ed4: slot5=4861 (copy),6=4811 (program rows),7=47b1 (zero rows),11=47ab (return0); handle slot0=0, slots8/9=null. Other constants are recorded in provider-table.json. Context200008c8+28 retains this provider pointer. Callers supply borrowed RAM; program helpers synchronously copy each128-byte input row into driver-local storage before requesting SROM. No heap ownership transfer or freeing is observed.

Program gate0x7ea4 (historically CheckRanges) always invokes slot11 with physicalu16 size at context+2. It then uses max(physical size, stepu32 at+4). If contextbyte15=0 it returns0. Otherwise a nonzero check result invokes slot7 and maps its nonzero status to093e0003; then slot6 is invoked and its nonzero status maps likewise. **The installed slot11 returns0**, so its conditional erase branch is not reached with this normal table. Generic callback cuts independently test the other branches; they are not claimed as stock-provider reachability.

Both application row adapters reject sizes not divisible by128 with06160002. For accepted sizes they iterate128-byte rows while address<modulo32(address+size), invoke Cy_Flash_WriteRow, **discard every return value**, and return0. The zero adapter prepares512 zero bytes and passes that buffer for each row; the program adapter advances its input pointer128 per row. The copy callback performs the actual forward copy. Raw wrapped endpoints/overlap are callee observations, not endorsed new-app inputs.

## Low-level flash choreography

`0x8d50..0x8e04` validates128-byte alignment and main flash address<10000, or the512-byte supervisory range0ffff200..0ffff3ff. Null data/invalid address returns00520021. It copies128 bytes into local parameters; issues CPUSS load opcode4 through SYSARG40100008/SYSREQ40100004; decodes status; on success saves PRIMASK and disables interrupts, then issues backup16hex, config15hex, main program5 or supervisory program18hex, and restore17hex. Program error takes precedence over restore error; otherwise restore status is returned. PRIMASK is restored after all tested post-critical outcomes.

Backup writes40030030=80000000 even when its status fails. Restore is issued only after reaching the program stage; backup/config failure skips it. This is static sequencing, not proof of hardware clock state or a physical fault. SROM clock/program bodies are external to the inspected OTA and modeled explicitly.

The status decoder0x8bf4 has in-frame branches through a20-entry table atb51c. Its historical58-byte catalogue range omits shared return blocks; authenticated disassembly includes through8c46. A-family status ->0; F0000001->00520001; F0000003/4->00520004; F0000005->00520005; F0000007->0; F0000008->00500008; F0000009->00500009; F0000011/13/14->00520021; other F-family values->005200ff; other families->00500023. It **reads SYSARG once**, with no retry/timer loop. The pinned newer PDL flash source includes WaitForSysCallFinish with a1000-attempt retry; that implementation is not attributed to these stock bytes. Public source is a behavioral comparator, not exact compiled attribution.

## Validation

- **828** original/native flash choreography cases and **28** decoder cases: real stock/native decoder, clock, critical and memory bodies; only CPUSS/SROM completion is synthetic. Transient parameter pointers are compared by contents/store count; final SP/PRIMASK compare.
- **336** real row-adapter and **72** normal installed-provider/program-gate comparisons execute actual flash choreography. They include injected flash errors and invalid raw addresses; aligned adapters still return0.
- **512** generic program-gate cases use three explicit callback-status cuts, covering size selection and error branches under a stable provider/context assumption. They do not prove callback reentrancy.
- **20** real copy-callback comparisons, including raw forward-overlap behavior, with no cuts.
- Two mutants (wrong program-vs-restore error precedence, propagate errors unlike stock adapter) are rejected.

The standalone source guest contains reconstructed/public executable code only. No original executable aliases or opcode arrays implement these functions. Source compatibility, per-suite instruction observations and global source coverage remain separate. SROM responses are injected immediately; no physical completion, timing, persistence, clock transition or exception delivery is proved.

## Consequence for command7

The write driver can distinguish failures, but application adapters erase that information. The coupled stock traces in ../touch-extended-rows-2026-10-08/command7-results.json demonstrate that low-level failure can coincide with application storage status0, after ACK preparation. A future CFW design needs explicit propagation of each row status, a separately exposed persistence outcome and ownership/scheduling validation. These are requirements, not implemented patches; the faithful reconstruction intentionally retains stock error loss.

Remaining source leads: integrity/historic-row recovery, actual producing library revision/configuration, and SROM semantics. Physical conclusions require the missing SROM implementation or faithful peripheral/ROM model and a hardware trace. Existing OTA bytes alone do not supply those external routines or live storage contents.
