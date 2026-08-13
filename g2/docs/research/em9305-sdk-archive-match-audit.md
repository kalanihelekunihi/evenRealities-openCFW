# EM9305 SDK archive-to-stock match audit

Status date: 2026-08-08  
Status: six SDK archives authenticated; 98 stock functions confirmed exact;
toolchain and former anonymous protocol-timer range identified; all bytes
remain stock-retained.

This focused first-six audit is now extended by the
[16-archive Packetcraft/EM census](em9305-expanded-sdk-archive-census.md),
which brings combined exact-function coverage to 1,244 functions / 139,782
bytes without changing stock-retained byte ownership.

## Result

The third-party EM9305 SDK v4.2 oracle contains relocation-bearing ARCv2 ELF
archives, not only headers and symbol maps. `tools/compare_em9305_sdk_archive.py`
extracts each object, masks only the four supported ARC relocation fields,
and scans every halfword-aligned stock application address. Unknown relocation
types fail closed. Expected matches are then required at their independently
recovered stock addresses.

The six enforced lanes confirm 98 exact stock functions totaling 7,172 bytes.
Ninety-two are globally unique normalized fingerprints totaling 7,146 bytes;
the difference is six small or intentionally repeated QP/C functions whose
known addresses still compare exactly. Three QP internal hooks are required to
differ from the SDK defaults and remain explicit vendor customizations.

| SDK archive | Git blob | SHA-256 | Exact stock functions | Unique fingerprints / bytes | Important result |
|---|---|---|---:|---:|---|
| `libs/third_party/QPC/lib_QPC.a` | `26fc11bf0144caab77608fa5794e544d4d1d8a38` | `c8b5834ca8c3b42fde7e2f8447772800561ddd5897123918e8353807242f8db5` | 36 | 30 / 3,018 | All 22 portable bodies, QF/QK/BSP hooks, BSP init, and QK SWI port confirmed |
| `libs/pml/lib_pml.a` | `45c88f15bc6367dc15e3cdcabb9a23be74bb9934` | `e57be8e7fd4352e99c3437bbea0563e1b1add61228781925f7212a07f0a04ce2` | 44 | 44 / 3,000 | PML power, sleep, RF-power, voltage-monitor, and PML-SVLD ISR bodies located |
| `libs/sleep_manager/lib_sleep_manager.a` | `05af021ac9132dc8c727913c4382eba9019aebdb` | `82968846c25b2a6685aa357386ad1dcb6bbe33bb138359de66ce91d10d600856` | 1 | 1 / 52 | `SLEEP_MANAGER_RCCAL_Callback` exact; configured sleep manager named separately |
| `libs/sleep_timer/lib_sleep_timer.a` | `3713f176b7f1614920a3043c4dcb41ba730e3fe0` | `cbf143b6d90832b349925bc1cfdd0963c2a7102b66c11b6aee9277739dcbe1b9` | 3 | 3 / 128 | init, compare, and wakeup-time bodies located |
| `libs/prot_timer/lib_prot_timer.a` | `cf8f1f22ea840568c83c6a2662c86e7d95b6581a` | `8ea99f2afa095f90d1c9555d748908bb6e03805db87d38a80a51f640f11788c7` | 13 | 13 / 932 | protocol-timer closure reaches the QP cluster boundary |
| `libs/unitimer/lib_unitimer.a` | `07ed4df5a464637adf024d383bc89d2fd0b57bb0` | `8699c09a59e65fec8f349a67fc445b8ab931a9e736d4bfabe01ebd773c005bd4` | 1 | 1 / 16 | `Timer_RegisterModule` located |

The authenticated archive `.comment` sections pin the compiler to Synopsys
MetaWare ARC Compiler **T-2022.09 build 004**, LLVM 14.0.6, EM-Micro target,
ARCv2 EM, and `-Os`. This replaces the earlier generic-compiler hypothesis.
The SDK's `MW_VERSION=2019.09` selects its bundled MetaWare runtime-library
directory; it is not the compiler version that produced these QP/vendor
objects.

## QK ARC port closure

The QP/C archive's `qk_port.s.obj` establishes this exact stock layout:

