# G2 thread-manager dependency boundary

Status: complete, corpus-independent raw-image closure over the authenticated
G2 2.2.6.10 Apollo payload. This is analysis only and performs no device or
flash operation.

## Result

`platform\threads\thread_manager.c` occupies `[0x004C94C8,0x004C9D44)`:
seventeen functions / 1,934 executable bytes plus a 238-byte trailing literal
pool, for 2,172 physical bytes. Ghidra found fifteen of the functions;
source-order recovery adds the kernel bootstrap at `0x004C9B48` (stored as the
thread-manager descriptor entry at `0x0079410C`) and the teardown helper at
`0x004C9B70`. Six functions reference the retained path cell `0x004C9CA0`
(14 raw references).

The preceding boundary is the `lv_bmp.c` literal pool: the third-party BMP
decoder callback at `0x004C93A0` is materialized by `addw r1,pc,#0x1d9` inside
the anchored `lv_bmp.c` function `0x004C91E0`, and the pool cell `0x004C948C`
holds the `lv_bmp.c` path pointer. The following boundary is the closed
`driver\uled\drv_mspi_uled.c` object at `0x004C9D44` (g2-uled-manager closure
`[0x004C9D44,0x004CA6F8)`), cross-pinned in the analyzer.

## Function inventory

Seventeen linked functions: four non-logging setup helpers
(`0x004C94C8`..`0x004C953E`, called only from the anchored `0x004C98C2`), the
ten-slot registered-callback dispatcher `0x004C953E`, six anchored functions
(`0x004C95BC`, `0x004C9778`, `0x004C98C2`, `0x004C995E`, `0x004C9B86`,
`0x004C9BE2`), the internal fan-out helpers `0x004C963A`/`0x004C96B6`, thread
create/terminate wrappers `0x004C9B1A`/`0x004C9B70`, the restored bootstrap
`0x004C9B48` (osKernelInitialize -> osThreadNew -> assert -> osKernelStart),
the public registration pair `0x004C9B86`/`0x004C9BE2` (already observed as
first-party providers from the closed Ring thread), the event-flag setter
`0x004C9C3C`, and the 6-byte state getter `0x004C9C50` with 630 inbound calls.

## Dependency result

The 140 direct body calls divide into 23 internal and 117 external calls:

| Provider | Calls | Provenance |
|---|---:|---|
| EasyLogger | 72 | selected source-equivalent commit `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`; includes the `elog_async` API `0x00448E48` and the output accessor `0x0043D0C8` |
| CMSIS-FreeRTOS | 30 | v10.5.1 commit `d213f261b5be6bb29a7cce8b84071706b72f4d53` over FreeRTOS-Kernel `def7d2df2b0506d3d249334974f51e427c17a41c` and CMSIS_5 `2b7495b8535bdcb306dac29b9ded4cfb679d7e5c` |
| FreeRTOS assert port | 3 | bounded fail-stop seam at `0x005FA0A4` |
| littlefs MX25U25643G port | 1 | bounded backend adapter over the v2.10.1 source-equivalent baseline `0494ce7169f06a734a7bd7585f49a9fa91fa7318` |
| closed first-party | 9 | compact-log init, MX25 flash driver, event-loop schedule/remove, NVDB product mode, transport protocol, DB API, AT core, UART sync |
| bounded first-party | 2 | unclosed UX-region `0x0047E232` and UART-region `0x0054171C` seams |

The exact CMSIS seams are `osKernelInitialize`, `osKernelStart`,
`osKernelGetTickCount`, `osThreadNew`, `osThreadGetId`, `osThreadSetPriority`,
`osThreadTerminate`, `osThreadFlagsSet`, `osThreadFlagsWait`,
`osEventFlagsNew`, `osEventFlagsSet`, and `osEventFlagsWait`. They use already
authenticated source bodies and add no new FreeRTOS version or commit
discriminator. There is no IAR DLIB edge in this object.

The ten indirect calls are the registered-callback dispatcher at
`0x004C9566`..`0x004C95AE`: each site loads a RAM control word through the
pool cells `0x004C9C70`..`0x004C9C94` (`0x20003F98`, `0x2000408C`,
`0x20003664`, `0x2000060C`, `0x20004120`, `0x20004044`, `0x20003FFC`,
`0x20004020`, `0x20004068`, `0x200040FC`) and calls the registered handler.
The dispatch is bounded to those ten registered slots.

## Ingress and behavior closure

The object has 680 direct `BL` entry sites, three stored Thumb entry pointers
(`0x004C9D24 -> 0x004C98C2` and `0x004C9D28 -> 0x004C9B1A` inside its own
pool, `0x0079410C -> 0x004C9B48` in the thread descriptor table), zero
wide-branch entries, zero strict-interior `BL` targets, and zero noncode `BL`
targets. One raw instruction-aligned 32-bit window at `0x00541825` spells
`0x004C9987` inside `0x004C995E`; it is a packed 16-bit field pair, not a
stored pointer. Two further raw byte windows at `0x004D0A71` and `0x004BF6FF`
spell interior/mid-instruction addresses and are likewise not promoted.

## Noncode accounting

The trailing 238-byte pool `[0x004C9C56,0x004C9D44)` holds the ten RAM
callback-cell pointers, the retained-path cell `0x004C9CA0`, the two self
entry-pointer cells, and the remaining function literals. All function bodies
decode completely; no embedded pools remain inside bodies.

## Discriminator evidence and limitations

No embedded reusable third-party body exists in this object; all reusable
utilities terminate at already selected providers. The private G2 producing
commit remains binary-unobservable. The two restored functions are admitted by
the stored descriptor pointer (`0x004C9B48`) and by adjacency-plus-call
evidence (`0x004C9B70`), not by path references.

## Reproduction

```sh
python3 openCFW/tools/analyze_g2_thread_manager.py
python3 -m unittest openCFW.tests.test_analyze_g2_thread_manager
```

The analyzer pins every function body, the complete physical interval and
literal pool, all call and ingress topology, both object boundaries against
the closed neighbors, retained-path references, provider commits, and
production-overlay exclusion.
