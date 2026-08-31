# G2 bootloader MSPI control source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

The complete enable/disable pair `[0x0041FE28,0x0041FE62)` now routes to
maintained clean-room C. The 32-byte enable body (SHA-256
`e192108a57e6cd824fb7b17e9e1fa3d39dd77e8dbea29cd967959f433f05a7f7`)
is idempotent on the active byte at `0x200271C6`, otherwise invokes the retained
control seam with `(handle,2,1)` and sets it. The 26-byte disable body (SHA-256
`d72aa87850dfc17bee8c0668d9286d189027b2ef9bf7f3a7727f243bef10f518`)
always invokes `(handle,0,1)` and clears the byte. The handle word is
`0x200270DC`; callers are `0x0041FF2A`, `0x00420520`, and `0x0041FF18`.

Host tests pin idempotence, handle/mode/flag arguments, ordering, and state.
Both profiles emit identical relocation-free 40-/32-byte leaves with SHA-256
`d2c4bcc5e93182f643d4c97f6fe2295851308b0efb33e2a5a5f7434da7cad2b8`
and `22eba2a5dc7603d067ed9bb72afe6f491a7b4c4fae06da054e572bc11165aed0`.
The later event-flags, guard, and XIP-config entries are now source-owned too.
The current cumulative Apple overlay/provider are 10,500 / 159,100 bytes;
Linux are 10,484 / 159,084. Accounting is 10,487 source-owned, 11,782
generated patch, 14 alignment, and 136,817 retained official bytes across 170
functions, 151 relocated leaves, and 168 patch sites.

Unsigned packages are 4,740,678 / 4,516,672 bytes with SHA-256
`81ae4b1c4f87e3d6348aa55426f6c7f3cc766aa079d94a96ec82f3ffddc76b2d`
and `bb52277456ff2d69aaa34f4639734ab5d23bcea984f153ac19795b372955de71`.
No hardware operation occurred. Live MSPI state/timing and cold boot remain
blocked by unavailable authorized responsive right-temple evidence; the left
temple must remain stock. Later services through `0x0041FF60` are now
source-owned; executable bodies after that address remain software
gaps, so firmware-wide completeness is not claimed.
