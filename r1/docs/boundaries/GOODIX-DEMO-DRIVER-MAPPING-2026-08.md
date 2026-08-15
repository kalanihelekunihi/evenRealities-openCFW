# Goodix GH3X2X demo/driver per-entry mapping (2026-08)

Per-entry mapping pass recommended by
[`goodix_gh3x2x_candidate-ATTRIBUTION-2026-08.md`](goodix_gh3x2x_candidate-ATTRIBUTION-2026-08.md).
Scope: all 499 `goodix_gh3x2x_candidate` ledger entries from `r1/docs/reference/FUNCTION-OWNERSHIP.csv`
(including the 8 anchors the ledger has already flipped to `goodix_gh3x2x_democode_v1_6_drvlib_v4_3_0_0`).
No ledger CSVs, generator scripts, source code, or other docs were modified by this pass.

## Upstream snapshot

- Repository: `github.com/coredevices/pebbleos-nonfree`, sparse path `gh3x2x/`
- Cloned commit: **`2c0034a23b675a5f9a29e4a47e8b504c7a88e321`** (depth-1, blob-filtered clone, 2026-08-14)
- Tree: Goodix GH3X2X democode v1.6 / algo-call v0.5 / DrvLib v4.3.0.0 / Virtual_Reg v3.4 /
  config `gh3x2x-v2.23_7ecd2a` (marker equality with R1 firmware established in the attribution report)

## License review evidence — `gh3x2x/LICENSE` clauses 4 and 5, verbatim

> 4. This software, with or without modification, must only be used with a Goodix
> integrated circuit.
>
> 5. Any software provided in binary form under this license must not be reverse
> engineered, decompiled, modified and/or disassembled.

Clause 4 is satisfied in context (the R1 ring contains the GH3x2x IC). Clause 5 keeps the
binary-only algorithm libraries (S1) and the `goodix_mem`/`GdMem` allocator (S2) blocked:
they ship as `.a` archives even in the public mirror, so no source-form redistribution
permission attaches to them.

## Method

Match standard (unchanged from the attribution report): control-flow structure + constants +
log-string topology, not byte identity. Evidence sources: `decompiler-output.c` (FUN_<addr>
bodies), `disassembly.s`, `call-graph.csv`, and strings recovered from
`rebuilt-application.bin` (load base 0x27000). The eight previously proven matches served as
anchors; matches were extended along call-graph adjacency (callee identity at known bl sites,
verified against the upstream callee sequence of each anchor). Firmware log strings carry an
R1 `[LOG_x] ` wrapper prefix that was stripped before comparison; several bodies also
reference upstream `__FUNCTION__` name strings (e.g. "Gh3x2xDemoInterruptProcess",
"GH3x2xSlotTimeInfo"), giving near-certain identification for those entries. S1/S2
classifications rely on the existing boundary docs (their per-entry pins are recorded in the
ledger evidence column) and were not re-proven here. Entries marked "(moderate)" in the
evidence column rest on call-position + accessor shape rather than a unique string/constant
signature.

## Summary counts

| Class | Entries | Meaning |
| --- | ---: | --- |
| MATCHED | 97 | address → upstream file:function in `gh3x2x/demo_code/` (per-entry evidence below) |
| S1 | 240 | closed algorithm libraries (NADT / SPO2+dlCom+neural / HR / HRV / packed-word integrity) — binary-only upstream, license clause 5, stay blocked |
| S2 | 47 | `goodix_mem`/`GdMem` allocator internals (12) + heap call-site glue (20) + heap-dependent alloc/teardown helpers (15) — stay blocked |
| UNRESOLVED | 115 | frozen-closure residue, non-unique stubs/thunks, generic helpers, candidates without a unique upstream body — stay gated |
| **Total** | **499** | |

Reconciliation with the attribution report (estimates S1 241 / S2 47 / S3+S4 ~51 / residue 160,
"±a few entries"): this pass maps 97 entries function-level — the ~51 estimated S3/S4 layer
members plus 46 more recovered from the frozen-closure residue (mostly the driver-layer
rawdata/frame pipeline: GetFrameNum/CalGsensorStep/CreatTagArray/HandleFrameData/
GetFrameDataAndProcess/FunctionProcess, and the virtual-reg config write path:
WriteVirtualReg/WriteSwConfigWithVirtualReg/WriteFunctionConfigWithVirtualReg/
WriteChnlMapConfigWithVirtualReg/GhGetFunctionIdViaVirReg and helpers). S1 counts 240 here;
the one-entry delta vs 241 is the packed-24-bit/integrity-helper edge the attribution report
flagged as approximate. S2 is unchanged at 47.

## Full 499-entry disposition table

