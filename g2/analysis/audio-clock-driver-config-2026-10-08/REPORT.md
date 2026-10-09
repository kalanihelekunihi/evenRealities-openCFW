# Clock configuration, native SYSPLL driver and stock-path reachability

Nine complete native functions pass **3,403 comparisons on one exact ELF**:1,407 SYSPLL driver,1,144 configuration/dispatch,816 reused manager regression fixtures with newly native driver dependencies,and36 complete configuration/request/repeat/release cases. These counts describe this artifact and overlap prior regressions. [Readable driver C](../../components/audio/clock_driver_config_offline/driver.c), [configuration C](../../components/audio/clock_driver_config_offline/config.c), [12-byte interface](../../components/audio/clock_driver_config_offline/driver.h), [exact build](exact-build-validation.json), [addresses/hashes](function-bindings.json). ELF SHA256 `8b7227684c467c5d3cc8e3ea2b97c61447cc270d254a1ec816eb1673f1617114`.

## States reached through verified stock configuration

All36 end-to-end cases start with the stock board HS=0,LS32768,external12MHz and invoke actual original or matching native configuration before request; no preseeded valid cache. Automatic generators execute original instructions. Physical readiness/lock fields are explicitly synthetic.

| Configuration and synthetic response | Configure→request→repeat→release | Ownership / cleanup |
|---|---|---|
| Auto HFRC2 adjusted196.608MHz, force-on wait times out | 0→0→0→0 | Caller bit acquired despite actual wait4; release clears last user |
| Auto SYSPLL48MHz external, SIMOBUCK status valid, lock stays0 | 0→4→0→0 | Late timeout keeps caller bit/driver handle; repeat bypasses lock; release cleans up |
| Explicit SYSPLL external with invalid ref divider64 | 0→6→6→0 | Cache-valid set by manager; driver rejects and setup cleanup clears caller/handle |
| Auto SYSPLL external, SIMOBUCK status not valid | 0→7→7→0 | Driver enable rejects; setup cleanup removes ownership |
| Explicit XTAL-reference config with stock HS=0 | Configure7; request not run | No valid config; earlier missing-XTAL error states require seeded cache or changed board history |

This proves offline control-flow reachability through internal stock APIs, **not a physical fault or a BLE/app route** to those APIs. [Exact sequences and real wait returns](reachability-results.json). Previous HFRC2 overwritten-acquisition-error fixtures remain outside fresh valid stock-default configuration; this batch does not reclassify them as normal startup paths.

For auto HFRC2 at196608000, generated stock config bytes are `010200009bc4200000000000`:external reference1,reference-divide enum2,ratio0x20C49B. Actual ratio provider uses integer reference division followed by single-precision division and Q15 conversion; no equivalence of physical oscillator frequency is assumed. Auto SYSPLL48MHz yields `010101010501140000000000`:external1,VCO1,integer1,refdiv1,postdiv5/1,feedback20,fraction0. Target setting is a generated configuration, not measured output.

## Manager configuration validity versus driver validation

HFRC2 supports requested0,196608000,250000000; other requests5. Active users permit only0↔250MHz transitions when both old/new selections lie in that pair. An explicit adjusted config validates reference availability only for byte0/1; cache copy includes all12 bytes. Active switching acquires the new reference but discards its request status, applies/disables adjustment, and releases unneeded sources. Configuration metadata changes can precede provider application; no IRQ-interleaving proof is supplied.

SYSPLL accepts arbitrary requested frequency with explicit config after reference-availability checks; auto generation can reject unsuitable frequency. Any active clock6 user prevents configuration with3. A success means the12-byte config and requested-Hz cache were stored and valid set. Divider checks occur later in driver configure. Unsupported raw reference enum bytes2/255 can pass manager availability checks; driver writes only bit0. These cases document absent validation, not supported enum semantics or a proven app-input path. Host/CFW interfaces should validate documented enums and parameter bounds before calling these APIs.

Public clock-config dispatcher byte-narrows selector:4→HFRC,5→HFRC2,6→SYSPLL; all other selectors return7, not invalid-argument6. This preserves the corrected HFRC provider identification0x4C38A0 and stock20-byte board setter0x4C45E2.

## SYSPLL driver lifecycle and lock boundary

Native init0x5398E0 accepts module0/nonNULL output and rejects already-initialized with7. It installs magic/prefix and module, calls original power-enable, **discards that return**, and returns the state pointer. Handle validation checks initialized+magic rather than proving pointer allocation provenance. Deinit optionally disables, queries power, invokes power-disable if active, ignores power-disable return and clears initialized; enable/disable use enabled bit25. Enable checks SIMOBUCK status bits16..19 unless already enabled; ready status is synthetic in tests.

Native configure rejects an enabled handle with7 and validates reference divider<64; integer feedback4..960 for mode1,other modes10..96; postdivs<8 andpostdiv1>=postdiv2. Zero reference/post dividers are not rejected here; hardware interpretation is not established. It preserves masked register fields, writes fractional low24 bits and dividers, updates retained reference through the prior native helper, then applies output/power-control bits. Config pointer must be nonNULL after handle validation; no new null guard is invented.

Lock wait requires controller enable bit29 and valid handle. Timeout is ceil((VCO1?1875:1000)*refdiv/12) in the source delay API's microsecond units, then actual wait5 polls0x400204E4 bit0. Direct divider0/1/63 cases test real provider timeout/success paths. Software timing, passive register responses and driver handle success are not physical readiness. Late manager lock errors are not rolled back; setup errors are.

## Remaining source-backed dependencies

Original oscillator/external-reference GPIO providers, HFRC/HFRC2 apply/force providers, delay/power waits, HFRC2 float ratio generator and SYSPLL postdivider/min-VCO generation remain explicit dependencies. Pinned local source includes the generator family; these are actionable native closure leads. No source-exhaustion claim. Full M55 exception behavior, actual IRQ scheduling, physical references and rail/lock traces remain external evidence boundaries.

All prior seals,110 inputs,four checkpoint images match; concurrent staging preserved read-only. No commits, production changes, hardware writes or shared campaign edits.
