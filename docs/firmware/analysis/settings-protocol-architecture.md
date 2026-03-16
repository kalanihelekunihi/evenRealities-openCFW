# Settings Protocol Architecture

Consolidated analysis of the settings notification protocol on service `0x0D-01`, covering firmware binary reverse engineering (Thumb disassembly of `ota_s200_firmware_ota.bin` v2.0.7.16) and BLE capture evidence from local packet logs.

---

## 1. Notification Capture Sweep

Scope: local `captures/**/*.txt` packets on service `0x0D-01`.
Method: decode transport packets and protobuf payloads, summarize `f1` and nested `f3={f1=event[,f2=status]}` tuples.

- Total `0x0D-01` packets found: **214**
- Unique payload/event patterns: **5**

| Event (`f3.f1`) | Status (`f3.f2`) | Payload Hex | Count |
|---:|---:|---|---:|
| 0 | - | `08011a00` | 74 |
| 6 | - | `08011a020806` | 72 |
| 11 | - | `08011a02080b` | 28 |
| 6 | 7 | `08011a0408061007` | 24 |
| 16 | - | `08011a020810` | 16 |

### Observations

- All observed packets use top-level `f1=1` and nested `f3` payloads (or empty `f3`).
- Non-empty nested events observed in captures: `6`, `11`, `16`; one variant includes `event=6,status=7`.
- Empty companion packets (`08011a00`) are common around non-empty event packets.

---

## 2. Service Correlation

Scope: local `captures/**/*.txt` only; no network or external references.
Target lane: compact settings status packets on `0x0D-01` (`f1=1`, `f3={f1=event[,f2=status]}` / empty `f3`).

Method:
- Count total compact events by scanning all parseable packet hex runs.
- Build nearest-prior-TX correlation from direction-aware logs only (TX/RX timestamp lines + `Sent:`/`Response:` lines).

- Full compact packet count: **214**
- Direction-aware packet count: **5135** across **9** files
- Direction-aware files: `captures/20260301-1-bleraw.txt`, `captures/20260301-1-testAll.txt`, `captures/20260301-2-bleraw.txt`, `captures/20260301-2-testAll.txt`, `captures/20260302-1-testAll.txt`, `captures/20260302-2-testAll.txt`, `captures/20260302-3-testAll.txt`, `captures/eventLog.txt`, `captures/rawBLE.txt`

| Event Key | Full Count | Correlated Count | Coverage | Top Preceding TX Services |
|---|---:|---:|---:|---|
| `event=0,status=-` | 74 | 42 | 56.76% | 0x80-0x20 (21), 0x0B-0x20 (13), 0x06-0x20 (8) |
| `event=6,status=-` | 72 | 39 | 54.17% | 0x06-0x20 (13), 0x07-0x20 (13), 0x0B-0x20 (13) |
| `event=6,status=7` | 24 | 13 | 54.17% | 0x07-0x20 (13) |
| `event=11,status=-` | 28 | 13 | 46.43% | 0x0B-0x20 (12), 0x0E-0x20 (1) |
| `event=16,status=-` | 16 | 8 | 50.0% | 0x06-0x20 (8) |

### Key Correlation Signals

- **`event=0,status=-`**: strongest preceding TX service is `0x80-0x20` (21/42, 50.0%). Next: `0x0B-0x20` (13). Median line distance: 36.
- **`event=6,status=-`**: strongest preceding TX service is `0x06-0x20` (13/39, 33.33%). Next: `0x07-0x20` (13). Median line distance: 9.
- **`event=6,status=7`**: strongest preceding TX service is `0x07-0x20` (13/13, 100.0%). Median line distance: 4.
- **`event=11,status=-`**: strongest preceding TX service is `0x0B-0x20` (12/13, 92.31%). Next: `0x0E-0x20` (1). Median line distance: 10.
- **`event=16,status=-`**: strongest preceding TX service is `0x06-0x20` (8/8, 100.0%). Median line distance: 5.

### Interpretation

