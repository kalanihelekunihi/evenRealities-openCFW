# CMSIS-FreeRTOS thread-creation source audit

Status: production source-owned; Apple and Linux profiles replayed  
Target: official G2 `s200_v2.2.6.10` Apollo application

## Result

The complete linked `osThreadNew` entry at
`[0x004490E2,0x004491AA)` is now source-owned. Its 200 physical bytes hash to
`9c6a8120325e47a0a098156f0a03d4716d0c8cb99df99144bb33f869d7b7aac6`.
The entry redirects atomically to `runtime_cmsis_thread_new.c`; no interior
entry, adjacent `osThreadGetId` byte, or inferred address is claimed.

The implementation is a bounded Apache-2.0 adaptation of Arm
CMSIS-FreeRTOS v10.5.1 `osThreadNew`. It preserves the stock defaults and
validation exactly:

- default stack depth 1,024 `StackType_t` words and priority 24;
- rejection from interrupt context, for a null function, priority outside
  `1..56`, or the unsupported joinable bit;
- byte-to-word stack conversion by division by four;
- static creation only with non-null control-block and stack storage, a
  positive stack size, and the G2 control-block threshold `0x70`;
- dynamic creation only when control-block storage/size and stack storage are
  absent; and
- the V10.5.1 `configSTACK_DEPTH_TYPE` 16-bit cast before `xTaskCreate`.

Hosted tests cover both creation paths, all validation gates, malformed
attribute combinations, default/overridden attributes, static threshold
edges, dynamic failure, and deliberate 16-bit stack-depth truncation.

## Origin, version, and commit boundary

The maintained source pin is annotated tag `v10.5.1`, tag object
`34e6e4c403c17de35ec0acf29610e374dc938604`, peeled commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`, and tree
`d3689a816acc77a3f0b7d35439d666ad8434b6ba`. The exact 70,106-byte
`cmsis_os2.c` is Git blob `88dca1d881f1a960872572a8a0efd94cde19dcea`
with SHA-256
`8a0d60b56ad30c4f7957f64fa581158017b6812ec94b832d974c773ae4f2bc36`.
That blob first appeared at commit
`13acfbef7be85119fc6bc56832c455d4547d92c7`; use the tagged commit for the
reproducible dependency closure and the first-appearance commit only for
source archaeology.

The stock `UXTH` before dynamic task creation also contains the type-casting
correction called out by CMSIS-FreeRTOS release 10.4.6 issue 51. This supports
the v10.5.x source interval but does not uniquely prove Even's checkout.
Source-identical and dead-code-only history still prevents a unique historical
commit claim.

## FreeRTOS and vendor seam

The wrapper calls the authenticated stock creators at fixed complete entries:

| Provider | Stock span | Bytes | SHA-256 |
|---|---:|---:|---|
| `xTaskCreateStatic` | `[0x00454820,0x004548BA)` | 154 | `21c10ddaf25950d84acbcf302f2de18d3471dd5321c4cd7aa50dcc8a6f29debe` |
| `xTaskCreate` | `[0x004548BA,0x00454938)` | 126 | `d4210ea6c22d8fb0aee4d89d3a1666874a489e77516041d6946bef9a05058b21` |

Those creators and their initializer are already provenance-bounded to
FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c`. The G2 `StaticTask_t` threshold
is `0x70`, not pristine upstream's `0x6C`, because of the separately recovered
one-word vendor TCB extension. Its minimal semantic patch is pinned by
`g2-tcb-v10.5.1.patch`; the vendor's original field name and private patch
commit remain unobservable. Retaining these two authenticated creator entries
keeps that bounded vendor seam explicit while removing the CMSIS wrapper from
opaque ownership.

## Production roots

| Profile | Source leaf | Overlay | Component | Package |
|---|---|---|---|---|
| Apple Clang 21 | 168 bytes at 137,092 / `7c9116f267ecf91961fa93271bab29fae6b6fab22626aea69d9d3de5a74bbdcd` | 137,260 / `89c779a63fdf9bde7008d17738d2aa392b48b7d8246532abbaa77c7bec15ce0d` | 3,660,656 / `a4b02fe3bc71e035db56cee97992f52f38f613dd3e22f5379b977dd834056de0` | 4,439,150 / `fcfed4ff1e555702d16ddef40bd155f6c11b8284c54f11ff352ebf25d98d2e8e` |
| Linux Clang 22.1.8 | 166 bytes at 138,972 / `e62db8f5166ad5936efc1243de4b929b4cd95b769bab6ab2d0b88d5d5ad2c16e` | 139,138 / `9bf5b5405f42d05043f784340d45bb75925cf7e40c6e8a11d51441fd27489694` | 3,662,534 / `9ea182ea2d84784754b71d7eff86cec792924ed1535ae4c132f2526669559f19` | 4,441,028 / `3a621893611484516cf0a2bc35e117fc44064ace1d84747005dd5658ec5e44cd` |

The canonical package accounts for 137,945 source bytes, 98,242 generated
bytes, and 4,202,963 opaque bytes. The stock entry is explicitly split as a
generated source-entry replacement, rather than left mislabeled inside an
opaque envelope. CMSIS ownership is now 36/38 linked public APIs and all five
private helpers. Only the writer-coupled `osKernelInitialize` and
`osKernelStart` pair remains stock-backed. No image was signed or flashed and
no hardware was accessed.
