# Stock TDK transport and GAF callgraph binding

Static-only locked2.2.6.10 main flash binding; no firmware executed, no device/emulator/canonical/index/source/Git changes. [Receipt](TDK-TRANSPORT-BINDING-RECEIPT.json) hashes seven selected intervals, five public-source inputs and the newly bound stock patch. Linear whole-main disassembly is a discovery aid; selected called entrypoints, instruction flow and literals supply the actual bindings. Some historical census rows label this subsystem first-party by link-order inference; those labels do not override the recovered public protocol correspondence.

## Bound transport

Public acquired inv_imu_transport.c provides a distinctive access sequence, not just a shared constant. Stock matches it:

- 508E92–508E9A is SRAM-write wrapper: BL508FA6 at508E94, then returns. 508E74 normal register write selects508FA6 for address>=256, otherwise508EB6. SRAM-read wrapper508E8A calls508F34.
- 508FA6–509024 checks bounds through508ED2, stores address high/low and buf[0] on stack, invokes delay callback with4, then sends3 bytes to direct register7C through508EB6 at508FE6. It delays4 again; on success it loops remaining bytes through register7E at50900A, delaying4 each iteration and ORing statuses. This is the public write_mreg/SRAM contract.
- 508EB6 loads the callback at device offset4, preserves length inr2, moves register tor0 and buffer tor1, invokes BLX at508EC2, maps nonzero callback status to-3. Read equivalent508E9A uses offset0. Bounds508ED2 checks forbidden ranges2400–3FFF,8400–9FFF and>=B000, matching the public map.
- Context initialization4A36AE installs literal pointers4A35B1(read),4A35EB(write),491103(delay) into context20073020 offsets0/4/12, then calls504784. Thumb bits are preserved; they name even code entries4A35B0/4A35EA/491102. Bus wrappers select bus4, slave69 and one-byte register header, reaching50436E(read) or5044B4(write); they map bus failures to-1. This binds actual sensor transport context, not generic anonymous constants.

These are structural/behavior bindings; exact SDK/compiler identity is unproven. Current public transport includes a context field in callback ABI; the stock callbacks use register/buffer/length without that context argument, so even similar public transport is not assumed source-identical.

## Bound GAF and mounting edges

DRV_IMUSetSensorParameters4A3820–4A457C calls506ECA at4A4054 with device context inr0 and stack parameterssp+80 inr1.506ECA–507576 is a GAF-parameter setup counterpart: it reads accel1B/gyro1C ODR fields, computes periods, writes many GAF SRAM fields and invokes dynamic services before installing its patch. This authenticates the caller and configuration routine needed by the previous finite search.

At50729A it loads patch pointer via literal5076DC =6D53D8.5072A0 supplies length125;5072A2 supplies SRAMdestinationC80;5072A8 calls508E92. Patch SHA25680eb396ba1b365d332aabebed514cccb19f5d5a8eba1d6543be61ceda4fa8b2f, prefixf1700c98f1700cacf1700cc0f1700ce4.5072B0 copies4 bytes from patch+8;5072C2 setsB4;5072C6 writes the copied keyf1700cc0 via the same SRAM wrapper. Selected complete setup range contains no additional unequal-period-conditioned0x50 write at that insertion point. The acquired1.1.8 source instead uses a189-byte patch atC5C and inserts an unequal-period-conditioned four-byte write to50 before its acceptance-key write. **The stock path/patch layout differs from acquired1.1.8; this does not select1.1.2 or identify another exact producing release.** Older1.1.2 C was acquired without its matching calibration header, so a byte comparison against that version's patch remains unavailable.

Mounting is also positively bound:4A41CC loads literal4A4990 =20000E00 (the independently proven Q14 cache),4A41D2 calls507710 with it.507710–507726 passes the provided buffer directly to SRAMwrapper508E92 at50771C, destination1AC, size18. Thus the previous “no direct MOV r1,#1AC” heuristic missed a real `mov.w` form. There is no int8 conversion in this tiny routine; this active path consumes the host float-derived Q14 cache. This resolves the actual mounting-write contract without claiming the int8 public wrapper is present.

## Scope and next finite opportunity

[Census](TDK-SRAM-DIRECT-CALL-CENSUS.json) retains106 linear-disassembly BL candidates to508E92 with raw call bytes and preceding context. This is not106 independently classified functions or an exhaustive callgraph; indirect calls, tail branches, data/code overlap and unused code remain outside that count. Only named bound edges above carry semantic conclusions.

The strongest next source-led discriminator is now specific: acquire the calibration header and EDMP map belonging to already known official1.1.2 pin (or other justified public historical revisions) and compare with authenticated125-byte patch/C80/B4 layout. Do not rerun broad calibration-prefix/MOV scans or infer private sensor ROM semantics. Alternatively further static consumers/callers can use these bound transport edges, but source completeness/byte equality and physical sensor execution remain separate unproven goals.