| Entry | Size | Ledger name | Disposition | Evidence |
| --- | ---: | --- | --- | --- |
| `0x00028ad4` | 62 | `FUN_00028ad4` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00028b18` | 114 | `FUN_00028b18` | S1 attribution; source-admitted | owner-authorized second-order difference-equation output with typed standard-round provider; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md |
| `0x00028cf4` | 200 | `FUN_00028cf4` | S1 attribution; source-admitted | owner-authorized double-precision 60-sample mean, 59:1 smoothing, and periodic rate-scaled emission |
| `0x00028dda` | 164 | `FUN_00028dda` | S1 attribution; source-admitted | owner-authorized raw Float32-to-packed-6/9 selector head and shared tail; pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00028de0` | 6 | `FUN_00028de0` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00028de6` | 106 | `FUN_00028de6` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00028dec` | 40 | `FUN_00028dec` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00028e14` | 66 | `FUN_00028e14` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00028e5c` | 20 | `FUN_00028e5c` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-PACKED-WORD-INTEGRITY-BOUNDARY.md |
| `0x00028e70` | 54 | `FUN_00028e70` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-PACKED-WORD-INTEGRITY-BOUNDARY.md |
| `0x00028eac` | 20 | `FUN_00028eac` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x00028ec0` | 10 | `FUN_00028ec0` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x0002907c` | 18 | `FUN_0002907c` | S1 attribution; source-admitted | owner-authorized seven-word NADT graph-executor veneer with explicit provider binding; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00029090` | 40 | `FUN_00029090` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md |
| `0x000290bc` | 32 | `FUN_000290bc` | S1 attribution; source-admitted | owner-authorized NADT summary builder and typed five-word downstream dispatch; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x000290dc` | 34 | `FUN_000290dc` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00029144` | 520 | `goodix_primitives_nadt_dual_window_features_extract` | source-admitted | owner-authorized fixed-125 dual-window autocorrelation, peak features, exact packed-5/10 quantization, and normalized correlation with caller workspace; no opaque bytes retained |
| `0x00029394` | 96 | `FUN_00029394` | S1 attribution; source-admitted | owner-authorized row-range normalization with exact threshold; pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x000294bc` | 54 | `FUN_000294bc` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-PACKED-WORD-INTEGRITY-BOUNDARY.md |
| `0x000294f8` | 20 | `FUN_000294f8` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-PACKED-WORD-INTEGRITY-BOUNDARY.md |
| `0x0002950c` | 14 | `FUN_0002950c` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-PACKED-WORD-INTEGRITY-BOUNDARY.md |
| `0x0002951a` | 196 | `FUN_0002951a` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x0002963a` | 28 | `FUN_0002963a` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x00029656` | 22 | `FUN_00029656` | S1 attribution; source-admitted | owner-authorized checked buffer-mean wrapper; pinned behavior remains in GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md |
| `0x000299ec` | 176 | `FUN_000299ec` | S1 attribution; source-admitted | owner-authorized six-float interval/state merge; pinned by GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md |
| `0x00029aa0` | 56 | `FUN_00029aa0` | S1 attribution; source-admitted | owner-authorized packed-mask column reduction; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00029ad8` | 340 | `goodix_primitives_spo2_report_state_update` | source-admitted | owner-authorized report reset/provider seam, 512-byte history shift, candidate gate, and three-phase event latch; no opaque bytes retained |
| `0x00029bbc` | 184 | `FUN_00029bbc` | UNRESOLVED (stays gated) | frozen-closure residue: Goodix 0x10-stride per-record teardown loop |
| `0x00029c74` | 30 | `FUN_00029c74` | UNRESOLVED (stays gated) | frozen-closure residue: copy 0x1c (7-entry) jump table to stack and call table[*param](param); Goodix-region s |
| `0x00029c98` | 40 | `FUN_00029c98` | UNRESOLVED (stays gated) | frozen-closure residue: Median-of-three selector; callers are gated Goodix scopes |
| `0x00029cc0` | 58 | `FUN_00029cc0` | UNRESOLVED (stays gated) | frozen-closure residue: Provider session-state reset over shared GH3X2X state at 0x20007A58; caller is the gat |
| `0x00029cdc` | 46 | `FUN_00029cdc` | UNRESOLVED (stays gated) | frozen-closure residue: Provider mode toggle between two gated Goodix register paths; caller is gated Goodix 0 |
| `0x00029d0a` | 42 | `FUN_00029d0a` | UNRESOLVED (stays gated) | frozen-closure residue: Provider min/max window tracker with saturation; callers are gated Goodix scopes |
| `0x00029d34` | 22 | `FUN_00029d34` | UNRESOLVED (stays gated) | frozen-closure residue: select fixed-point constant pair (0xf33333/0xecCCcd, 0xa66666/0xc00000) by flag; exclu |
| `0x00029d58` | 4 | `thunk_FUN_0002b91c` | UNRESOLVED (stays gated) | frozen-closure residue: Exact four-byte B.W thunk into the frozen Goodix GH3X2X provider component. The branch |
| `0x00029d5c` | 300 | `FUN_00029d5c` | UNRESOLVED (stays gated) | frozen-closure residue: Goodix GH3X2X channel decimation and rolling-window update |
| `0x00029e8c` | 190 | `FUN_00029e8c` | UNRESOLVED (stays gated) | frozen-closure residue: Goodix 20-channel masked callback dispatch with per-channel state records |
| `0x00029f88` | 20 | `FUN_00029f88` | UNRESOLVED (stays gated) | frozen-closure residue: record init: zero 2 bytes, fill 0x20 bytes with 0xff from +3; Goodix-region, callers 0 |
| `0x00029f9c` | 96 | `FUN_00029f9c` | MATCHED → kernel/gh_demo.c:Gh3x2xDemoStopAlgoInner | GH3X2X_AlgoDeinit inlined: frame-info null check, started-bitmap &= ~mode, 20-func loop calling deinit cb at +8 of 0xC-stride record, clears init-flag byte |
| `0x0002a090` | 70 | `FUN_0002a090` | MATCHED → demo_algo_code/goodix_algo_application/src/gh3x2x_demo_algo_memory.c:GH3X2X_AlgoMemConfig | param==0→-5=RESOURCE_ERROR; AlgoDeinit(0xFFFFFFFF)=0x29F9C; store size; AlgoMemInit inlined: status gate + goodix_mem_init=0x6DFD6 edge (per heap doc) — exact |
| `0x0002a0f4` | 110 | `FUN_0002a0f4` | MATCHED → demo_algo_code/goodix_algo_application/src/gh3x2x_demo_algo_call.c:GH3X2X_AlgoVersion | "no_ver" default literal; switch(funcID): case6→SpO2 builder 0x6EC90, HR 0x6D424, HRV 0x6DF60, NADT 0x6E788; memcpy out |
| `0x0002a168` | 48 | `FUN_0002a168` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002a198` | 52 | `FUN_0002a198` | MATCHED → driver/src/gh_drv_config.c:GH3X2X_CheckChipModel | ReadReg(0x0724=EFUSE_CTRL_EFUSE1_AUTOLOAD_0); if ((val>>5)&7)==1: loop 8 slots WriteRegBitField(0x010A=SLOT0_CTRL_0 + 0x1C*n, 4,5, 0) — exact |
| `0x0002a1cc` | 42 | `FUN_0002a1cc` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002a1f8` | 8 | `FUN_0002a1f8` | MATCHED → driver/src/gh_drv_interface.c:GH3X2X_ClearDivZeroFlag | g_uchChipDivZeroFlag=0 byte clear; called by HandleFrameData at upstream position (platform entity macro empty in this build) |
| `0x0002a204` | 10 | `FUN_0002a204` | MATCHED → driver/src/gh_drv_control.c:GH3X2X_ClearSoftEvent | g_unSoftEvent &= ~param (word at state+0x1c) |
| `0x0002a214` | 82 | `FUN_0002a214` | MATCHED → driver/src/gh_drv_control.c:GH3X2X_CommunicateConfirm | 3 tries (=MAX_CNT); ReadReg(0x36)==0xAA55; read/invert-write/verify/restore on 0x1EC=RG_SLOT_TMR0; return 0 / -4=COMM_ERROR — exact |
| `0x0002a266` | 68 | `FUN_0002a266` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002a2ac` | 52 | `FUN_0002a2ac` | MATCHED → driver/src/gh_drv_interface.c:GH3X2X_DelayUs | if g_pDelayUsFunc null → busy loop, inner count 9 = GH3X2X_DELAY_ONE_US_CNT(9u); else call callback — exact |
| `0x0002a31c` | 6 | `FUN_0002a31c` | MATCHED → driver/src/gh_drv_dump.c:GH3X2X_DumpModeSet | g_usDumpMode = val (6-byte halfword store) |
| `0x0002a328` | 76 | `FUN_0002a328` | MATCHED → driver/src/gh_drv_control.c:GH3X2X_EnterLowPowerMode | CHIP_SLEEP macro: WriteReg(0x88=PMU_CTRL4,/3), SendCmd(0xC4)=DSLEEP, DelayUs(0x32), sleep-flag bit set — exact |
| `0x0002a380` | 166 | `FUN_0002a380` | MATCHED → driver/src/gh_drv_control.c:GH3X2X_ExitLowPowerMode | CHIP_WAKEUP + WAKE_UP_CONFIRM macro (gh_drv_control.h:71/80): SendCmd(0xC3), DelayUs(500), ReadReg(0x36)==0xAA55, "[GH3X2X_WakeUpConfirm] Chip wake up fail!!!" retry logs — exact |
| `0x0002a474` | 16 | `FUN_0002a474` | UNRESOLVED (stays gated) | frozen-closure residue: reset state record (0xff byte, zero +1/+0xe/+0x14); caller 0x29cc0 Goodix-region init |
| `0x0002a488` | 38 | `FUN_0002a488` | MATCHED → driver/src/gh_drv_control.c:GH3X2X_FifoWatermarkThrConfig | clamp [3=THR_MIN, 800=THR_MAX]; WriteReg(0x000A=FIFO_WATERLINE); cache at +0xE (same field StartSampling reads) — exact |
| `0x0002a4b4` | 76 | `FUN_0002a4b4` | MATCHED → driver/src/gh_drv_control.c:GH3X2X_FunctionStart | null gate; CalFunctionSlotBit; if started-bitmap==0 → StartSampling=0x2AD18 with -6 check; bitmap /= funcID; frame fields +0x30/+0x38 clear; Memset(result,0xFF,chnlNum) — exact |
| `0x0002a508` | 52 | `FUN_0002a508` | MATCHED → driver/src/gh_drv_control.c:GH3X2X_FunctionStop | null gate; CalFunctionSlotBit(0x2C248); started-bitmap &= ~funcID; AlgoRecordResult flag/bit clear; if bitmap==0 → StopSampling=0x2AD7C — exact |
| `0x0002a540` | 6 | `FUN_0002a540` | MATCHED → demo_algo_code/goodix_algo_application/src/gh3x2x_demo_algo_memory.c:GH3X2X_GetAlgoMemStatus | returns g_uchAlgoMemStatus byte; compared ==1=ALGO_MEM_INIT_OK by AlgoInit |
| `0x0002a54c` | 4 | `FUN_0002a54c` | UNRESOLVED (stays gated) | frozen-closure residue: return-0 stub inside contiguous Goodix-candidate stub cluster (0x2A540/0x2A550/0x2A55C |
| `0x0002a550` | 6 | `FUN_0002a550` | MATCHED → driver/src/gh_drv_control.c:GH3X2X_GetConfigFuncMode | returns word at 0x20007A58+0x18; first call of SamplingControl per upstream |
| `0x0002a55c` | 4 | `FUN_0002a55c` | MATCHED → kernel/gh_demo.c:GH3X2X_GetDemoVersion | returns "GH(M)3X2X_DEMO_v1.6_AC_v0.5(build:…)" string @0x2A560; prior-proven |
| `0x0002a598` | 4 | `FUN_0002a598` | MATCHED → driver/src/gh_drv_control.c:GH3X2X_GetDriverLibVersion | returns "v4.3.0.0 (build:…)" string @0x2A59C; prior-proven |
| `0x0002a5c4` | 6 | `FUN_0002a5c4` | MATCHED → driver/src/gh_drv_control.c:GH3X2X_GetGsensorEnableFlag | returns enable byte; SamplingControl call position matches upstream GetGsensorEnableFlag (moderate) |
| `0x0002a5d0` | 28 | `FUN_0002a5d0` | MATCHED → driver/src/gh_drv_control.c:GH3X2X_GetIrqStatus | ReadReg(0x508=INT_STR); WriteReg(0x508,val) clear; return val&0x7FFF=MSK_ALL_BIT — exact |
| `0x0002a5ec` | 22 | `FUN_0002a5ec` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002a604` | 6 | `FUN_0002a604` | MATCHED → driver/src/gh_drv_control.c:GH3X2X_GetSoftEvent | return g_unSoftEvent (same +0x1c word) |
| `0x0002a610` | 4 | `FUN_0002a610` | UNRESOLVED (stays gated) | frozen-closure residue: return-0 stub inside contiguous Goodix-candidate cluster (0x2A604/0x2A614/0x2A658) |
| `0x0002a614` | 4 | `FUN_0002a614` | MATCHED → driver/src/gh_drv_config.c:GH3X2X_GetVirtualRegVersion | returns "Gh3x2x_Virtual_Reg_v3.4" string @0x2A618 |
| `0x0002a630` | 36 | `FUN_0002a630` | UNRESOLVED (stays gated) | frozen-closure residue: One-time provider lane-table init over 0x20030204; caller is gated Goodix 0x0006D3C0 |
| `0x0002a658` | 2 | `FUN_0002a658` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002a65a` | 2 | `FUN_0002a65a` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002a65c` | 38 | `FUN_0002a65c` | UNRESOLVED (stays gated) | frozen-closure residue: Indirect provider op call with the 0xAAAA payload word over shared GH3X2X state RAM |
| `0x0002a754` | 152 | `FUN_0002a754` | MATCHED → driver/src/gh_drv_control.c:GH3X2X_Init | config-init→CommunicateConfirm→WriteReg(0x508,0x7FFF)→ReadReg(0x88)→LoadNewRegConfigArr 4-arg→WriteReg(0x700,…)→poll 0x718 bit0→ReadReg(0x712)→SetDrvEcode→init-hook; R1 adds reg-0x72/0x11 errata write; prior-proven |
| `0x0002a7f4` | 16 | `FUN_0002a7f4` | MATCHED → driver/src/gh_drv_config.c:GH3X2X_InitSensorParameters | clears 3 enable words; called by WriteVirtualReg END_FLAG arm at upstream position (moderate) |
| `0x0002a810` | 4 | `thunk_FUN_0002b6e0` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002a814` | 50 | `FUN_0002a814` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002a84c` | 320 | `FUN_0002a84c` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002a86c` | 62 | `FUN_0002a86c` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002a8dc` | 136 | `FUN_0002a8dc` | MATCHED → driver/src/gh_drv_config.c:GH3X2X_LoadNewRegConfigArr | 4-arg ABI (arr,len,chip=0,agc*); callee of proven Init; virtual-reg split at 0x3000+; prior-proven |
| `0x0002a968` | 54 | `FUN_0002a968` | MATCHED → driver/src/gh_drv_control.c:GH3X2X_Memcpy | null/src/size checks; (dst/src)&3==0 → word copy; byte tail — exact |
| `0x0002a99e` | 52 | `FUN_0002a99e` | MATCHED → driver/src/gh_drv_control.c:GH3X2X_Memset | null check; 4-aligned word-fill (b<<24/b<<16/b<<8/b) while size≥4; byte tail — exact |
| `0x0002a9d2` | 2 | `FUN_0002a9d2` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002a9d4` | 20 | `FUN_0002a9d4` | MATCHED → driver/src/gh_drv_dump.c:GH3X2X_ReadElectrodeWearDumpData | g_uchElectrodeWearStatus = ReadRegBitField(0x050C=INT_STR2,…) via 0x2AA98; InterruptProcess position (moderate: body commented out in public snapshot, declared in gh_drv_dump.h) |
| `0x0002a9ec` | 32 | `FUN_0002a9ec` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002aa10` | 90 | `FUN_0002aa10` | MATCHED → driver/src/gh_drv_control.c:GH3X2X_ReadFifodata | null→-2; clamp to g_usMaxNumReadFromFifo (ret 4=READ_FIFO_CONTINUE); range ≤0xC80; ReadFifo; GetRawdata hook; *lenOut=len — exact topology |
| `0x0002aa74` | 30 | `FUN_0002aa74` | MATCHED → driver/src/gh_drv_interface.c:GH3X2X_ReadReg | op non-null check, TryWakeUp(0x2AE08), call read op (ops+0x28) |
| `0x0002aa98` | 50 | `FUN_0002aa98` | MATCHED → driver/src/gh_drv_interface.c:GH3X2X_ReadRegBitField | mask ((1<<(msb-lsb+1))-1)<<lsb; TryWakeUp; read op; (val&mask)>>lsb — exact |
| `0x0002aad0` | 6 | `FUN_0002aad0` | MATCHED → driver/src/gh_drv_interface.c:GH3X2X_RegisterDelayUsCallback | single callback store at state+8; same slot called by DelayUs=0x2A2AC |
| `0x0002aadc` | 24 | `FUN_0002aadc` | MATCHED → driver/src/gh_drv_control.c:GH3X2X_RegisterHookFunc | stores 9 hook fn pointers into driver-state struct +0x20..+0x40 (init/start/stop/getrawdata/iostruct/reset-by-protocol/cfg-start/cfg-stop/write-alg-config) |
| `0x0002aaf8` | 54 | `FUN_0002aaf8` | MATCHED → driver/src/gh_drv_interface.c:GH3X2X_RegisterI2cOperationFunc | null checks + chip<4; stores 0x28/(sel<<1) I2C device id + 2 callbacks + 5 op pointers; returns -2/0; prior-proven |
| `0x0002aba4` | 54 | `FUN_0002aba4` | MATCHED → driver/src/gh_drv_control.c:GH3X2X_ResetHardAdt | ExitLowPowerMode; WriteRegBitField(0x408=ADT_WEARON_CR,0,0,0); WriteReg(0x508,0xC00=WEAR_ON/WEAR_OFF); WriteRegBitField(0x408,0,0,1); EnterLowPowerMode — exact sequence/constants |
| `0x0002abdc` | 12 | `FUN_0002abdc` | MATCHED → driver/src/gh_drv_interface.c:GH3X2X_SendCmd | calls registered send-cmd op (ops+0x20) if non-null |
| `0x0002abec` | 12 | `FUN_0002abec` | MATCHED → driver/src/gh_drv_control.c:GH3X2X_SensorPramInit | clears 3 enable bytes (+5/+6/+7 of 0x20007A58 state); called by DrvConfigInit path 0x29CC0 at upstream position (moderate) |
| `0x0002abfc` | 14 | `FUN_0002abfc` | MATCHED → driver/src/gh_drv_interface.c:GH3X2X_SetChipSleepFlag | g_uchGhx2xChipSleepFlag /= (1<<(idx&0xff)) byte OR at state+2; same byte TryWakeUp/EnterLowPowerMode use |
| `0x0002ac10` | 6 | `FUN_0002ac10` | MATCHED → driver/src/gh_drv_control.c:GH3X2X_SetConfigFuncMode | g_unConfigFuncMode = param (word at 0x20007A58+0x18; same field GetConfigFuncMode reads) |
| `0x0002ac1c` | 16 | `FUN_0002ac1c` | MATCHED → driver/src/gh_drv_control.c:GH3X2X_SetMaxNumWhenReadFifo | if val ≤ 0xC80=FIFO_DATA_BYTES_MAX_LEN: cache=(val&~3) at +0x12 — exact clamp/rounding |
| `0x0002ac30` | 10 | `FUN_0002ac30` | MATCHED → driver/src/gh_drv_control.c:GH3X2X_SetSoftEvent | g_unSoftEvent /= param (same +0x1c word) |
| `0x0002ac40` | 10 | `FUN_0002ac40` | MATCHED → driver/src/gh_drv_control.c:GH3X2X_SlotEnRegSet | WriteReg(0x0108=SLOT_ENABLE_CFG_REG_ADDR, val) — exact register |
| `0x0002ac4c` | 58 | `FUN_0002ac4c` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002ac8c` | 58 | `FUN_0002ac8c` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002accc` | 36 | `FUN_0002accc` | MATCHED → driver/src/gh_drv_control.c:GH3X2X_SoftReset | SendCmd(0xC2=GH3X2X_CMD_RESET) via CHIP_RESET macro; ActiveChipResetFlag(+10)=1; reset-from-protocol flag(+8) clear + hook at +0x40 — exact |
| `0x0002acf4` | 28 | `FUN_0002acf4` | UNRESOLVED (stays gated) | frozen-closure residue: one-time init: flag-gated call 0x29f88 then byte defaults at +1/+0xb/+0x13; exclusive  |
| `0x0002ad14` | 2 | `FUN_0002ad14` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002ad18` | 90 | `FUN_0002ad18` | MATCHED → driver/src/gh_drv_control.c:GH3X2X_StartSampling | status!=2 gate; FifoPackageID=0xFF; reg-0x72&0x11 errata gate (same errata as Init); waterline=ReadReg(0xA)→+0xE; ReadReg(0)/WriteReg(0,/1); status=2; start-hook(+0x24) — exact modulo errata |
| `0x0002ad7c` | 48 | `FUN_0002ad7c` | MATCHED → driver/src/gh_drv_control.c:GH3X2X_StopSampling | status(+9)==1//2 gate → set 1=INITED; ReadReg(0)/WriteReg(0,clear bit0=CARDIFF_CTRL START); stop-hook(+0x28) call; else -6=NO_INITED — exact |
| `0x0002adb0` | 30 | `FUN_0002adb0` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002add0` | 40 | `FUN_0002add0` | UNRESOLVED (stays gated) | frozen-closure residue: in-place 16-bit byte-pair swap (endianness fixup) of sample buffer; callerless, no poi |
| `0x0002ae00` | 4 | `FUN_0002ae00` | UNRESOLVED (stays gated) | frozen-closure residue: constant-1 provider stub; exclusive Goodix-candidate caller 0x6a4d8 |
| `0x0002ae04` | 2 | `FUN_0002ae04` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002ae06` | 2 | `FUN_0002ae06` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002ae08` | 26 | `FUN_0002ae08` | MATCHED → driver/src/gh_drv_interface.c:GH3X2X_TryWakeUp | tests sleep-flag bit, clears it, calls ExitLowPowerMode=0x2A380 — exact |
| `0x0002ae28` | 48 | `FUN_0002ae28` | MATCHED → driver/src/gh_drv_dump.c:GH3X2X_UpdateAgcInfo | 3 Memcpys: TiaGainRecord⇐AfterSoftAgc (0x20), DrvCurrent (0x10), DcCancel (0x40) within AGC info struct — exact sizes/topology; InterruptProcess position |
| `0x0002aedc` | 178 | `FUN_0002aedc` | UNRESOLVED (stays gated) | frozen-closure residue: Goodix 0x3000-windowed register write dispatcher |
| `0x0002af32` | 80 | `FUN_0002af32` | UNRESOLVED (stays gated) | frozen-closure residue: Goodix packed half-word lane update inside the 0x3000-windowed register-write path (ca |
| `0x0002af84` | 108 | `FUN_0002af84` | MATCHED → driver/src/gh_drv_config.c:GH3X2X_WriteChnlMapConfigWithVirtualReg | addr&0xFFF; %0x22==0 → SetFunctionChnlNum(fi[addr/0x22],loByte) via 0x2CCD0; else idx=(%0x22)-2 <0x20=CHANNEL_MAP_MAX_CH → SetFunctionChnlMap(fi,idx+1,hi)+(fi,idx,lo) via 0x2CCC0 — exact |
| `0x0002b010` | 76 | `FUN_0002b010` | MATCHED → driver/src/gh_drv_config.c:GH3X2X_WriteFunctionConfigWithVirtualReg | funcID=(addr-0x3000)/0x300; alg-cfg window [0x30C0+id*0x300, 0x3300+id*0x300) → WriteAlgConfig hook call — exact window constants |
| `0x0002b0b8` | 32 | `FUN_0002b0b8` | MATCHED → driver/src/gh_drv_interface.c:GH3X2X_WriteReg | op non-null check, TryWakeUp, call write op (ops+0x24) with (addr,val) |
| `0x0002b0dc` | 72 | `FUN_0002b0dc` | MATCHED → driver/src/gh_drv_interface.c:GH3X2X_WriteRegBitField | same mask; read op + modify + write op (read-modify-write) — exact |
| `0x0002b148` | 52 | `FUN_0002b148` | MATCHED → driver/src/gh_drv_config.c:GH3X2X_WriteSwConfigWithVirtualReg | loop 7 entries of 8-byte module-info records (addrStart/addrEnd/ParmSet): in-range → call ParmSet(addr,val) — exact table-driven dispatch |
| `0x0002b180` | 122 | `FUN_0002b180` | MATCHED → driver/src/gh_drv_config.c:GH3X2X_WriteVirtualReg | addr<0x3000→SwConfigWrite(0x2B148); 0x3000≤addr<0xFF00→FunctionConfigWrite(0x2B010); case 0x1000=END_FLAG: GhDrvConfigManagerInit(0x2EDEC)+hook+flag=1+InitSensorParameters(0x2A7F4)+SetConfigFuncMode(0x2AC10)+GhGetFunctionIdViaVirReg(0x2EDFC) — exact |
| `0x0002b218` | 448 | `FUN_0002b218` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002b4c4` | 14 | `FUN_0002b4c4` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002b4d8` | 4 | `FUN_0002b4d8` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002b4f8` | 42 | `FUN_0002b4f8` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002b524` | 378 | `FUN_0002b524` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002b6a4` | 58 | `FUN_0002b6a4` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002b6e0` | 514 | `FUN_0002b6e0` | UNRESOLVED (stays gated) | frozen-closure residue: private GH3X2X eight-channel register-profile decoder |
| `0x0002b8ec` | 42 | `FUN_0002b8ec` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002b91c` | 120 | `FUN_0002b91c` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002b998` | 666 | `FUN_0002b998` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002bd84` | 152 | `FUN_0002bd84` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002be24` | 388 | `FUN_0002be24` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002bfaa` | 412 | `FUN_0002bfaa` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002c148` | 48 | `FUN_0002c148` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002c178` | 202 | `FUN_0002c178` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002c248` | 52 | `FUN_0002c248` | MATCHED → driver/src/gh_drv_control.c:GH3x2xCalFunctionSlotBit | loop chnlNum(+8): if unChnlEnForUserSetting(+4) bit → slotBit /= 1<<(chnlMap[i]>>5); store at +9 — exact |
| `0x0002c27c` | 34 | `FUN_0002c27c` | MATCHED → driver/src/gh_drv_control.c:GH3x2xCalGsensorStep | float step = (float)num/(float)frames with zero guards; called 3× (gs/cap/temp) by FunctionProcess — exact |
| `0x0002c2a4` | 72 | `FUN_0002c2a4` | MATCHED → driver/src/gh_drv_control.c:GH3x2xCreatTagArray | builds 32-byte tag array + complete mask from channel map; called by GetFrameNum and GetFrameDataAndProcess at upstream positions |
| `0x0002c2ec` | 222 | `FUN_0002c2ec` | MATCHED → kernel/gh_demo.c:Gh3x2xDemoSearchCfgListByFunc | 2 exact cfg-search log strings; calls 0x2A266 config-array function-support scan; called by StartSamplingInner at matching bl site |
| `0x0002c43c` | 132 | `FUN_0002c43c` | MATCHED → driver/src/gh_drv_control.c:GH3x2xFunctionProcess | callees CheckRawdataBuf(0x2A1CC)/GetFrameNum(0x2C640)/CalGsensorStep×3(0x2C27C)/GetFrameDataAndProcess(0x2C4FC) — upstream call topology exact |
| `0x0002c4c0` | 30 | `FUN_0002c4c0` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002c4e4` | 24 | `FUN_0002c4e4` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002c4fc` | 320 | `FUN_0002c4fc` | MATCHED → driver/src/gh_drv_control.c:GH3x2xGetFrameDataAndProcess | CreatTagArray(0x2C2A4) + HandleFrameData(0x2C694) callees; called by FunctionProcess tail — exact |
| `0x0002c640` | 82 | `FUN_0002c640` | MATCHED → driver/src/gh_drv_control.c:GH3x2xGetFrameNum | incomplete-mask from **(fi+0x30); CreatTagArray(0x2C2A4) 32-byte tags; loop bytes: tag=byte>>3, mask/=1<<tagArray[tag], frame++ when complete — exact |
| `0x0002c694` | 650 | `FUN_0002c694` | MATCHED → driver/src/gh_drv_control.c:GH3x2xHandleFrameData | 3× Memset + ClearDivZeroFlag(0x2A1F8) + SetFrameFlag2(0x2EB0C) callees match upstream call list |
| `0x0002c930` | 18 | `FUN_0002c930` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002c944` | 342 | `FUN_0002c944` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002caa4` | 34 | `FUN_0002caa4` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002cac6` | 18 | `FUN_0002cac6` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-HRV-PROVIDER-BOUNDARY.md |
| `0x0002cad8` | 376 | `FUN_0002cad8` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002cc5c` | 46 | `FUN_0002cc5c` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-HRV-PROVIDER-BOUNDARY.md |
| `0x0002cc94` | 38 | `FUN_0002cc94` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002ccc0` | 16 | `FUN_0002ccc0` | MATCHED → driver/src/gh_drv_control.c:GH3x2xSetFunctionChnlMap | fi null && chnlId < limit(byte +0xC) → pchChnlMap(+0x10)[id] = tag — exact |
| `0x0002ccd0` | 32 | `FUN_0002ccd0` | MATCHED → driver/src/gh_drv_control.c:GH3x2xSetFunctionChnlNum | fi null gate; clamp to uchFuntionChnlLimit(fi[3] byte); store uchChnlNum at fi[1]+8; if >0: g_unConfigFuncMode(+0x18) /= unFunctionID — exact |
| `0x0002ccf4` | 6 | `FUN_0002ccf4` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002cd00` | 132 | `FUN_0002cd00` | MATCHED → kernel/gh_demo.c:GH3x2xSlotTimeInfo | exact string "[%s]:CfgIndex[%d]:Slot time = %d" + __FUNCTION__ "GH3x2xSlotTimeInfo" ref |
| `0x0002cdd4` | 462 | `FUN_0002cdd4` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002cfe8` | 378 | `FUN_0002cfe8` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002d16c` | 22 | `FUN_0002d16c` | UNRESOLVED (stays gated) | frozen-closure residue: call Goodix-candidate 0x6ec28(**(param+4)) and map to 0/-1 result |
| `0x0002d184` | 410 | `FUN_0002d184` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002d324` | 22 | `FUN_0002d324` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002d33c` | 6 | `FUN_0002d33c` | MATCHED → driver/src/gh_drv_control.c:GH3x2x_GetActiveChipResetFlag | returns byte at state+10; same field SoftReset(0x2ACCC) sets to 1 |
| `0x0002d348` | 6 | `FUN_0002d348` | MATCHED → driver/src/gh_drv_control.c:GH3x2x_GetChipResetRecoveringFlag | returns flag byte at state+0xB; same field written by 0x2D3A8 |
| `0x0002d354` | 74 | `FUN_0002d354` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002d3a8` | 6 | `FUN_0002d3a8` | MATCHED → driver/src/gh_drv_control.c:GH3x2x_SetChipResetRecoveringFlag | writes flag byte at state+0xB |
| `0x0002d458` | 4 | `FUN_0002d458` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md |
| `0x0002d460` | 294 | `FUN_0002d460` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x0002d54c` | 116 | `FUN_0002d54c` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x0002d5c0` | 152 | `FUN_0002d5c0` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x0002d658` | 16 | `FUN_0002d658` | MATCHED → module/gh_soft_adt/gh_multi_sen_pro.c:GetNextEventPointer | returns &manager.pstMultiSensorWearEvent[*idx].uchNext = base + idx*0x10 + 0x18; null when idx==0 — exact |
| `0x0002d66c` | 2 | `FUN_0002d66c` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002d670` | 238 | `FUN_0002d670` | MATCHED → kernel/gh_demo.c:Gh3x2xDemoArrayCfgSwitch | exact strings "Current cfg is already cfg%d, no need switch.", "Error ! cfg%d switch fail !!!", "cfg%d switch success !!!."; callees SamplingControl/SoftReset/delay/Init/EnterLowPowerMode |
| `0x0002d824` | 78 | `FUN_0002d824` | MATCHED → kernel/gh_demo.c:Gh3x2xDemoFunctionProcess | loop 0x14: if frameInfo[i] && g_unDemoFuncMode(+0x24) bit i → GH3x2xFunctionProcess(0x2C43C) with 8 data args + fi — exact |
| `0x0002d87c` | 480 | `FUN_0002d87c` | MATCHED → kernel/gh_demo.c:Gh3x2xDemoInit | 6 exact log strings + __FUNCTION__ ref; callee set matches upstream (GetDemoVersion/GetDriverLibVersion/GetVirtualRegVersion/AlgoVersion/RegisterI2cOperationFunc/RegisterHookFunc/RegisterDelayUsCallback/SetChipSleepFlag/SoftReset/DrvConfigManagerInit/Init/StopSampling/GetConfigVersion/SetMaxNumWhenReadFifo/EnterLowPowerMode/WearEventManagerInit/TimerInit/MoveDetecterInit/FunctionInfoForUserInit); prior-proven |
| `0x0002db8c` | 958 | `FUN_0002db8c` | MATCHED → kernel/gh_demo.c:Gh3x2xDemoInterruptProcess | 11 exact log strings (recovery fail/success, "Got chip reset event !!!", "GetEvent Error!!!0x%x" x3) + __FUNCTION__ ref; callees GetSoftEvent/GetIrqStatus/ClearSoftEvent/ReadReg/ReadFifodata/SetSoftEvent/UpdateAgcInfo/WearEventHook/FifoRecovery all verified |
| `0x0002e0d0` | 454 | `FUN_0002e0d0` | MATCHED → kernel/gh_demo.c:Gh3x2xDemoSamplingControl | exact strings "Current g_unDemoFuncMode= 0x%x", "set particular watermark for ADT only. value = %d", "recover watermark. value = %d" + __FUNCTION__ ref; callee topology matches |
| `0x0002e340` | 24 | `FUN_0002e340` | MATCHED → kernel/gh_demo.c:Gh3x2xDemoStartAlgoInner | GH3X2X_AlgoInit inlined: GetChipResetRecoveringFlag gate, frame-info null check, started-bitmap /= mode, GetAlgoMemStatus(0x2A540)==1 gate, 20-func init-cb loop |
| `0x0002e358` | 144 | `FUN_0002e358` | MATCHED → kernel/gh_demo.c:Gh3x2xDemoStartSampling | tail calls StartSamplingInner(mode,0)=0x2E36C then StartAlgoInner=0x2E340; prior-proven |
| `0x0002e36c` | 418 | `FUN_0002e36c` | MATCHED → kernel/gh_demo.c:Gh3x2xDemoStartSamplingInner | 7 exact log strings incl "[Gh3x2xDemoStartSampling] unFuncMode = 0x%x" and "Cfg Error:Reg cfg file not exist!!!APP mode:0x%x"+while(1); callee order matches upstream; prior-proven |
| `0x0002e61c` | 76 | `FUN_0002e61c` | MATCHED → kernel/gh_demo.c:Gh3x2xDemoStartSamplingWithCfgSwitch | __FUNCTION__ ref + "[%s]:Array None!!!"; then ArrayCfgSwitch(0x2D670)/StartAlgoInner/StartSamplingInner(mode,1) |
| `0x0002e6a8` | 42 | `FUN_0002e6a8` | MATCHED → kernel/gh_demo.c:Gh3x2xDemoStopSampling | calls StopSamplingInner=0x2E6BC then if GetChipResetRecoveringFlag(0x2D348)==0 → StopAlgoInner=0x29F9C; upstream topology exact |
| `0x0002e6bc` | 60 | `FUN_0002e6bc` | MATCHED → kernel/gh_demo.c:Gh3x2xDemoStopSamplingInner | exact log "[Gh3x2xDemoStopSampling] unFuncMode = 0x%x"; calls SamplingControl(mode,STOP=1) |
| `0x0002e734` | 18 | `FUN_0002e734` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002e746` | 48 | `FUN_0002e746` | MATCHED → driver/src/gh_drv_control.c:Gh3x2xFifoRecovery | ReadRegBitField(0,0,0); WriteRegBitField(0,0,0,0); BspDelayMs(10); WriteRegBitField(0,0,0,bak) — exact |
| `0x0002e778` | 40 | `FUN_0002e778` | MATCHED → driver/src/gh_drv_control.c:Gh3x2xFunctionInfoForUserInit | loop 0x14: if frameInfo[i]: usSampleRateForUserSetting(+2 halfword)=0; unChnlEnForUserSetting(+4 word)=0xFFFFFFFF — exact |
| `0x0002e7a4` | 28 | `FUN_0002e7a4` | MATCHED → kernel/gh_demo.c:Gh3x2xFunctionSlotBitInit | loop 0x14=FUNC_OFFSET_MAX: if frameInfo[i] → CalFunctionSlotBit(0x2C248) — exact |
| `0x0002e7c4` | 174 | `FUN_0002e7c4` | MATCHED → kernel/gh_demo.c:Gh3x2xGetConfigVersion | exact strings "%s : Config Version : %x", "%s : No Config Version !!!" + __FUNCTION__ ref; walks cfg arr for timestamp regs |
| `0x0002e8c4` | 4 | `FUN_0002e8c4` | UNRESOLVED (stays gated) | frozen-closure residue: constant-4 provider stub; exclusive Goodix-candidate caller 0x6d3c0 |
| `0x0002e8c8` | 4 | `FUN_0002e8c8` | UNRESOLVED (stays gated) | frozen-closure residue: constant-1 provider stub; exclusive Goodix-candidate caller 0x6ec28 |
| `0x0002e8cc` | 28 | `FUN_0002e8cc` | owner-authorized; source-admitted | exact ordered `WriteReg(0x502,0)` then `WriteRegBitField(0,10,10,0)` wrapper over explicit typed bindings |
| `0x0002e8e8` | 94 | `FUN_0002e8e8` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002e950` | 2 | `FUN_0002e950` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002e964` | 374 | `FUN_0002e964` | MATCHED → kernel/gh_demo.c:Gh3x2xSetCurrentSlotEnReg | exact log "Current uchSlotEn= 0x%x"; ReadReg/WriteReg/WriteRegBitField + SlotEnRegSet(0x2AC40) per upstream |
| `0x0002eb0c` | 36 | `FUN_0002eb0c` | MATCHED → kernel/gh_demo.c:Gh3x2xSetFrameFlag2 | if *punFrameCnt==0 → frameFlag[2] /= 0x02; if electrode-wear status byte → /= 0x04 — exact; called by HandleFrameData |
| `0x0002eb4e` | 50 | `FUN_0002eb4e` | MATCHED → kernel/gh_demo.c:Gh3x2x_NormalizeGsensorSensitivity | loop over 6-byte (x,y,z) halfword records per gsensor point; InterruptProcess call position matches (moderate: decompiled body shows degenerate self-assigns, shift count likely 0) |
| `0x0002eb80` | 2 | `FUN_0002eb80` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002eb84` | 444 | `FUN_0002eb84` | MATCHED → kernel/gh_demo_hook.c:Gh3x2x_WearEventHook | exact strings "Wear off, no living-object!!!" / "Wear off, no object!!!" / "Wear on, living-object!!!" / "Wear on, object !!!"; GhMultSensorWearEventSend inlined ("[MultiSensor] new event received, Evt = 0x%x." + GetCurTs/GetNextEventPointer/PrintAllEvt callees) |
| `0x0002ed98` | 100 | `FUN_0002ed98` | MATCHED → driver/src/gh_drv_control.c:GH3X2X_ReinitAllSwModuleParam | 0x100A=REINIT_PARAM_ADDR gate + val!=0; 7× SetFunctionChnlNum(fi[HR..ADT],0) via 0x2CCD0; AGC-reset call 0x2A86C; DumpModeSet(0) via 0x2A31C — exact topology (WriteSwConfigWithVirtualReg 0x100A arm) |
| `0x0002edaa` | 14 | `FUN_0002edaa` | MATCHED → driver/src/gh_drv_config.c:GH3X2X_WriteSwConfigWithVirtualReg | 0x1100=PPG_DUMP_MODE_ADDR arm: DumpModeSet(val) via 0x2A31C (outlined switch arm) |
| `0x0002ede0` | 6 | `FUN_0002ede0` | UNRESOLVED (stays gated) | frozen-closure residue: Entry belongs to the frozen direct-call-graph component anchored by exact Goodix GH3X2 |
| `0x0002edec` | 10 | `FUN_0002edec` | MATCHED → driver/src/gh_drv_config.c:GhDrvConfigManagerInit | Memset(g_stGhDrvConfigManger,0,8); called by DemoInit directly before GH3X2X_Init and by WriteVirtualReg END_FLAG arm — exact positions |
| `0x0002edfc` | 44 | `FUN_0002edfc` | MATCHED → driver/src/gh_drv_config.c:GhGetFunctionIdViaVirReg | (addr-0x2000)<0x880 && %0x22==0 && data!=0 → 1<<((addr-0x2000)/0x22) — exact constants (CHNLMAP_OFFSET=0x22) |
| `0x0002ee28` | 10 | `FUN_0002ee28` | MATCHED → module/gh_soft_adt/gh_multi_sen_pro.c:GhMultiSensorTimerInit | Memset(g_stGhMultiSensorTimer,0,0x10) |
| `0x0002ee38` | 6 | `FUN_0002ee38` | MATCHED → module/gh_soft_adt/gh_multi_sen_pro.c:GhGsMoveDetecterIsEnable | returns uchMoveDetEnable byte; called by InterruptProcess at upstream position |
| `0x0002ee44` | 8 | `FUN_0002ee44` | MATCHED → module/gh_soft_adt/gh_multi_sen_pro.c:GhMultSensorWearEventManagerGetCurTs | returns GU64 timestamp at manager+8 (8-byte return distinctive) |
| `0x0002ee50` | 36 | `FUN_0002ee50` | MATCHED → module/gh_soft_adt/gh_multi_sen_pro.c:GhMultSensorWearEventManagerInit | Memset(manager,0,0x58); uchHead(+1)=0xFF=LL_INDEX_INVALID; loop 4 events stride 0x10 set uchNext(+0x18)=0xFF — exact |
| `0x0002ef6c` | 210 | `FUN_0002ef6c` | MATCHED → module/gh_soft_adt/gh_multi_sen_pro.c:GhMultiSensorPrintAllEvt | exact strings "[MultiSensor] print events start…", "EvtPosi = %d, Evt = 0x%x, Ts = %llu.", "print events end, uchEvtNum = %d."; calls GetNextEventPointer=0x2D658 |
| `0x0002f0f8` | 10 | `FUN_0002f0f8` | MATCHED → module/gh_soft_adt/gh_multi_sen_pro.c:GhGsMoveDetecterInit | Memset(g_stGhGsMoveDetecter,0,0xC) |
| `0x0002f224` | 56 | `FUN_0002f224` | S1 attribution; source-admitted | owner-authorized sample variance; pinned behavior remains in GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md |
| `0x0002f260` | 74 | `FUN_0002f260` | S1 attribution; source-admitted | owner-authorized counted UInt32 history with oldest-value eviction; pinned by GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md |
| `0x0002f2f8` | 378 | `FUN_0002f2f8` | S1 attribution; source-admitted | owner-authorized positive indexed-difference mean/relative-variance summarizer with terminal recovery; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x0002f624` | 52 | `FUN_0002f624` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x0002f65c` | 4 | `thunk_FUN_00036bfa` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x0002f660` | 354 | `FUN_0002f660` | S1 attribution; source-admitted | owner-authorized dual-feature update with explicit ratio windows and bounded half-scale sample conversion; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x0002f7dc` | 138 | `FUN_0002f7dc` | S1 attribution; source-admitted | owner-authorized three-stage Float32 tensor projection with fixed `0x1F0` middle bank; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x0002fee2` | 114 | `FUN_0002fee2` | S1 attribution; source-admitted | owner-authorized rolling-feature/pair-average composition including the shared `0x0002f2ac` cadence tail; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x0002ff10` | 338 | `goodix_primitives_spo2_spectral_peak_concentration_db` | source-admitted | owner-authorized strict spectral-peak, optional second-harmonic window, energy concentration, and typed log10 reconstruction; no opaque bytes retained |
| `0x0003007e` | 16 | `dlCom graph-builder table wrapper` | S1 attribution; source-admitted | owner-authorized direct veneer to the reconstructed complete generated executor; pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00030090` | 128 | `FUN_00030090` | S1 attribution; source-admitted | owner-authorized capped running triplet and explicit timestamp binding; pinned by GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md |
| `0x00030114` | 96 | `FUN_00030114` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00030178` | 494 | `FUN_00030178` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00030368` | 286 | `goodix_primitives_hr_weighted_feature_update` | source-admitted | owner-authorized clean-room five-history mean/center/weighted-feature pipeline with typed interpolation and four coefficient banks; no opaque bytes retained |
| `0x000304a0` | 54 | `FUN_000304a0` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x000305d8` | 50 | `FUN_000305d8` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x00030800` | 364 | `FUN_00030800` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00030970` | 108 | `FUN_00030970` | S1 attribution; source-admitted | owner-authorized signed-mask count with uniform-sign suppression and caller scratch; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00030b6c` | 300 | `goodix_primitives_nadt_window_filter_i32` | source-admitted | owner-authorized clean-room eleven-boundary plus uniform 23-tap reflected filter with typed matrix and caller scratch; no opaque bytes retained |
| `0x00030cd8` | 312 | `FUN_00030cd8` | S1 attribution; source-admitted | owner-authorized type-5 interpolated Float32 quantile over caller-owned sort scratch; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00030e1c` | 72 | `FUN_00030e1c` | S1 attribution; source-admitted | owner-authorized wrapping-age/strict-gate triplet snapshot copier; pinned by GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md |
| `0x0003113c` | 1240 | `FUN_0003113c` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00031624` | 192 | `FUN_00031624` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00031774` | 82 | `FUN_00031774` | S1 attribution; source-admitted | owner-authorized strict positive local-peak maximum selector; pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00031914` | 48 | `FUN_00031914` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00032744` | 86 | `FUN_00032744` | owner-authorized; source-admitted | typed channel scale/copy with explicit scale vector and factor replaces both private globals |
| `0x00032788` | 88 | `goodix_primitives_nadt_default_initialize` | source-admitted | owner-authorized clean-room default initializer wrapper; no opaque bytes retained |
| `0x00032808` | 2814 | `FUN_00032808` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md |
| `0x000335b4` | 522 | `goodix_primitives_spo2_channel_scale_decode` | source-admitted | owner-authorized direct/packed width decoding with three explicit scale-table spans and typed `pow`; no opaque bytes retained |
| `0x00033800` | 38 | `FUN_00033800` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x00034194` | 630 | `goodix_primitives_nadt_generated_subgraph_execute` | source-admitted | owner-authorized fixed 19-operator NADT quantized/Float32 subgraph with explicit range words, scalar descriptor, callbacks, and 0x7C0-byte workspace; no opaque bytes retained |
| `0x0003441c` | 116 | `FUN_0003441c` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00034490` | 106 | `FUN_00034490` | S1 attribution; source-admitted | owner-authorized grouped row-wise weighted-sum kernel; pinned by GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md |
| `0x00034500` | 1102 | `FUN_00034500` | S1 attribution; source-admitted | owner-authorized exact 36-byte SpO2 report analyzer with bounded spectra/history; pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x0003497c` | 180 | `FUN_0003497c` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00034a3c` | 28 | `FUN_00034a3c` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x00034a58` | 14 | `FUN_00034a58` | S1 attribution; source-admitted | owner-authorized sample-standard-deviation tail; pinned behavior remains in GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md |
| `0x00034a66` | 22 | `FUN_00034a66` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md |
| `0x00034aa0` | 98 | `FUN_00034aa0` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x00034b08` | 76 | `FUN_00034b08` | source-admitted | owner-authorized typed command/status poll (commands 0xA6/0xAE, bit 0x2000 selection, 0x140-tick timeout) |
| `0x00034b54` | 348 | `goodix_primitives_spo2_packed_channel_standard_deviations` | source-admitted | owner-authorized four-channel packed-6/9 population-deviation adapter with stride-three selection and caller-owned 60-float scratch; no opaque bytes retained |
| `0x00034cbc` | 956 | `goodix_primitives_hr_extrema_tracker_update` | source-admitted | owner-authorized full-buffer trough/peak state machine with explicit curves and caller-owned 41-point spline workspace; pinned by GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md |
| `0x00035084` | 84 | `FUN_00035084` | S1 attribution; source-admitted | owner-authorized Float32 round-to-nearest with exact halves away from zero; pinned by GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md |
| `0x00035772` | 48 | `FUN_00035772` | S1 attribution; source-admitted | owner-authorized caller-scratch copy/typed-transform/prefix-copy adapter; pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x000357a2` | 44 | `FUN_000357a2` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x000357ce` | 68 | `FUN_000357ce` | S1 attribution; source-admitted | owner-authorized channel/geometry wrapper with exact 125-sample and modulo-25 readiness status; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00035812` | 62 | `FUN_00035812` | S1 attribution; source-admitted | owner-authorized stable float insertion sort; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00035850` | 1162 | `FUN_00035850` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00035d6e` | 196 | `FUN_00035d6e` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00035f44` | 44 | `FUN_00035f44` | S1 attribution; source-admitted | owner-authorized signed decimal truncation; pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00035f70` | 192 | `FUN_00035f70` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00036034` | 394 | `goodix_primitives_nadt_sample_prepare` | source-admitted | owner-authorized three-lane direct/calibrated NADT preparation with explicit prior-configuration state and visible seven-level scale table |
| `0x000361d8` | 88 | `FUN_000361d8` | S1 attribution; source-admitted | owner-authorized capped squared deviation around rounded signed-32 mean; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00036230` | 12 | `FUN_00036230` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x0003623c` | 70 | `FUN_0003623c` | S1 attribution; source-admitted | owner-authorized indexed signed-16 trimmed mean with target-width wrapping; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00036282` | 52 | `FUN_00036282` | S1 attribution; source-admitted | owner-authorized one-record veneer to the admitted transition updater; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x000362b6` | 62 | `FUN_000362b6` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x00036394` | 110 | `FUN_00036394` | S1 attribution; source-admitted | owner-authorized target-width Int16 sample standard deviation; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00036408` | 364 | `FUN_00036408` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00036590` | 364 | `FUN_00036590` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00036718` | 26 | `FUN_00036718` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00036734` | 140 | `FUN_00036734` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x000367c4` | 230 | `goodix_primitives_spo2_dispatch_logistic_score` | source-admitted | owner-authorized clean-room transient-history dispatch and capped logistic score transform with explicit providers; no opaque bytes retained |
| `0x000368d0` | 160 | `FUN_000368d0` | S1 attribution; source-admitted | owner-authorized caller-scratch quartile-band median replacement; pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00036974` | 460 | `FUN_00036974` | S1 attribution; source-admitted | owner-authorized completed-record builder and sixteen-word live serializer; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00036b58` | 116 | `FUN_00036b58` | S1 attribution; source-admitted | owner-authorized default-range in-place Float32-to-Int8 quantizer wrapper; pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00036bd4` | 38 | `FUN_00036bd4` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00036bfa` | 44 | `FUN_00036bfa` | UNRESOLVED (stays gated) | frozen-closure residue: context-buffer zeroing (three buffers at 0x1C0/0x1DC/0x1F4, lengths <<2) on mode==1; c |
| `0x00036c26` | 262 | `FUN_00036c26` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00036c32` | 46 | `FUN_00036c32` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00036c60` | 26 | `FUN_00036c60` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x00036dd4` | 216 | `FUN_00036dd4` | S1 attribution; source-admitted | owner-authorized five-stage rolling feature with both bit-exact 25-tap kernels visible in C; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00036eb4` | 72 | `FUN_00036eb4` | S1 attribution; source-admitted | owner-authorized two-word bit-reversal permutation; pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00036efc` | 118 | `FUN_00036efc` | S1 attribution; source-admitted | owner-authorized strided descending top-selection helper; pinned by GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md |
| `0x00036f88` | 744 | `goodix_primitives_nadt_output_state_select` | source-admitted | owner-authorized exact five-state one-lane rate/output selector with typed thresholds, flags, history, and state |
| `0x0003727c` | 100 | `FUN_0003727c` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x000372b0` | 214 | `goodix_primitives_spo2_decimal_residual` | source-admitted | owner-authorized clean-room scaled decimal-residual extraction with explicit log10f binding; no opaque bytes retained |
| `0x0003738c` | 22 | `FUN_0003738c` | S1 attribution; source-admitted | owner-authorized conditional float-buffer standard-deviation wrapper; pinned behavior remains in GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md |
| `0x000373a4` | 216 | `goodix_primitives_nadt_optical_sample_transform` | source-admitted | owner-authorized clean-room two-stage optical transform with typed coefficient/history banks and explicit round binding; no opaque bytes retained |
| `0x0003754a` | 2 | `thunk_FUN_00037574` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00037574` | 48 | `FUN_00037574` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x0003757c` | 12 | `FUN_0003757c` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x00037588` | 372 | `goodix_primitives_hr_interpolate_periodic_sample` | source-admitted | owner-authorized 25-phase HR resampler with caller-owned previous-sample and phase state; no opaque bytes or absolute RAM banks retained |
| `0x00037710` | 16 | `FUN_00037710` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md |
| `0x00037720` | 24 | `FUN_00037720` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md |
| `0x0003773c` | 150 | `FUN_0003773c` | S1 attribution; source-admitted | owner-authorized evenly spaced cardinal-spline sampler; pinned by GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md |
| `0x000377d8` | 178 | `FUN_000377d8` | S1 attribution; source-admitted | owner-authorized positive cosine-similarity helper; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00037890` | 500 | `goodix_primitives_nadt_generated_graph_execute` | source-admitted | owner-authorized explicit seven-stage tensor topology with typed `0x34194` subgraph and node bindings; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md |
| `0x00037a84` | 220 | `goodix_primitives_nadt_peak_dispersion_quality` | source-admitted | owner-authorized clean-room phase dispersion and bounded quality estimator; no opaque bytes retained |
| `0x00037b68` | 24 | `FUN_00037b68` | UNRESOLVED (stays gated) | frozen-closure residue: int -> int8 clamp with -0x80 centering (unsigned-to-signed sample conversion); callerl |
| `0x00037b80` | 554 | `goodix_primitives_nadt_auxiliary_state_classify` | source-admitted | owner-authorized 50-sample NADT range/deviation/extrema classifier with explicit state, thresholds, diagnostics, and caller workspace; no opaque bytes retained |
| `0x00037db4` | 56 | `FUN_00037db4` | S1 attribution; source-admitted | owner-authorized warm-up sample average finalizer; pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00037dec` | 158 | `FUN_00037dec` | S1 attribution; source-admitted | owner-authorized baseline-qualified event-pair/history rebalancer; pinned by GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md |
| `0x00037e8a` | 44 | `FUN_00037e8a` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x00037f54` | 206 | `goodix_primitives_spo2_expand_packed_banks` | source-admitted | owner-authorized clean-room seven-bank packed-6/9 expansion with explicit source bindings; no opaque bytes retained |
| `0x00038030` | 28 | `FUN_00038030` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md |
| `0x00038050` | 16 | `dlCom graph-builder table wrapper` | S1 attribution; source-admitted | owner-authorized direct veneer to the reconstructed complete generated executor; pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x0003ddf4` | 40 | `FUN_0003ddf4` | UNRESOLVED (stays gated) | frozen-closure residue: Copies a seven-entry function table from flash and dispatches by index; three callsite |
| `0x0003de20` | 234 | `goodix_primitives_hr_mad_inlier_mask` | source-admitted | owner-authorized clean-room MAD inlier mask with caller scratch; no opaque bytes retained |
| `0x0003df18` | 104 | `FUN_0003df18` | UNRESOLVED (stays gated) | frozen-closure residue: Goodix per-channel state zero-init helper (0x19/0x7D counts via 0x6635C) |
| `0x0003e6b0` | 68 | `FUN_0003e6b0` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x0003e6c8` | 216 | `goodix_primitives_nadt_gaussian_interval_probability` | source-admitted | owner-authorized clean-room Gaussian interval integrator with explicit math providers; no opaque bytes retained |
| `0x0003efd8` | 54 | `FUN_0003efd8` | UNRESOLVED (stays gated) | frozen-closure residue: Scaled logistic 100/(1+exp(-k*(x-t))) scorer; three callsites inside gated Goodix 0x00 |
| `0x0003f740` | 168 | `FUN_0003f740` | S1 attribution; source-admitted | owner-authorized gated packed-6/9 triplicate workspace expansion; pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x0003f7f8` | 164 | `FUN_0003f7f8` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x0003f89c` | 316 | `FUN_0003f89c` | S1 attribution; source-admitted | owner-authorized bounded Int16 mean/deviation/threshold/outlier summarizer; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x000417f0` | 16 | `dlCom graph-builder table wrapper` | S1 attribution; source-admitted | owner-authorized direct veneer to the reconstructed complete generated executor; pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x000419c8` | 120 | `FUN_000419c8` | source-admitted | owner-authorized threshold-crossing peak accumulator over signed-32 sample arrays and the admitted word-window state |
| `0x00041f4c` | 210 | `goodix_primitives_spo2_rolling_percentile_select` | source-admitted | owner-authorized clean-room rolling percentile selector with explicit sorted-window state; no opaque bytes retained |
| `0x00042024` | 228 | `FUN_00042024` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00042bd0` | 316 | `goodix_primitives_nadt_periodic_peak_rate` | source-admitted | owner-authorized clean-room peak selection, interval-stability gate, rounded 1500-unit rate, and 40..200 clamp with caller scratch; no opaque bytes retained |
| `0x00042d1c` | 6 | `FUN_00042d1c` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x0004304c` | 50 | `FUN_0004304c` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00043860` | 28 | `FUN_00043860` | S1 attribution; source-admitted | owner-authorized signed-16 descriptor mean adapter; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x0004387c` | 686 | `FUN_0004387c` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00043b30` | 62 | `FUN_00043b30` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00044a78` | 348 | `FUN_00044a78` | S1 attribution; source-admitted | owner-authorized saturating quality counters and tail-spread flag update; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00047240` | 3240 | `FUN_00047240` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00047fa8` | 112 | `FUN_00047fa8` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00048018` | 392 | `FUN_00048018` | S1 attribution; source-admitted | owner-authorized four-point cardinal-spline evaluator; pinned by GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md |
| `0x000481a4` | 144 | `FUN_000481a4` | S1 attribution; source-admitted | owner-authorized primary/secondary event-pair aligner with wrapping mode offset; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x0004fdb8` | 64 | `FUN_0004fdb8` | S1 attribution; source-admitted | owner-authorized fixed-32-byte record history with oldest-record eviction; pinned by GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md |
| `0x0005144c` | 66 | `FUN_0005144c` | S1 attribution; source-admitted | owner-authorized signed-32 vector mean with 64-bit accumulation; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x000567c4` | 94 | `FUN_000567c4` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md |
| `0x00056828` | 20 | `FUN_00056828` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md |
| `0x0005683c` | 36 | `FUN_0005683c` | UNRESOLVED (stays gated) | frozen-closure residue: Six-field provider descriptor init plus paired buffer zeroing; callers are gated Goodi |
| `0x00056860` | 20 | `FUN_00056860` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x00056874` | 56 | `FUN_00056874` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x0005a5ec` | 54 | `FUN_0005a5ec` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-PACKED-WORD-INTEGRITY-BOUNDARY.md |
| `0x0005cd90` | 102 | `FUN_0005cd90` | UNRESOLVED (stays gated) | frozen-closure residue: Goodix 0x104-stride session-buffer init driver |
| `0x0005cdf8` | 150 | `FUN_0005cdf8` | S1 attribution; source-admitted | owner-authorized elapsed-gated typed dispatch and exact Float32 output scaler; pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x0005cea8` | 40 | `FUN_0005cea8` | S1 attribution; source-admitted | owner-authorized input-word copy and typed five-binding dispatch wrapper; pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x0005ced4` | 158 | `FUN_0005ced4` | S1 attribution; source-admitted | owner-authorized signed min/max and Float32 running mean/squared-deviation update; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md |
| `0x0005d01c` | 400 | `FUN_0005d01c` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x0005d5d0` | 16 | `FUN_0005d5d0` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x000617f8` | 1100 | `FUN_000617f8` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00061c48` | 318 | `FUN_00061c48` | S1 attribution; source-admitted | owner-authorized vector magnitude/delta and cadence-averaged degree-angle state update; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00061da4` | 334 | `goodix_primitives_spo2_channel_records_assemble` | source-admitted | owner-authorized packed three-group record assembler with integrity prepass, MSB-first masks, bounded typed scaling provider, and no opaque bytes retained |
| `0x00061ef2` | 16 | `FUN_00061ef2` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00061f04` | 138 | `FUN_00061f04` | S1 attribution; source-admitted | owner-authorized strided incremental sample standard deviation; pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00061f94` | 30 | `FUN_00061f94` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00061fb4` | 28 | `FUN_00061fb4` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00061fd4` | 22 | `FUN_00061fd4` | S1 attribution; source-admitted | owner-authorized zero-safe sample-standard-deviation wrapper; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md |
| `0x00061fea` | 22 | `FUN_00061fea` | S1 attribution; source-admitted | owner-authorized zero-safe population-standard-deviation wrapper; pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00066276` | 20 | `FUN_00066276` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x0006628a` | 20 | `FUN_0006628a` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x0006629e` | 20 | `FUN_0006629e` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x000662b2` | 20 | `FUN_000662b2` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x000662c6` | 20 | `FUN_000662c6` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x000662da` | 16 | `FUN_000662da` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x000662ea` | 26 | `FUN_000662ea` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x00066304` | 26 | `FUN_00066304` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x0006631e` | 28 | `FUN_0006631e` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x0006633a` | 34 | `FUN_0006633a` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x0006635c` | 50 | `FUN_0006635c` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x00066394` | 28 | `FUN_00066394` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x000663b4` | 120 | `FUN_000663b4` | S1 attribution; source-admitted | owner-authorized UInt8 population-standard-deviation helper; pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00066430` | 34 | `FUN_00066430` | S1 attribution; source-admitted | owner-authorized float-buffer incremental-deviation wrapper; pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00066458` | 52 | `FUN_00066458` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00066470` | 68 | `FUN_00066470` | S1 attribution; source-admitted | owner-authorized populated float-window mean; pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00066490` | 4 | `FUN_00066490` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00066494` | 92 | `FUN_00066494` | S1 attribution; source-admitted | owner-authorized indexed float-window removal and sum/cursor maintenance; pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x000664f4` | 54 | `FUN_000664f4` | UNRESOLVED (stays gated) | frozen-closure residue: Bounded word-window push with oldest-entry eviction; reached from gated Goodix 0x00034 |
| `0x0006652a` | 54 | `FUN_0006652a` | S1 attribution; source-admitted | owner-authorized signed-16 rolling-window push; pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00066560` | 64 | `FUN_00066560` | S1 attribution; source-admitted | owner-authorized byte rolling-window push and cursor wrap; pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x000665a0` | 104 | `FUN_000665a0` | S1 attribution; source-admitted | owner-authorized decimated signed-16 rolling window; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00066608` | 154 | `FUN_00066608` | S1 attribution; source-admitted | owner-authorized decimated float rolling window with running sum; pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x000666a4` | 110 | `FUN_000666a4` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x0006671c` | 266 | `goodix_primitives_spo2_biquad_cascade_process` | source-admitted | owner-authorized clean-room scattered biquad cascade with typed state/coefficient bindings; no opaque bytes retained |
| `0x000667c0` | 6 | `FUN_000667c0` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x000667c6` | 52 | `FUN_000667c6` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x000667e4` | 48 | `FUN_000667e4` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00066840` | 46 | `FUN_00066840` | UNRESOLVED (stays gated) | frozen-closure residue: DSP version builder |
| `0x00066890` | 14 | `FUN_00066890` | UNRESOLVED (stays gated) | frozen-closure residue: shared version qualifier |
| `0x000668a4` | 50 | `FUN_000668a4` | S1 attribution; source-admitted | owner-authorized reciprocal-maximum vector normalization; pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x000668dc` | 36 | `FUN_000668dc` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00066900` | 434 | `FUN_00066900` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00066ab2` | 124 | `FUN_00066ab2` | S1 attribution; source-admitted | owner-authorized one-based packed-mask row selector with first-maximum ties; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00066b30` | 222 | `goodix_primitives_nadt_symmetric_fir_i32` | source-admitted | owner-authorized clean-room reflected-boundary FIR with caller scratch; no opaque bytes retained |
| `0x00066c18` | 48 | `FUN_00066c18` | S1 attribution; source-admitted | owner-authorized bounded percentile lookup; pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x0006a018` | 4 | `FUN_0006a018` | UNRESOLVED (stays gated) | frozen-closure residue: return library pointer 0x000ad1ac; exclusive Goodix-candidate caller 0x2f624 |
| `0x0006a020` | 8 | `FUN_0006a020` | UNRESOLVED (stays gated) | frozen-closure residue: GH3X2X driver version builder |
| `0x0006a130` | 4 | `FUN_0006a130` | UNRESOLVED (stays gated) | frozen-closure residue: return library pointer 0x0009d640; exclusive Goodix-candidate caller 0x6d204 |
| `0x0006a138` | 4 | `FUN_0006a138` | UNRESOLVED (stays gated) | frozen-closure residue: return library pointer 0x000a04cc; exclusive Goodix-candidate caller 0x6d204 |
| `0x0006a140` | 6 | `FUN_0006a140` | UNRESOLVED (stays gated) | frozen-closure residue: return constant 0x12f9; exclusive Goodix-candidate caller 0x6d204 |
| `0x0006a148` | 4 | `FUN_0006a148` | UNRESOLVED (stays gated) | frozen-closure residue: return library pointer 0x000a50b0; exclusive Goodix-candidate caller 0x6d204 |
| `0x0006a150` | 4 | `FUN_0006a150` | UNRESOLVED (stays gated) | frozen-closure residue: return library pointer 0x000a692c; exclusive Goodix-candidate caller 0x6d204 |
| `0x0006a4d8` | 376 | `FUN_0006a4d8` | UNRESOLVED (stays gated) | frozen-closure residue: provider algorithm-output callback dispatcher |
| `0x0006a500` | 110 | `FUN_0006a500` | UNRESOLVED (stays gated) | frozen-closure residue: provider configuration-table loader |
| `0x0006c6a8` | 1370 | `FUN_0006c6a8` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x0006cc2c` | 4 | `FUN_0006cc2c` | UNRESOLVED (stays gated) | frozen-closure residue: return library pointer 0x000ad13c; exclusive Goodix-candidate caller 0x6d3c0 |
| `0x0006cc34` | 30 | `FUN_0006cc34` | UNRESOLVED (stays gated) | frozen-closure residue: bounded copy of version string 'pv_v1_1_0' (max 0xa); exclusive Goodix-candidate calle |
| `0x0006cc60` | 88 | `FUN_0006cc60` | S2 attribution; source-admitted | owner-authorized record-family and processing-context teardown over the local allocator/release seams; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x0006ccc0` | 984 | `FUN_0006ccc0` | S1 attribution; source-admitted | owner-authorized exact GH_SPO2/dlCom typed input diagnostic emitter with bounded sinks; pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x0006d204` | 406 | `goodix_primitives_hr_primary_context_create` | source-admitted | owner-authorized typed constructor validates the exact config/ABI, replaces global owners and ROM constructor dispatch with explicit bindings, and unwinds all allocations |
| `0x0006d3c0` | 96 | `FUN_0006d3c0` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md |
| `0x0006d424` | 180 | `FUN_0006d424` | S1 attribution; source-admitted | owner-authorized exact GH_HR composite identity builder; pinned by GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md |
| `0x0006d51c` | 1382 | `FUN_0006d51c` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md |
| `0x0006da9c` | 4 | `FUN_0006da9c` | S1 attribution; source-admitted | owner-authorized explicit HRV configuration binding replaces the fixed private RAM address; pinned by GOODIX-HRV-PROVIDER-BOUNDARY.md |
| `0x0006daa4` | 30 | `FUN_0006daa4` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-HRV-PROVIDER-BOUNDARY.md |
| `0x0006dad0` | 126 | `FUN_0006dad0` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-HRV-PROVIDER-BOUNDARY.md |
| `0x0006db58` | 4 | `thunk_FUN_0006dad0` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-HRV-PROVIDER-BOUNDARY.md |
| `0x0006db5c` | 926 | `FUN_0006db5c` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-HRV-PROVIDER-BOUNDARY.md |
| `0x0006df14` | 76 | `FUN_0006df14` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-HRV-PROVIDER-BOUNDARY.md |
| `0x0006df60` | 58 | `FUN_0006df60` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-HRV-PROVIDER-BOUNDARY.md |
| `0x0006dfc8` | 4 | `thunk_FUN_0002d460` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x0006dfcc` | 40 | `FUN_0006dfcc` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x0006dfd6` | 124 | `FUN_0006dfd6` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x0006e004` | 4 | `thunk_FUN_0002d54c` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x0006e008` | 1294 | `FUN_0006e008` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x0006e540` | 4 | `FUN_0006e540` | S1 attribution; source-admitted | owner-authorized explicit NADT result binding replaces the fixed private RAM address; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md |
| `0x0006e548` | 30 | `FUN_0006e548` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x0006e574` | 210 | `goodix_primitives_nadt_context_reset` | source-admitted | owner-authorized clean-room selective state/workspace reset with explicit release seam; no opaque bytes retained |
| `0x0006e664` | 712 | `goodix_primitives_nadt_context_initialize` | source-admitted | owner-authorized clean-room scattered initializer with typed workspace and allocator seam; no opaque bytes retained |
| `0x0006e788` | 126 | `FUN_0006e788` | S1 attribution; source-admitted | owner-authorized exact GH_NADT preprocessing/DSP identity builder; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x0006e838` | 682 | `goodix_primitives_nadt_preprocess_execute` | source-admitted | owner-authorized exact GH_NADT preprocessing stage orchestrator with caller-owned replacements for five transient allocations; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md |
| `0x0006eaf8` | 4 | `FUN_0006eaf8` | UNRESOLVED (stays gated) | frozen-closure residue: return library pointer 0x000ad160; exclusive Goodix-candidate caller 0x6ec28 |
| `0x0006eb00` | 30 | `FUN_0006eb00` | UNRESOLVED (stays gated) | frozen-closure residue: bounded copy of version string 'pre_pv_v1_1_0' (max 0xe); exclusive Goodix-candidate c |
| `0x0006eb30` | 94 | `FUN_0006eb30` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x0006eb94` | 128 | `FUN_0006eb94` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x0006ec28` | 100 | `FUN_0006ec28` | UNRESOLVED (stays gated) | frozen-closure residue: SpO2 output wrapper |
| `0x0006ec90` | 182 | `FUN_0006ec90` | UNRESOLVED (stays gated) | frozen-closure residue: SpO2 version builder |
| `0x0006f838` | 190 | `FUN_0006f838` | S1 attribution; source-admitted | owner-authorized three-stage UInt8 tensor workspace pipeline; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x0006f920` | 64 | `FUN_0006f920` | UNRESOLVED (stays gated) | frozen-closure residue: Goodix 6-byte record iteration with callback and >100-count trap |
| `0x0006f964` | 60 | `FUN_0006f964` | UNRESOLVED (stays gated) | frozen-closure residue: hal_gsensor_start_cache diagnostic and cached-buffer arm; sole caller is the gated Goo |
| `0x0006f9d4` | 12 | `FUN_0006f9d4` | UNRESOLVED (stays gated) | frozen-closure residue: indirect-call trampoline through RAM hook 0x2002fd28+4; exclusive Goodix-candidate cal |
| `0x0006fde0` | 54 | `FUN_0006fde0` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x000708f8` | 498 | `goodix_primitives_spo2_normalized_spectra_prepare` | source-admitted | owner-authorized fixed four-input plus packed-average normalized spectrum preparation with caller workspace; pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00070b60` | 178 | `FUN_00070b60` | S1 attribution; source-admitted | owner-authorized clamped-deviation mean-outlier counter; pinned by GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md |
| `0x00072c48` | 372 | `goodix_primitives_hr_secondary_context_initialize` | source-admitted | owner-authorized typed constructor for nine pair buffers, nine Int16 buffers, and seven Float32 histories with explicit coefficient binding and failure cleanup |
| `0x00072dcc` | 490 | `FUN_00072dcc` | S1 attribution; source-admitted | owner-authorized period batch reset/accumulation and channel/vector average finalizer; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00072fb8` | 222 | `FUN_00072fb8` | source-admitted | owner-authorized masked contiguous sign-run zeroing with explicit source/output extents |
| `0x0007309c` | 130 | `FUN_0007309c` | S1 attribution; source-admitted | owner-authorized quartile-spread signed outlier mask over bounded caller scratch; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x0007311e` | 54 | `FUN_0007311e` | S1 attribution; source-admitted | owner-authorized complete mask-count and difference-summary composition; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00073154` | 22 | `FUN_00073154` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x000739a8` | 1120 | `FUN_000739a8` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x0007400c` | 80 | `FUN_0007400c` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x0007405c` | 208 | `FUN_0007405c` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x0007412c` | 94 | `FUN_0007412c` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00074190` | 334 | `FUN_00074190` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x000742e4` | 1426 | `FUN_000742e4` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00074a20` | 120 | `FUN_00074a20` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00074aa4` | 4 | `FUN_00074aa4` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00074b44` | 144 | `FUN_00074b44` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00074c6c` | 30 | `FUN_00074c6c` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00074c90` | 4 | `FUN_00074c90` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00074cb4` | 34 | `FUN_00074cb4` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x000759f4` | 20 | `FUN_000759f4` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md |
| `0x00075e1c` | 318 | `FUN_00075e1c` | S1 attribution; source-admitted | owner-authorized real-input FFT magnitude reduction with explicit square-root binding and source-visible cosine table |
| `0x000765e4` | 192 | `FUN_000765e4` | source-admitted | owner-authorized Float32/packed-5/10 conversion, double-precision normalization, and bounded caller-buffer handoff |
| `0x000766ac` | 478 | `goodix_primitives_nadt_spectral_peak_prepare` | source-admitted | owner-authorized fixed-125 quartile-mask/scale/FFT/peak pipeline with caller workspace and explicit 0x35850 harmonic-selector binding |
| `0x000768b8` | 396 | `FUN_000768b8` | S1 attribution; source-admitted | owner-authorized 128-point complex radix-2 DIF core using the recovered mathematical quarter-wave cosine table |
| `0x00076a44` | 34 | `FUN_00076a44` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x00076a68` | 252 | `FUN_00076a68` | S1 attribution; source-admitted | owner-authorized exact sixteen-word scaled record serializer; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00076b78` | 100 | `FUN_00076b78` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00077d2c` | 250 | `FUN_00077d2c` | S1 attribution; source-admitted | owner-authorized caller-scratch event alignment, dual 125-sample summaries, means, and cosine percentage; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x0007cba0` | 38 | `FUN_0007cba0` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x0007dcd8` | 60 | `FUN_0007dcd8` | S1 attribution; source-admitted | owner-authorized zero-safe sample variance; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md |
| `0x0007dd18` | 58 | `FUN_0007dd18` | S1 attribution; source-admitted | owner-authorized zero-safe population variance; pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x0007dd58` | 874 | `goodix_primitives_nadt_alternate_state_classify` | source-admitted | owner-authorized fixed-200 alternate-state classifier with explicit persistent state and caller-owned scratch; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md |
| `0x000856ec` | 1154 | `FUN_000856ec` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00085ca4` | 22 | `FUN_00085ca4` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00086bac` | 394 | `goodix_primitives_hr_candidate_window_select` | source-admitted | owner-authorized newest-first four-candidate HR position-band selector with typed records, clamps, tags, fallback, and compaction |
| `0x00087618` | 176 | `FUN_00087618` | S1 attribution; source-admitted | owner-authorized alternating-extrema index collector; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x000876c8` | 932 | `FUN_000876c8` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00087a78` | 26 | `FUN_00087a78` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md |
| `0x00088e80` | 518 | `goodix_primitives_nadt_channel_quality_update` | source-admitted | owner-authorized one-record flag and exact 0.4/0.4/0.2 logistic quality-score update; pinned by GOODIX-NADT-QUALITY-PROVIDER-BOUNDARY.md |
| `0x00091870` | 32 | `FUN_00091870` | S1 attribution; source-admitted | owner-authorized primary statistics plus secondary Int16 mean summary builder; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00091890` | 78 | `FUN_00091890` | UNRESOLVED (stays gated) | frozen-closure residue: Goodix 0x104-stride session-buffer teardown/zero driver |
| `0x000928ca` | 2 | `thunk_FUN_000928da` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x000928e0` | 26 | `FUN_000928e0` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00092900` | 30 | `FUN_00092900` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00092988` | 46 | `FUN_00092988` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x000929b6` | 32 | `FUN_000929b6` | UNRESOLVED (stays gated) | frozen-closure residue: Max-plus-argmax scan over a provider sample vector; caller is gated Goodix 0x00066AB2 |
| `0x000929d6` | 46 | `FUN_000929d6` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00092a04` | 336 | `FUN_00092a04` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00092b58` | 2 | `thunk_FUN_00092b60` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x00092b68` | 44 | `FUN_00092b68` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x00093e14` | 38 | `FUN_00093e14` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x00093e3a` | 36 | `FUN_00093e3a` | UNRESOLVED (stays gated) | frozen-closure residue: Paired pool-free loop over 0x18-stride records; part of the 0x0006EB30 free chain |
| `0x00093e5e` | 68 | `FUN_00093e5e` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x00095750` | 198 | `FUN_00095750` | S1 attribution; source-admitted | owner-authorized exact Float32 maximum-absolute cap, tiny-signal zeroing, clamp, and normalization |
| `0x00095828` | 674 | `goodix_primitives_nadt_signal_confidence_update` | source-admitted | owner-authorized exact dual-rate selection, 124-interval deviation classifier, rolling-rate acceptance state, and Gaussian confidence update with caller workspace |
| `0x00095b04` | 22 | `FUN_00095b04` | S1 attribution; source-admitted | owner-authorized configured-shape veneer for the in-place quantizer; pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x000968c4` | 290 | `goodix_primitives_nadt_inference_bridge` | source-admitted | owner-authorized clean-room tail-window preparation, normalization, generated-graph dispatch, and raw-branch scalar clamp with caller scratch; no opaque bytes retained |
| `0x00096a20` | 32 | `FUN_00096a20` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |
| `0x0009775c` | 58 | `FUN_0009775c` | S1 attribution; source-admitted | owner-authorized reverse-clamped weighted sum; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00097984` | 86 | `FUN_00097984` | S1 attribution; source-admitted | owner-authorized alternating-extrema bounded-history update; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x000982c2` | 246 | `FUN_000982c2` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x00098e4c` | 126 | `FUN_00098e4c` | S1 attribution; source-admitted | owner-authorized strict signed-16 local-extrema index extraction; pinned by GOODIX-NADT-PROVIDER-BOUNDARY.md (+NADT accumulation/peak-mask/quality docs) |
| `0x00098ffc` | 20 | `FUN_00098ffc` | S2 (blocked) | goodix_mem/GdMem allocator or heap-dependent glue; pinned by SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md |
| `0x00099010` | 4 | `thunk_FUN_00043b30` | S1 (blocked) | closed algorithm-library body, binary-only even upstream (license clause 5); pinned by GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md |

## Notes and divergences observed during mapping

- R1 carries a Goodix errata patch absent from the public v4.3.0.0 tree: `GH3X2X_Init`
  (0x2A754) and `GH3X2X_StartSampling` (0x2AD18) both gate on/modify register 0x72 bits 0x11.
- `GH3X2X_ExitLowPowerMode` (0x2A380) evidence strings live in the `GH3X2X_WAKE_UP_CONFIRM`
  macro in `gh_drv_control.h`, not a .c body; the match is against macro-expanded source.
- `Gh3x2x_WearEventHook` (0x2EB84) has `GhMultSensorWearEventSend` inlined by Even's build
  (both functions' log strings appear in the one body).
- `GH3X2X_ReadElectrodeWearDumpData` (0x2A9D4): the body is commented out in the public
  snapshot (`gh_drv_dump.c`) but the function is declared in `gh_drv_dump.h` and called by
  `Gh3x2xDemoInterruptProcess`; the R1 body matches the commented-out reference body.
  Recorded as moderate confidence.
- `GH3X2X_CheckRawdataBuf` is a `return 0` stub in the public tree; the R1 body at 0x2A1CC is
  the real packed-24-bit validation loop calling the gated integrity validator 0x294F8. The
  upstream stub does not establish ownership of the R1 body → left UNRESOLVED.
- Firmware rodata contains unreferenced upstream name strings for `Gh3x2xDemoHardConfigReset`,
  `Gh3x2xInterruptModeSwitch`, `Gh3x2xDemoSetFuncionFrequency`, `Gh3x2xDemoSetFuncionLedCurrent`
  — those functions are absent from the R1 build (no xref); nothing to map.
- 0x2E734 (sole caller is the R1 adapter 0x508DA "bounded identity probe"): wraps
  `GH3X2X_CommunicateConfirm` with an R1-specific return mapping (0 / 0xFFFFFFA5); no upstream
  function carries that contract → UNRESOLVED (likely R1-authored glue inside the gate).
- Notable near-misses left UNRESOLVED: 0x2AEDC (alg-config virtual-reg write path; window
  arithmetic 0x3000/0x300/0x30C0/0x3300 matches `GH3X2X_WriteFunctionConfigWithVirtualReg` /
  `GH3X2X_WriteAlgConfigWithVirtualReg` (`gh3x2x_demo_algo_config.c`), but the per-function
  switch body diverges from the public tree — Even build or newer Goodix revision), its
  lane-write helper 0x2AF32, the AGC-pipeline cluster 0x29D5C/0x2B524/0x2B998/0x2B91C
  (gh_agc.c candidates, not body-verified in this pass), and the 2-byte `bx lr` stub cluster
  (0x2A658/0x2A65A/0x2A9D2/0x2AE04/0x2AE06/0x2AD14/0x2D66C/0x2E950/0x2EB80 — non-unique).
- 0x2EB34 (`Gh3x2x_BspDelayMs`-equivalent: per-ms loop of 1000 µs delay calls, invoked with 15
  after soft reset exactly as upstream `Gh3x2x_BspDelayMs(15)`) is **not** a ledger entry;
  noted only as supporting adjacency evidence.

## Residual pass 2026-08-14

Second pass over the 115 UNRESOLVED entries from the first pass. Same upstream snapshot
(`coredevices/pebbleos-nonfree` @ `2c0034a2`, `gh3x2x/`), same match standard (control-flow +
constants + log-string topology; call-graph adjacency from already-matched anchors). This pass
additionally used: (a) the `g_pfnAlgorithmCallFunc` 20x3 table recovered from rodata at 0x9D404
(via `DAT_00029f50` in 0x29E8C), which fixes Init/Exe/Deinit slot identity per algorithm;
(b) the AGC register-accessor table pair (`g_usGH3x2xSlotRegBase` + `g_pstGH3x2xAgcReg`, 3-byte
{offset,msb,lsb} entries) behind `GH3x2xSetAgcReg`/`GH3x2xGetAgcReg`; (c) rodata gap arithmetic
between HRNet weight-array accessor targets. No files other than this report were modified.

Summary of this pass: **71 newly MATCHED, 3 reclassified S1, 6 reclassified S2, 6 reclassified
R1-GLUE, 29 remain UNRESOLVED.** New ledger totals for the 499-entry class: MATCHED 168,
S1 243, S2 53, R1-GLUE 6, UNRESOLVED 29.

Key structural results:

- The entire soft-AGC module `module/gh_agc/gh_agc.c` is present in the R1 build and is now
  fully mapped (23 entries: 0x29C98/0x29D0A/0x29D34/0x29D58/0x29D5C/0x2A810/0x2A814/0x2A84C/
  0x2A86C/0x2ADB0/0x2B4F8/0x2B524/0x2B6A4/0x2B6E0/0x2B8EC/0x2B91C/0x2B998/0x2BD84/0x2BE24/
  0x2BFAA/0x2C148/0x2C178/0x2C4E4 plus `GH3x2xSetAgcReg`/`GH3x2xGetAgcReg` from
  `driver/src/gh_drv_dump.c`). `GH3x2xAgcMainChnlPro` is inlined into `GH3X2X_LedAgcProcess`
  (0x2A84C); `GH3X2X_AgcSetSatFlag` and `GH3x2xAgcRawdata2Ipd` are inlined into
  `GH3x2xAgcMainChnlKeyValueCal` (0x2B998); `GH3x2xNewAgcSetNewSubChnl` is inlined into
  `GH3x2xAgcChnlInfoInit` (0x2B6E0); the module resets are inlined into `GH3X2X_LedAgcReset`
  (0x2A86C: memsets 0x18/0x50/0x158/0x10/0x288 = sizeof cfg + 8x10 + 8x0x2B + 8x2 + 24x0x1B).
- 0x2AEDC resolved: it IS `GH3X2X_WriteAlgConfigWithVirtualReg`. The first-pass "switch
  divergence" is build-flag skew, not version skew: the R1 build enables only HR/HRV/SPO2, so
  the ECG/BT/AF case bodies compile out and fold into default. Case 1 = HR with
  `GH3X2X_WriteHrAlgConfigWithVirtualReg` inlined (0x35C0 = GH3X2X_HR_ALGO_CHNL_NUM_ADDR,
  HBA_SCENES_SLEEP=20 sleep-flag store, chnl-map write tail at 0x200/0x202); case 2 = HRV via
  0x2AF32 with 5-entry param array; case 6 = SPO2 (0x44C0 bound). Window arithmetic
  (0x3000/0x300/0x30C0/0x3300) matches the pinned tree exactly.
- 0x2AF32 = `GH3X2X_WriteAlgParametersWithVirtualReg` (offset/2 parity halfword merge; exact).
- `gh3x2x_demo_accppg_sync.c` ships empty bodies upstream (`GH3X2X_TimestampSyncPpgInit`,
  `...SetPpgIntFlag`, `...AccInit`, `...Send2AlgoCall`, fill functions) and
  `GH3X2X_TimestampSyncGetFrameDataFlag` is `return 1` — so R1's 2-byte `bx lr` stubs and the
  const-1 stub at the corresponding call positions match by call position (moderate).
- The R1 build's HR neural net differs from the public snapshot: the accessor-target array
  between knConfNet (2979 words, exact gap) and knTdfusion (1567 words, exact gap) is 4857
  words (0x12F9), matching no public `NET_SIZE`; its addr/size accessor pair stays gated.

Per-entry verdicts (all 115 first-pass UNRESOLVED entries):

| Address | Residual verdict | Mapping / evidence |
| --- | --- | --- |
| `0x00029bbc` | S2 (blocked) | 23-pointer context teardown; every callee S2-pinned (0x667C0/0x6628A/0x662C6 goodix_mem free wrappers); sole caller S2 0x6CC60 |
| `0x00029c74` | S2 (blocked) | type-tag dispatch through ROM table 0xBCF78 into heap destructors (0x3E6B0 context destructor, 0x3757C guarded free — both ledger heap-gated); sole caller S2 0x6CC60 |
| `0x00029c98` | MATCHED | module/gh_agc/gh_agc.c:GH32x2xMedSel — median-of-three compare tree exact |
| `0x00029cc0` | MATCHED | driver/src/gh_drv_control.c:GH3X2XDrvConfigInit — ProtocolFlagInit inlined + FifoControlInit(0x2A474) + SensorPramInit(0x2ABEC, matched) + DrvControlInit inlined (algoEnable=1 ... sleepFlag=3, divZero=0) — full field pattern |
| `0x00029cdc` | MATCHED | demo_algo_code/goodix_algo_application/src/gh3x2x_demo_algo_hook.c:GH3X2X_AdtAlgorithmResultReport — updateFlag gate; snResult[0]==1 → ClearSoftEvent(0x20)/SetSoftEvent(0x10), ==2 reversed (WEAR_OFF/ON_ALGO_ADT=32/16); called from 0x2B218 (AdtAlgoExe) tail |
| `0x00029d0a` | MATCHED | gh_agc.c:GH3X2X_AgcGetExtremum — cnt<=discard → max=0/min=0x1000000, else running max/min |
| `0x00029d34` | MATCHED | gh_agc.c:GH3X2X_AgcGetThreshold — spo2 pair 0xF33333/0xC00000 vs general 0xECCCCD/0xA66666 (8388608*1.9/1.5/1.85/1.3) exact |
| `0x00029d58` | MATCHED | thunk_FUN_0002b91c — 4-byte B.W veneer to GH3x2xAgcInfoUpdate (0x2B91C, matched this pass) |
| `0x00029d5c` | MATCHED | gh_agc.c:GH3X2X_AgcSubChnlGainAdj — 24-entry stride-0x1B sub-chnl loop; MedSel(0x29C98)/GetExtremum(0x29D0A)/AdjustGainByExtremum(0x2D184)/SetAgcReg(5+adc via 0x2CC94) callee chain exact; 1/5 Fs discard + 1 s analysis window |
| `0x00029e8c` | MATCHED | demo_algo_code/.../gh3x2x_demo_algo_call.c:GH3X2X_AlgoCalculate — 20-func bitmap loop (FUNC_OFFSET_MAX=20), started-bitmap gate, sleep-flag → punFrameFlag[2]|=8, 0xC-stride call table at +4, 0x44-byte result memset/0xFF/BitCount(0x2D324); R1 adds a result-mirror memcpy at frame+0x40 not in the pinned tree (noted) |
| `0x00029f88` | MATCHED | gh3x2x_demo_algo_config.c:GH3X2X_AlgoChnlMapInit — flag=0/num=0 + 32x0xFF from offset 3 (ALGO_CHNL_NUM=32) exact |
| `0x0002a168` | UNRESOLVED (stays gated) | FIFO post-read validate-and-patch loop: per 4-byte record, makeup-3-byte, call S1 packed-word validator 0x2950C, patch low byte; injected inside matched GH3X2X_ReadFifodata (0x2AA10); no upstream v4.3.0.0 counterpart (Even workaround or newer Goodix rev — unprovable) |
| `0x0002a1cc` | UNRESOLVED (stays gated) | unchanged from first pass: real GH3X2X_CheckRawdataBuf body while upstream is a stub; ownership unprovable |
| `0x0002a266` | MATCHED | driver/src/gh_drv_config.c:GH3X2X_DecodeRegCfgArr — *out=0; null/len → -2; loop *out \|= GhGetFunctionIdViaVirReg (0x2EDFC, matched) over 4-byte {addr,data} records |
| `0x0002a474` | MATCHED | gh_drv_control.c:GH3X2X_FifoControlInit — 0xFF package-id byte + zeroed mode/cnt/waterline fields; call position inside matched DrvConfigInit (moderate) |
| `0x0002a54c` | UNRESOLVED (stays gated) | return-0 stub, callerless, non-unique |
| `0x0002a5ec` | MATCHED | gh_agc.c:GH3X2X_GetRegBitField — ((1<<(msb-lsb+1))-1)<<lsb mask/shift formula exact |
| `0x0002a610` | UNRESOLVED (stays gated) | return-0 stub, callerless, non-unique |
| `0x0002a630` | MATCHED | gh3x2x_demo_algo_config.c:GH3X2X_HbaAlgoChnlMapDefultSet — flag gate + AlgoChnlMapInit(0x29F88) + num=4 (__HR_ALGORITHM_SUPPORT_CHNL_NUM__) + map[0..3]=0..3 |
| `0x0002a658` | MATCHED | gh3x2x_demo_algo_hook.c:GH3X2X_HrAlgorithmResultReport — call position inside matched GH3x2xHrAlgoExe (0x2C944); upstream body defers to platform `gh3x2x_hr_result_report`, R1 build stubs to `bx lr` (moderate, call-position only) |
| `0x0002a65a` | MATCHED | gh3x2x_demo_algo_hook.c:GH3X2X_HrvAlgorithmResultReport — call position inside matched GH3x2xHrvAlgoExe (0x2CAD8); stubbed likewise (moderate) |
| `0x0002a65c` | UNRESOLVED (stays gated) | indirect provider op with 0xAAAA payload word; upstream 0xAAAA user is demo_mp rawdata tag but gh3x2x_demo_mp_get_rawdata body does not match; likely R1 transport glue — unprovable |
| `0x0002a810` | MATCHED | thunk_FUN_0002b6e0 — veneer to GH3x2xAgcChnlInfoInit (0x2B6E0, matched this pass) |
| `0x0002a814` | MATCHED | gh_agc.c:GH3X2X_LedAgcPramWrite — 2-byte loop, offset = posi*2+cnt, bound 0x18 = sizeof(g_stSoftAgcCfg), 1-byte memcpy into cfg struct |
| `0x0002a84c` | MATCHED | gh_agc.c:GH3X2X_LedAgcProcess with GH3x2xAgcMainChnlPro inlined — fifoLen gate, AgcSubChnlGainAdj(0x29D5C), 0x20-byte IpdMean zero, MainChnlKeyValueCal(0x2B998), per-slot CalDrvCurrentAndGain(0x2B524), SetAgcReg gain/drv paths, SubChnlAdjGainAndClearCnt(0x2C178), HaveAgcAtLastReadPrd/DropFlag/g_NewAgcMainChelFlag updates — exact |
| `0x0002a86c` | MATCHED | gh_agc.c:GH3X2X_LedAgcReset with AgcModuleReset/NewAgcSubChnlModuleReset inlined — memsets 0x18 (g_stSoftAgcCfg) + 0x50/0x158/0x10/0x288 arrays exact |
| `0x0002a9d2` | UNRESOLVED (stays gated) | R1 deferred-log flush stub (called with formatted buffers from 15 sites); no upstream identity |
| `0x0002a9ec` | MATCHED | driver/src/gh_drv_interface.c:GH3X2X_ReadFifo — hook-null check → GH3X2X_TryWakeUp(0x2AE08, matched) → g_pGh3x2xReadFifoFunc(buf,len); call position inside matched ReadFifodata (moderate-high) |
| `0x0002ac4c` | MATCHED | gh3x2x_demo_algo_hook.c:GH3X2X_SoftAdtGreenAlgorithmResultReport — wear state machine; snResult==1 → Clear(2)/Set(8), bit1 → Clear(8)/Set(2) (SOFT_EVENT_WEAR_OFF=2/WEAR_ON=8 exact); color==0 dispatch in matched SoftAdtAlgoExe |
| `0x0002ac8c` | MATCHED | gh3x2x_demo_algo_hook.c:GH3X2X_SoftAdtIrAlgorithmResultReport — twin over second state global; color==1 dispatch |
| `0x0002acf4` | MATCHED | gh3x2x_demo_algo_config.c:GH3X2X_Spo2AlgoChnlMapDefultSet — flag gate + AlgoChnlMapInit + num=1 + map[ALGO_RED_CHNL_POS=8]=0 / map[ALGO_IR_CHNL_POS=16]=1 |
| `0x0002ad14` | MATCHED | gh3x2x_demo_algo_hook.c:GH3X2X_Spo2AlgorithmResultReport — call position inside matched GH3x2xSpo2AlgoExe (0x2CFE8); stubbed in R1 build (moderate) |
| `0x0002adb0` | MATCHED | gh_agc.c:GH3X2X_StoreDrvCurrentAfterAgc — halfword low/high byte merge by drv index exact |
| `0x0002add0` | UNRESOLVED (stays gated) | in-place 16-bit byte-pair swap loop; callerless; no unique upstream body |
| `0x0002ae00` | MATCHED | demo_algo_code/.../gh3x2x_demo_accppg_sync.c:GH3X2X_TimestampSyncGetFrameDataFlag — `return 1` exact; caller 0x6A4D8 pairs it with matched GetGsensorEnableFlag(0x2A5C4) in the upstream gh3x2x_frame_data_hook_func gate idiom (moderate) |
| `0x0002ae04` | MATCHED | gh3x2x_demo_accppg_sync.c:GH3X2X_TimestampSyncPpgInit — upstream body is empty; called with unFuncMode at the start-path position of matched Gh3x2xDemoSamplingControl (moderate) |
| `0x0002ae06` | MATCHED | gh3x2x_demo_accppg_sync.c:GH3X2X_TimestampSyncSetPpgIntFlag — upstream body empty; called with arg 1 immediately before ReadFifodata in matched Gh3x2xDemoInterruptProcess (moderate-high) |
| `0x0002aedc` | MATCHED | gh3x2x_demo_algo_config.c:GH3X2X_WriteAlgConfigWithVirtualReg — 0x3000/0x300/0x30C0/0x3300 window exact; HR/HRV/SPO2 cases inlined (0x35C0/0x44C0 bounds, HBA_SCENES_SLEEP=20 → Gh3x2xSleepFlagSet inlined, chnl-map tail 0x200/0x202/default 2-byte write); ECG/BT/AF cases compiled out in the R1 build (build-flag skew, same source) |
| `0x0002af32` | MATCHED | gh3x2x_demo_algo_config.c:GH3X2X_WriteAlgParametersWithVirtualReg — usValIndex=offset/2, buffer index offset/4 - base, low/high halfword merge on index parity exact |
| `0x0002b218` | MATCHED | demo_algo_code/goodix_algo_call/src/gh3x2x_demo_algo_call_adt.c:GH3x2xAdtAlgoExe — MovingAvaFilter(0x2E8E8), diff, reflex-model wear-on (raw>thr && diff>thr) / wear-off (raw<thr), result codes 1/2, log strings "wear on/off event, Rawdata = %d, unRawdataDiff = %d" exact modulo Even's [RING] tag and R1 log plumbing |
| `0x0002b4c4` | MATCHED | gh3x2x_demo_algo_call_adt.c:GH3x2xAdtAlgoInit — g_pfnAlgorithmCallFunc row-0 init slot; MovingAvaFilterInit inlined (zeroed point-count) + wear status reset + return OK |
| `0x0002b4d8` | MATCHED | gh3x2x_demo_algo_call_adt.c:GH3x2xAdtVersion — returns "GX_HARDADT_SOFTCHECK_v0.1" pointer; two call sites inside matched GH3X2X_AlgoVersion (0x2A0F4) ADT case |
| `0x0002b4f8` | MATCHED | gh_agc.c:GH3x2xAgcCalDrvCurrent — cur*ideal/ipd, zero→max(min,1), clamp [min,max] exact |
| `0x0002b524` | MATCHED | gh_agc.c:GH3x2xAgcCalDrvCurrentAndGain — full state load (stride 10/0x2B/2), IPD triads general 2000/3060/1000 vs spo2 20000/25000/15000, H-thd double-hit fast drop (gain=0/drv=min/IniteFirst=0/cnt=0), sat→gain--, CalDrvCurrent(0x2B4F8)+CalExtremum(0x2B6A4)+AdjustGain(0x2D184) branch topology, AGC_READ_CHECK block exact |
| `0x0002b6a4` | MATCHED | gh_agc.c:GH3x2xAgcCalExtremum — min==0x1000000 guard, base=min>0x800000?0x800000:min-1, drv-ratio rescale exact |
| `0x0002b6e0` | MATCHED | gh_agc.c:GH3x2xAgcChnlInfoInit with GH3x2xNewAgcSetNewSubChnl inlined — 8x4 gain/dc-cancel copies (+0x20/+0x60), drv halfword copy (+0x40), slot-enable bitmask loop with >7 → while(1), spo2 slot flag, bak-reg copies, bg-cancel nibble select from g_stSoftAgcCfg+6/7, EcgPpgRxEn mask, 32000/(fastest+1)/(srmul+1), sub-chnl fill with 24-bound while(1) — exact |
| `0x0002b8ec` | MATCHED | gh_agc.c:GH3x2xAgcFindSubChnlSlotInfo — 8-entry stride-10 scan, +7 enable byte, (+3)>>2 == slot |
| `0x0002b91c` | MATCHED | gh_agc.c:GH3x2xAgcInfoUpdate — ReadRegBitField(4,0,7) fastest rate, GetAgcReg(5+src)/GetDrvCurrent refresh, sample rate to key-info +0x26, SetAgcReg(AGC_EN=0) hardware-agc disable — exact |
| `0x0002b998` | MATCHED | gh_agc.c:GH3x2xAgcMainChnlKeyValueCal with AgcSetSatFlag + AgcRawdata2Ipd inlined — 8-slot loop, gain-table lookup, spo2/general IPD/threshold select, 5 Fs sat window with >>4 (6.25%) rule, median+extremum+sumAdjust accumulation, mean via __aeabi_ldivmod (64-bit Ipd), 15-count ideal-adjust window — exact |
| `0x0002bd84` | MATCHED | gh_agc.c:GH3x2xAgcMeanInfoReset — slot-bitmap loop, key-info +0x24 cnt clear, 4 rx x 24 sub-chnl (stride 0x1B) cnt clears — exact |
| `0x0002be24` | MATCHED | gh_agc.c:GH3x2xAgcRegParse — all nine reg-type cases (0/6/8/0xC/0xE/0x10/0x14/0x16/0x18) with exact (lsb,msb) pairs per upstream gh_agc.h defines |
| `0x0002bfaa` | MATCHED | gh_agc.c:GH3x2xAgcRegvalGet — SYS_SAMPLE_RATE_CTRL(4) special case, 0x10A..+0xDF window, /0x1C slot, %0x1C reg type, 20-out-pointer AgcRegParse(0x2BE24) call with writeback |
| `0x0002c148` | MATCHED | gh_agc.c:GH3x2xAgcRegvalReset — memset 0xA1, 8 slots stride 0x14, GainCode[0..3]=GAINCODE_DEF_VAL(4), AdjUpLimit=ADJUPLIMIT_DEF_VAL(0xFF) |
| `0x0002c178` | MATCHED | gh_agc.c:GH3x2xAgcSubChnlAdjGainAndClearCnt — 4-rx x 24-subchnl loop, FindSubChnlSlotInfo, thresholds, CalExtremum+AdjustGainByExtremum, SetAgcReg(5+rx) + gain store — callee topology exact |
| `0x0002c4c0` | MATCHED | driver/src/gh_drv_dump.c:GH3x2xGetAgcReg — slot-base halfword table + 3-byte {offset,msb,lsb} AGC-reg table → ReadRegBitField(0x2AA98); table layout exact |
| `0x0002c4e4` | MATCHED | gh_agc.c:GH3x2xGetDrvCurrent — agcEn==2 → GetAgcReg(4=DRV1) else 3=DRV0 exact |
| `0x0002c930` | MATCHED | demo_algo_code/goodix_algo_call/src/gh3x2x_demo_algo_call_hr.c:GH3x2xHrAlgoDeinit — g_pfnAlgorithmCallFunc row-1 deinit slot; call goodix_hba_deinit_func(0x6CC60, S2 heap teardown) + SUCCESS→OK/GENERIC_ERROR map |
| `0x0002c944` | MATCHED | gh3x2x_demo_algo_call_hr.c:GH3x2xHrAlgoExe — hba input assembly incl. `cnt + 4*(cnt/4)` map-index quirk, sleep flag, 24/1/0 const fields, goodix_hba_calc(0x6C6A8, S1), snResult[0..5] + 0x3F result bits + record-result mirror; R1 carries one extra S1 lib call (0x6CCC0) after calc (noted) |
| `0x0002caa4` | MATCHED | gh3x2x_demo_algo_call_hr.c:GH3x2xHrAlgoInit — init_func(pstFunctionInfo->usSampleRate) via 0x6D3C0, 0/-1 map, pstAlgoRecordResult(0x40) flag+snResult[0] zeroing — exact |
| `0x0002cad8` | MATCHED | gh3x2x_demo_algo_call_hrv.c:GH3x2xHrvAlgoExe — last-HR fetch via frame-info[1]+0x40 record result, direct rawdata loop with puchFrameLastGain/0xFF-invalid update, drv (>>8)+(>>16) byte sum, goodix_hrv_calc(0x6D51C, S1), UPDATE-only gate, 0x7F result bits — exact |
| `0x0002cc94` | MATCHED | gh_drv_dump.c:GH3x2xSetAgcReg — table twin of GetAgcReg → WriteRegBitField(0x2B0DC) |
| `0x0002ccf4` | MATCHED | gh3x2x_demo_algo_config.c:Gh3x2xSleepFlagGet — returns the sleep-flag byte (same global written by the Gh3x2xSleepFlagSet inline in 0x2AEDC HR case) |
| `0x0002cdd4` | MATCHED | demo_algo_code/goodix_algo_call/src/gh3x2x_demo_algo_call_nadt.c:GH3x2xSoftAdtAlgoExe — nadt input assembly incl. cap-enable block (cap_channel_num=4), ppg_colour_flg, sleep/bit24/chip1 fields, goodix_nadt_calc(0x6E008, S1), IR timeout (unFunctionID==0x8000=SOFT_ADT_IR), 0x3 result bits + color-dispatched report (0x2AC4C/0x2AC8C) — exact |
| `0x0002cfe8` | MATCHED | demo_algo_code/goodix_algo_call/src/gh3x2x_demo_algo_call_spo2.c:GH3x2xSpo2AlgoExe — map-gated 12-channel loop, ret in {SUCCESS=0, FRAME_UNCOMPLETE=3, WIN_UNCOMPLETE=4}, GH3x2x_Round(final_spo2/10000) via 0x2D354, 6 result fields; R1 skew: usResultBit=0xFF (upstream 0x7F) and an extra 7th result field mirroring snResult[0] (noted) |
| `0x0002d16c` | MATCHED | gh3x2x_demo_algo_call_spo2.c:GH3x2xSpo2AlgoInit — goodix_spo2_init_func(0x6EC28) wrapper, 0/-1 map; row-6 init slot |
| `0x0002d184` | MATCHED | gh_agc.c:GH3x2x_AgcAdjustGainByExtremum — 0x1000000 guard, g_usGH3x2xTiaGainR float-ratio gain walk both directions, 8*max < 7*H_thd anti-nonlinearity hysteresis — exact |
| `0x0002d324` | MATCHED | gh3x2x_demo_algo_config.c:GH3x2x_BitCount — shift-and-count popcount loop exact |
| `0x0002d354` | MATCHED | gh3x2x_demo_algo_config.c:GH3x2x_Round — ±0.00001 epsilon dead-band, ±0.5 pre-rounding exact |
| `0x0002d66c` | UNRESOLVED (stays gated) | 2-byte stub called once from matched GH3x2xGetFrameDataAndProcess (0x2C4FC) right after HandleFrameData — hint only, non-unique |
| `0x0002e734` | R1-GLUE | first-pass evidence stands: wraps GH3X2X_CommunicateConfirm with R1-specific 0/0xFFFFFFA5 return mapping; sole caller is the R1 adapter 0x508DA; no upstream function carries that contract |
| `0x0002e8c4` | MATCHED | demo_algo_code/goodix_algo_application/src/gh3x2x_demo_algo_memory.c:Gh3x2xGetHrAlgoSupportChnl — return 4 = __HR_ALGORITHM_SUPPORT_CHNL_NUM__; exclusive caller 0x6D3C0 (hba init flow) (moderate) |
| `0x0002e8c8` | MATCHED | gh3x2x_demo_algo_memory.c:Gh3x2xGetSpo2AlgoSupportChnl — return 1 = __SPO2_ALGORITHM_SUPPORT_CHNL_NUM__; call position inside matched goodix_spo2_init_func (moderate) |
| `0x0002e8cc` | owner-authorized; source-admitted | callerless register pair write reconstructed from exact Thumb-2 constants and ordering over the two admitted public-democode operations |
| `0x0002e8e8` | MATCHED | gh3x2x_demo_algo_call_adt.c:Gh3x2xMovingAvaFilter — 6-deep window (GH3X2X_MOVINF_AVA_WINDOW_SIZE), shift-on-full, append, mean over count-1, return 1 — exact |
| `0x0002e950` | UNRESOLVED (stays gated) | 2-byte stub, two call sites with mode arg inside Gh3x2xDemoStartSampling path — non-unique |
| `0x0002eb80` | UNRESOLVED (stays gated) | 2-byte stub on the no-fifo-data paths of Gh3x2xDemoInterruptProcess — non-unique |
| `0x0002ede0` | UNRESOLVED (stays gated) | return *(state+4) accessor; non-unique |
| `0x00032744` | owner-authorized; source-admitted | float channel-scale/copy helper now uses explicit caller-supplied scale vector/factor and bounded output |
| `0x000335b4` | source-admitted | packed-channel direct/width scaling helper; sole caller `0x61DA4` and all table/math bindings are transparent typed C |
| `0x00034b08` | source-admitted | typed command/status/clock provider seam preserving commands 0xA6/0xAE and the wrapping 0x140-tick timeout |
| `0x00036bfa` | UNRESOLVED (stays gated) | context-buffer zeroing on mode==1; callerless |
| `0x00037b68` | UNRESOLVED (stays gated) | int→int8 clamp with -0x80 centering; callerless; generic |
| `0x0003ddf4` | R1-GLUE | ops-table dispatch trampoline (copies 7-entry ROM table 0xBCF40, calls table[*param](param[1], param+2)); table targets span gomore_health_algorithm_candidate (0x72BE0/0x48D22/0x28B8A) and goodix (0x5D01C) functions — cross-vendor wiring can only be Even product glue; caller S1 HR lib 0x6D204 |
| `0x0003df18` | S2 (blocked) | per-channel session-state zero-init via S2-pinned 0x6635C (0x19/0x7D counts); sole caller 0x5CD90 (S2 apparatus) |
| `0x0003efd8` | source-admitted | owner-authorized scaled logistic scorer `100/(1+exp(-k(x-t)))` with explicit exponential provider; reused by the local `0x88E80` quality stage |
| `0x000419c8` | source-admitted | owner-authorized threshold-crossing peak accumulator; caller S1 0x3441C; bounded typed state in `reconstructed/goodix_primitives/` |
| `0x0005683c` | UNRESOLVED (stays gated) | six-field descriptor init + paired buffer zeroing; callers S1 NADT 0x6E574/0x6E664; generic shape |
| `0x0005cd90` | S2 (blocked) | 0x104-stride session-buffer init driver; callees 0x3DF18 (S2 apparatus) + S2-pinned 0x6635C/0x6633A; sole caller S2 0x3727C |
| `0x00061da4` | source-admitted | owner-authorized packed three-channel decoder/record assembler with explicit 0x335B4 scaling-provider seam; caller S1 SPO2 calc 0x6E838 |
| `0x000664f4` | UNRESOLVED (stays gated) | bounded word-window push with memmove eviction; caller 0x419C8 (gated); generic container helper |
| `0x00066840` | S1 (blocked) | COMMON_DSP/COMMON_DL version builder ("_v1_3_0" + "30234f22"); those strings exist only inside the upstream binary .a archives (no source form) — license clause 5 |
| `0x00066890` | S1 (blocked) | version-qualifier word store + return 1; called only from the lib version builder 0x6EC90; no source form upstream |
| `0x0006a018` | MATCHED | algo_lib/algo_params/SPO2/goodix_spo2_net_for_gh3x2x-v2.23_7ecd2a.c:get_Spo2WRWeights_addr — returns pointer to float weight array (first word 0, matching upstream array head); caller S1 spo2 lib 0x2F624 (moderate) |
| `0x0006a020` | MATCHED | same file:get_Spo2WRWeights_version — memcpy(dst, "gh3x2x-v2.23_7ecd2a", len); exact NET_VERSION string; called from the lib version builder 0x6EC90 |
| `0x0006a130` | MATCHED | algo_lib/algo_params/HR/04_EXCLUSIVE/HRNet_knConfNetWeights.c:get_knConfNetWeightsArr_addr — gap to next accessor's array = 2979 words = NET_SIZE exact; caller S1 HR lib 0x6D204 (moderate) |
| `0x0006a138` | UNRESOLVED (stays gated) | HRNet weight-array addr accessor for a 4857-word net (with 0x6A140) — no public counterpart (R1 net revision skew); 4-byte stub non-unique without the pair |
| `0x0006a140` | UNRESOLVED (stays gated) | returns 0x12F9 = 4857 — size accessor paired with 0x6A138; matches no upstream NET_SIZE (R1 HR net revision absent from pinned tree) |
| `0x0006a148` | MATCHED | HRNet_knTdfusionWeights.c:get_knTdfusionWeightsArr_addr — preceding array gap = 1567 words = NET_SIZE exact (moderate) |
| `0x0006a150` | UNRESOLVED (stays gated) | return-pointer stub (0xA692C, weight-region tail); no size pairing available; non-unique |
| `0x0006a4d8` | R1-GLUE | occupies the gh3x2x_frame_data_hook_func integration point: upstream skeleton visible (GetFrameDataFlag/GetGsensorEnableFlag gate + AlgoCalculate(0x29E8C) call), but the per-function dispatch through an 8-entry R1 hook table and the "[LOG_I] pstFrameInfo : %d %d %d %d %d %d" string are Even-authored (string absent from upstream tree) |
| `0x0006a500` | MATCHED | gh3x2x_demo_algo_call.c:GH3X2X_AlgoCallConfigInit with GH3X2X_LoadGoodixAlgoRegConfigArr inlined — cfg-index bound, 8-byte {arr,len} config records, 4-byte {addr,data} loop into WriteAlgConfigWithVirtualReg(0x2AEDC); R1 extras: reset-recovering gate (0x2D348), AlgoMemConfig(0x7540) (0x2A090), 4 cfg lists vs 1 upstream (moderate) |
| `0x0006cc2c` | UNRESOLVED (stays gated) | return-pointer stub into zeroed rodata (0xAD13C); caller S1 0x6D3C0; target content does not disambiguate config vs weights |
| `0x0006cc34` | MATCHED | algo_lib/algo_params/goodix_hrv_config.c:goodix_hrv_config_get_version — min(len,10) bounded copy of "pv_v1.1.0" + NUL exact; NOTE hr_pre goodix_hba_config_get_version is source-identical — caller 0x6D3C0 (HR flow) favors hba (moderate) |
| `0x0006eaf8` | MATCHED | algo_params/SPO2/goodix_spo2_config_for_gh3x2x-v2.23_7ecd2a.c:goodix_spo2_config_get_instance — return &external_cfg; call position + 0x4C-byte memcpy into stSpo2Cfg inside matched goodix_spo2_init_func (moderate) |
| `0x0006eb00` | MATCHED | same file:goodix_spo2_config_get_version — min(len,14) bounded copy of "pre_pv_v1.1.0" (SPO2_INTERFACE_VERSION, spo2_pre_exc) + NUL exact |
| `0x0006ec28` | MATCHED | gh3x2x_demo_algo_call_spo2.c:goodix_spo2_init_func — 150-byte version buffer, Spo2AlgoChnlMapDefultSet(0x2ACF4), chnl-num ≤ GetSpo2AlgoSupportChnl(0x2E8C8) gate → 1, config_get_instance(0x6EAF8) + 0x4C memcpy + fs/valid_chl_num stores, config_get_version(0x6EB00, 20=SPO2_INTERFACE_VERSION_LEN_MAX), goodix_spo2_init(0x6EB94, S1) — full topology exact (first-pass "SpO2 output wrapper" label corrected: it is the init wrapper) |
| `0x0006ec90` | S1 (blocked) | goodix_spo2_version (closed-lib export): assembles "GH_SPO2_pre_pv_v2_1_10_0" + drv/net (0x6A020) + hash strings "277e89de"/"1f1cf98b" + DSP version (0x66840/0x66890); string set exists only inside upstream binary libs |
| `0x0006f920` | R1-GLUE | 6-byte record iteration feeding r1_gsensor_sample_sink_nop (0x2ADFC, ledger r1_product_specific) per record, plus >100-count trap; called from matched Gh3x2xDemoInterruptProcess — Even gsensor-cache pump |
| `0x0006f964` | R1-GLUE | hal_gsensor_start_cache_data — Even implementation of the upstream-declared integration point (gh_demo_user.c contract; call position in matched Gh3x2xDemoSamplingControl start path); R1 body = "[LOG_D] hal_gsensor_start_cache" log + R1 hooks |
| `0x0006f9d4` | R1-GLUE | hal_gsensor_stop_cache_data — stop-path position (commented out upstream, Even re-enabled); trampoline through R1 RAM hook 0x2002FD28+4 |
| `0x00072fb8` | source-admitted | owner-authorized masked contiguous sign-run zeroing; caller S1 NADT 0x766AC; bounded typed C in `reconstructed/goodix_primitives/` |
| `0x000765e4` | source-admitted | owner-authorized Float32/packed-5/10 conversion, optional `2/input_count` scaling, and bounded caller-buffer handoff; heap ownership is caller-explicit locally |
| `0x00091890` | S2 (blocked) | 0x104-stride session-buffer teardown twin of 0x5CD90; callees S2-pinned 0x304A0/0x662C6 + ledger heap-free helper 0x662B2; sole caller S2 0x37E8A |
| `0x000929b6` | UNRESOLVED (stays gated) | max-plus-argmax scan; caller S1 NADT 0x66AB2; generic |
| `0x00093e3a` | S2 (blocked) | paired pool-free loop over 0x18-stride records via ledger heap-free helper 0x66276; sole caller S2 0x37E8A (part of the 0x6EB30 free chain) |

Residual-pass notes:

- The `g_pfnAlgorithmCallFunc` table (0x9D404) pins R1's enabled algorithm set: ADT (row 0),
  HR (row 1), HRV (row 2), SPO2 (row 6), SOFT_ADT_GREEN (row 9) and SOFT_ADT_IR (row 15) share
  the soft-ADT triple; all other rows are zero — consistent with the 0x2AEDC build-flag finding.
- 0x6D3C0 stays S1-pinned per GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md, but note it sits at
  the goodix_hba_init_func call position (calls the hba config version getter 0x6CC34 and the
  HR support-chnl getter 0x2E8C4). If a future pass re-opens S1 pins, 0x6D3C0 (96 B) and its
  neighbor 0x6D204 are the first candidates to re-audit.
- The remaining 29 UNRESOLVED are: 12 non-unique stubs/accessors (0x2A54C/0x2A610/0x2A9D2/
  0x2ADD0/0x2D66C/0x2E8CC/0x2E950/0x2EB80/0x2EDE0/0x6A150/0x6CC2C), 3 version-skewed HRNet
  accessor residues (0x6A138/0x6A140 counted here with 0x6A150 above), 2 validation-path
  residues with no upstream body (0x2A168/0x2A1CC), and 12 closed-lib-closure helpers whose
  callers are S1-pinned (0x32744/0x335B4/0x34B08/0x36BFA/0x37B68/0x3EFD8/0x419C8/0x5683C/
  0x61DA4/0x664F4/0x72FB8/0x765E4/0x929B6 — 13 bodies; 0x34B08/0x36BFA/0x37B68 are callerless
  generic helpers folded into this group). All stay gated.

## Residual re-audit 2026-08-14 (third pass: 29 UNRESOLVED + 0x6D3C0/0x6D204 hint)

Third pass over the 29 UNRESOLVED entries left by the residual pass, plus the re-audit hint
(0x6D3C0 at the `goodix_hba_init_func` call position, neighbor 0x6D204). Same upstream
snapshot (`coredevices/pebbleos-nonfree` @ `2c0034a2`, `gh3x2x/`), same match standard
(control-flow + constants + log-string topology; call-graph adjacency from already-matched
anchors; rodata gap arithmetic for weight-array accessors). This pass additionally used:
(a) the upstream `hr_exc/goodix_hba.h` header (`goodix_hba_config` field layout,
`sizeof == 0x24`, `HBA_INTERFACE_VERSION "pv_v1.1.0"`, `HBA_INTERFACE_VERSION_LEN_MAX 20`,
`goodix_hba_version(uint8_t[120])`, `GX_ALGO_HBA_RWONG_INPUT == 1`); (b) the byte content of
the R1 rodata target of 0x6CC2C; (c) the full public HRNet `NET_SIZE` inventory
(knBasic 1033, knSmall 1861, knWeights 6660, knConfNet 2979, knSceneNet 2599,
knSceneSwitch 5951, knMulti 1269, knTdfusion 1567); (d) the upstream empty-body functions
(`gh3x2x_demo_accppg_sync.c`, `gh_demo_user.c:Gh3x2x_UserHandleCurrentInfo`,
`gh_uprotocol.c`/`gh_zip.c` upload stubs) and their exact upstream call positions.

Result: **6 flips to MATCHED (ledger regenerated: MATCHED 174, candidate family 319), 0x6D204
identity confirmed but stays S1, 23 stay UNRESOLVED.** The R1 build's HR net revision still
differs from the public tree (the 4857-word net has no public counterpart).

### Flips (ledger + verify pins updated)

| Address | New mapping | Evidence |
| --- | --- | --- |
| `0x0006D3C0` | MATCHED (high) → demo_algo_code/goodix_algo_call/src/gh3x2x_demo_algo_call_hr.c:`goodix_hba_init_func` | Full statement-level topology vs upstream: memset 120-byte version buffer (= `goodix_hba_version(uint8_t[120])` prototype) → version call (0x6D424, S1) with error gate → `GH3X2X_HbaAlgoChnlMapDefultSet` (0x2A630, matched) → `g_stHbaAlgoChnlMap.uchNum` (byte at map+1) > `Gh3x2xGetHrAlgoSupportChnl` (0x2E8C4, matched) → return 1 = `GX_ALGO_HBA_RWONG_INPUT` → `goodix_hba_config_get_arr` (0x6CC2C) → `GH3X2X_Memcpy` (0x2A968, matched) 0x24 = `sizeof(goodix_hba_config)` → `stHbCfg.fs = fs` (offset 4), `stHbCfg.valid_ch_num = uchNum` (offset 8) per upstream struct layout → memset 20-byte `chVer` (`HBA_INTERFACE_VERSION_LEN_MAX`) → `goodix_hba_config_get_version` (0x6CC34, matched) → `goodix_hba_init` (0x6D204). Sole caller 0x2CAA4 = matched `GH3x2xHrAlgoInit`, arg = `pstFunctionInfo->usSampleRate` at the exact upstream call position. Debug logs compiled out as elsewhere in the R1 build. |
| `0x0006CC2C` | MATCHED (high) → algo_lib/algo_params/HR/04_EXCLUSIVE/goodix_hba_config.c:`goodix_hba_config_get_arr` | Returns &external_hba_cfg at 0xAD13C; the 0x24-byte target content is **byte-exact** with upstream `external_hba_cfg` (mode=0, fs=25, valid_ch_num=4, earliest=9, latest=20, sigma=1, raw_ppg_scale=202, delay_time=5, valid_score_scale=1 — all nine fields). Sole caller 0x6D3C0 at the exact `goodix_hba_config_get_arr` position; consumer copies 0x24 = `sizeof(goodix_hba_config)`. (Residual-pass note "zeroed rodata" was wrong — the array is populated and matches upstream.) |
| `0x0006A150` | MATCHED (high) → algo_lib/algo_params/HR/04_EXCLUSIVE/HRNet_knWeights.c:`get_knWeightsArr_addr` | Returns 0xA692C; gap to the next proven rodata landmark (external_hba_cfg at 0xAD13C, byte-exact per above) = 0x6810 bytes = **6660 words = knWeights NET_SIZE exact**, unique among the eight public NET_SIZEs; no subset-sum of the other public sizes fits the gap. Same gap-arithmetic standard as 0x6A130 (2979) / 0x6A148 (1567). Adjacency chain confirmed: knConfNet [0x9D640,0xA04CC) → 4857-word R1-revision net [0xA04CC,0xA50B0) → knTdfusion [0xA50B0,0xA692C) → knWeights [0xA692C,0xAD13C). One literal-pool reference into the array interior (0xA7325, from S1 code 0x95C88) is consistent with lib-internal layer slicing. Content not verifiable (R1 HR net revision skew) — same caveat as the previously accepted accessors. |
| `0x0002EDE0` | MATCHED (high) → driver/src/gh_drv_config.c:`GhDrvConfigManagerGetCurFunctionSupprort` | Body exact: returns word at g_stGhDrvConfigManger+4 (`unGhFuncSupportedAtCurCfg`); same 8-byte global memset by matched `GhDrvConfigManagerInit` (0x2EDEC). Caller position exact: sole caller 0x2E36C = matched `Gh3x2xDemoStartSamplingInner` at the cfg-switch test `(unFuncModeTemp2 & ~support) != 0`, including the ADT special case (`unFuncMode==1 → 1, else & ~1`; GH3X2X_FUNCTION_ADT == 1) verbatim from upstream. |
| `0x0002EB80` | MATCHED (high) → demo_kernel_code/kernel/gh_demo_user.c:`Gh3x2x_UserHandleCurrentInfo` | Upstream body is empty (comment-only) → `bx lr`; void/no-arg. Call position exact: "Step 5: do soft agc process" in `Gh3x2xDemoInterruptProcess`, immediately before the soft-AGC block (R1: LedAgcProcess = 0x2A84C, matched). R1's two call sites (no-fifo-event path and post-`GH3X2X_UpdateAgcInfo` path, both gated by the `uchIntRepeatNum` equivalent) are the compiler's branch folding of the single upstream unconditional call. Same empty-body + call-position standard as 0x2AE04/0x2AE06. |
| `0x0002D66C` | MATCHED (candidate/moderate) → demo_kernel_code/module/gh_protocol/gh_uprotocol.c:`Gh2x2xUploadDataToMaster` | Call position exact: immediately after `GH3x2xHandleFrameData` (0x2C694, matched) inside matched `GH3x2xGetFrameDataAndProcess` (0x2C4FC), under the downsample-factor guard, with the exact 4-arg signature (pstFrameInfo, usFrameCnt, usFrameNum, puchTagArray) followed by `usFrameCnt++`. Upstream body is empty in this build configuration. Caveat (hence candidate): the `#if __SUPPORT_ZIP_PROTOCOL__` twin `Gh2x2xUploadZipDataToMaster` (gh_zip.c:820) is also an empty stub; the R1 build's flag choice is not directly recoverable, so the precise upstream name is ambiguous between the two identically-empty bodies. |

### Historical hint entry, now reduced

| Address | Verdict | Evidence |
| --- | --- | --- |
| `0x0006D204` | Historical S1 identity retained; now owner-authorized source-admitted | Called from matched `goodix_hba_init_func` (0x6D3C0) with (cfg, 0x24, interface-ver) exactly per the upstream prototype; body gates on `param_2 != 0x24` and string-compares the interface version against "pv_v1.1.0" = `HBA_INTERFACE_VERSION`; internals allocate the 0x150-byte context via the local allocator (0x2D54C), register the HRNet weight accessors (0x6A150/0x6A140/0x6A138/0x6A130/0x6A148), and wire selectors 0/1/6 through the 0x3DDF4 ops trampoline. The clean-room constructor preserves those facts with typed bindings and paired failure cleanup; it incorporates neither the HR `.a` nor copied firmware data. |

### Entries that stay UNRESOLVED (per-entry reasons, re-verified this pass)

| Address | Verdict | Re-audit evidence |
| --- | --- | --- |
| `0x0002A54C` | UNRESOLVED (unprovable) | `return 0`; callerless; no rodata/table reference (binary scanned for both 0x2A54C/0x2A54D); no distinguishing content — non-unique by construction. |
| `0x0002A610` | UNRESOLVED (unprovable) | `return 0`; callerless; no rodata reference; non-unique. |
| `0x0002A9D2` | UNRESOLVED (unprovable) | Empty void body called from 15 matched Goodix demo functions with pre-formatted 0xB4-byte buffers — R1 deferred-log flush plumbing; no upstream identity (upstream logs inline via macros; the flush indirection is Even-specific, but Even authorship cannot be proven from the body alone). |
| `0x0002ADD0` | UNRESOLVED (unprovable) | In-place 16-bit byte-pair swap loop; callerless; no rodata reference; no byte-swap counterpart anywhere in the pinned tree (grep-verified). |
| `0x0002E8CC` | owner-authorized; source-admitted | `goodix_primitives_reset_register_fields` preserves `WriteReg(0x502,0)` then `WriteRegBitField(0,10,10,0)` through typed operations; tests pin constants, order, and missing-provider rejection. |
| `0x0002E950` | UNRESOLVED (unprovable) | Empty void body called with unFuncMode inside matched `Gh3x2xDemoStartAlgoInner`'s inlined `GH3X2X_AlgoInit` 20-function init loop (both the init-fail break path and the per-iteration path). Checked every upstream candidate: all `gh3x2x_demo_accppg_sync.c` empty functions (AccInit takes void and is called from gh_demo_user.c; PpgInit matched at 0x2AE04; Send2AlgoCall/Fill* uncalled or wrong signature/position) and `GH3X2X_SEND_MSG_ALGO_START` (called once, after the loop, not inside it). No upstream counterpart at this position — likely Even instrumentation; unprovable. |
| `0x0002A168` | UNRESOLVED (stays gated) | Unchanged: FIFO post-read validate-and-patch loop injected into matched `GH3X2X_ReadFifodata`, calling the S1 packed-word validator 0x2950C; no upstream v4.3.0.0 counterpart (Even workaround or newer Goodix revision — unprovable). |
| `0x0002A1CC` | UNRESOLVED (stays gated) | Unchanged: real `GH3X2X_CheckRawdataBuf` body where upstream is a `return 0` stub; ownership unprovable. |
| `0x0006A138` | UNRESOLVED (stays gated) | Addr accessor (returns 0xA04CC) for the 4857-word R1-revision HR net; 4857 matches none of the eight public NET_SIZEs (1033/1567/1861/2599/2979/5951/6660/1269 — enumerated this pass). Now known to be consumed by closed-lib `goodix_hba_init` (0x6D204). The R1 HR net revision is absent from the pinned tree — unprovable. |
| `0x0006A140` | UNRESOLVED (stays gated) | Size accessor paired with 0x6A138 (returns 0x12F9 = 4857); same revision-skew reasoning. |
| `0x00032744` | owner-authorized; source-admitted | Float channel-scale/copy helper with explicit scale inputs and tested copy/multiply modes. |
| `0x000335B4` | source-admitted | `goodix_primitives_spo2_channel_scale_decode`; direct/width formulas and all table/math dependencies are transparent typed bindings. |
| `0x00034B08` | source-admitted | Typed command/status poll (commands 0xA6/0xAE selected by parameter bit `0x2000`, 0x140-tick timeout). Its pointer (0x34B09) is stored into an ops record at offset +0x18 by 0x31D88, reached from the R1 ST25DV bus-registration adapter 0x44BEC. Exact authorship remains unresolved, but the complete behavior is owner-authorized transparent C with explicit providers. |
| `0x00036BFA` | UNRESOLVED (unprovable) | Context-buffer zeroing on mode==1 (three buffers, lengths <<2); callerless; no rodata reference. |
| `0x00037B68` | UNRESOLVED (unprovable) | int→int8 clamp with −0x80 centering; callerless; no rodata reference; generic. |
| `0x0003EFD8` | source-admitted | Owner-authorized scaled logistic scorer with explicit exponential provider; reused by local `0x88E80`. |
| `0x000419C8` | source-admitted | Owner-authorized threshold-crossing peak accumulator; caller S1 0x3441C; bounded typed state in `reconstructed/goodix_primitives/`. |
| `0x0005683C` | UNRESOLVED (stays gated) | Six-field descriptor init + paired buffer zeroing; callers S1 NADT 0x6E574/0x6E664; generic shape. |
| `0x00061DA4` | source-admitted | Owner-authorized packed three-channel decoder/record assembler with explicit 0x335B4 scaling-provider seam; caller S1 SPO2 calc 0x6E838. |
| `0x000664F4` | source-admitted | Owner-authorized bounded word-window push with eviction; caller 0x419C8 is also source-admitted. |
| `0x00072FB8` | source-admitted | Owner-authorized masked contiguous sign-run zeroing; caller S1 NADT 0x766AC; bounded typed C in `reconstructed/goodix_primitives/`. |
| `0x000765E4` | source-admitted | Owner-authorized Float32/packed-5/10 conversion, optional double-precision `2/input_count` scaling, and bounded caller-buffer handoff. |
| `0x000929B6` | UNRESOLVED (stays gated) | Max-plus-argmax scan; caller S1 NADT 0x66AB2; generic. |

Re-audit notes:

- The 499-entry class totals are now: MATCHED 174, S1 243, S2 53, R1-GLUE 6, UNRESOLVED 23.
- 0x6D3C0's flip removes the stale "heart-rate output wrapper" boundary label (same
  first-pass mislabel pattern as 0x6EC28, corrected by the residual pass).