| Stock range | Bytes | Identity/state |
|---|---:|---|
| `[0x00302518,0x0030251C)` | 4 | `qkPortDummy`; exact archive bytes |
| `[0x0030251C,0x003025CE)` | 178 | `IRQHandler_SWI0`; exact after relocation normalization |
| `[0x003025CE,0x003025D0)` | 2 | compiler alignment |
| `[0x003025D0,0x003025DC)` | 12 | `QK_noPreemption`; exact archive bytes |
| `[0x003025DC,0x003025F6)` | 26 | `QK_restoreContext`; exact after relocation normalization |
| `[0x003025F6,0x003025F8)` | 2 | compiler alignment |
| `[0x003025F8,0x00302664)` | 108 | `IRQHandler_SWI1`; exact archive bytes |

`BSP_Init` is independently unique at `[0x00302E80,0x00302E8E)`. Together
these results close the previously unresolved QK SWI entry/restore port rather
than inferring interrupt behavior solely from portable QK call sites.

## Protocol-timer/QP boundary closure

The former 280-byte anonymous prefix of the QP discovery cluster is fully
classified:

| Stock range | Bytes | Identity/state |
|---|---:|---|
| `[0x00310C00,0x00310C08)` | 8 | tail of vendor-modified `ProtTimer_SetHwTriggerEnable`; full function begins at `0x00310BE0` |
| `[0x00310C08,0x00310CEA)` | 226 | exact `ProtTimer_StoreConfig` archive body after relocation normalization |
| `[0x00310CEA,0x00310CEC)` | 2 | compiler alignment |
| `[0x00310CEC,0x00310D18)` | 44 | exact `ProtTimer_UpdateRestartTime` archive body after relocation normalization |

The SDK version of `ProtTimer_SetHwTriggerEnable` has the same 40-byte size,
register target, and role, but stock adds saved-status `CLRI; SYNC` / `SETI`
protection. It is therefore named and behaviorally bounded but deliberately
classified as vendor-modified, not an exact archive match. No anonymous
executable byte remains inside `[0x00310C00,0x003117EC)`.

## Sleep path

The prior 516-byte anonymous idle callee at `[0x003126E0,0x003128E4)` is
`SLEEP_MANAGER_GoToSleep`. Its SDK reference body is 508 bytes and does not
normalize-match stock, consistent with linked configuration/vendor changes;
the stock boundary remains 516 bytes because its final delayed call and branch
occupy the additional eight bytes. The adjacent 52-byte
`SLEEP_MANAGER_RCCAL_Callback` at `[0x003128E4,0x00312918)` is an exact archive
match. The sleep manager remains stock-retained and only partially behaviorally
reversed.

## Reproduction and evidence hashes

On Lorelei, run each archive with the authenticated stock image and GNU ARC
binutils 2.46:

```sh
python3 tools/compare_em9305_sdk_archive.py \
  --image firmware_ble_em9305.bin \
  --archive lib_QPC.a \
  --archive-kind qpc \
  --binutils-dir /path/to/arc-linux-gnu/bin \
  --json
```

The enforced JSON report SHA-256 values are:

| Lane | Report SHA-256 |
|---|---|
| QP/C | `c19dae056a024ac32ad69783be5f2be510f60eb166658023e128e1d0cb493b35` |
| PML | `ecf3255b02f16d73336acdd8e3ead86f7df0bce770ad6ff5897d615b5a1eea6d` |
| sleep manager | `ffbf2937e169b6ae7628b234ff695564ad5e4b5523c3783c17932bdd9535b1ab` |
| sleep timer | `a69ddf181bd9b7219c4104f99482e59a527018aab84452961c535c32efea0f54` |
| protocol timer | `f522d99703ecc6caaac282f85c76bce3e7061e1015af037865b4c49b41c55acd` |
| unitimer | `b2a6d56e3986a3505a205f8ca1cf07f37556f56a3aae1d9e0e3ee3999a2160c4` |

The public SDK mirror is an evidence oracle, not an authoritative EM release
repository, and has no repository-level license declaration. These archives
must not be copied into a production source package without an applicable
license. Until then, the authenticated stock spans remain cut-forward.
