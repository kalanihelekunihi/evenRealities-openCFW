# G2 ICM45608 production dependency boundary

Status: production-routed clean-room C for all 53 recovered first-party entry
points, plus one Thumb callback adapter. The exact G2 transport/device ABI,
reset/identity initialization, FIFO acquisition, eDMP/GAF fusion, auxiliary
magnetometer, extended AID/B2S images and event routing, sample-ring parsing,
transforms, event policy, identity reads, and CSV capture are implemented and
host-tested. No known software implementation gap remains in this object;
physical validation is separately blocked.

## Source and public evidence

`components/apollo_main/core_overlay/imu_icm45608.c` is an OpenCFW clean-room
implementation under GPL-3.0-only. The repository also carries an immutable,
BSD-3-Clause TDK InvenSense `motion.arduino.ICM45608` snapshot at tag `1.1.2`,
commit `b79ae575f7f310e5ae2e1164096d1a858bb74662` (driver `1.1.0`): 52 upstream
files / 594,177 bytes / aggregate SHA-256
`cc6088eed9f14a02af419a29856064ab62e4b79e2860a135e1d84ba22e1c9570`.
This is the last authenticated public release with the 16-byte,
three-argument transport callback ABI observed in stock G2. The production
adapter does not copy the unavailable historical Even Realities implementation.

The current source uses the public ICM45608 register interface for
`PWR_MGMT0` (`0x10`), accelerometer and gyroscope configuration (`0x1b` and
`0x1c`), FIFO configuration (`0x1d` through `0x22`), raw sensor data beginning
at `0x00`, and `WHO_AM_I` (`0x72`). It source-owns the 72-byte device layout,
three-argument callbacks, six-argument retained I2C-provider calls, `0x81`
identity check, reset/RESET_DONE sequence, FIFO/endianness/eDMP state reset,
FSYNC tag read, INT1 pin setup, exact upstream GAF/MRM/AID/B2S RAM images,
APEX interrupt configuration, and AID/B2S state reads. Power/delay/tick,
filesystem, and event dispatch remain bounded platform services.

## Production routing

The source compiles as 54 independently authenticated Cortex-M55 leaves: 53
recovered object functions and one source-owned delay callback adapter. The
leaves contribute 8,610 text bytes and 30 alignment bytes with 83 authenticated
relocations. Fifty-two guarded `B.W` replacements cover 11,672 stock body
bytes. The stock two-byte no-op cannot contain a wide branch; it is retained
unchanged and unreachable because its only caller is source-replaced. The
remaining 762 stock alignment/literal bytes are compatibility data.

The canonical artifacts after this increment are:

- overlay: 326,460 bytes,
  `78915b5c9fcc8200ac54a6e1e9a899c0223e3621e46f580c79b51286f9ef67d8`;
- Apollo component: 3,849,856 bytes,
  `d5ca988001c5a906876e7a630c28cbedff436c2df4c8260fd86ed16aeea1e01c`;
- EVENOTA package: 4,628,350 bytes,
  `7e6abf1247754df84f6f729a9247de351a4b1bf1155703cf321078d31f89ba01`;
- flash plan: 3,041,934 bytes,
  `d53f44f4cbf38c8407c3d7386cb4218f15d038682071201dc81a3e0a09d9a717`.

The source manifest has 143 IMU regions: 52 generated entry replacements, 54
compiled leaves, 15 generated-alignment regions, and 22 official compatibility
regions.

## Software closure and remaining physical evidence

The production route now covers the vendor surface used by
`DRV_IMUSetSensorParameters` and `DRV_IMUReadData`: FIFO and register
acquisition, eDMP/APEX/GAF configuration and decode, auxiliary I2C
magnetometer access, exact extended-program image loading, and AID/B2S event
state publication. Host and Cortex-M55 target tests close the software path.
This is not a declaration of hardware-validated IMU functional parity.

Hardware validation is explicitly blocked: the authorized right temple is
nonresponsive; the authorized left temple must remain stock; and no responsive
authorized G2 ICM45608 path, calibrated motion rig, or golden FIFO/eDMP trace
is available. No flashing or signing was performed.

Reproduce the software checks with:

```sh
python3 tools/analyze_g2_imu_icm45608.py
python3 third_party/invensense-icm45608/verify_snapshot.py
python3 -m unittest -v \
  tests.test_analyze_g2_imu_icm45608 \
  tests.test_imu_icm45608_candidate \
  tests.test_invensense_icm45608_snapshot
```