- Ledger/pin updates: generator tables `APP_GOODIX_PUBLIC_DEMOCODE` (+0x6D3C0/0x6CC2C/0x6A150/
  0x2EDE0/0x2EB80) and `APP_GOODIX_PUBLIC_DEMOCODE_MODERATE` (+0x2D66C) in
  `r1/tools/build_r1_source_ownership.py`; regenerated `r1/docs/FUNCTION-OWNERSHIP.csv` /
  `FUNCTION-OWNERSHIP-SUMMARY.json` (+ reference copies); `r1/tools/verify_openr1.py`
  `goodix_democode_symbols`/`goodix_democode_entries` (+6), provider-count pins
  (democode 168→174, candidate 325→319), both family entry-set digests re-pinned to the new
  legitimate state, and the stale cluster comment corrected (64→110 attributed members; the
  116-entry cluster set and both cluster digests are unchanged — the three cluster-member
  flips keep their cluster membership, exactly as the previously attributed members do).

## Third-party source census 2026-08-14

A fourth, read-only pass over every public GH3x2x distribution reachable in August 2026.
Nothing below changes any entry verdict; the 23 documented-unprovable entries stay gated.

- **Architecture blocker strengthened from "unlinkable" to instruction level.** All seven
  `.a` archives in the pinned snapshot (`algo_lib/{NADT,SPO2,COMMON_DL,HRV,COMMON_DSP,HR}`
  plus `drv_lib` `gh_common`) are Armv8-M.mainline "star-mc1" FPv5 softfp builds that
  actually use FPv5-only instructions (`vselgt`/`vseleq`/`vselge`, `vmaxnm`/`vminnm`,
  `vrintm`/`vrintp`). These cannot execute on the R1's Cortex-M4F (Armv7E-M, FPv4-SP) at
  all — verified with `readelf`/disassembly, reproducible via
  `~/vendor-cache/gcc-arm-none-eabi-9-2020-q2-update/bin/arm-none-eabi-readelf`. Even a
  licensed copy of these exact archives would not run on the R1; only a Cortex-M4 rebuild
  of the same source could.
