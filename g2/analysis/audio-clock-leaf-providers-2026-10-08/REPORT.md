# Native GPIO, clock power leaves and HFRC2 ratio generation

Thirteen reconstructed leaves pass **1,374 direct comparisons**, plus **12 meaningful repeat/error/cleanup sequences**. The same exact ELF also passes **3,403 reused composition fixtures** from driver/config/manager/stock-reachability suites with these children now native. Total4,789 artifact comparisons is not a distinct whole-firmware coverage count. [Readable C](../../components/audio/clock_leaf_providers_offline/providers.c), [interfaces](../../components/audio/clock_leaf_providers_offline/providers.h), [exact build](exact-build-validation.json), [addresses/byte hashes](function-bindings.json). ELF SHA256 `204874191bb4384febf3aba82237d637071474e322c5f558a52860d99561938a`.

## External reference and GPIO ownership

Request0x4C3CD4 requires configured external frequency nonzero, else7; already-owned user returns0. First acquisition enters a critical section, calls native GPIO setter for pin15 with raw configuration10, publishes clock3 user bit, and restores prior IRQ mask. The GPIO status is discarded. Stock constants0x78EE34/38 are3; acquisition replaces the low function nibble with10, last-user release writes3. Both words are scalar recovered configuration data, not retained executable blobs.

Repeated acquisition is idempotent. Another-user release leaves pad15 unchanged. Last release writes configuration3 and does **not restore the old pad word**; tests begin with0xDEADBEEF and finish10→10→3. Prior native GPIO validation/PADKEY/IRQ helper executes. This path does not enable SIP pin136 or wait for external-clock detection; physical12MHz availability is not proved by configured frequency or ownership.

## Power commands and error/status distinction

SYSPLL power enable clears regulator bit21 at0x400201B0 for chip-major byte>=0x22, delays1 inside the saved critical section, clears controller bits31 and30, restores IRQ mask, then delays5. Older-major skips regulator/delay1. Disable sets31/30, delays1 then sets regulator21 for major>=0x22, and restores mask. Both return0 after commands; no physical status poll occurs. Power-enabled query is exactly inverse of controller bit31, not a measured supply-ready flag. Native driver/config composition preserves these distinctions.

HFRC force changes0x40004044 bit0 after byte-narrowing bool input. HFADJ apply writes the entire packed config OR1; disable clears bit0. HFRC2 force sets bit5 then calls actual wait5(100,0x40004030,bit24,bit24,1) only when bit5 was previously clear. A synthetic absent-ready bit makes actual first call return4 while leaving force bit5 set. Repeat force-on returns0 without any wait; force-off clears bit5. The tested direct sequence is4→0→0. This is a software command/cache effect, not an observed failed oscillator.

HF2ADJ apply returns6 for NULL. Otherwise it ORs preset register0x4000404C with7, writes reference lowbit to0x40004048 bit29, divider low2 and ratio low29 into0x40004050, and enables bit0. Disable clears only enablebit0. Raw out-of-range enum/ratio bits are masked, not validated. Stock-default successful configuration paths remain verified with native children; timeout/lock/power inputs remain synthetic. [Repeated cleanup](sequence-results.json), [stock configuration reachability](reachability-results.json).

## Native generator math and numerical limits

HFRC target performs unsigned integer target/reference division. HFRC2 ratio first integer-divides reference by1 shifted by divider, converts target/effective reference to single precision, divides, then converts to unsigned Q15. Native source uses one named VFP fixed-point conversion instruction to preserve stock saturation/rounding/status effects; it is compiled source, not an opcode array or executable blob. Direct tests compare output and FPSCR under default/rounding-up/flush-to-zero settings, including zero/out-of-range synthetic inputs. Stock-supported auto configuration uses divider2 and valid board frequency; malformed shift/divide cases use the explicit **DIV_0_TRP=0 offline profile**. Enabled divide traps, exception entry and physical clock behavior are not modeled or claimed.

At stock HS=0/external12MHz, generated HFRC2 reference remains external and the prior configured196.608MHz fixture is reproduced. SYSPLL postdivider generation remains original code:0x539794 calls min-VCO0x539674 twice. Pinned source includes generate/minFVCO/with_postdiv families; this is the next concrete math lead, not a source-exhaustion boundary.

## Remaining dependencies and preservation

Clock/GPIO/power leaves and HFRC ratio generation are now native in composed tests; original delay/status waits, oscillator and SYSPLL postdivider/min-VCO math remain explicit. No physical readiness, observed hardware fault, live IRQ or BLE/app reachability claim. Counts overlap prior regression input sets.

Prior seals,110 authenticated inputs,four checkpoints and concurrent staging are preserved. Only new owned analysis/component directories were edited; no commits, production edits, device writes or campaign/gate changes.
