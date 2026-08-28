# G2 touch configuration bootstrap (batch 16)

Batch 16 admits the 156-byte application configuration bootstrap at `0x065C`
as isolated MIT clean-room source. It initializes the already typed storage
boundary, loads the eight-byte `UNVE` configuration, defaults a zero timeout,
or prepares storage and writes the authenticated defaults after the exact
10-millisecond delay.

The call closure uses the Batch 15 MIT adapters, the existing MIT bounded
storage-policy seam, authenticated Apache-2.0 delay behavior, and the shipped
compiled-out no-op logger. No Em_EEPROM EULA body is called or copied directly.
Host tests cover retained/defaulted configurations, read/prepare/write failures,
accepted provider status, callback absence, and Cortex-M0+ symbol closure.

The concrete gap falls from 56 functions / 5,120 bytes to 55 / 4,964 bytes;
application contracts fall from 44 to 43. All twelve external/unavailable
functions, resident loaders, EULA provider bodies, system/halt boundaries, and
`0x1B6C`/`0x1C54`/`0x2638` remain unadmitted.

This source is isolated and not production-routed. Hardware validation remains
blocked by unavailable physical evidence.