- `event=16,status=-` correlates exclusively with preceding `0x06-0x20` (Teleprompter) TX packets in direction-aware logs.
- `event=11,status=-` is dominated by preceding `0x0B-0x20` (Conversate) TX packets.
- `event=6,status=7` correlates exclusively with preceding `0x07-0x20` (EvenAI) TX packets.
- `event=6,status=-` appears near `0x06-0x20`, `0x07-0x20`, and `0x0B-0x20`, indicating shared render-mode signaling across module transitions.
- `event=0,status=-` frequently follows mode/control transitions and clusters near `0x80-0x20`, `0x0B-0x20`, and `0x06-0x20` in available directional logs.

---

## 3. Callgraph Resolution (Notify Wrappers)

Scope: `ota_s200_firmware_ota.bin` (v2.0.7.16) only.
Method: Thumb disassembly directly from firmware bytes; no external sources.

### BL Target Sweep

| Target | BL Callsites |
|---|---|
| `0x4AACB4` | 0x4AAFA0, 0x4AB016, 0x4AB098 |
| `0x4AAF04` | 0x465296, 0x4652B6, 0x46726E, 0x4F61DE, 0x5431FC, 0x5434DE |
| `0x4AAFB4` | 0x464CF2, 0x4652B2 |
| `0x4AB02C` | 0x466854, 0x466C86, 0x466DE4 |
| `0x4AA60E` | 0x4AA80C, 0x4AAF58 |

### Key Findings

- **F-001**: `0x4AACB4` has exactly three BL callsites in v2.0.7.16: `0x4AAFA0`, `0x4AB016`, `0x4AB098`.
- **F-002**: `0x4AB098` is inside wrapper function `0x4AB02C` (not a standalone third producer function).
- **F-003**: Wrapper `0x4AB02C` sets root-case lane to case5/subcase2 and writes status via `uxtb` before calling `0x4AACB4` at `0x4AB098`.
- **F-004**: Wrapper `0x4AAFB4` sets root-case lane to case5/subcase1 and calls `0x4AACB4` at `0x4AB016`.
- **F-005**: Wrapper `0x4AAF04` zeroes a `0x68`-byte struct, calls helper `0x4AA60E`, and on success forwards that struct to `0x4AACB4` at `0x4AAFA0`.
- **F-006**: Helper `0x4AA60E` stamps leading fields including `byte[0]=2` and `halfword[8]=4` before filling additional status/context lanes from runtime state.

### Disassembly Evidence

#### `wrapper_4AAF04`

```
0x004AAF4E: add r0, sp, #8
0x004AAF50: movs r1, #0x68
0x004AAF56: add r0, sp, #8
0x004AAF58: bl #0x4aa60e
0x004AAF9E: add r0, sp, #8
0x004AAFA0: bl #0x4aacb4
```

#### `wrapper_4AAFB4`

```
0x004AAFBA: add r0, sp, #0xc
0x004AAFC4: strb.w r0, [sp, #0xc]
0x004AAFCA: strh.w r0, [sp, #0x14]
0x004AAFD0: strh.w r0, [sp, #0x18]
0x004AAFD4: str r4, [sp, #0x1c]
0x004AB014: add r0, sp, #0xc
0x004AB016: bl #0x4aacb4
```

#### `wrapper_4AB02C`

```
0x004AB03C: strb.w r0, [sp, #0xc]
0x004AB042: strh.w r0, [sp, #0x14]
0x004AB048: strh.w r0, [sp, #0x18]
0x004AB04E: uxtb r0, r0
0x004AB050: str r0, [sp, #0x1c]
0x004AB05C: uxtb r0, r0
0x004AB098: bl #0x4aacb4
```

#### `helper_4AA60E`

```
0x004AA66C: strb r0, [r4]
0x004AA670: strh r0, [r4, #8]
0x004AA67E: strb r0, [r4, #0xc]
0x004AA684: strb r0, [r4, #0xc]
0x004AA686: bl #0x467274
```

### Interpretation

- `0x4AB098` is confirmed as the internal `BL 0x4AACB4` inside wrapper `0x4AB02C`; it is not an independent third wrapper function.
- The case5 notify wrappers are now structurally explicit in binary terms:
  - `0x4AAFB4`: case5/subcase1 path
  - `0x4AB02C`: case5/subcase2 path (status narrowed via `uxtb`)
