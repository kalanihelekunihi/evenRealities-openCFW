# Touch read closure, canonical promotion and stronger SDK attribution

The independent touch persistence reconstruction now has a canonical home in [g2/components/touch/eeprom_offline](../../components/touch/eeprom_offline/README.md). Eleven C/header files are source inputs, with explicit ownership/provenance. Original sealed analysis remains untouched. This isolated offline module is not linked into the accepted bootloader checkpoint or production payload and is not deployable firmware. Fixed guest addresses, bounded sensor/reset contracts and preserved raw stock error behavior remain explicit.

## New read behavior

`read.c` reconstructs stock simple read0x7e44, extended read0x82e0 and dispatcher0x8a78. Read dispatch rejects sizezero/nullbuffer/out-of-capacity raw modulo32 sum; simple mode calls provider slot5 and maps its nonzero return to093e0002. Extended mode clears destination, calls integrity recovery (ignoring its status), locates each active historic half, validates primary/mirrorCRC and loads accepted historic bytes. Invalid zero-sequence/zero-checksum rows producezero bytes with statuszero; erasedFF differs. It then overlays intersecting valid active payloads in row order. Overlaycopy and historic copy return statuses are ignored in extended read; corrupt payload rows are skipped. Historic badchecksum outranks redundant-copy-used, then success. Payload overlay can produce usefulbytes while the historic status remainsbadchecksum.

The address/length payload header is u32LE at offsets8/12, payload starts16, historic half starts64 in tested128-byte rows. Wear1 follows rows directly; wear2 locates appropriate historic windows from previous wear block relative to contextlast. Valid coherent geometry, stable provider/memory and bounded headers are preconditions. No general malformed-memory safety claim.

## Exact current offline validation

Canonical-source ELF SHA **cfc597b15147754af416d4dc59dd853c0ecb567edd503fee4105f9fbe0271604**:

| Suite | Cases | Boundary |
| --- | ---: | --- |
| Read dispatcher/simple/extended |690| No function-entry cuts; actual stock/native helpers,CRC,copy; synthetic storage |
| Integrity/recovery/history/merge |1148| No function cuts; read-only synthetic rows |
| Full extended write |1728| No function cuts; SROM responses/full/torn guest writes synthetic |
| Complete command7 callback→deferred→dispatch→simple/extended→history→flash |800| No function cuts; synthetic SROM; sequential invocations |
| Negative read controls |2 rejected| Omit header overlay; accept bad historicCRC |

Read visits616/620 original instructionbytes. Unvisited0x83a0..0x83a4 is row-search exhaustion; coherent tested geometry does not produce it. Coverage is bounded, not API completeness. Compared destination guards, returns, context,SP,PRIMASK and unchanged storage. Seven synthetic patterns plus zero-sequence/nonzeroCRC pattern, simple/extended, wear1/2, redundancy0/1, two last-row choices and five requestwindows comprise640 cases;50 further cases use exact recorded command7 storage snapshots. Existing earlier SDK/history mutation evidence is preserved separately.

The original integrity batch [report](../touch-history-closure-2026-10-08/REPORT.md) explains unsigned sequence selection, redundant recovery, zero-versus-erased handling and discarded providererrors. That prior exact-source800-case command7 image SHA is216bca061ebbfb01e4e112149ec0d7dfa457e1e87cb311a12b6800aa5ed9971c; this promoted-image800-case receipt is a fresh separate validation, not a copy of that result.

## SDK inference advanced by actual source compilation

The earlier [v2.20 source](https://github.com/Infineon/emeeprom/blob/0eeaba0dd7364dfa6badb48fe5d6692309a949e5/cy_em_eeprom.c) is a behavioral comparator but uses direct memory copies. A bounded pinned-release check finds block-storage use in2.40/2.50, but their context lacks sector-size field+4. [v2.60 header](https://github.com/Infineon/emeeprom/blob/6cacf37b5cfec2dc9acf1a2c222c1e3038d03bd9/include/cy_em_eeprom.h) supplies the matching32-byte ABI: sector/erase size+4,logical capacity+8,provider+28. The real block-storage1.2.1 header compiles to48-byte provider with read+20(slot5),is-erase-required+44(slot11). See sdk-abi-results.json. This corrects the genericstep interpretation of context+4; the canonical layout calls itsector_bytes. Installed stock get-program-size0x4784 andget-erase-size0x4788 both return128, statically grounding the physical/sector equality used by this module. Actual capacity/wear/last-row configuration is still not captured live.

Unmodified [v2.60 source](https://github.com/Infineon/emeeprom/blob/6cacf37b5cfec2dc9acf1a2c222c1e3038d03bd9/source/cy_em_eeprom.c), GNU13.3.1 Cortex-M0+ Thumb-Og short-enum build, reproduces13 selected stockfunctions totaling1476compiledbytes including literal words after linking at recovered addresses. **No relocation masking**: resolvedBLbytes are compared too. v2.70 andv2.70.1 reproduce the same selected1476bytes, so producerrevision is notunique. Source/license cached only in/tmp; no vendor source body exported into this independent module.

Exact selectedfunctions: ReadSimpleMode36;WriteRow100;CalculateRowChecksum12;GetStoredRowChecksum4;CheckRowChecksum36;GetStoredSeqNum4;DefineLastWrittenRow180;CheckLastWrittenRowIntegrity180;GetNextRowPointer30;GetReadRowPointer34;CopyHistoricData180;ReadExtendedMode628;Cy_Em_EEPROM_Read52. SDK names and mapped addresses/hashes are in sdk-exact-results.json.

The60-byte SDKCalcChecksum differs in branch layout; **515** no-cut SDK/original instruction comparisons match outcomes for bounded buffers0..128. It is not admitted as exactcompiledbytes. Preliminary CopyHeadersData also differs in compiledlayout and is not admitted as exactSDKsource. Our independently reconstructed history merge remains validated by the1148/1728/800 native suites. The SDK link assigns external address contracts for stock division/divmod/memset; their source is not part of this1476-byte attribution. Compilation supplied only missingcy_israddress prototype from the existing system shim, no executable stand-in. This is selected-body provenance, not a complete source-builtimage or unique toolchain proof.

## App implications and remaining boundary

Accepted command7ACK070017 and deferredstatuszero cannot certify durable storage. Stock row adapters discard flashdrivererrors. RAM queries6/8 do not test persistent readback. Readback can reportzero status on zero-initialized storage even when a synthetic failedwrite leaves requestedconfig absent. These constructed fixtures are not physical failure rates, ACK delivery evidence or a demonstrated hardware fault.

The next actionable static dependency is EEPROM initialization0x898c/8a38 and its app wrapper: recover actual programmed configuration/defaults and validate against the stronger block-storage SDK candidates. Subrow sector-size>row-size write wrapping remains explicitly unimplemented/unexercised in this module. Capture of actualEEPROMcontents and residentSROM behavior/physicaltrace is needed for hardware durability/timing conclusions; no externalinput is needed to continue bounded initializer/source analysis. No source-complete, wholeOTAbyte-equality, productionreplacement, scheduling/drain or flashsafe claim.
