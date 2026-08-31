# G2 bootloader MX25U25643G write-transfer source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

The complete authenticated 176-byte entry `[0x0042069E,0x0042074E)` now
routes to `open_cfw_bootloader_mspi_write_transfer_42069e` in maintained
clean-room C. The stock SHA-256 is
`18bdd1fb9df8bf0b73bb5ed09e8f9ed218ba263f8f11caf97c98fc17af2aa20e`;
the 5,396-byte source SHA-256 is
`7fa590ec5cd0fbd87feb193c9bdec3becb0a6acea6334555c84683e3565451c1`.

Stock disassembly and host evidence pin null-handle status 2, the
`0x02000000` exclusive address ceiling, the 256-byte inclusive transfer
ceiling, and status 5 for either bound violation. Unlike the read wrapper,
zero length and a null buffer are accepted. The exact 24-byte Ambiq transfer
descriptor carries write mode 1, optional address publication, a truncated
16-bit instruction, direction 0, and a 1,000,000-cycle blocking timeout. Raw
HAL status is returned and nonzero status alone emits the diagnostic at
`0x00431468`. Eight authenticated calls enter at `0x00420538`, `0x00420570`,
`0x004208FA`, `0x00420992`, `0x004209D2`, `0x00420A8A`, `0x00420B78`, and
`0x00420D5C`. Retained seams are the handle word at `0x200270DC`, blocking
MSPI transfer at `0x004262E0`, and source-routed log dispatch at `0x00415FAE`.

Apple clang 21 and Homebrew clang 22.1.8 both emit the same relocation-free
148-byte leaf, SHA-256
`dac51840015d8553b2684538ff0a5a092d6c03122aa933a3af8d706a2e9d2b73`.
Apple places it at offset 12,340/runtime `0x004374AC`; Linux places it at
offset 12,324/runtime `0x0043749C`. Apple/Linux overlay/provider identities
are 12,488/161,088 bytes with SHA-256
`77dff0165822de281b2dee07aadb9a8929458638edaddbd88307262109524ac7` /
`045df48a04b26efec310a82889958916af6b889f40def73d72b77ad1fc60678b`
and 12,472/161,072 bytes with SHA-256
`a655be737233d67c5c919bcd5bc24cc15d256891f6ed25e0d74eb1fd01ca5b1a` /
`0007788956f2df45dc0a0ba122e4080e0bd8f701d08cc5d205166955fa147555`.

Canonical accounting is 12,473 source-owned, 13,812 generated patch, 16
alignment, and 134,787 retained official bytes across 180 routed functions,
161 relocated leaves, and 178 patch sites. Unsigned Apple/Linux packages are
4,742,666 / 4,518,660 bytes with SHA-256
`23135a2ef52282793bf44a56fb1c27a40ec7fe371d463a2cf4afa4fcf972c03f` /
`981f7a127509a4643027ac45f71bc49f24241b4c072ff0dd1cc6b14ff53ac3b3`.
Their flash plans are 4,529,678 / 2,412,736 bytes with SHA-256
`59a1946f42f9c51198757cc3ee9c64e59cc3602fcc6d45fdecdc618afa001d28` /
`d225ffdbef5150d6bcbe4905ed7f9e6e7d98cbbbbf278c52d6ff190da885da7e`;
they contain 6,511 / 3,456 placed regions and two unresolved hardware regions.

Nothing was signed, flashed, installed, reset, booted, or sent to hardware.
Live descriptor ABI, HAL timeout/status behavior, write-enable/program/erase
sequencing, external-flash writes, JEDEC/MSPI/XIP behavior, and cold boot
remain blocked by unavailable physical evidence from an authorized responsive
right G2 temple; the left temple must remain stock. Executable bodies at and
after `0x0042074E` remain software gaps, so firmware-wide completeness is not
claimed.