- The third caller path (`0x4AAFA0`) is routed through wrapper `0x4AAF04`, which depends on helper `0x4AA60E` and likely stages a non-case5 envelope (`byte[0]=2`, `halfword[8]=4`).

---

## 4. Device Status Wrapper (Case 4 Map)

Scope: `ota_s200_firmware_ota.bin` (v2.0.7.16) only.
Method: Thumb disassembly windows at known addresses (`0x4AAF04`, `0x4AA60E`, caller sites); no external sources.

### Focus

- Resolve `0x4AAF04` behavior and caller contexts.
- Tie helper `0x4AA60E` copy lanes to settings/local-data status fields.
- Replace stale focus on `0x4AB098` callgraph ambiguity with on-wire emission semantics.

### Key Findings

- **F-001**: `0x4AAF04` zeroes a `0x68`-byte struct, calls `0x4AA60E`, then forwards that struct to `0x4AACB4`.
- **F-002**: `0x4AA60E` stamps header lanes (`byte[0]=2`, `halfword[8]=4`) and copies settings lanes into wrapper offsets aligned with local-data case4 state (`+0x20/+0x24/+0x28/+0x2C` propagation).
- **F-003**: All known `0x4AAF04` callers either write settings lanes (`+0x20/+0x24/+0x28/+0x2C`) or gate emission immediately before calling wrapper.
- **F-004**: `0x4AB098` remains internal to `0x4AB02C`; unresolved work is now exact on-wire emission conditions for `0x4AAF04` outputs.

### Wrapper `0x4AAF04`

```
0x004AAF4E: add r0, sp, #8
0x004AAF50: movs r1, #0x68
0x004AAF52: bl #0x482378
0x004AAF58: bl #0x4aa60e
0x004AAF5C: cmp r0, #0
0x004AAFA0: bl #0x4aacb4
```

### Helper `0x4AA60E` Header and Lane Staging

```
0x004AA66A: movs r0, #2
0x004AA66C: strb r0, [r4]            ; byte[0] = 2
0x004AA66E: movs r0, #4
0x004AA670: strh r0, [r4, #8]        ; halfword[8] = 4
0x004AA676: ldrh r1, [r0, #8]
0x004AA678: cmp r1, #4
0x004AA67E: strb r0, [r4, #0xc]
0x004AA684: strb r0, [r4, #0xc]
0x004AA686: bl #0x467274
```

### Helper `0x4AA60E` Settings Copy Map

| Address | Destination | Source |
|---|---|---|
| `0x004AA6F2` | `str r0, [r4, #0x10]` | `[settings+0x01]` |
| `0x004AA6F6` | `str r0, [r4, #0x14]` | `[settings+0x08]` |
| `0x004AA6FA` | `str r0, [r4, #0x18]` | `[settings+0x09]` |
| `0x004AA772` | `str r0, [r4, #0x34]` | `[settings+0x0A]` |
| `0x004AA776` | `str r0, [r4, #0x38]` | `[settings+0x0C]` |
| `0x004AA77E` | `str r0, [r4, #0x44]` | `[settings+0x20]` |
| `0x004AA782` | `str r0, [r4, #0x48]` | `[settings+0x24]` |
| `0x004AA786` | `str r0, [r4, #0x4c]` | `[settings+0x28]` |
| `0x004AA796` | `str r0, [r4, #0x5c]` | `[settings+0x2C]` |
| `0x004AA798` | `bl #0x4a4b92` | (function call) |
| `0x004AA79C` | `str r0, [r4, #0x64]` | (return value) |

### Caller Contexts for `0x4AAF04`

**`0x465296`**:
```
0x0046528E: bl #0x467274
0x00465294: str r1, [r0, #0x2c]
0x00465296: bl #0x4aaf04
```

**`0x4652B6`**:
```
0x004652A2: bl #0x467274
0x004652A8: str r1, [r0, #0x2c]
0x004652B2: bl #0x4aafb4
0x004652B6: bl #0x4aaf04
```

**`0x46726E`**:
```
0x00467262: bl #0x4b513c
0x00467266: str r0, [r4, #0x24]
0x00467268: bl #0x4b5142
0x0046726C: str r0, [r4, #0x28]
0x0046726E: bl #0x4aaf04
```