- **Second independent public drop found; unblocks nothing.**
  `github.com/linhui200699/ats3089` carries
  `zephyr/framework/sensor/sensor_algo/SensorAlgoHR_GH3x2x_V4200/` — democode v1.6, DrvLib
  v4.2.0.1, HBA interface `pv_v1.0.0` (R1: `pv_v1.1.0`). Notably it includes public
  Cortex-M4 hard-float Goodix algorithm `.a` builds, proving that M4-compatible Goodix
  builds exist — but they are a different (older) algorithm revision, ship under the same
  Goodix clause-5 license, and match no additional R1 bodies.
- **HRNet NET_SIZE census.** Across five public drops spanning three HRNet revisions
  (1033/1567/1861/2599/2979/5951/6660/1269; 1033/1861/3785/2979/2599/5951/1269/660;
  3785/1861/2979/2599/3214), the R1's 4857-word net appears in none of them. The R1 HRNet
  is a fourth, still-private revision; 0x6A138/0x6A140 stay unprovable.
- **Specific residue re-checks against v4.2.0.1.** 0x2A1CC (`GH3X2X_CheckRawdataBuf`) is
  also a `return 0` stub in v4.2.0.1 (unchanged from v4.3.0.0); the 0x2A168 FIFO
  validate-patch loop and the 0x2E8CC WriteReg-0x502 pair have no v4.2.0.1 counterpart.
  All 23 residues remain documented-unprovable.
- **Official channels.** The official Goodix org (`github.com/goodix-ble`, 21 repos)
  contains zero GH-series content; official GH3x2x driver distribution is account-gated on
  goodix.com. The acquisition route is unchanged: a licensed Goodix SDK matching the R1
  revision, in a Cortex-M4-compatible build.
