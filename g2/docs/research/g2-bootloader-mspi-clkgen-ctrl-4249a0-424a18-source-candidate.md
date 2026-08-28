# G2 bootloader `mspi_clkgen_ctrl` source closure (`0x004249A0`–`0x00424A18`)

Status: production-routed exact dual-profile source; physical validation is
blocked by unavailable physical evidence.

The official 120-byte AmbiqSuite 5.1.0 function has SHA-256
`86e27ef6ed8e0e1ba9c0f2ba553376ae57fcf0154bba95f37d1eb4a6ef7c3dd0`
and eight direct callers. It updates a five-bit clock-generator field per MSPI
module at `0x40004110`, optionally configures the four clock-select bits,
sets or clears enable atomically under PRIMASK, and delays 10 microseconds after
enable.

The typed host model covers enable, disable, configure-skipped, clock-select
conversion, exact write order, delay, and critical-token restoration. The
target body has authenticated calls to critical-save `0x0041B8EC` and delay
`0x0041D1C0`; applying those two relocations produces exact official bytes
under both reviewed compiler profiles.

Production admission leaves the four-byte `0x40060000` literal at
`0x0042499C` authenticated and retained. This software-only source wave
performed no hardware operation. Live clock-generation, timing,
power-transition, and cold-boot qualification is blocked by unavailable physical evidence;
this source closure does not by itself declare firmware functional completeness.