**`0x5431FC`**:
```
0x005431F4: bl #0x467274
0x005431FA: str r1, [r0, #0x20]
0x005431FC: bl #0x4aaf04
```

**`0x5434DE`**:
```
0x005434D6: bl #0x467274
0x005434DC: str r1, [r0, #0x20]
0x005434DE: bl #0x4aaf04
```

**`0x4F61DE`**:
```
0x004F61DA: cmp r5, #0
0x004F61DC: beq #0x4f61e2
0x004F61DE: bl #0x4aaf04
```

### Interpretation

- The helper's header lane write (`halfword[8]=4`) plus settings-lane copy map strongly indicates that `0x4AAF04` emits settings root-case4 local-data/status envelopes through shared notifier `0x4AACB4`.
- Caller contexts match this interpretation: they update status lanes (`+0x20/+0x24/+0x28/+0x2C`) then immediately dispatch via `0x4AAF04`.

---

## 5. Root-Case Wrapper Sweep (Cross-Version)

Scope: `ota_s200_firmware_ota.bin` across local versions v2.0.1.14 through v2.0.7.16.
Method: scan for `strh.w` root-case staging slot (`ad f8 14 00`) and extract preceding `movs r0,#imm` when encoded as `xx 20`.

| Version | Hits | imm=5 | imm=6 | imm=7 | unknown-imm |
|---|---:|---:|---:|---:|---:|
| v2.0.1.14 | 7 | 1 | 0 | 0 | 5 |
| v2.0.3.20 | 9 | 2 | 0 | 0 | 6 |
| v2.0.5.12 | 9 | 2 | 0 | 0 | 6 |
| v2.0.6.14 | 9 | 2 | 0 | 0 | 6 |
| v2.0.7.16 | 9 | 2 | 0 | 0 | 6 |

### Observations

- Root-case wrapper staging with immediate `5` is present in every version (consistent with case5 notify wrappers).
- No direct root-case wrapper staging with immediate `6` or `7` was found in any scanned version.
- This supports the hypothesis that descriptor-declared root cases `6/7` are not emitted by known wrapper constructors in these builds.

---

## Summary of Notify Architecture

Three wrapper functions feed into shared notifier `0x4AACB4`:

| Wrapper | Root Case | Subcase | Callsites |
|---|---|---|---|
| `0x4AAF04` | case4 (local-data/status) | N/A (header-stamped) | 0x465296, 0x4652B6, 0x46726E, 0x4F61DE, 0x5431FC, 0x5434DE |
| `0x4AAFB4` | case5 | subcase1 | 0x464CF2, 0x4652B2 |
| `0x4AB02C` | case5 | subcase2 (uxtb-narrowed) | 0x466854, 0x466C86, 0x466DE4 |

Event-to-service mapping from capture correlation:

| Event | Status | Primary TX Service | Confidence |
|---|---|---|---|
| 0 | - | 0x80-0x20 (Auth) | 50% of correlated |
| 6 | - | 0x06/0x07/0x0B (shared render) | ~33% each |
| 6 | 7 | 0x07-0x20 (EvenAI) | 100% |
| 11 | - | 0x0B-0x20 (Conversate) | 92% |
| 16 | - | 0x06-0x20 (Teleprompter) | 100% |

---

## Open Work

1. Decode `0x4AACB4 -> 0x46F6EA` route argument transitions specifically for `0x4AAF04` origin packets to lock channel/shape semantics in mixed traffic.
2. Correlate `0x4F61DE` conditional branch (`r5 != 0`) with capture windows to determine trigger family when wrapper emits without explicit nearby settings writes.
3. Add simulator replay fixtures that assert selector4 subtype3 gate changes emit both case5/subcase1 and case4 local-data notifies in firmware-like order.

---

## Source Artifacts

- `captures/firmware/analysis/2026-03-05-settings-compact-notify-capture-sweep.json`
- `captures/firmware/analysis/2026-03-05-settings-compact-notify-service-correlation.json`
- `captures/firmware/analysis/2026-03-05-settings-device-status-wrapper-case4-map.json`
- `captures/firmware/analysis/2026-03-05-settings-notify-wrapper-callgraph-resolution.json`
- `captures/firmware/analysis/2026-03-05-settings-root-case-wrapper-sweep.json`
