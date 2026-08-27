# G2 bootloader EasyLogger port source closure

The eleven callable EasyLogger boot-port entries in
`[0x0041A648,0x0041A700)` are replaced by maintained freestanding C. The
intervening 22-byte interval `[0x0041A6DA,0x0041A6F0)` is authenticated
format-string/literal data and remains official rather than being mislabeled
as executable source.

## Authenticated stock boundaries

| Entry | Stock bytes | SHA-256 | Direct callers |
|---|---:|---|---|
| `0x0041A648..0x0041A65B` mutex create | 20 | `88fc734f91a9595fff96effb708c9b8e593b6bca403cf1590ec754ecb851c862` | `0x0041A688` |
| `0x0041A65C..0x0041A671` mutex acquire | 22 | `169a7ddcc907f767865c49a201f325c33770f7731e8359424abbe08bc380f34f` | `0x0041A69C` |
| `0x0041A672..0x0041A683` mutex release | 18 | `0538c89be6a767f59d04ff9ba0d37c6f8e98a3fffa5d35457104a277590e055a` | `0x0041A6A4` |
| `0x0041A684..0x0041A691` port init | 14 | `f0eefbc1594e2e86a7268d2ec186bf619fe4651b65e54a3d86b6b2c0bc3e1a30` | `0x00417350` |
| `0x0041A692..0x0041A699` output | 8 | `ececfe97080e5d40476e61bb0fa28b31ff6460285d33e9433047d4359d34e408` | `0x00417AC2` |
| `0x0041A69A..0x0041A6A1` output lock | 8 | `f4f02ad3353ef68eadb1408b05bd4b2b89440a4f4656dd1075ba92268d770e35` | `0x0041757E`, `0x00417B9C` |
| `0x0041A6A2..0x0041A6A9` output unlock | 8 | `a56bdb9407dda49c85a75ce1e3c34b88b0744e3797b68725874d0e3df10eee3e` | `0x004175A0`, `0x00417BB2` |
| `0x0041A6AA..0x0041A6C1` get time | 24 | `d4721c085671021321dfc612a27220d9f5e2722f2b1c33c4bb479fbbada6b193` | `0x00417888` |
| `0x0041A6C2..0x0041A6D9` task name | 24 | `6369de337442570729fecc8933cc1d333aecd1a4356f2eadde26f623342e1472` | `0x0041A6F2`, `0x0041A6FA` |
| `0x0041A6F0..0x0041A6F7` process info | 8 | `3e76180d81350b11618fc002f8cd142d0ae1c44e2f587c61c2edf0342a72d65f` | `0x004178C4` |
| `0x0041A6F8..0x0041A6FF` thread info | 8 | `981e6fe98ffa9b8a2e314502aafc3c1382cec761a7874d200491addc71da6244` | `0x00417900` |

The caller census scans every aligned Thumb `BL` in the authenticated
148,599-byte boot image and fails closed if any caller changes.

## Maintained behavior and seams

`runtime_easylogger_port_41a648.c` is a 12,540-byte MIT adaptation of
EasyLogger commit `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`; its SHA-256 is
`2d2196f1eed0c4d3e712e6ae8cffef60793dfdeecdb9327c24c9083b31f39677`.
It preserves the recovered G2 ABI:

- lazy mutex creation at handle cell `0x200270E8`, using attributes
  `0x00433D28`; null-handle lock/unlock is a no-op and the 1,000-tick CMSIS
  acquire/release statuses are intentionally ignored like stock;
- port initialization always returns success after the create attempt;
- output forwards `(log, size, level)` unchanged to Thumb seam `0x0041B855`;
- time formatting reads tick seam `0x004160E9`, writes the 28-byte buffer at
  `0x20026F18`, and uses bounded formatter seam `0x0041B219` with the retained
  `%d` literal at `0x0041A6DC`;
- task naming consults kernel-state, current-thread, and thread-name seams
  `0x00418B57`, `0x00418B4F`, and `0x00418373`, falling back to the retained
  unknown-name literal at `0x00434084`.

All calls between independently placed source leaves deliberately enter their
guarded stock Thumb seams. Host tests cover lazy creation, null handles,
status-insensitive lock/release, exact output argument forwarding, tick
formatting, and every task-name branch. A separate Cortex-M55 freestanding
compile gate rejects target warnings or unresolved language-runtime needs.

## Production evidence

Apple Clang 21 emits relocation-free leaves of
`32/24/20/16/8/8/8/40/40/8/8` bytes at overlay offsets
`8876/8908/8932/8952/8968/8976/8984/8992/9032/9072/9080`. Exact-root Linux
Clang 22.1.8 emits byte-identical leaves at offsets 16 bytes earlier. The
combined source contribution is 204 bytes.

After integration, Apple produces a 9,088-byte overlay (SHA-256
`aeceaf38dee61ece3a1fc9518d5d08dd5eb4148d3ff8811659fe695a24cb1578`)
and a 157,688-byte provider (SHA-256
`48bc79d2391b5842316fe9c045727b90da96009ecd2dbc21d70fd3af5e3acff7`).
Linux produces 9,072 / 157,672 bytes with SHA-256
`34d79ac61578fb5c189b06a15c44731506c9cf92f7642f21b531fedc0c0dc2d3` and
`9fcb060ca96964b71da9b1c6f75b1afc5d923a285ce07f6d7e43de31c311be75`.
Canonical Apple accounting is 9,075 source-owned, 10,370 generated patch,
14 alignment, and 138,229 retained official bytes across 149 functions and
147 patch sites. The overlay ends at `0x004367F8`, leaving 6,152 bytes of
headroom.

The unsigned Apple package is 4,739,266 bytes, SHA-256
`f7350f9208368191553ac0c3da07a68af90d66578595b858ad62a519a6dbbc81`;
its 4,478,598-byte flash plan has SHA-256
`17f90bb2d7379b0c051adc54a5d77704fbc9c6052fbc7d1cca196da306d9cfd6`
and records 6,440 placed, two unresolved, five container-only, and six
protected regions. The Linux package is 4,515,260 bytes, SHA-256
`96c1a37d4a14af132f338de523115cf614f9ef5c72da337eeb8382f1c6ea4c45`;
its 2,383,563-byte flash plan has SHA-256
`ea9b3f3218a665831eb7e42931ca1c82e13e9d66632134a27561040d5859d4d9`
and records 3,417 placed regions with the same unresolved/container/protected
boundaries.

No signer, device, debugger, serial endpoint, flasher, reset, boot, or output
transport was accessed. Live mutex scheduling, task naming, formatting, and
transport remain blocked by unavailable authorized responsive right-temple
evidence; the authorized left temple must remain stock. Later retained
bootloader executable spans remain software gaps, so firmware-wide functional
completeness is not claimed.
