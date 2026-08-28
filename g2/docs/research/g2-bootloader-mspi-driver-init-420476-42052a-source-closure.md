# G2 bootloader MX25U25643G public initializer source closure

## Result

The complete authenticated 180-byte entry `[0x00420476,0x0042052A)` now
routes to maintained clean-room C in
`components/bootloader/core_overlay/runtime_mspi_driver_init_420476.c`.
The stock body SHA-256 is
`5be1a86e4e5b4c50b9d8eac9043747caec7abd1ad916fc13ceace39fa5ddb662`;
the 5,602-byte source SHA-256 is
`65a390f2c770079f4255ea489cc02bc0f593674de7688d3fb550f201ebc8785f`.

The entry initializes MSPI1 through the separately source-owned low-level
initializer, returns and logs its exact nonzero status, waits 10 ms, performs
the retained device-mode preparation, synchronizes around the source-owned
automatic timing selection, reads and logs the packed JEDEC identifier, and
returns the exact read failure. On success it performs the retained final
device setup, selects mode one, initializes the source-owned event-flags
service, enables MSPI through the source-owned control leaf, and returns zero.

## Evidence and pins

Stock decoding pins every call, the state-output slot at `0x200270D8`, the
`DRV_Mx25u25643g_init` logger identity, diagnostic lines `0x284`, `0x28E`, and
`0x292`, and format strings for initialization failure, ID failure, and the
six-digit ID. Host tests prove the exact success order and ID propagation and
both short-circuiting failure paths. A freestanding Cortex-M55 compile is part
of the gate.

Both reviewed profiles emit a 204-byte leaf with five strict
`R_ARM_THM_CALL` relocations to source-owned low-level-init, delay,
timing-selection, event-flags-init, and MSPI-enable functions. Apple places it
at offset 11,728/runtime `0x00437248`, with raw/final SHA-256
`9f93f834b499f13412e425a025c6be9d1e86a60c7f461b223e654fdf5134bdd9` /
`31195e4775918f5fb7b0925f2cfa15b4a8f699688ae3bb0888527299de197e7c`.
Linux places it at offset 11,708/runtime `0x00437234`, with raw/final SHA-256
`ea8a92c692b267632c58d67df08d88a4e1606e932b548931511577f040def5f0` /
`b096ea573418bdc7c2f6e4057c76beec536db1878a5c3c014bb6f845c5eb54b0`.

Apple/Linux overlay/provider identities are 11,932/160,532 and
11,912/160,512 bytes. Canonical accounting is 11,917 source-owned bytes,
13,264 generated patch bytes, 16 alignment bytes, and 135,335 retained
official bytes across 176 routed functions, 157 relocated leaves, and 174
patch sites.

Unsigned Apple/Linux packages are 4,742,110 / 4,518,100 bytes with SHA-256
`d237651197debbd2f9d662ef6956f917470432c369983b8d1c07f5786145749b` /
`c9ea31e7f8b2d9fa173b72162b260e41a4e2511a1992bfc058630e427ea77458`.
Their flash plans contain 6,503 / 3,452 placed regions and two unresolved
address regions.

## Physical-evidence boundary

Nothing was signed, flashed, installed, reset, booted, or sent to hardware.
Live JEDEC identity, HAL, RTOS, interrupt, MSPI, external-flash, XIP, timing,
and cold-boot behavior cannot be validated because no authorized responsive
right G2 temple is available; the left temple must remain stock. Executable
service bodies after `0x0042052A` remain software gaps. Firmware-wide
functional completeness is therefore not claimed.
