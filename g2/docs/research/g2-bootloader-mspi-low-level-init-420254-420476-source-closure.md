# G2 bootloader MSPI low-level initializer source closure

## Result

The complete authenticated 546-byte entry `[0x00420254,0x00420476)` is now
replaced by maintained clean-room C in
`components/bootloader/core_overlay/runtime_mspi_low_level_init_420254.c`.
Its sole stock caller is `0x00420480`. The stock body SHA-256 is
`a3c3fab2d311bebbeb0a655aca6ee81a0afaf790008ca5bd11f23b05802bcb94`;
the 10,627-byte source SHA-256 is
`e5170727ba0e6fbc412ccc2dc1a845f777a66c1bd10eba3248db041bde31548d`.

The implementation preserves the one-instance busy rejection, HAL
initialize/power/configure/device-config/enable sequence, default and custom
device configuration selection, exact error returns, stage-specific logging,
and configure/device/enable cleanup. On success it applies the source-owned
XIP and pin-group configuration, fetches clock-pin 103, clears and enables
interrupt mask `0x1A80`, installs IRQ 21 at priority 4, enables the master
interrupt, publishes the state at `0x20026FD0`, returns it through the output
pointer, and emits the success diagnostic. The controller configuration pins a
256-word TCB at `0x200F4C00` with clock-on-deep-sleep disabled.

## Retained compatibility seams

The entry deliberately retains the authenticated Ambiq-compatible boundaries
at initialize `0x00424A5A`, power `0x00426808`, configure `0x00424AF0`, device
configure `0x00424BE4`, enable `0x00425066`, deinitialize `0x0042516C`, pin
configuration lookup `0x0041D90E`, interrupt clear/enable
`0x00426506`/`0x00426450`, master interrupt enable `0x0041B8E0`, and
EasyLogger `0x004176CE`. XIP configuration, pin-group selection, NVIC priority,
and NVIC enable are strict calls to separately source-owned leaves.

## Build and routing evidence

Both reviewed profiles emit a 492-byte leaf with four strict
`R_ARM_THM_CALL` relocations. Apple places it at overlay offset 11,236/runtime
`0x0043705C`, with raw/final SHA-256
`d04f06e63eb149ba70e030001552991f0222d43ec3aa74321640675ba0439e33` /
`a2eeead28dbb8476a9772b171133db5e8475deb85de7b72ff75abbbf7f6a92ea`.
Linux places it at offset 11,216/runtime `0x00437048`, with raw/final SHA-256
`495cc6693a913e68390f37bfba6cc84d4f312821882342770fea10567d6ddee5` /
`54cacd6a9de303677dbc1cc634d58df869a463adba260500603fe71a569b9176`.

The full-span patch is a `B.W` followed by 271 Thumb NOPs. Apple/Linux
overlay/provider identities are 11,728/160,328 and 11,708/160,308 bytes,
respectively. Canonical provider accounting is 11,713 source-owned bytes,
13,084 generated patch bytes, 16 alignment bytes, and 135,515 retained
official bytes across 175 routed functions, 156 relocated leaves, and 173
patch sites.

Unsigned Apple/Linux packages are 4,741,906 / 4,517,896 bytes with SHA-256
`b440e9852e9bd24f2747249953998eb578e68043a8f66f1a70e247cb3fb01c2a` /
`8938298ab593c95da48cd0697fccbee38cf3a2a1033cb44ef275ec7495162e1f`.
Their flash plans have 6,501 / 3,451 placed regions and two unresolved address
regions. Host tests cover success order and publication, custom/default
configuration, the busy state, every failure stage, cleanup, exact diagnostics,
stock topology, and target compilation.

## Physical-evidence boundary

Nothing was signed, flashed, installed, reset, booted, or sent to hardware.
Live HAL, interrupt, MSPI, external-flash, XIP, timing, and cold-boot behavior
cannot be validated because no authorized responsive right G2 temple is
available; the left temple must remain stock. Executable service bodies after
`0x00420476` remain software gaps. Firmware-wide functional completeness is
therefore not claimed.
