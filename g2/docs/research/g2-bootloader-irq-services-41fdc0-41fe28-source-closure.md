# G2 bootloader IRQ-service cluster source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

Three complete entries at `[0x0041FDC0,0x0041FE28)` now route to maintained
clean-room C in `runtime_irq_services_41fdc0.c`:

- `[0x0041FDC0,0x0041FDDE)`, 30 bytes, SHA-256
  `6fbb6367b6801ee7979acd72367d57b54bd1c55c41b17f7a70365bcd94b8991c`:
  signed-IRQ guard and NVIC set-enable write; sole caller `0x00420414`.
- `[0x0041FDDE,0x0041FE06)`, 40 bytes, SHA-256
  `1fa388746ea65ab90eb2ad94d86503527e74b1bd1a24a3b2b5c6491059d93011`:
  four-bit priority encoding and external/system-handler priority selection;
  sole caller `0x0042040E`.
- `[0x0041FE06,0x0041FE28)`, 34 bytes, SHA-256
  `35d4b9a6550f30c232ef637ab736df92e1ffca38fc55af1ccdc0da43bffd3236`:
  MSPI status-get, interrupt-clear, and interrupt-service sequence using the
  handle at `0x200270DC`; vector-table ingress at file offset `0x94`.

Host tests cover negative IRQ rejection, bank/mask derivation, positive and
negative priority addressing, low-nibble priority encoding, exact MSPI handle,
status propagation, and call order. Both reviewed Clang profiles emit the same
relocation-free 32-, 32-, and 48-byte leaves with SHA-256
`a0b40ca8273aa7d4e30b39a932157c6d1ab613aa5daa0d63cd8460129647975e`,
`8b9fce902a009a23dc8d8b9be0e1c54487b2df821852dd97217ce6d96af9e9e6`,
and `554fc96172fb02ad47a180f43424b16d860c0b249a1e380b57584e56c10cfb54`.

Apple overlay/provider identities are 10,116 / 158,716 bytes with SHA-256
`f8088800044634921e2446b45e7133e0a9d3232e5ce5ad78f31eb6990b1e32b8`
and `1594aefde3a94be29dec7c4d3ab3ac20cf57e2a6f220f7eeca8609ffb222dede`;
Linux identities are 10,100 / 158,700 bytes with SHA-256
`ae413000d796c164e5bc06f197ff9bbf2543140d2ed6a50bfc62eecb225bb213`
and `34259f9296124eed2b7cebc3488994087b3308fc26383d78f82fd9948e568eae`.
Canonical accounting is 10,103 source-owned, 11,470 generated patch, 14
alignment, and 137,129 retained official bytes across 162 functions, 143
relocated leaves, and 160 patch sites.

Unsigned Apple/Linux packages are 4,740,294 / 4,516,288 bytes with SHA-256
`b2ce7f54b0d6fb58fe46c78d715f7498d9188dba826197225ad203db0bc64181`
and `c8c34b6acf8ed5b356f61334121e5c6d3bfc8628302bd3af4398192c83403a88`.
Their flash plans contain 6,474 / 3,438 placed regions and two unresolved
boundaries each. No hardware operation occurred.

Live NVIC state, exception priorities, interrupt timing, MSPI status/clear/
service effects, and cold boot remain blocked by unavailable authorized
responsive right-temple evidence; the left temple must remain stock.
Executable bodies after `0x0041FE28` remain software gaps, so firmware-wide
functional completeness is not claimed.
