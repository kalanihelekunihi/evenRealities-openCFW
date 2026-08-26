# G2 `imu_icm45608.c` recovery

Status: complete linked-object census and fail-closed behavioral analysis; a
clean-room candidate now production-routes every recovered entry point plus
the exact public TDK FIFO/eDMP/GAF, magnetometer, AID, and B2S feature path.
No known software implementation gap remains in this object, and hardware
validation is blocked. Run addresses use `run = file_offset + 0x00437FE0`.

## Result

The retained path is `driver\sensor\imu\imu_icm45608.c`. Eleven functions
were visible through the authenticated retained-path corpus, but raw Thumb
control flow, three callback pointers, diagnostic symbols, and source order
restore another 42 entries. The resulting 53-function object occupies
`[0x004A35B0,0x004A6644)`. Its bodies contribute 11,674 bytes with SHA-256
`9a2ab101ce16b0bbb2c08a8338249ca8eb97ecece2fb331fe0595a3cb628e21e`;
21 alignment/literal regions contribute 762 bytes with SHA-256
`f715282f60d047a6a9aa7942b9396eabe3ad99cebafbd7a705178ba10b0da912`.
The complete 12,436-byte physical object has SHA-256
`d4946b892b0fcb6e45a3cb2f4dadd452e737712815577d6780c26ff7e1185e22`.
The previous object's literal pool ends at the first entry and a new Thumb
prologue begins at `0x004A6644`, closing both physical boundaries.

The large Ghidra-missed front half is real code rather than opaque data. It
contains bus callbacks, filter/configuration helpers, and the 3,420-byte
`DRV_IMUSetSensorParameters`. The tail contains nine six-byte state
getters/setters before the final literal pool. Fifteen exact diagnostic names
survive, including `DRV_IMUReadData`, `DRV_IMUDataParserCallback`, the AID,
head-up and compass paths, all four raw-CSV operations, and both WHO_AM_I
readers. The complete byte ledger is pinned in
`tools/manifests/g2-imu-icm45608-function-map.tsv`.

## Device and sample pipeline

The object installs odd Thumb entries `0x004A35B1`, `0x004A35EB`, and
`0x004A56D5` as the bus-read, bus-write, and FIFO parser callbacks. The main
driver context is rooted at `0x20073020`. Initialization configures the device,
applies one of the observed output-data-rate selections, sets the orientation
matrix, and registers FIFO parsing. The large read path obtains device/FIFO
data and feeds postprocessing, while the callback decodes packet fields into
a 20-slot sample ring at `0x200640A0`.

The ring has a 12-byte header and `0x70`-byte records. Parsed records carry
timestamp, validity flags, accelerometer/gyroscope/magnetometer vectors, and
orientation/fusion results. Fixed-point vectors are converted to floats, a
3-by-3 orientation transform is applied, and quaternion data is converted to
Euler angles. A consumer scans for the latest complete record and serializes
three vectors into a 36-byte output. The AID path reports activity/inactivity
and sedentary state; independent checks emit tilt, tap, head-up/head-down, and
compass-calibration events.

`DRV_IMUAccelConfig` accepts an interval from 100 through 4,999 inclusive and
rejects values outside that range. The periodic forwarding helper uses that
interval to gate report emission.

## Raw CSV capture

Raw capture builds `/log/imu_rawdata_%02d%02d%02d.csv`, closes any prior open
file, writes a CSV header, and records formatted samples. The file handle,
sample count, active flag, and start time are at `0x20074684`, `0x20074688`,
`0x20074FDD`, and `0x2007468C`. Capture stops explicitly or automatically
after 120,000 ms. The stop path closes the file, clears its state, and reports
the number of saved samples. Header, line-overflow, write, create, and close
failures retain distinct diagnostics.

## Ingress and ownership

Across the image, 72 `BL` encodings target exact entries: 35 external and 37
inside the object. The 53 bodies contain 464 direct call sites. The three
stored function pointers are the intended callback table entries described
above. Ten `B.W` instructions inside `DRV_IMUSetSensorParameters` branch to
its shared epilogue at `0x004A4576`; no external `B.W` or `BL` targets a
strict interior. Eighteen other all-byte numeric windows resemble an entry or
interior value, but 17 are unaligned instruction/data overlaps and the one
aligned occurrence is unrelated static data. Real external strict-interior
ingress is zero.

The historical source inventory and license remain unavailable; exact-symbol
and filename searches did not identify a public source copy. OpenCFW now owns
a separate clean-room C implementation. Fifty-two guarded redirects replace
11,672 stock function bytes; the stock two-byte no-op remains unchanged and
unreachable, and the 762 alignment/literal bytes remain compatibility data.
Stock disassembly also fixes the vendor ABI: a 72-byte device at `0x20073020`,
three-argument transport callbacks, a FIFO callback at offset 24, and
six-argument retained I2C providers. TDK's BSD-3-Clause tag `1.1.2` at commit
`b79ae575f7f310e5ae2e1164096d1a858bb74662` is the exact public baseline.
The clean-room adapter now owns the `0x81` identity/reset/RESET_DONE and INT1
initialization sequence; opaque retained vendor initialization is no longer
called. The admitted TDK source now also owns FIFO parsing and register
polling, eDMP/GAF configuration and decode, auxiliary I2CM magnetometer access,
exact AID/B2S extended-program image loading, and event-state publication.
The residual is physical validation only.
See `g2-imu-icm45608-dependency-boundary.md` for production and residual-gap
details.

Reproduce the audit with:

```sh
python3 openCFW/tools/analyze_g2_imu_icm45608.py
python3 -m unittest openCFW.tests.test_analyze_g2_imu_icm45608
```
