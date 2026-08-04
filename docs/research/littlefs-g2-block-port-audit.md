# G2 littlefs block-device port audit

## Verdict

The Apollo-main and bootloader littlefs block-device callbacks are recovered
to source-level fidelity. They use the standard littlefs v2.10.1 callback ABI,
the same hard-coded external-flash partition and geometry, and the same
zero/nonzero result policy. Their instruction streams are identical after
normalizing link relocations and diagnostic literal addresses.

**A safe read-only source port is implementable now.** The bounded first
implementation should:

1. compile the vendored littlefs v2.10.1 core with `LFS_READONLY`;
2. install only the recovered read callback, with explicit bounds checks;
3. mount directly, without the stock recovery initializer; and
4. leave program, erase, format, boot-count update, and recovery remount paths
   unreachable.

This is not yet evidence that a fully source-owned external-NOR transport is
safe to deploy. A first read-only port can call the authenticated stock
MX25U25643G read seam. Replacing that last seam requires the board's complete
MSPI initialization, pin, timing, clock, XIP-aperture, and power policy. A
captured external-flash golden image is also still required before accepting
the vendored littlefs core on hardware.

No flash, serial, debug, pogo, or hardware write was performed during this
audit.

## Reproducer and inputs

The read-only reproducer is:

```sh
python3 tools/analyze_g2_littlefs_ports.py
python3 tools/analyze_g2_littlefs_ports.py --json
```

It verifies every hash in this report, both 84-byte configuration objects,
the callback call targets, the immediately underlying driver functions,
source-path evidence, diagnostic formats, and normalized main/boot callback
equivalence. It only reads local files.

| Image | SHA-256 | Address mapping |
|---|---|---|
| `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` | 32-byte package header; installed payload at `0x00438000` |
| `blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin` | `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5` | Raw image at `0x00410000` |

Both authenticated images contain these exact build paths:

```text
D:\01_workspace\s200_ap510b_iar_git\third_party\littlefs\port\littlefs_mx25u25643g_porting.c
D:\01_workspace\s200_ap510b_iar_git\driver\flash\drv_mx25u25643g.c
```

The chip identity is therefore not a family-level guess: it is a Macronix
MX25U25643G 256-Mbit/32-MiB serial NOR. The recovered command stream also
matches the manufacturer's command set:

- `0x6C`: QREAD4B, quad-output read with a four-byte address;
- `0x02`: page program while the device is in four-byte-address mode;
- `0x20`: 4-KiB sector erase while in four-byte-address mode;
- `0x06`: write enable; and
- `0x04`: write disable.

