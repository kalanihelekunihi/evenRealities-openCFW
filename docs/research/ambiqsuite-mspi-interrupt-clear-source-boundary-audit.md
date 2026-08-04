# Apollo510 MSPI interrupt-clear source-boundary audit

## Verdict

`am_hal_mspi_interrupt_clear` is an unequivocal Apollo510 HAL source boundary
for the G2 NOR/MSPI transport. The official main and boot images contain
byte-identical 48-byte implementations, and every operation maps directly to
AmbiqSuite 5.1.0:

- validate the initialized Ambiq handle prefix and `0xBEBEBE` magic;
- read `ui32Module` at handle offset `+4`;
- write the supplied mask to `MSPIn(module)->INTCLR`;
- perform the required volatile `INTSTAT` readback; and
- return `AM_HAL_STATUS_INVALID_HANDLE` (`2`) or success (`0`).

The correct source candidate is the complete Ambiq
[`mcu/apollo510/hal/mcu/am_hal_mspi.c`](https://github.com/AmbiqMicro/ambiqhal_ambiq/blob/5efc0228528a8adce5eae0d226fac85d2551eb3b/mcu/apollo510/hal/mcu/am_hal_mspi.c)
translation unit at commit
[`5efc0228528a8adce5eae0d226fac85d2551eb3b`](https://github.com/AmbiqMicro/ambiqhal_ambiq/commit/5efc0228528a8adce5eae0d226fac85d2551eb3b),
not a decompiled local rewrite.

The pinned Apollo510 HAL and CMSIS Core dependency closure is now vendored in
OpenCFW and verified offline. This makes the exact upstream reuse proof
self-contained. The leaf is not yet production-integrated: it still must be
compiled from the complete translation unit with section GC and connected to
authenticated main/boot redirects. It should not be integrated as a
hand-copied standalone overlay because its handle type is private to
`am_hal_mspi.c`.

No hardware, debugger, serial, flash, or write operation was performed.

## Complete-translation-unit section-GC proof

The authenticated, unmodified 5.1.0 `am_hal_mspi.c` compiles cleanly for
`arm-none-eabi`/Cortex-M55 with API validation enabled. An isolated proof then
roots only `am_hal_mspi_interrupt_clear` and links with `--gc-sections`:

```sh
python3 tools/prove_ambiq_mspi_interrupt_clear_gc.py \
  --sdk-root third_party/ambiqsuite-apollo510 \
  --cmsis-core third_party/cmsis-core/CMSIS/Core/Include \
  --lld /path/to/lld \
  --json
```

`--lld` is optional when `ld.lld` or `lld` is already on `PATH`. The local
proof used Apple Clang 21.0.0 and LLD 22.1.8. Its authenticated full object
contained 20 unresolved references used by other MSPI functions and a
`0x2390`-byte private `g_MSPIState`. The final statically linked ARM ELF
contained:

| Fact | Result |
|---|---:|
| `.text` | 48 bytes |
| global code/data symbols | `am_hal_mspi_interrupt_clear` only |
| unresolved symbols | 0 |
| `g_MSPIState` retained | no |
| leaf text relocations | 0 |

This confirms that complete-TU reuse does **not** require linking CMDQ,
clock-manager, power-control, delay, or interrupt-master dependencies merely
to retain this leaf. It also avoids copying a private Ambiq type into OpenCFW.

The compile proof includes static assertions for the exact private/public ABI
seam used by this function:

```text
sizeof(am_hal_handle_prefix_t)               = 4
offsetof(am_hal_mspi_state_t, prefix)        = 0
offsetof(am_hal_mspi_state_t, ui32Module)    = 4
MSPI0_BASE                                   = 0x40060000
MSPI1_BASE - MSPI0_BASE                      = 0x1000
offsetof(MSPI0_Type, INTSTAT)                = 0x204
offsetof(MSPI0_Type, INTCLR)                 = 0x208
```

The compiled Clang leaf is also 48 bytes, but it is not byte-identical to the
stock image because of ordinary compiler instruction-selection differences.
Source equivalence and ABI/register equivalence are the supported claim; a
byte-for-byte reproduction is not required.

## Required build and ABI seams

The focused disassembly and compile proof reduce the integration contract to
the following concrete requirements:

- target 32-bit little-endian Arm/Thumb for Cortex-M55;
- keep Ambiq API validation enabled (do not define
  `AM_HAL_DISABLE_API_VALIDATION`), because both stock copies check the
  initialized bit and `0xBEBEBE` magic;
- compile the full authenticated `am_hal_mspi.c` with
  `-ffunction-sections -fdata-sections` and link with `--gc-sections`;
- use the pinned Apollo510 register definitions and a compatible CMSIS Core
  header set; and
- either create the handle with the same source translation unit or preserve
  the proven first-eight-byte handle ABI shown above.

The target linker script must also place or discard `.ARM.exidx` deliberately.
LLD retained 16 bytes of unwind-index metadata in the isolated proof even
though the leaf itself is only 48 bytes. This is an artifact-layout seam, not
a runtime HAL dependency.

For this leaf, no FPU, CMDQ, power-control, clock-manager, delay, interrupt
master, secure/non-secure veneer, or writable-data ABI is reachable. The
function has no relocation to `g_MSPIState` and uses no request enum.

One compiler seam remains if a non-GCC/Clang ABI is selected: the Ambiq handle
prefix uses C bitfields. The stock word and the Cortex-M55 Clang build both
encode initialized-plus-magic as `0x01BEBEBE`; an IAR build should retain an
equivalent compile/static assertion before being treated as interchangeable.

## Reproducer

The standard-library-only analyzer authenticates both official images, exact
function bytes, boundaries, literals, direct `BL` topology, and absence of
stored even or Thumb entry pointers:

```sh
python3 tools/analyze_g2_mspi_interrupt_clear.py
python3 tools/analyze_g2_mspi_interrupt_clear.py --json
```

An available Ambiq source tree can additionally be authenticated:

```sh
python3 tools/analyze_g2_mspi_interrupt_clear.py \
  --ambiq-source \
    third_party/ambiqsuite-apollo510/mcu/apollo510/hal/mcu/am_hal_mspi.c
```

The complete vendored dependency closure is authenticated without a network
or compiler:

```sh
python3 third_party/ambiqsuite-apollo510/verify_snapshot.py
python3 third_party/cmsis-core/verify_snapshot.py
```

Pinned upstream identities:

| Property | Value |
|---|---|
| Repository | `AmbiqMicro/ambiqhal_ambiq` |
| Commit | `5efc0228528a8adce5eae0d226fac85d2551eb3b` |
| Commit subject | `Import Apollo510 HAL from AmbiqSuite SDK 5.1.0` |
| File revision | `release_sdk5p1p0-366b80e084` |
| Source function | `am_hal_mspi_interrupt_clear`, lines 4135–4161 |
| File Git blob | `c12ef914660227aba3ebef3a0fb3ec749510c1bc` |
| File SHA-256 | `5a91ab0c67bda4bd61c7d436b94b5a7c81693b948a331d282ae10e88cc5bf85f` |
| License | BSD-3-Clause |

The Ambiq snapshot contains 71 authenticated upstream files and pins tree
`02b79dbf428a8cded053c65c92cc58fa5fdb8e78`. The sibling CMSIS Core
snapshot contains the seven reached headers plus its Apache-2.0 license from
CMSIS_5 commit `d23a6949a0331ca96853bcd98b0fdcc4db47184c`, tree
`3474af187114165f3623732474e4e1bd4b3d01d8`. Both `PROVENANCE.json`
inventories record each file's size, Git blob SHA-1, and SHA-256.

## Official bounds and identity

| Image | Installed range | Bytes | SHA-256 |
|---|---:|---:|---|
| Main | `[0x004C23DE,0x004C240E)` | 48 | `4b01a25a8075cf158eb59da277f8730e36c751ee01c67bae86bc172ec877bd48` |
| Boot | `[0x00426506,0x00426536)` | 48 | `4b01a25a8075cf158eb59da277f8730e36c751ee01c67bae86bc172ec877bd48` |

Both ranges contain exactly:

```text
0200002806d0006820f07e40dff8f036984201d002200ae0
5068b84a12eb0033c3f8081212eb0032d2f8040200207047
```

The preceding function in both images ends with `pop {r4}; bx lr`
(`10bc7047`). The following interrupt-service function begins immediately
with `push.w {r0,r1,r2,r3,r4,r5,r6,r7,r8,lr}` (`2de9ff41`). There are no
external branches into the body.

The two literal pools independently resolve the same ABI and register values:

| Evidence | Main literal | Boot literal | Value |
|---|---:|---:|---:|
| initialized handle word | `0x004C2ADC` | `0x00426C04` | `0x01BEBEBE` |
| MSPI register base | `0x004C26DC` | `0x00426804` | `0x40060000` |

The high byte's bit zero in `0x01BEBEBE` is the initialized bit combined with
the 24-bit `0xBEBEBE` magic. The body also proves:

```text
handle ui32Module offset: +0x004
module register stride:   0x1000
INTSTAT offset:            +0x204
INTCLR offset:             +0x208
```

## Stock call topology

The complete aligned Thumb `BL` scan finds these callers and no stored
function pointers.

### Main

| Call site | Role |
|---:|---|
| `0x0046F4FE` | G2 MSPI1/NOR IRQ wrapper: status-get, clear, service |
| `0x0046FD4A` | G2 MX25U25643G/MSPI1 low-level initializer |
| `0x00592672` | additional MSPI IRQ wrapper |
| `0x0059CE4C` | additional MSPI transaction setup |
| `0x0059D0D8` | additional MSPI controller initializer |
| `0x005BBD62` | additional MSPI IRQ wrapper |

The littlefs/NOR path is specifically the first two entries. The initializer
clears mask `0x1A80` before enabling that mask. The IRQ wrapper reads status,
clears precisely that returned status, then passes it to
`am_hal_mspi_interrupt_service`.

### Boot

| Call site | Role |
|---:|---|
| `0x0041FE1A` | boot MSPI1/NOR IRQ wrapper: status-get, clear, service |
| `0x004203CC` | boot MX25U25643G/MSPI1 low-level initializer |

The boot initializer likewise supplies mask `0x1A80`.

## Exact upstream mapping

AmbiqSuite 5.1.0 source performs:

```c
if (!AM_HAL_MSPI_CHK_HANDLE(pHandle)) {
    return AM_HAL_STATUS_INVALID_HANDLE;
}
ui32Module = pMSPIState->ui32Module;
MSPIn(ui32Module)->INTCLR = ui32IntMask;
*(volatile uint32_t*)(&MSPIn(ui32Module)->INTSTAT);
return AM_HAL_STATUS_SUCCESS;
```

The stock instruction sequence preserves every material operation, including
the easy-to-miss volatile readback at body offset `+0x28`. Its address
calculation is `0x40060000 + module*0x1000`; the write and read offsets are
`+0x208` and `+0x204`.

This is stronger than a generic register-level resemblance:

1. main and boot independently contain the same complete machine body;
2. both resolve the same handle and register literals;
3. both use the upstream return values and ordering; and
4. the complete direct-call topology is accounted for.

## Version limit

The exact `am_hal_mspi_interrupt_clear` source body is also present in
AmbiqSuite 5.0.0 (`release_sdk5p0p0-5f68a8286b`). Therefore this leaf proves
that the 5.1.0 source is an exact reusable implementation, but it does **not**
uniquely prove that Even's opaque historical build used SDK 5.1.0.

That distinction matters for larger MSPI integration. The G2 binary's
`am_hal_mspi_control` request ordinals differ from the public 5.1.0 header.
All downstream board code must be rebuilt against named 5.1.0 enums; opaque
stock callers must not pass their raw numeric request values into a 5.1.0
source HAL.

The selected interrupt-clear leaf has no request-enum argument, so that
specific mismatch does not affect it.

## Reuse assessment and ranked integration plan

1. **Vendored and mechanically proven:** retain the authenticated AmbiqSuite
   5.1.0 Apollo510 and CMSIS Core snapshots, compile the complete
   `am_hal_mspi.c` with function/data sections, and retain only
   `am_hal_mspi_interrupt_clear`. Full-TU section GC is proven; production
   overlay integration and authenticated main/boot redirects remain.
2. **Then:** rebuild the recovered G2 MSPI1 IRQ wrapper and initializer
   against the same named 5.1.0 headers, eliminating the private stock-handle
   ABI seam.
3. **Then:** bring over `interrupt_status_get`, `interrupt_enable`, and
   `interrupt_service` from the same translation unit as one coherent IRQ
   cluster.
4. **After board-source recompilation:** integrate named MSPI configure,
   device-configure, control, PIO-transfer, and retained-power APIs.
5. **Hardware gate:** first exercise only JEDEC ID and bounded read-only NOR
   access. Program and erase remain disabled pending golden-image and
   disposable-device power-loss testing.

The current OpenCFW tree contains the complete dependency closure exercised
by the proof. The exact pinned inputs include:

| Input | SHA-256 |
|---|---|
| `am_mcu_apollo.h` | `c79aef5ca1e75c11e78b023cfbb39ca478245ec4997c537b97f6c939d317c457` |
| `apollo510.h` | `b6ca35dc828ef95825c0a22f06e6ca5ed558a6542dc74310515fdc350051a797` |
| `am_hal_global.h` | `05218d399ad4bb1338aa76d84f76bcc9e8f8585cf8c1530e262316cfddc6b075` |
| `am_hal_mspi.h` | `2a682bb7c1618982d6a802f3220a38696cd594c89d90e64b1a698d226b0a557b` |
| `am_hal_status.h` | `7ffa44277fab4731bdcb742c807c9f026aadfe8456545d8f04f5053621661ee2` |
| `core_cm55.h` | `23c98f9996ce044c7a4a3affe4d7be36d15c67d4a1389d604e06d02672bdb1d7` |
| `cmsis_version.h` | `184c19fd3ee73632edf35a0b4d49cd48be75fbf49e6ccb19d9db05fa83bea4b3` |

Therefore exact upstream reuse is mechanically safe and self-contained for
this leaf, but it is not yet part of either production overlay. Remaining work
is to add a production build path that compiles the complete authenticated
translation unit with the proven Cortex-M55 flags, retains only the leaf, and
installs authenticated main/boot redirects. Broader source-owned G2 MSPI
callers must be compiled against the same named 5.1.0 headers; opaque stock
callers must not cross the known raw `am_hal_mspi_control` ordinal seam. No
reverse engineering of this leaf's algorithm is required.
