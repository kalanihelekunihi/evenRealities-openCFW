# G2 BQ27427 fuel-gauge recovery

## Result

The retained first-party `driver/chg/drv_bq27427.c` object is completely
bounded in the official G2 `s200_v2.2.6.10` OTA. It contains 37 linked bodies,
4,440 bytes of executable code, and 396 bytes of owned alignment, literal, and
diagnostic data. The physical interval is:

```text
[0x0053AFC0, 0x0053C2A4)  4,836 bytes
SHA-256 ed5d39ec1667c7b623eba6dfd0deddb9d732ab53dc0e8c6b18392c77a6a929a5
```

The clean-room candidate is
[`chg_bq27427.c`](../../components/apollo_main/core_overlay/chg_bq27427.c).
It remains intentionally absent from `overlay.json`; production ownership is
still zero until its transport, delay, placement, redirect, and package seams
are reviewed together.

## Authority and boundaries

The authority is
`blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin`, SHA-256
`36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`,
loaded at `0x00437FE0`. The exact retained path is:

```text
D:\01_workspace\s200_ap510b_iar_git\driver\chg\drv_bq27427.c
```

The 37 bodies run in source order from the I2C helpers through
`DRV_Bq27427HwInit`. Their concatenated digest is
`0cdbcb99880d06d844f54b183fbcd484ec45b4c299bf230e2c251c32d28d4529`.
The exact per-body ledger is
[`g2-chg-bq27427-function-map.tsv`](../../tools/manifests/g2-chg-bq27427-function-map.tsv).

The six non-code intervals total 396 bytes and hash to
`2945fc1a3fc2e2b8c8db96a3577605d213c1962e4a1ef2d7a2c95c1af960ae83`.
The final 224-byte pool owns configuration, function-name, diagnostic,
runtime-global, and source-path relocations. The next unrelated function begins
exactly at `0x0053C2A4`.

## Ingress closure

There are 88 direct BL entry sites: 86 inside the object and two exterior
roots:

| Site | Target | Role |
|---|---|---|
| `0x004C688A` | `0x0053C0F4` | periodic/status wrapper |
| `0x0050943C` | `0x0053C0FE` | hardware initialization |

The bodies contain 287 direct calls. An exhaustive raw stored-word scan finds
no even or Thumb-tagged entry/interior pointers. There is no `B.W` entry or
strict-interior ingress. One raw BL-looking window at `0x0063062A` decodes to
`0x0053B4BE`, but it is outside authenticated code and is retained as an
explicit decoder false positive rather than promoted as a caller.

## Hardware and runtime ABI

The stock transport uses I2C bus 7 and seven-bit address `0x55`. Two-byte
commands are split into adjacent one-byte reads and assembled little-endian;
two-byte writes are little-endian. Block data is 32 bytes. The block-write
wrapper stages up to 35 bytes and deliberately returns success after logging a
provider failure.

The live telemetry record begins at `0x20073B18`:

| Offset | Field |
|---:|---|
| `+0x04` | state of charge |
| `+0x08` | battery voltage in mV |
| `+0x0C` | signed average current in mA |
| `+0x10` | temperature in centi-degrees C |

Temperature command `0x02` returns tenths of kelvin; stock subtracts 2731 and
then multiplies by ten for the runtime record. Average current (`0x10`) and
average power (`0x18`) are sign-extended 16-bit values.

## Authenticated initialized configuration

The IAR initialized-data record independently reconstructs the unseal key and
DM descriptor table:

```text
0x200006E8  00 80 00 80                    key 0x80008000
0x200006EC  64-byte descriptor array       SHA-256 4c4a1ae9...1b037a08a
```

Each descriptor is `{subclass, offset, width, reserved, min16, max16}`:

| Index | Subclass | Offset | Width | Min | Max |
|---:|---:|---:|---:|---:|---:|
| 0 | 82 | 6 | 2 | 0 | 8000 |
| 1 | 82 | 8 | 2 | 0 | 32767 |
| 2 | 82 | 10 | 2 | 3000 | 4400 |
| 3 | 64 | 4 | 1 | 0 | 255 |
| 4 | 82 | 2 | 1 | 0 | 255 |
| 5 | 81 | 0 | 2 | 0 | 2000 |
| 6 | 105 | 5 | 1 | 0 | 32767 |

An eighth zero-width sentinel follows. ROM `[0x0078A8BC,0x0078A8C8)` contains
the exact product settings `{240, 80, 3100}`. Stock accepts energy below
37,500, charge below 8,001, and voltage from 2,500 through 3,700 inclusive.

## Data-memory protocol

The 36-byte local block is `{subclass, block, data[32], valid, dirty}`. Reads
select class `0x3E` and block `0x3F`, wait 1 ms, read `0x40..0x5F`, and compare
register `0x60` with `0xFF - (sum(data) & 0xFF)`. Two-byte descriptor updates
are big-endian within data memory.

Writes enter CFGUPDATE with control `0x0013`, disable block-data control through
`0x61`, select class/block, write data and checksum, then leave CFGUPDATE with
control `0x0042`. Both transitions poll flag bit 4 up to 100 times with 25-ms
delays. Chemistry selection uses control query `0x0008` and control word
`0x0031`. Sealing uses `0x0020`; unsealing writes the upper and then lower
halves of `0x80008000`.

## Candidate and tests

The candidate is an independently authored behavioral reconstruction. It does
not copy Linux source. The Linux `bq27xxx_battery.c` family is recorded only as
a naming/architecture lineage clue; TI's BQ27427 technical reference manual is
the primary public register/command reference.

Host tests cover little-endian register I/O, signed readings, checksum and
big-endian DM writes, the exact `{240,80,3100}` update image, validity gates,
runtime telemetry, and the zero/`0xFF` flag failure rule. A freestanding Thumb
build pins the intended global symbol surface. The fail-closed analyzer also
pins every body, non-code interval, initialized-data byte, call closure, and
the candidate's continued production exclusion.

## Reproduce

```sh
python3 tools/analyze_g2_chg_bq27427.py
python3 -m unittest \
  tests.test_analyze_g2_chg_bq27427 \
  tests.test_chg_bq27427_candidate
```