The primary device reference is the
[Macronix MX25U25643G datasheet](https://www.macronix.com/Lists/Datasheet/Attachments/8766/MX25U25643G%2C%201.8V%2C%20256Mb%2C%20v1.1.pdf).

## Configuration and partition geometry

Apollo main has an 84-byte `struct lfs_config` at `0x006E83A4`,
SHA-256
`f38bd899e180d29ee60609a2452d25c2d2d6c6fef4eb455064e23a6ca7c6e813`.
The bootloader object is at `0x00431070`, SHA-256
`724c351d2136e3c2f10b59ad84d547da4632739ea1f20eb839e9af2cfbd5b6e8`.

| Field | Main | Boot |
|---|---:|---:|
| `context` | `0` | `0` |
| `read` | `0x004763B9` | `0x004212D9` |
| `prog` | `0x004763F1` | `0x00421311` |
| `erase` | `0x00476429` | `0x00421349` |
| `sync` | `0x004764DD` | `0x004213D5` |
| `read_size` | 16 | 16 |
| `prog_size` | 256 | 256 |
| `block_size` | 4,096 | 4,096 |
| `block_count` | 3,008 (`0xBC0`) | 3,008 (`0xBC0`) |
| `block_cycles` | 500 | 500 |
| `cache_size` | 4,096 | 4,096 |
| `lookahead_size` | 256 | 256 |
| `compact_thresh` | 0 | 0 |
| Optional buffers and limits | all zero | all zero |

Read and program calculate:

```c
address = 0x01400000u + block * 0x1000u + offset;
```

Erase calculates the same expression without `offset`. Consequently:

```text
partition start:       0x01400000
partition size:        0x00BC0000 = 12,320,768 bytes = 11.75 MiB
partition end:         0x01FC0000 exclusive
physical NOR size:     0x02000000 = 32 MiB
space after partition: 0x00040000 = 256 KiB
```

The callback does not read `cfg->block_size`, `cfg->block_count`, or
`cfg->context`; it ignores the configuration pointer. Changing the table
without changing the port would therefore not change its address mapping.

## Exact callback ABI

The ABI is the upstream littlefs callback ABI on 32-bit AAPCS/Thumb:

```c
int read(
    const struct lfs_config *cfg, // r0, ignored
    uint32_t block,               // r1
    uint32_t offset,              // r2
    void *buffer,                 // r3
    uint32_t size                 // caller stack
);

int prog(
    const struct lfs_config *cfg, // r0, ignored
    uint32_t block,               // r1
    uint32_t offset,              // r2
    const void *buffer,           // r3
    uint32_t size                 // caller stack
);

int erase(
    const struct lfs_config *cfg, // r0, ignored
    uint32_t block                // r1
);

int sync(
    const struct lfs_config *cfg  // r0, ignored
);
```

Read and program push eight registers, then load `size` from `[sp,#0x20]`.
This proves the fifth-argument location independently of the recovered
header. Erase consumes only `r1`. Sync is exactly:

```asm
movs r0, #0
bx   lr
```

## Callback body evidence

| Image | Callback | Range | Bytes | SHA-256 | Direct device-driver call |
|---|---|---:|---:|---|---:|
| Main | read | `0x004763B8..0x004763EF` | 56 | `7e8b4188becb1bdb7d8a777ef724b61ee9bf9fc0e48459e35bdca22e47f11b58` | `0x00471021` |
| Main | program | `0x004763F0..0x00476427` | 56 | `dbabdf2f5643d8ea04715e492ffccc397fad2381af5a5d1ef4d17f89f46fe1d6` | `0x004708A9` |
| Main | erase | `0x00476428..0x00476451` | 42 | `7f21bcf5257604c375938af66981e04db70054eb897b387e4af5354eb669ad2c` | `0x0047075D` |
| Main | sync | `0x004764DC..0x004764DF` | 4 | `a7ddd513d149ea16fdd4db3f82267f83087aeaddd06b5dde5468adb704205fc4` | none |
| Boot | read | `0x004212D8..0x0042130F` | 56 | `26e2b4b9fe7f3389d15261fe01621eb3b37bfc4b9923ebfac70609216ac92a90` | `0x00420F71` |
| Boot | program | `0x00421310..0x00421347` | 56 | `6d46e88d2df85850b8ec35b4f55e5e0522884210c8bf5a3419e328599ffebf60` | `0x00420B0D` |
| Boot | erase | `0x00421348..0x00421371` | 42 | `df1788d1db60223b7af5050ab14307a3bf27f30fc6d61917adee77f679b3b872` | `0x00420A09` |
| Boot | sync | `0x004213D4..0x004213D7` | 4 | `a7ddd513d149ea16fdd4db3f82267f83087aeaddd06b5dde5468adb704205fc4` | none |

The read/program/erase callbacks pass `(address, buffer, size)` or
`(address)` to those driver calls. On zero they return zero. On every
nonzero driver result they log the complete operation and return:

```asm
mvns r0, #4
```

That instruction produces `0xFFFFFFFB`, or littlefs `LFS_ERR_IO` (`-5`).
No device result is mapped to `LFS_ERR_CORRUPT`; all distinctions are lost
after the diagnostic.

The diagnostic formats are identical in main and boot:

```text
lfs READ fail: block=%u, off=%u, size=%u, addr=0x%08X, st=%d
lfs PROG fail: block=%u, off=%u, size=%u, addr=0x%08X, st=%d
lfs ERASE fail: block=%u, addr=0x%08X, st=%d
```

After normalizing direct-call targets, PC-relative diagnostic loads, and
relative branch destinations, all four main callback instruction lists equal
their bootloader counterparts exactly.

## External-flash driver seams

The directly usable opaque boundary is:

| Operation | C ABI | Main Thumb entry | Boot Thumb entry |
|---|---|---:|---:|
| Read | `int fn(uint32_t address, void *buffer, uint32_t size)` | `0x00471021` | `0x00420F71` |
| Program | `int fn(uint32_t address, const void *buffer, uint32_t size)` | `0x004708A9` | `0x00420B0D` |
| Erase | `int fn(uint32_t address)` | `0x0047075D` | `0x00420A09` |

Driver handle globals are at `0x20074544` in main and `0x200270DC` in
boot. The surrounding transaction wrappers use mutex globals at
`0x20074548` and `0x200270E0`, respectively. These are runtime state, not
littlefs `context`.

### Read path

The recovered read driver:

1. rejects a null driver handle, null buffer, or zero length with status 6;
2. rejects `address >= 0x02000000` with status 5;
3. enters the transaction wrapper;
4. reconfigures the NOR/MSPI path to quad mode;
5. calls the busy-wait helper but ignores its result;
6. zeroes a 24-byte `am_hal_mspi_pio_transfer_t`;
7. submits QREAD4B with a one-second HAL timeout;
8. leaves the transaction wrapper; and
9. returns the HAL transfer result unchanged.

The recovered IAR ABI for the PIO transaction is:

| Offset | Member | Read value |
|---:|---|---:|
| `0x00` | `ui32NumBytes` | requested size |
| `0x04` | `bScrambling` | 0 |
| `0x05` | `bDCX` | 0 |
| `0x06` | `eDirection` | 0, receive |
| `0x07` | `bSendAddr` | 1 |
| `0x08` | `ui32DeviceAddr` | calculated external-flash address |
| `0x0C` | `bSendInstr` | 1 |
| `0x0E` | `ui16DeviceInstr` | `0x006C` |
| `0x10` | `bTurnaround` | 1 |
| `0x11` | `bEnWRLatency` | 0 |
| `0x12` | `bContinue` | 0 |
| `0x14` | `pui32Buffer` | destination pointer |

Main calls `am_hal_mspi_blocking_transfer` at `0x004C2098`; boot calls it
at `0x004262E0`. Both complete 364-byte HAL bodies normalize
instruction-identically. Their SHA-256 values are
`12dd31986d405542640cf5b2de6f46e691ed91628c645a4806b3134883b401c4`
and
`91c3b42f59f32e97e91133a7c66234488e6b0076c4dd4362a0ed7dd9d56492e3`.

The structure layout, validation order, state offsets, control-word
construction, and transfer behavior match Ambiq's open-source Apollo510
HAL imported from AmbiqSuite 5.1.0. The reference import is commit
[`5efc0228528a8adce5eae0d226fac85d2551eb3b`](https://github.com/AmbiqMicro/ambiqhal_ambiq/commit/5efc0228528a8adce5eae0d226fac85d2551eb3b);
its pinned Git blobs are:

```text
am_hal_mspi.c c12ef914660227aba3ebef3a0fb3ec749510c1bc
am_hal_mspi.h 738ae35ffbe8ca3158df18d3b28794bf0c7b2589
```

This is a source-equivalent reference, not a claim that Even used that later
public Git commit as its historical checkout.

### Program path

The program driver rejects the same null/zero arguments with status 6 and a
starting address outside the 32-MiB device with status 5. It then:

1. locks the transaction and switches to serial mode;
2. splits the request at 256-byte page boundaries;
3. waits for idle;
4. sends write-enable (`0x06`);
5. sends page-program (`0x02`) with address and payload;
6. delays/polls for completion;
7. sends write-disable (`0x04`);
8. repeats until the requested length is exhausted; and
9. restores quad mode and unlocks.

The lower transfer helper rejects lengths greater than 256 and individually
checks each chunk's starting address. The top-level function does not
preflight `address + size`, so a request crossing the physical end may
program an initial in-range prefix before the next chunk fails.

### Erase path

The erase driver:

1. returns 2 if the driver handle is null;
2. returns 6 unless the address is 4-KiB aligned;
3. returns 5 for an address at or beyond `0x02000000`;
4. locks and switches to serial mode;
5. reports status 3 if the pre-write-enable busy wait times out;
6. sends write-enable, sector erase (`0x20`), and write-disable;
7. reports status 4 if the post-erase busy wait times out; and
8. restores quad mode and unlocks.

The driver does not take a size because every invocation erases exactly one
4-KiB sector.

### Mode and transaction boundaries

Main and boot have source-equivalent transaction/mode structure but
different diagnostic density:

- composite transaction lock calls a CMSIS mutex wait and conditionally wakes
  MSPI through `am_hal_mspi_power_control(handle, AM_HAL_SYSCTRL_WAKE, true)`;
- composite unlock conditionally enters retained deep sleep through
  `am_hal_mspi_power_control(handle, AM_HAL_SYSCTRL_DEEPSLEEP, true)` and
  releases the mutex;
- serial mode is selected before program and erase;
- quad mode, QREAD4B, and a 1,000,000-microsecond blocking HAL transfer are
  used for read; and
- the mode helpers call open-source `am_hal_mspi_control`, including clock
  and XIP configuration requests.

The lock, unlock, and mode-helper result paths are diagnostic-only from the
caller's perspective. A mutex wait failure is logged but does not prevent
the flash operation. Mode-reconfiguration failures are also logged but not
propagated through the public read/program/erase result.

## Bounds and mutation risks

The callbacks are faithful but not defensive:

- They do not check `block < 3008`.
- They do not check `offset + size <= 4096`.
- They do not check read/program alignment against 16/256-byte minima.
- The 32-bit address calculation can wrap for malformed block/offset values.
- The read driver validates only the starting address, not
  `address + size`; a malformed cross-end read is delegated to the HAL/device.
- A cross-end program can partially modify flash before returning an error.
- Program or erase can complete physically and then return failure because a
  later busy wait or write-disable operation failed.
- A mutex-acquisition failure does not abort the operation.
- The read path ignores the busy-wait result.
- Sync is always zero and performs no additional barrier.
- All driver failures collapse to `LFS_ERR_IO`, including failures that occur
  after a partial mutation.

These behaviors are safe only under the invariants supplied by the normal
littlefs core and correct configuration. A standalone source port should add
checked arithmetic:

```text
block < 3008
offset <= 4096
size <= 4096 - offset
physical address range wholly inside 0x01400000..0x01FC0000
```

For stock-equivalence testing, log any new rejection separately because
these checks intentionally tighten malformed-input behavior.

## Safe read-only source boundary

The vendored v2.10.1 core has an upstream-supported `LFS_READONLY` build.
Under that define:

- format, remove, rename, file write/truncate/sync, mkdir, and other mutation
  APIs are not compiled;
- block programming, block erase, and block sync internals are not compiled;
  and
- `lfs_init` requires `cfg->read` but does not require `cfg->prog`,
  `cfg->erase`, or `cfg->sync`.

The recommended first hardware boundary is therefore:

```c
// Illustrative contract only; not installed by this audit.
int g2_lfs_read_checked(
    const struct lfs_config *cfg,
    lfs_block_t block,
    lfs_off_t offset,
    void *buffer,
    lfs_size_t size
);
```

It may reuse the authenticated main read driver at `0x00471021` or the boot
read driver at `0x00420F71` while the NOR transport remains opaque. It should
reject any range outside the recovered partition before calling that seam.
A dedicated read-only config can leave program/erase/sync null because the
read-only core does not consume them.

Do **not** call the existing stock-style filesystem initializer for this
bring-up. Its recovery behavior can unmount, format, remount, create
directories, and update `boot_count`. A safe path must call `lfs_mount`
directly and expose only read/stat/directory traversal APIs.

This makes the callback and upstream-core portion implementable now, but
hardware acceptance still requires:

1. a complete external-flash capture made through a reviewed read-only path;
2. a host mount of a copy with the pinned v2.10.1 `LFS_READONLY` core;
3. disk-version, superblock, block-count, tree, metadata, and file-content
   comparison against stock reads; and
4. repeated on-device reads proving stable results without flash changes.

Mutation and power-loss tests belong only on disposable image copies until
that gate passes.

## Remaining unknowns

The callback boundary itself has no material ABI uncertainty. The following
items remain before deleting its opaque external-driver seam:

- exact Apollo510 MSPI instance and board pin/pad configuration;
- complete serial/quad device-configuration objects;
- timing-scan results and fallback timing values;
- XIP aperture and cache/DAXI ownership policy;
- power-enable, clock, and reset ordering;
- flash mutex initialization/lifecycle and the meaning of both mode-state
  bytes;
- exact boot-versus-main initialization differences;
- the complete device-ID/quad-enable/four-byte-mode startup sequence; and
- golden external-flash contents and observed filesystem disk version.

The public AmbiqSuite 5.1.0 HAL can replace the identified HAL bodies.
`drv_mx25u25643g.c` and
`littlefs_mx25u25643g_porting.c` do not appear in the official Ambiq HAL
repository and should remain classified as G2/downstream glue until a
matching public source is found or the above configuration is independently
recovered.
