# R1 source BLE candidate: pinned Cordio nRF52840, 2026-11-11

The pinned `third-party/upstream/cordio` tree includes a complete BLE host,
controller and Nordic nRF52840 radio platform. Its `ble-apps/build/tag/gcc`
sample was built unchanged with the installed `arm-none-eabi-gcc` 15.3.1.
All output was redirected under ignored
`build/r1-cordio-tag-20261111/`; the submodule remained clean. The build
command used its own makefile with absolute `INT_DIR` and `BIN_DIR` overrides.
The sample links without undefined symbols.

| Standalone Cordio sample property | Observed value |
| --- | ---: |
| Flash load end / `tag.bin` size | `0x1c24c` (115,276 bytes) |
| Flash address space below the current R1 app origin `0x27000` | `0xadb4` bytes remain |
| `.text` and read-only content reported by `size` | 114,653 bytes |
| Initialized data | 620 bytes |
| `.bss` | 10,508 bytes |
| Linked archive members | 31: 30 `libc_nano.a`, one `libnosys.a` |
| Precompiled Nordic CC310 members linked | 0 |

An isolated second build appended `-mfpu=fpv4-sp-d16 -mfloat-abi=hard` to
Cordio's compile and link flags. It also links successfully. `readelf -A`
reports `Tag_ABI_VFP_args: VFP registers` and `Tag_FP_arch: VFPv4-D16`,
matching the current R1 application ELF on those ABI attributes. Its
`tag.bin` is 115,308 bytes, leaving `0xad94` bytes below `0x27000`, and has
SHA-256 `5f65a7dcc9442c9deff4951fc3b513a4a21701b7404dff63a4c0421710f24111`.
The ignored makefile copy and full build log are under
`build/r1-cordio-tag-20261111/`. ABI attribute agreement is a prerequisite
for integration, not evidence of API or runtime compatibility.

The same hard-float Cordio source also compiles against the repository's
pinned `vendor-cache/r1/nRF5_SDK_17.1.0_ddde560` BSP and links. The isolated
makefile adds a source pattern rule for that BSP path; no pinned file was
edited. Its `tag.bin` is 115,436 bytes, SHA-256
`6bd7109cd19683ac10cf3d16ca579166c09003b785904760949ce476e5ce06bd`.

A second link of those exact compiled objects used an ignored copy of
Cordio's linker script with flash limited to `0x00000000..0x00026fff` and
RAM to `0x20000000..0x200064a7`, matching the space before the current R1
application origins. It passes static placement: flash load ends at
`0x1c2ec`, `.bss` ends at `0x20002b7c`, the 4 KiB stack occupies
`0x200054a8..0x200064a7`, and the linker reports a heap interval
`0x20002b7c..0x200054a7` (10,540 bytes). The relinked binary SHA-256 is
`235e0fa8c7135dcd31a738a09a0d17dbf18040f7955b622a96bc9e4058b16254`.
This proves only the sample's static fit. It does not establish runtime heap
or stack sufficiency, R1 SVC compatibility, IRQ coexistence, radio behavior,
source-only library linkage, or an installable image.

An isolated source-provider link adds five pinned musl memory/string C units
and the existing R1 C `memcmp`, `strcpy` and `strncpy` owners. It replaces
eight of the sample's 31 linked C-library archive members; **23 remain**.
The lower-region sample still links, with a 116,264-byte binary, SHA-256
`521893c1f9ae9f6140ee594c5cfc2475e80d004d0ee8400271232683bba71e76`.
The source objects, an ignored `endian.h` compatibility header for pinned
musl, makefile copy and link map are under
`build/r1-cordio-tag-20261111/source-libc/` and `source-libc-plus-bin/`.
Disabling the sample's optional trace output saves 7,540 binary bytes but
leaves all 23 archive members, mostly through its terminal and C runtime
startup path. No production Cordio source was edited.

A relocatable link of 247 compiled Cordio core, WSF, Nordic platform and
SDK driver objects, excluding the sample application and profiles, succeeds
without any archive. Its ignored artifact is
`build/r1-cordio-tag-20261111/cordio-core.o`. As expected for a library,
it retains unresolved imports for the future integration caller, libc and
linker boundaries. It also exposes `CC_AESCCM` and `SaSi_LibInit/Fini` from
the Nordic CryptoCell platform source. Those optional paths were garbage
collected from the sample image, but a source-only encrypted R1 replacement
must either provide equivalent C crypto or prove the paths unused for its
required features.

An ignored relocatable-link probe with the 941 current R1 application input
objects finds 52 duplicate strong symbols when all Cordio core objects are
included. A broad exclusion of nine Nordic SDK driver/system objects removes
51 of them. Three of those nine (`nrfx_i2s`, `nrfx_qspi` and `nrfx_uarte`)
can be added back without a duplicate symbol; the exclusion was broader
than necessary. The remaining collision is **`RTC1_IRQHandler`**: R1's FreeRTOS
tick owner is `r1/src/application/rtos/port-start/rtc.c`, while Cordio's
`pal_rtc.c` owns the same IRQ and directly uses `NRF_RTC1` in its timer,
baseband and radio paths. The SDK's nRF52840 peripheral definitions give
RTC1 four compare channels but RTC0 only three. Cordio uses all four:
WSF timer channel 0, radio channels 1 and 2, and baseband-start channel 3.
Changing only `RTC1` to `RTC0` would therefore be an invalid port. The
probe receipts are `combined-probe.log`, `combined-no-sdk-probe.log` and
their object lists under ignored `build/r1-cordio-tag-20261111/`.

The resident stack needs a real timer-ownership design before combining its
code with R1. Static flash/RAM fit and a clean standalone link do not solve
this IRQ and compare-channel conflict.

The implemented opt-in resource assignment is R1 FreeRTOS tick on
RTC0, R1's structured `sys rtc` clock on RTC2, and Cordio on RTC1. The R1
tick uses the RTC's TICK event and compare channel 0 for tickless sleep, so
RTC0's three channels suffice for that owner. Retargeting must change the
pinned port's `portNRF_RTC_REG` and `portNRF_RTC_IRQn`, the
`xPortSysTickHandler` name, application vector slot 27 (RTC0) and slot 33
(RTC1), and both source counter readers (`app_timer_counter.c` and
`system_timer.c`). The RTC1-specific static assertions in the R1 port
contracts also need updating. It cannot be accomplished by renaming an IRQ
symbol at link time: that would leave register reads and tickless compare
operations on RTC1. The app's RTC2 descriptor is separately initialized at
`0x40024000`, IRQ 36, and continues to use the pinned nrfx driver.

This assignment also requires one low-frequency-clock owner. R1's tick
requests the LFCLK through `nrf_drv_clock_lfclk_request`; pinned Cordio's
`PalRtcInit` directly writes `NRF_CLOCK->LFCLKSRC` and starts that clock.
The R1-owned C port `r1/src/application/ble/cordio_rtc_r1.c` now requests
one LFCLK reference through the R1 clock manager, waits for it to run, and
never restarts it on counter reads. It is compiled only with
`--cordio-rtc0` and replaces the pinned Cordio `pal_rtc.o` in the joint
link. `sdk_config.h` now keeps the legacy `CLOCK_CONFIG_LF_SRC` alias at the
recovered RC value 0, so `apply_old_config.h` cannot silently overwrite the
recovered `NRFX_CLOCK_CONFIG_LF_SRC` with the SDK example's crystal value 1.
Disassembly of `nrfx_clock_enable` confirms a zero write to LFCLKSRC at
`0x40000518`; the new `PalRtcInit` calls
`nrf_drv_clock_lfclk_request` and `nrf_drv_clock_lfclk_is_running`.
An ignored host fake-register test under
`build/r1-cordio-tag-20261111/rtc1-pal-host/` passes repeated initialization
(one clock reference), counter reads, compare programming, IRQ callback
dispatch and priority 6. Its fake HAL intentionally has no `NRF_CLOCK`
register, so a direct LFCLK write would fail to compile. This does not test
hardware timing or the Nordic clock manager's asynchronous behavior.
Its RTC1 IRQ priority uses CMSIS's unshifted value 6; the upstream `0x80`
value would truncate to priority zero on this three-bit NVIC. The port still
requires a verified bootstrap order after `nrf_drv_clock_init`, and runtime
clock reference lifetime has not been tested on hardware. Pinned
`PalSysInit` directly starts HFCLK and its critical-section helpers
unconditionally enable interrupts on exit. The R1 C port
`r1/src/application/ble/cordio_sys_r1.c` now holds one HFCLK manager
reference, preserves the incoming PRIMASK across nested critical sections,
and leaves HFCLK running through sleep. Its current isolated fake-HAL check
under `build/r1-cordio-heap-probe-20261111/sys-pal-host/` covers repeated
initialization, one HFCLK request, no development-kit LED calls,
nested/unmatched critical-section exits, an initially masked caller,
busy-state calls and sleep. That fake HAL contains no
`NRF_CLOCK` register, so direct HFCLK programming would fail to compile.
The source remains an opt-in candidate: a future BLE bootstrap must call it
after `nrf_drv_clock_init` and validate clock and interrupt behavior on R1.
The pinned Cordio startup, excluded from the joint application link, normally
initializes `SystemHeapStart` and `SystemHeapSize` from its linker heap bounds.
The R1 C port `r1/src/application/ble/cordio_heap_r1.c` initially supplied
the pinned sample's 10,540-byte, eight-byte-aligned WSF heap. It initializes
the heap once from `PalSysInit`, checks rounded reservations and reports
used/available bytes. The later R1 resource profile reserves 16,384 bytes
because the pinned sample configuration cannot fit the earlier capacity.
The ARM object places the buffer in `.bss.r1_cordio_heap` as `NOBITS`, so it adds no stored
zero bytes to flash. The current ignored fake-HAL heap check passes allocation,
one-time initialization, exhaustion and overflow cases under ordinary Clang
and ASan/UBSan. The system PAL's stack helper now uses the R1 linker names
`__StackLimit` and `__StackTop`; its stack-fill high-water semantics remain
unverified because the R1 startup has not been shown to fill that range.
The two-region flash/RAM layout below uses the space reserved for S140;
the upper R1 application region has only 6,800 bytes of RAM headroom in the
default strict image.
Cordio's radio path programs TIMER0 and PPI
channels 10, 13, 14 and 15, so those resources and radio interrupts require
an application-wide ownership audit before an integrated image is credible.
An ignored `rtc0-tick-probe/` copied the four affected R1 application C units
and overlaid the two pinned FreeRTOS configuration headers. It compiled the
RTC0 tick, counter readers and vector table with the recorded per-unit Clang
commands. Disassembly confirms that `app_timer_cnt_get` and
`osKernelGetSysTimerCount` read RTC0 `COUNTER` at `0x4000b504`, and the tick
handler accesses RTC0 registers. Vector relocations place the R1 tick at
slot 27 while Cordio retains RTC1 at slot 33. A relocatable link of the 941
R1 application inputs (four replaced by the probe units) plus the 238-object
Cordio core with shared SDK drivers excluded succeeds with no duplicate
strong symbol. Its output still has 98 undefined entries, including linker
boundaries, `main`, optional Nordic CryptoCell and Cordio platform symbols.
This is a compile/link topology result, not a final image, protocol bridge,
IRQ timing test or hardware validation. The probe files and `combined.log`
are under ignored `build/r1-cordio-tag-20261111/rtc0-tick-probe/`.

The production R1 source now has an opt-in RTC0 tick route, selected by
`python3 tools/build/sources.py build --device r1 --normal-svc --cordio-rtc0 --out build/<fresh-directory>`.
It changes the FreeRTOS tick IRQ and vector slot, the tickless RTC register,
and both counter readers only in this source-built BLE variant. The same
conditional vector table now routes Cordio's RADIO, TIMER0, TIMER1 and
CCM/AAR handlers at slots 17, 24, 25 and 31, in addition to RTC1 at slot 33.
The R1 tick occupies RTC0 slot 27. Relocations of the compiled vector object
confirm those six destinations; routing does not establish IRQ timing or
peripheral ownership. The default stock-compatible route remains RTC1. In
the current ignored receipt
`build/sources-r1-cordio-two-region-20261111/report.json`, 1,209/1,209
application and 85/85 bootloader C units compile and compose without
duplicate strong symbols. The application composition includes 236 pinned
Cordio/SDK C units from the manifest, excludes the original RTC, system,
WSF heap and sample startup objects, and resolves RADIO, TIMER0, TIMER1,
RTC1 and CCM/AAR handlers. It has 71 unresolved imports, including 52 Nordic
`sd_*` application interfaces and the two lower-BSS linker boundaries. The
changes from the earlier ignored
`rtc0-tick-probe/combined-r1-heap-no-startup.o` joint link include the C
vector and factory GAP address services, plus those new linker boundaries.
It is not a final application image. The BLE bridge, HFCLK service
integration and radio resource ownership remain open.
The ignored response file `cordio-core-with-r1-heap-no-startup.rsp` names
236 C-built objects: 233 from pinned Cordio C and three pinned Nordic SDK
drivers. The current manifest replaces one pinned Cordio PAL object with the
R1 port of `pal_cfg.c`, leaving 232 pinned Cordio units, one R1 PAL and the
three SDK units (`nrfx_i2s.c`, `nrfx_qspi.c`, `nrfx_uarte.c`). All 236 are
explicit `cordio-rtc0` units in the R1
manifest, compiled with the pinned Cordio sample's hard-float GCC flags.
The default build selects none of them and still strictly links both R1
payloads. A resolved two-region final image and Nordic/Cordio protocol bridge
remain necessary; the current sample board definition also needs R1 hardware
porting before runtime use.
The pinned Cordio Nordic `pal_cfg.c` derives its default BLE address from
`FICR.DEVICEID`, whereas the nRF52840 has separate `FICR.DEVICEADDR` registers
and the Nordic SDK identifies `DEVICEADDR` as the SoftDevice's default
advertising address. The R1-owned `cordio_cfg_r1.c` and
`gap_factory_address_c.c` now use the same factory-address helper, with
random-static high bits. The address has not been read from physical R1
hardware. See the pinned
`platform/targets/nordic/sources/pal_cfg.c` and the
[Nordic FICR register reference](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/ficr.html).

A strict application-link attempt with this variant, recorded under ignored
`build/r1-cordio-variant-final-probe-20261111/`, fails on 45 reachable
`sd_*` imports. The linker garbage-collects the uncalled Cordio controller
and its heap, so its apparent 6,432-byte RAM headroom is not a whole-stack
fit measurement. A second ignored link probe under
`build/r1-cordio-rooted-probe-20261111/` explicitly retains `PalSysInit`;
it places the 10,540-byte C WSF heap and overflows the current stock-layout
RAM region by 4,144 bytes, even before the Nordic API bridge is implemented.
These probes establish a concrete RAM-layout problem for a source-built BLE
image; they are not firmware images.
An earlier opt-in R1 linker probe placed the 10,540-byte C heap at
`0x20000000..0x2000292b`, inside the memory formerly reserved for S140,
while retaining the existing application RAM region. The default strict
application image still has SHA-256
`653b09e3d0a52402db2fb4cde65320418954d1a569e9bf4908688127840340c6`
and 6,800 bytes of upper RAM headroom. An ignored rooted link receipt at
`build/r1-cordio-factory-address-rooted-probe-20261111/` confirms the heap
placement with no region overflow. It still fails on 45 reachable `sd_*`
imports, two of which become reachable when `PalSysInit` is retained. This
layout and the controller have not been validated on hardware.

Rooting `LlInitControllerInit` as well as `PalSysInit` without new flash
placement overflows the current upper application flash region by 54,480
bytes and leaves only 924 bytes of upper RAM headroom. Ignored two-region
linker probes under `build/r1-cordio-controller-split-flash-v2-probe-20261111/`
and `build/r1-cordio-controller-split-ram-flash-probe-20261111/` place reachable
Cordio code at `0x1000` in the former S140 flash region and its uninitialized
data after the WSF heap in former S140 RAM. The latter probe places 62,006
bytes in lower flash and 5,716 bytes of Cordio BSS in lower RAM, with no
region overflow, 480 bytes of upper flash headroom and 6,644 bytes of upper
RAM headroom. The opt-in `openr1_cordio.ld` now owns these lower sections and
the conditional C `Reset_Handler` zeros the lower BSS before entry. The
current rooted link receipt at `build/r1-cordio-isolated-controller-rooted-20261111/`
places the same 62,006-byte code and 5,716-byte BSS sections without region
overflow; reset code reduces upper flash headroom to 448 bytes. Future
bridge and bootstrap code will change these figures. The linker still fails
on 45 reachable `sd_*` calls, so this is a size and placement probe only.

The later direct-clock Cordio receipt at
`build/sources-r1-cordio-direct-clock-20261111/report.json` compiles all
1,294 R1 units with no failed or duplicate strong symbols. Only this variant
compiles the pinned `nrf_drv_clock.c` without `SOFTDEVICE_PRESENT`, retaining
the nrfx clock interrupt and direct HFCLK path. Its application composition
has 68 unresolved imports, down from 71, including 49 `sd_*` calls; the
bootloader still has 32 `sd_*` imports, for a 50-interface union. A rooted
two-region link probe at
`build/r1-cordio-direct-clock-controller-rooted-20261111/` retains both
`PalSysInit` and `LlInitControllerInit`: 43 reachable `sd_*` calls remain,
with no region overflow. It places 62,006 bytes of Cordio code in lower
flash and 5,716 bytes of BSS in lower RAM; upper flash and RAM have 672 and
6,628 bytes free, respectively. These are diagnostic figures from a failed
link, not a runnable firmware image.

The shared C event-wait service in the subsequent
`build/sources-r1-cordio-wfe-shared-20261111/report.json` closes
`sd_app_evt_wait` in both normal-function payloads. Its 1,210 application
and 86 bootloader units all compile and compose without duplicate strong
symbols. The application now has 67 unresolved imports, including 48
`sd_*` calls; the bootloader has 31 `sd_*` calls, for a 49-interface union.
The unrooted strict link at `build/r1-cordio-wfe-final-probe-20261111/`
and the rooted controller probe at
`build/r1-cordio-wfe-controller-rooted-20261111/` each fail on 42 reachable
`sd_*` calls without a region overflow. The rooted probe retains 62,006
bytes of Cordio code and 5,716 bytes of BSS in the lower regions; upper
flash and RAM retain 672 and 6,628 bytes, respectively. Its linker failure
still precludes an image.

The 10,540-byte heap was insufficient before any controller allocation.
The ignored ARM-layout probe under `build/r1-cordio-heap-probe-20261111/`
measured 12-byte WSF pool headers and four-byte allocation granularity.
With the pinned nRF52840 sample's eight advertising reports, 16 TX and
eight RX buffers, 24 ISO buffers and 512-byte ACL data, its five WSF pools
alone require **29,436 bytes**: 18,896 bytes beyond that heap. The prior
rooted link therefore established static section placement, not runtime
memory fit.

The R1 PAL now selects one legacy advertising set, three peripheral links,
251-byte ACL buffers for the recovered 247-byte ATT MTU, eight TX and eight
RX buffers, one report slot and no ISO buffers. It keeps the required
251-byte extended scan buffer bound. The resulting WSF descriptors are
`(16,8)`, `(32,4)`, `(128,1)`, `(269,1)` and `(279,16)`; with the measured
ARM layout they require **5,196 bytes**. This leaves 11,188 bytes of the
new 16,384-byte WSF heap for link-layer allocations. The ignored
`build/r1-cordio-r1-memory-controller-rooted-20261111/` link probe places
that heap at `0x20000000..0x20003fff`, 5,716 bytes of Cordio BSS at
`0x20004000..0x20005653`, and leaves 3,668 bytes in lower RAM without a
region overflow. It retains 42 unresolved `sd_*` calls. The revised PAL
and heap pass the 1,210-unit application composition; the heap's repeated
init, reservation and exhaustion checks also pass ordinary Clang and
ASan/UBSan under the ignored host fake-HAL probe. Actual controller
initialization, runtime allocation, BLE behavior and hardware fit remain
unverified.

The R1 system PAL now omits the pinned development-kit LED setup and trap
LED write. The ignored
`build/r1-cordio-r1-memory-no-led-controller-rooted-20261111/` map has no
retained `PalLedInit`, `PalLedOn` or `PalLedOff` symbol. Its 16,384-byte
heap and 5,716-byte lower BSS still fit with 3,668 lower-RAM bytes free;
retained Cordio code is 61,832 bytes and the link still has 42 reachable
`sd_*` calls. The fake-HAL system/heap checks pass under ordinary Clang and
ASan/UBSan. Other sample board conditional code needs an R1 pin ownership
audit before a hardware run.

The fresh default-profile receipt at
`build/sources-r1-wfe-stock-20261111/report.json` compiles all 974
application and 86 bootloader units without failure or duplicate strong
symbol. Their strict links at `build/r1-wfe-stock-app-link-20261111/` and
`build/r1-wfe-stock-boot-link-20261111/` preserve the previous image sizes
and SHA-256 values: 694,228 bytes at
`653b09e3d0a52402db2fb4cde65320418954d1a569e9bf4908688127840340c6`
for the application, and 23,024 bytes at
`08e108776638ad4feaf2eada3861ab37d587b44ae3b5b75daacfa386ea67ac67`
for the bootloader.

The remaining bootstrap boundary is concrete: R1's
`native_softdevice_bootstrap.c` invokes `nrf_sdh_enable_request`, configures
BLE RAM and GATTS, then calls `nrf_sdh_ble_enable` and `sd_ble_opt_set`.
The pinned Cordio controller sample instead loads baseband and LL runtime
configuration, initializes WSF buffers/timers, calls
`LlInitControllerInit`, loads the factory address, and enters its own WSF
loop. The source-built port must join that initialization to R1's FreeRTOS
and Nordic event path; retaining `LlInitControllerInit` for sizing does not
perform the bootstrap or translate events.

`nrf_sdh_enable_request` calls `sd_softdevice_enable` inside a critical
region, while the R1 `PalSysInit` waits for an HFCLK interrupt. Calling the
latter from that service would deadlock with interrupts masked. The later
`nrf_sdh_ble_enable` call occurs outside the critical region and is a possible
bootstrap boundary, but requires actual BLE state, events and scheduling.
The R1 system PAL avoids the development-kit LED startup path; other sample
board conditional paths still need a pin-ownership review.

The latest receipts use the corrected R1 SDK resource assertion in
`native_softdevice_bootstrap.c`, where the recovered SDK header resolves to
three peripheral links and a 247-byte MTU. The Cordio core compile profile
resolves its separate sample-board `sdk_config.h` to one link and a 23-byte
MTU, so the assertion cannot live in that profile; further SDK peripheral
configuration needs an explicit R1 ownership audit. The fresh variant build
`build/sources-r1-cordio-r1-memory-r1-contract-20261111/report.json`
compiles and composes all 1,210 application and 86 bootloader units with no
failed unit or duplicate strong symbol. Its unrooted strict link still has
42 reachable `sd_*` calls. The rooted map under
`build/r1-cordio-r1-memory-r1-contract-controller-rooted-20261111/`
retains the 16,384-byte heap, 5,716-byte lower BSS and 61,832-byte lower
code section without region overflow or development-kit LED code. Fresh
default-profile strict links under `build/r1-memory-stock-app-link-20261111/`
and `build/r1-memory-stock-boot-link-20261111/` preserve the previous
694,228-byte and 23,024-byte image hashes.

The pinned controller sample selected `CHCI_TR_UART=1`. If retained,
`LlInitControllerInit` reaches `PalUartInit` and configures UARTE0 on the
sample board's fixed P0.26/P0.27 pins. The R1 Cordio profile now selects
`CHCI_TR_UART=0` and `CHCI_TR_CUSTOM=0`, so it does not initialize an
external HCI transport. This is Cordio's integrated ExactLE host path:
its HCI commands call `Ll*` APIs directly, and `hciCoreInit` registers
`hciCoreEvtProcessLlEvt` through `LlEvtRegister` and its ACL handlers through
`LlAclRegister`. `LlEvtRegister` stores one callback, so controller
initialization must precede `hciCoreInit`; otherwise the controller's LHCI
registration replaces the host event callback. The Nordic `sd_*` API and
event adapter remains a separate, unimplemented boundary.

The pinned `chci_tr.c` does not compile when both external transport modes
are disabled because its fallback branch names two UART-only static
functions. `r1/src/application/ble/cordio_chci_tr.c` is the selected R1
copy, with only those invalid references removed from executable code. The
upstream copy is not a second compiled provider.

The fresh integrated-host receipt at
`build/sources-r1-cordio-integrated-host-clean-20261111/report.json`
compiles and composes all 1,210 application and 86 bootloader units with
zero failed units or duplicate strong symbols. Its unrooted strict link at
`build/r1-cordio-integrated-host-clean-strict-20261111/` fails on 42 reachable
`sd_*` imports. The ignored `LlInitControllerInit`-rooted link at
`build/r1-cordio-integrated-host-clean-rooted-20261111/` has the same 42 imports,
no `ChciTr*` missing hook, and no retained `PalUartInit` or `PalLedInit`.
The lower sections hold 60,464 bytes of Cordio code, 16,384 bytes of heap
and 5,640 bytes of BSS without region overflow. `HciCoreInit` is not
retained in that artificial root; the required controller-then-host
bootstrap remains to be wired into the application.

`r1/src/application/ble/cordio_controller_bootstrap.c` now contains that
controller-then-host initialization sequence as a callable C unit. It
loads the R1 PAL runtime profile, checks the WSF pool requirement before
allocation, initializes WSF, reserves its pool, initializes the controller,
reserves the reported LL allocation, loads the factory BLE address, and
registers the ExactLE HCI handler after controller LHCI registration. The
function rejects a second attempt after partial failure; its caller must
have initialized `nrf_drv_clock` and enabled interrupts. The ignored
`build/r1-cordio-controller-bootstrap-probe-20261111/` host harness checks
normal ordering, pool exhaustion, a zero LL allocation, a mismatched pool
size and repeated calls under ASan/UBSan. These mocks do not measure the
actual controller's dynamic allocation.

`build/sources-r1-cordio-bootstrap-20261111/report.json` compiles and
composes all 1,211 application and 86 bootloader units without failures or
duplicate strong symbols. The strict application link at
`build/r1-cordio-bootstrap-strict-20261111/` still has 42 reachable `sd_*`
imports. Rooting `r1_cordio_controller_bootstrap` under
`build/r1-cordio-bootstrap-rooted-20261111/` retains both
`LlInitControllerInit` and `HciCoreInit`, with 65,640 bytes of lower Cordio
code, 16,384 bytes of heap and 6,076 bytes of BSS. It has no lower-region
overflow, no retained sample UART/LED initialization and no added undefined
symbol. This is a controller/HCI initialization routine, but it is not called
by the current Nordic bootstrap and WSF dispatch is not yet attached to
FreeRTOS. A working source-built BLE stack remains unproven.

The default SVC profile still compiles 974 application and 86 bootloader
units under `build/sources-r1-bootstrap-stock-20261111/report.json`. Its
fresh strict links at `build/r1-bootstrap-stock-app-link-20261111/` and
`build/r1-bootstrap-stock-boot-link-20261111/` pass with no unresolved
symbol and produce the same 694,228-byte application and 23,024-byte
bootloader images as before this bootstrap unit was added.

The fresh stock-profile receipt at
`build/sources-r1-integrated-host-fixed-stock-20261111/report.json`
compiles and composes 974 application and 86 bootloader units. Its strict
links under `build/r1-integrated-host-fixed-stock-app-link-20261111/` and
`build/r1-integrated-host-fixed-stock-boot-link-20261111/` both pass with
zero unresolved symbols and produce 694,228-byte and 23,024-byte images.
That stock profile retains the existing S140 boundary and does not prove
the source-built BLE variant is complete.

The intermediate custom-transport probe at
`build/sources-r1-cordio-internal-hci-boundary-20261111/report.json`
exposed two `ChciTr*` hooks, but the integrated host does not need that
external path. Its rooted map retained neither `PalUartInit` nor
`PalLedInit`. That probe was replaced by the no-external-transport profile;
its 44 unresolved calls are historical, not the current target. Static
section fit does not establish runtime allocation, controller operation or
a bootable image.

The manifest's original `BT_VER=8` compiled a Bluetooth 4.2 controller
while the bootstrap requested 5.2 at runtime. This omitted 5.x LL paths
from the earlier memory probes. The pinned BLE 5.2 makefile lists 251
controller C sources; the candidate initially selected 124. Adding the
missing upstream sources and compiling with `BT_VER=11` raised the
bootstrap-rooted Cordio BSS to 11,912 bytes; together with the 16,384-byte
heap it overflowed the reclaimed 25,768-byte BLE RAM region by 2,528
bytes. The 5.0 profile (`BT_VER=9`) retains the PHY features used by R1
without the product-unused 5.2 ISO role, but the complete upstream source
set still overflowed BLE RAM by 1,124 bytes before resource tuning.

R1 has no central or observer role. The R1-owned
`r1/src/application/ble/cordio_init_r1.c` replaces the pinned LL
initializer and skips extended-scanner allocation for this role. A generic
scanner query still retained Cordio's `LL_MAX_PER_SCAN=6` static table,
measured at 4,224 bytes in the ARM map. Setting the compile-time capacity
to one reduces that table to 704 bytes. The resulting 5.0 bootstrap-rooted
map at `build/r1-cordio-ble50-scan1-rooted-20261111/` holds 89,920 bytes
of Cordio code, 16,384 bytes of heap and 6,868 bytes of BSS, leaving 2,516
bytes in lower RAM without an overflow. Its 42 remaining undefined symbols
are all Nordic `sd_*` calls. A dormant 5.2 BIS master object caused two
`libgcc` archive members to be pulled in even though their input sections
were discarded; excluding that object in an ignored link probe removed both
archive members without introducing another undefined symbol. The R1
manifest now omits it.

The ignored ARM layout probes under
`build/r1-cordio-dynamic-memory-probe-20261111/` measured the relevant
32-bit structures. For the current one-advertising-set, three-connection
profile, the pinned allocation formulas require 384 bytes for three
four-entry LL lists, 3,024 bytes for connection contexts and eight TX
descriptors, and 2,359 bytes for the advertising context and two 31-byte
data buffers. With scanning skipped, this is 5,767 LL bytes, rounded to
5,768 by `WsfHeapAlloc`. Adding the measured 5,196-byte WSF pool reserve
leaves **5,420 bytes** of the 16,384-byte heap. This is a source and ARM
structure calculation, not an execution of `LlInitControllerInit`; hardware
initialization and runtime allocation checks remain open.

The current BLE 5.0 peripheral variant is recorded at
`build/sources-r1-cordio-ble50-final-profile-20261111/report.json`:
1,336 application and 86 bootloader C units compile and compose without
failed units or duplicate strong symbols. The unrooted strict link at
`build/r1-cordio-ble50-final-strict-20261111/` has 42 reachable Nordic
`sd_*` imports and no archive member. Rooting
`r1_cordio_controller_bootstrap` at
`build/r1-cordio-ble50-final-rooted-20261111/` retains `HciCoreInit`,
89,920 bytes of Cordio code, the 16,384-byte heap and 6,868 bytes of BSS.
There is no region overflow or archive member; lower RAM has 2,516 bytes
of static headroom. The link still fails on the same 42 Nordic calls.
The default SVC profile was rebuilt at
`build/sources-r1-ble50-stock-20261111/report.json`; its strict application
and bootloader links under `build/r1-ble50-stock-app-link-20261111/` and
`build/r1-ble50-stock-boot-link-20261111/` both pass and preserve the
previous image SHA-256 values.

The latest repository-wide `make sources` receipt is
`build/sources-all-r1-wfe-20261111/report.json`: all selected G2 and R1
payload units compile and compose with zero failed units or duplicate strong
symbols, and both manifests stayed fixed during compilation. Its R1 default
profile includes 974 application and 86 bootloader units. The earlier
`build/sources-all-r1-two-region-20261111/report.json` exited nonzero only
because the separately edited G2 manifest changed during that G2 build.
The prior repository-wide receipt
`build/sources-all-r1-factory-address-20261111/report.json` passed before
the conditional R1 reset-zeroing change.

The R1 manifest now builds `r1/src/application/ble/cordio_ccm.c` with the
already-pinned tiny-aes-c block cipher and the pinned Nordic SDK C
`nrf_ecb.c`. The former implements Cordio's `CC_AESCCM` call in C, including
full-length tag comparison, rejection of altered tags and clearing the
plaintext buffer on authentication failure. The latter supplies Cordio's
three `nrf_ecb_*` hardware AES entry points. The AES-CCM provider passed the
three SP800-38C examples embedded in the pinned Mbed TLS source, 300
deterministic differential encryption/decryption cases against the pinned
Mbed TLS C implementation (nonce sizes 7–13, even tag sizes 4–16, messages
0–256 bytes, AAD up to `0xfeff` bytes), and an `0xff00`-byte AAD boundary
comparison against OpenSSL. Mbed TLS in this SDK uses the short AAD length
encoding at exactly `0xff00`, so that boundary required the independent
OpenSSL check. These host checks and the test source remain under ignored
`build/r1-cordio-tag-20261111/ccm-source-probe/`.

The default R1 source build compiles 974/974 application and 86/86 bootloader C
units, with zero duplicate strong symbols. Both strict links pass; the
application image is 694,228 bytes with 6,800 bytes of RAM headroom. The
32-byte increase and SHA-256 change to
`653b09e3d0a52402db2fb4cde65320418954d1a569e9bf4908688127840340c6`
come from correcting the shared clock configuration, not from a reachable
Cordio caller. The bootloader image remains 23,024 bytes with SHA-256
`08e108776638ad4feaf2eada3861ab37d587b44ae3b5b75daacfa386ea67ac67`.

In the ignored RTC0/Cordio relocatable probe, excluding the test-only
`pal_bb_ble_tester.o` removes 20 unresolved test-mode variables, and the
two source AES providers close four more imports. Before restoring the three
safe Nordic drivers, that probe has 74 undefined entries: 52 linker/trace
boundaries, 15 nrfx platform calls, three Goodix optional calls, two `SaSi`
lifecycle calls, one `main` entry and one weak UART vector. Restoring the
pinned C `nrfx_i2s`, `nrfx_qspi` and `nrfx_uarte` objects closes all 15 nrfx
calls plus the weak UART vector without new duplicates, leaving **58**
undefined entries: the 52 boundaries, three Goodix calls, two `SaSi` calls
and `main`. The receipt is `rtc0-tick-probe/combined-shared-sdk.log` and its
object response file under the ignored Cordio build directory. These are
object-level imports, not a final-link failure
count; section collection and the final linker script change the reachable
set. The two `SaSi_LibInit/Fini` calls are in Cordio's
unmodified CryptoCell initialization. The software CCM provider requires no
CryptoCell runtime, but the Nordic PAL still enables CryptoCell directly;
its initialization and ownership need a source port if that lifecycle is
used. No direct `PalCryptoInit/DeInit` caller appears in the pinned Cordio
source, so a future final link may discard those functions; the relocatable
probe cannot establish reachability. A no-op library shim would conceal this
decision. The combined probe is not an executable firmware image.

This is a **sample build**, not an R1 SoftDevice replacement. Linker garbage
collection includes only the sample's features. The R1 application's static
[SVC inventory](s140-source-dependency-inventory.md) uses 41 distinct BLE
services plus SoC, SoftDevice manager and MBR services. Cordio exposes a
different host/controller API and startup ownership. A C compatibility layer
would have to preserve the Nordic calls and event formats actually consumed
by R1, bind its radio and interrupt paths, and fit flash and RAM alongside
the current application. The sample's 31 archive members would need pinned
C source providers before it met the source-only build requirement. The
Nordic platform also contains five inline-assembly sites for semihosting,
interrupt masking and wait-for-interrupt; their contracts need separate
review for an assembly-free target.
Cordio produces different executable bytes from Nordic S140/MBR, so it cannot
satisfy a byte-identity requirement for those locked vendor regions. It is
only a candidate for the separate goal of a whole-device C-source build.

At the standalone sample stage, the R1 source-built application and
bootloader still required the vendor S140/MBR image. No Cordio host/controller
sources or Nordic API bridge had yet been added to the R1 application image,
and no R1 hardware behavior was claimed.
The isolated `tag.bin` SHA-256 is
`54d20eee9c86d018301a77f1a2858299e9c5c98986156ce8e7e0c167f6a7970f`.

## R1 BLE resource configuration and controller enable candidate

`r1/src/application/ble/cordio_softdevice_config.c` now owns the Nordic
entry points `sd_ble_cfg_set`, `sd_ble_enable` and `sd_ble_version_get` in the opt-in Cordio
variant. It accepts the seven configurations sent by the pinned SDK and R1
bootstrap only at the recovered values: three peripheral connections, no
central connections, event length six, MTU 247, two custom UUID bases, a
2,048-byte GATTS attribute table, Service Changed enabled, and four queued
notifications. It checks the RAM base against the linker-owned
`__data_start__` address (`0x200064a8` in the current map). Invalid settings
receive an error, and enable requires all seven settings before calling the
controller bootstrap. A failed bootstrap cannot be retried after partial
WSF/LL initialization.
Once enabled, the version query reads Cordio's live LL company, Bluetooth
version and implementation revision through `LlGetVersion`.

An ignored host probe at
`build/r1-cordio-softdevice-config-probe-20261111/` compiles this provider
against the pinned Nordic headers and passes with AddressSanitizer and
UndefinedBehaviorSanitizer. It exercises incomplete settings, a mismatched
RAM base, a rejected queue size, successful enable, controller version and
repeated enable.

`build/sources-r1-cordio-version-stable-20261111/report.json` compiles all 1,337
application C units and 86 bootloader units with no known failures or
duplicate strong symbols. The strict app link at
`build/r1-cordio-version-stable-strict-20261111/report.json` has **39** reachable
undefined Nordic calls, down from 42; it retains no archive members and
reports no region overflow. The lower BLE RAM region has 2,513 bytes of
static headroom and the upper app RAM has 6,592 bytes. The strict link still
fails. This configuration owner does not implement SoftDevice lifecycle,
WSF dispatch, Nordic BLE event translation, or BLE services, so the enable
path is not evidence of usable radio behavior on hardware.

The default stock-region build remains independent of this opt-in variant.
`build/sources-r1-post-cordio-version-stock-20261111/report.json` compiles
974/974 application and 86/86 bootloader units without failures or duplicate
strong symbols. Fresh strict application and bootloader links under
`build/r1-post-cordio-version-stock-*-link-20261111/` produce the same
694,228-byte and 23,024-byte images and hashes as the previous stock-profile
receipts.

## FreeRTOS owner for WSF dispatch

`r1/src/application/ble/r1_wsf_task.c` starts a static FreeRTOS task after
Cordio controller initialization. The task calls `WsfTimerSleepUpdate` and
`wsfOsDispatcher`, then delays one 1,024 Hz scheduler tick. It does not call
Cordio's bare-metal `WsfTimerSleep`, which would put the CPU to sleep while
FreeRTOS owns scheduling. The task uses a 2,048-byte static stack and a
112-byte static task control block. The opt-in link script maps its code into
lower BLE flash and leaves its state in upper application RAM.

`build/sources-r1-cordio-wsf-task-20261111/report.json` compiles 1,338/1,338
application C units and 86/86 bootloader units with no failures or duplicate
strong symbols. The strict link receipt is
`build/r1-cordio-wsf-task-layout-strict-20261111/report.json`: 39 Nordic
imports remain, no archive member is linked, lower BLE RAM has 2,513 bytes
of static headroom and upper RAM has 4,428 bytes. The linker map places
`r1_cordio_wsf_task_start` at `0x17286` and the stack at `0x20038968`.
FreeRTOS execution, WSF event timing, stack high-water mark and radio
behavior are not yet measured on R1 hardware.

The stock profile was rebuilt after this addition at
`build/sources-r1-post-wsf-stock-20261111/report.json`; all 974 application
and 86 bootloader units compiled without failures or duplicate strong
symbols. Its strict application and bootloader links under
`build/r1-post-wsf-stock-*-link-20261111/` still produce the exact prior
hashes `653b09e3d0a52402db2fb4cde65320418954d1a569e9bf4908688127840340c6`
and `08e108776638ad4feaf2eada3861ab37d587b44ae3b5b75daacfa386ea67ac67`.

## Cordio manager enable boundary

The opt-in source provider now owns `sd_softdevice_enable` in
`r1/src/application/ble/cordio_softdevice_config.c`. R1 calls it from the
manager thread after the FreeRTOS RTC0 tick has requested the shared LFCLK.
The provider validates the recovered RC clock source, calibration intervals,
accuracy and fault callback; it refuses startup if LFCLK is not running.
`cordio_lifecycle_hw.c` checks that the SDK event IRQ is disabled, sets its
FreeRTOS-safe priority to six, and clears pending state before the Nordic SDK
enables that IRQ. The provider then permits BLE configuration and Cordio
bootstrap. The fault callback is retained for a future fault adapter; no
Cordio fault callback route is established yet.

The host configuration probe now also checks invalid clock settings, a
stopped LFCLK, an already enabled SDK event IRQ, and repeated manager enable
with sanitizers. `build/sources-r1-cordio-manager-enable-20261111/report.json`
compiles 1,339/1,339 application C units and 86/86 bootloader units without
failures or duplicate strong symbols. The strict link receipt at
`build/r1-cordio-manager-enable-strict-20261111/report.json` has **38**
reachable Nordic imports, no archive members and no region overflow. Lower
BLE RAM has 2,505 bytes of static headroom; upper RAM has 4,428 bytes.
`sd_softdevice_disable`, SoC events and the BLE service/event adapter are
still missing. This manager enable contract is not a functional SoftDevice
replacement by itself.

The default stock profile was independently rebuilt at
`build/sources-r1-post-manager-enable-stock-20261111/report.json` with
974/974 application and 86/86 bootloader units compiled. Fresh strict links
at `build/r1-post-manager-enable-stock-*-link-20261111/` pass with no
undefined references or archive members and retain the exact application
and bootloader hashes recorded above.

## Cordio host protocol initialization

The earlier controller bootstrap registered HCI only. R1 now has a separate
`r1/src/application/ble/cordio_host_bootstrap.c` owner called between
controller initialization and starting WSF dispatch. It registers Cordio's
security, peripheral Device Manager, L2CAP, ATT client/server and SMP
handlers in the WSF scheduler, including responder Secure Connections. The
host receive limit is 251 ACL bytes, and an R1-owned ATT configuration sets
the local MTU to 247 bytes. These sizes match the controller's configured
251-byte ACL buffers and R1's recovered Nordic GATT MTU setting.

`build/sources-r1-cordio-host-init-stable-20261111/report.json` compiles
1,340/1,340 application C units and 86/86 bootloader units without known
failures or duplicate strong symbols. The strict link at
`build/r1-cordio-host-init-stable-strict-20261111/report.json` retains the
DM, L2CAP, ATT and SMP handler initializers, no archive members, and no
region overflow. It still fails on 38 reachable Nordic imports. Lower BLE
flash has 34,848 bytes of headroom; lower BLE RAM has only **549 bytes** of
static headroom, while upper application RAM has 4,252 bytes. Future event
queue state must be placed in upper RAM or the layout changed. Runtime WSF
heap consumption and stack use have not been measured on hardware.

The Nordic event adapter has not yet registered connection, security or ATT
callbacks, so host initialization alone does not make the BLE services
usable. The reset callback and readiness gate below establish only Cordio's
internal HCI reset sequence.

The default stock profile independently compiles 974/974 application and
86/86 bootloader units at
`build/sources-r1-post-host-init-stock-20261111/report.json`. Its fresh
strict application and bootloader links at
`build/r1-post-host-init-stock-*-link-20261111/` pass and retain the exact
prior hashes `653b09e3d0a52402db2fb4cde65320418954d1a569e9bf4908688127840340c6`
and `08e108776638ad4feaf2eada3861ab37d587b44ae3b5b75daacfa386ea67ac67`.

## Cordio host reset readiness

The host bootstrap now registers a DM callback for `DM_RESET_CMPL_IND` and
enqueues `DmDevReset` before starting WSF dispatch. `sd_ble_enable` waits up
to 512 FreeRTOS ticks for a successful reset callback before reporting
success. A missing callback, reset error or buffer allocation failure leaves
the provider failed rather than claiming a usable stack. The callback uses an
atomic readiness flag across the WSF and manager tasks; the wait yields each
tick so the lower-priority WSF task can run. Connection and attribute events
are not translated by this callback.

`build/sources-r1-cordio-host-reset-20261111/report.json` compiles all
1,340 application and 86 bootloader C units without known failures or
duplicate strong symbols. The strict link at
`build/r1-cordio-host-reset-strict-20261111/report.json` still fails on 38
Nordic imports. It retains no archive members, has no region overflow,
34,614 bytes of lower BLE flash headroom, 549 bytes of lower BLE RAM
headroom and 4,252 bytes of upper application RAM headroom. The host reset
sequence has not been executed on R1 hardware, so the wait's success and
timing are unverified.

## Cordio connection event boundary

The opt-in source candidate now registers the application's Cordio DM
connection callback. `r1_gap_event_bridge.c` translates successful open,
close and connection-parameter update notifications into Nordic GAP events.
The Cordio connection ID (1..3) maps to the R1 application's link index
(0..2), independently of the controller's HCI handle. An eight-event,
single-producer/single-consumer ring backs `sd_ble_evt_get`, including
length peek, buffer-size retry and 4-byte event-buffer alignment. Publishing
raises the SDK event IRQ so R1's existing BLE IO worker polls the queue.
Queue overflow or a mismatched connection ID/handle calls `WsfAssert`
instead of dropping a link transition silently.

The ring lives in upper application RAM; its code remains in reclaimed lower
flash. The final source receipt is
`build/sources-r1-cordio-gap-events-final-20261111/report.json`: 1,341/1,341
application and 86/86 bootloader C units compiled without known failures or
duplicate strong symbols. The strict link receipt
`build/r1-cordio-gap-events-final-strict-20261111/report.json` reduces the
reachable Nordic imports from 38 to **37**, with no archive members or region
overflow. Lower BLE flash has 33,686 bytes of headroom, lower BLE RAM has
549 bytes, and upper application RAM has 3,828 bytes.

This is an initial GAP event path, not a complete BLE adapter. Advertising
configuration and buffer ownership, security, PHY, ATT/GATT and SoC events
still need translation. The connected event currently assumes
advertising set zero and supplies no advertising buffer pointers. The event
path and IRQ timing have not been exercised on R1 hardware.

The default stock profile independently compiles 974/974 application and
86/86 bootloader units at
`build/sources-r1-gap-events-stock-20261111/report.json`. Fresh strict links
at `build/r1-gap-events-stock-*-link-20261111/` pass and retain the exact
application SHA256
`653b09e3d0a52402db2fb4cde65320418954d1a569e9bf4908688127840340c6`
and bootloader SHA256
`08e108776638ad4feaf2eada3861ab37d587b44ae3b5b75daacfa386ea67ac67`.

The same adapter now routes `sd_ble_gap_disconnect` through Cordio's
`DmConnClose`, translates Nordic data-length requests to `DmConnSetDataLen`,
and publishes Cordio's data-length change event back to the R1 observer.
The request validates the R1 controller's 251-octet and 2,120-microsecond
limits and returns the Nordic limitation record when exceeded. Cordio's
asynchronous DM functions do not report message-allocation failure to their
callers, so a successful return from these wrappers is not yet proof that
the request reached the controller. This needs runtime instrumentation.

`build/sources-r1-cordio-data-length-20261111/report.json` compiles all
1,341 application and 86 bootloader units with no failures or duplicate
strong symbols. The strict link at
`build/r1-cordio-data-length-strict-20261111/report.json` has **35**
reachable Nordic imports, no archive members and no memory overflow. Lower
BLE flash has 33,154 bytes of headroom, lower BLE RAM has 549 bytes, and
upper application RAM has 3,828 bytes. Data-length requests and callbacks
have not been tested on R1 hardware.

Connection-parameter update requests now use Cordio's `DmConnUpdate` after
validating the Bluetooth interval, latency and supervision-timeout bounds.
The NULL-parameter peripheral form still requires a PPCP attribute and
currently returns invalid state. Cordio's `dm_phy.c` and exactLE
`hci_cmd_phy.c` are now compiled for the opt-in profile; `DmPhyInit` runs
during host bootstrap. Nordic PHY requests are forwarded through `DmSetPhy`,
and Cordio's completion is translated back to `BLE_GAP_EVT_PHY_UPDATE`,
including the coded-PHY value conversion. These paths are source compiled
only; radio timing and event behavior still require device validation.

`build/sources-r1-cordio-phy-complete-20261111/report.json` compiles
1,343/1,343 application and 86/86 bootloader C units without failures or
duplicate strong symbols. Its strict link at
`build/r1-cordio-phy-complete-strict-20261111/report.json` has **33**
reachable Nordic imports, no archive members and no region overflow. Lower
BLE flash has 32,326 bytes of headroom; lower BLE RAM has 549 bytes and
upper application RAM has 3,828 bytes.

## Legacy advertising and Generic Access service

The opt-in candidate now owns the R1 application's single legacy advertising
set. `r1_adv_bridge.c` validates the supported Nordic legacy types,
advertising data lengths, channels, interval and duration, then sends set
configuration, start and stop operations through Cordio DM. It keeps the
application-owned advertising buffer references until connection or timeout
and returns them in the corresponding Nordic event. The SDK event IRQ carries
advertising timeout events to the existing Nordic observer. Explicit stop
does not produce a timeout event. Cordio reports high-duty directed timeout
as a failed connection completion, so the host callback maps that case to
Nordic advertising termination. The source path for connection and
advertiser TX power uses Cordio LL, with Nordic link handles mapped to
Cordio's HCI handles for connection power.

`r1_gap_service_cordio.c` installs a source-owned Generic Access ATT group
for the device name, appearance and preferred connection parameters.
`r1_gap_identity_bridge.c` connects the Nordic setters and getters used by
R1's startup and advertising encoder to that group. The name is limited to
32 bytes, which covers R1's recovered generated name; this candidate
currently supports open write permission. The name read takes its length
and value under one scheduler lock. A NULL peripheral connection-parameter
request now uses the stored PPCP value.

The advertising state and TX power sanitizer probe at
`build/r1-cordio-adv-probe-20261111/` passes configuration, start, explicit
stop, timeout, connection buffer handoff and handle/error checks. The GAP
service sanitizer probe at `build/r1-cordio-gap-service-probe-20261111/`
passes ATT group ownership, name size/readback, appearance and PPCP
readback. These probes use host stubs for Cordio scheduling and radio
operations; they are not hardware validation. Cordio's asynchronous DM
advertising APIs return `void`, so message-allocation failures still need a
source-owned error channel. Updating legacy advertising data while active is
currently rejected. Extended advertising, privacy and authentication remain
outside this boundary.

`build/sources-r1-cordio-gap-final-20261111/report.json` compiles all
1,346/1,346 application and 86/86 bootloader C units with no failures or
duplicate strong symbols. The strict link at
`build/r1-cordio-gap-final-strict-20261111/report.json` has **23** reachable
Nordic imports, no archive members, no region overflow, 29,670 bytes of
lower BLE flash headroom, 549 bytes of lower BLE RAM headroom and 3,600 bytes
of upper application RAM headroom. It does not produce an application image
yet. The remaining imports cover BLE security, GATT client/server, SoC
events, flash operations and disable.

The default stock profile independently compiles 974/974 application and
86/86 bootloader units at
`build/sources-r1-post-gap-stock-20261111/report.json`. Fresh strict links
at `build/r1-post-gap-stock-*-link-20261111/` retain the exact application
SHA256 `653b09e3d0a52402db2fb4cde65320418954d1a569e9bf4908688127840340c6`
and bootloader SHA256
`08e108776638ad4feaf2eada3861ab37d587b44ae3b5b75daacfa386ea67ac67`.

## ATT MTU and GATT client reads

The Cordio ATT callback now forwards negotiated MTU events to the Nordic
GATT observer. An R1 client request calls `AttcMtuReq`, and its completion
produces `BLE_GATTC_EVT_EXCHANGE_MTU_RSP`. For a peer-initiated exchange,
Cordio responds first with its configured 247-byte server MTU; the callback
then produces `BLE_GATTS_EVT_EXCHANGE_MTU_REQUEST` and the Nordic reply call
acknowledges the already completed exchange. The event therefore reports
the negotiated MTU rather than the peer's unbounded offered MTU. R1's
current server reply of 247 is supported; another server reply is rejected.
The callback timing and behavior need device validation.

The event queue now stores eight variable-length event copies in FreeRTOS
heap_4, each bounded by the SDK's 500-byte event buffer. The WSF task is the
sole producer. The R1 BLE IO worker and flash wait loop can both poll events,
so removal uses a short FreeRTOS task critical section. The heap APIs are not
safe for an interrupt-context caller. The queue preserves peek and
short-buffer retry, and frees each accepted event after delivery. Allocation
or queue exhaustion
is reported to the producer and asserted, since dropping an event would
desynchronize the application's link state. Runtime heap high-water and
burst behavior remain unmeasured on hardware.

The client adapter now sends ordinary and offset reads through Cordio's ATT
Read and Read Blob procedures. It sends standard 16-bit UUID reads through
ATT Read By Type, including the peer manager's Client Address Resolution
characteristic query. The response bridge publishes variable-length Nordic
`READ_RSP` and `CHAR_VAL_BY_UUID_READ_RSP` events, preserves the requested
handle and offset, and maps ATT error codes to Nordic GATT status. One read
per connection is tracked; unsupported vendor-specific UUID reads return
`NRF_ERROR_NOT_SUPPORTED`. Cordio's request functions return `void`, so
message allocation failure remains unobservable at the API boundary.

The sanitizer probe at `build/r1-cordio-att-mtu-probe-20261111/` covers MTU
request/reply, event queue peek/retry/free, a 246-byte read value, UUID
handle/value framing, error status and disconnect. The opt-in build at
`build/sources-r1-cordio-client-read-final-20261111/report.json` compiles
1,346/1,346 application and 86/86 bootloader units with no failures or
duplicate strong symbols. Its strict link at
`build/r1-cordio-client-read-final-strict-20261111/report.json` has 19 reachable
Nordic imports, no archive members or overflow, 28,194 bytes of lower BLE
flash headroom, 549 bytes of lower BLE RAM headroom and 3,428 bytes of upper
application RAM headroom. `make sources-check` reports zero unbuilt R1 units.
The source-only application does not link yet; security, GATT server,
remaining SoC events, flash scheduling and disable still need adapters.

The default stock profile was rebuilt after this change at
`build/sources-r1-after-client-read-stock-20261111/report.json`:
974/974 application and 86/86 bootloader C units compile without failures or
duplicate strong symbols. Strict application and bootloader links at
`build/r1-after-client-read-stock-*-link-20261111/` remain image-valid and
retain the SHA256 hashes recorded above.

## Generic Attribute system service

The source-built ATT database now has contiguous system handles: Generic
Access occupies 1–7, and Generic Attribute occupies 8–11. The latter
exposes Service Changed and its per-connection CCCD. Cordio's CCC utility
registers the descriptor, initializes its table on connection and releases
it on disconnection. A peer CCCD write produces a Nordic
`BLE_GATTS_EVT_WRITE` event through the existing observer queue. The
Nordic `initial_user_handle_get` and system `attr_get` calls now report the
same handle map, which lets the peer manager locate Service Changed and its
CCCD. The `value_get` adapter snapshots Cordio ATT values and the
connection-specific CCCD under the WSF database lock. These handlers are
still host-probe only; bonded restore and post-disconnect system attribute
retention remain for the dedicated system-attribute adapter.

The updated sanitizer probes at `build/r1-cordio-gap-service-probe-20261111/`
and `build/r1-cordio-att-mtu-probe-20261111/` pass the system group,
attribute UUID map, CCCD change event and value read. The opt-in source
build at `build/sources-r1-cordio-system-value-20261112/report.json` compiles
1,346/1,346 application and 86/86 bootloader units with no failures or
duplicate strong symbols. Its strict link at
`build/r1-cordio-system-value-strict-20261112/report.json` has **16**
reachable Nordic imports, no archive members or memory overflow, 26,970
bytes of lower BLE flash headroom, 525 bytes of lower BLE RAM headroom and
3,340 bytes of upper application RAM headroom. `make sources-check` still
reports zero unbuilt R1 units. No complete source-only application image
exists yet.

## Application services and authorized writes

The opt-in ATT database now allocates the R1 BAE8 and buttonless DFU
services from source. Service and characteristic UUID bytes have owned
lifetime in the database. Characteristic declarations, values and CCCDs
receive contiguous handles after the system service; BAE8's normal writes
produce Nordic write events, while DFU's authorized write request is held
with Cordio's `ATT_RSP_PENDING` mechanism until the application calls
`sd_ble_gatts_rw_authorize_reply`. The WSF task now runs above the BLE IO
worker so the ATT pending state is established before the worker handles the
authorization event. This scheduling contract needs device validation.

The host sanitizer probes at `build/r1-cordio-service-add-probe-20261112/`,
`build/r1-cordio-att-mtu-probe-20261111/` and
`build/r1-cordio-gap-service-probe-20261111/` pass service allocation,
normal writes, deferred authorization, CCC registration and Nordic event
framing. The source build at
`build/sources-r1-cordio-chars-auth-20261112/report.json` compiles
1,348/1,348 application and 86/86 bootloader units with no failures or
duplicate strong symbols. Its strict link at
`build/r1-cordio-chars-auth-strict-20261112/report.json` has 13 reachable
Nordic imports, no archive members or memory overflow, 24,190 bytes of
lower BLE flash headroom, 525 bytes of lower BLE RAM headroom and 3,240
bytes of upper application RAM headroom. These checks establish source
compilation and static fit only; no device or radio behavior has been
validated.

## GATT transmit completion

The opt-in GATTS adapter now accepts BAE8 notifications and DFU indications
through Cordio's ATT transmit calls. It checks the characteristic property,
per-connection CCCD, payload bound and negotiated ATT MTU. Cordio copies the
payload into its transmit message before the API returns. One notification
and one indication may be pending per link; the single-notification bound
allows an unambiguous mapping from Cordio's handle-only completion callback
to Nordic `HVN_TX_COMPLETE`. Indications produce `HVC`, while the system
Service Changed handle produces `SC_CONFIRM`. Failure callbacks release the
pending slot without claiming a successful transmission. Device timing,
transmit failure and reconnection still require validation.

The ARM source build at
`build/sources-r1-cordio-hvx-final-20261112/report.json` compiles
1,348/1,348 application and 86/86 bootloader units without failures or
duplicate strong symbols. The strict link at
`build/r1-cordio-hvx-strict-20261112/report.json` has **11** reachable
Nordic imports, no archive members, no region overflow, 22,702 bytes of
lower BLE flash headroom, 525 bytes of lower BLE RAM headroom and 3,224
bytes of upper application RAM headroom. `make sources-check` reports zero
unbuilt R1 units. The updated host sanitizer probe also checks the real
BAE8/DFU handle-to-CCCD and maximum-length lookups. The remaining imports
are GAP security (`authenticate`, `sec_info_reply`, `sec_params_reply`),
GATTS system attributes (`sys_attr_get`, `sys_attr_set`), BLE option and
user memory, SoC event retrieval, flash page erase/write and SoftDevice
disable. A fully linked source-only R1 application image does not yet exist.

## Persistent GATT client configuration

The Cordio candidate now exports and restores each registered CCCD as a
checked little-endian `(handle, value)` pair, filtered by the Nordic system
or user-service flags. A disconnect snapshots the values before Cordio
releases its per-link CCC table, allowing the peer manager's later
`sys_attr_get` call. A new connection invalidates that snapshot; a bonded
peer's saved values are restored with `sys_attr_set`. The source-owned
encoding round trips within this candidate. It has not been shown to match
the stock S140 encoding, so an older persisted cache may be rejected as
invalid data and cause the peer manager to reset subscriptions.

The sanitizer probe at `build/r1-cordio-gap-service-probe-20261111/` covers
both CCCD classes, a round trip, invalid handle rejection and the
post-disconnect snapshot. The ARM source build at
`build/sources-r1-cordio-sysattr-20261112/report.json` compiles
1,348/1,348 application and 86/86 bootloader units with no failures or
duplicate strong symbols. Its strict link at
`build/r1-cordio-sysattr-strict-20261112/report.json` has **9** reachable
Nordic imports, zero archive members or region overflow, 21,746 bytes of
lower BLE flash headroom, 525 bytes of lower BLE RAM headroom and 3,172
bytes of upper application RAM headroom. No source-only application image
exists yet; the remaining imports are security, BLE option, user memory,
SoC events, flash operations and disable.

## BLE option and SoC event delivery

R1's startup sets only `BLE_COMMON_OPT_CONN_EVT_EXT` to enabled. Cordio's
`lctrExceededMaxDur` already checks time before the next scheduled radio
operation for each packet, so the source adapter accepts that enabled
option. Other options and disabling that behavior remain unsupported; this
mapping still needs timing validation on R1 hardware.

A source-owned, eight-slot task-context SoC event queue now implements
`sd_evt_get`. Its publisher raises the existing SoftDevice event IRQ for
Nordic's SoC observer poller; future flash completion producers will use
the same queue and must treat overflow as a failed publish. The ignored
ASan/UBSan probe at `build/r1-cordio-soc-event-probe-20261112/` covers
empty, ordered, full and index-wrap behavior. There is no flash operation
publisher yet.

`build/sources-r1-cordio-soc-event-20261112/report.json` compiles
1,350/1,350 opt-in application and 86/86 bootloader units with no failures
or duplicate strong symbols. The strict link at
`build/r1-cordio-soc-event-strict-20261112/report.json` has **7**
reachable Nordic imports, no archive members or region overflow, 21,638
bytes of lower BLE flash headroom, 525 bytes of lower BLE RAM headroom and
3,136 bytes of upper application RAM headroom. The imports are three GAP
security calls, user memory reply, flash erase/write and SoftDevice
disable. The application remains unlinked.

## Legacy bonding bridge

The source candidate now routes Cordio's main DM security callback to a
Nordic GAP adapter. It maps the R1 peripheral security request, incoming
pairing parameters, the peer manager's reply, local and peer LTK/IRK key
events, LTK lookup, authentication status and connection security update.
The R1 application requests legacy bonding without MITM or LE Secure
Connections, and Cordio's pinned SMP configuration has matching no-input
I/O capability and 7–16 byte key bounds. The adapter retains the peer
manager's key destination pointers through the asynchronous key events.

The source candidate currently excludes **local IRK distribution** when
accepting pairing: Cordio requires a persistent local IRK pointer and none
has been provisioned in source. Peer IRKs can still be received. A secure
persistent local IRK and compatibility with previously bonded devices remain
required for a complete firmware. Cordio's `void` security-request APIs
also do not report WSF message allocation failure at the Nordic call
boundary. BLE radio pairing has not been tested on R1 hardware.

The ASan/UBSan probe at `build/r1-cordio-security-probe-20261112/` covers
security request, peer parameter event, reply, keyset writes, completion,
LTK lookup and encryption event. The ARM source build at
`build/sources-r1-cordio-security-20261112/report.json` compiles
1,351/1,351 opt-in application and 86/86 bootloader units without failures
or duplicate strong symbols. The strict link at
`build/r1-cordio-security-strict-20261112/report.json` has **4** reachable
Nordic imports, no archive members or region overflow, 19,878 bytes of
lower BLE flash headroom, 525 bytes of lower BLE RAM headroom and 2,504
bytes of upper application RAM headroom. The remaining imports are user
memory reply, flash erase/write and SoftDevice disable. The source-only
application image is still incomplete.

## User memory and remaining flash boundary

R1 configures the Nordic queued-write module with zero queued attributes.
The Cordio GATT adapter handles accepted writes in its own ATT queue and
rejects prepare writes to the reconstructed user services. The source
profile therefore does not publish `BLE_EVT_USER_MEM_REQUEST`.
`sd_ble_user_mem_reply` now checks its arguments and returns
`NRF_ERROR_INVALID_STATE` for an active link because no Nordic user-memory
request is pending; it does not report a fictitious successful reply.

`build/sources-r1-cordio-usermem-20261112/report.json` compiles
1,352/1,352 opt-in application and 86/86 bootloader units without failures
or duplicate strong symbols. The strict link at
`build/r1-cordio-usermem-strict-20261112/report.json` has **3** reachable
imports, no archive members or region overflow, 19,846 bytes of lower BLE
flash headroom, 525 bytes of lower BLE RAM headroom and 2,504 bytes of
upper application RAM headroom. `make sources-check` reports zero unbuilt
R1 units. The remaining imports are `sd_flash_page_erase`, `sd_flash_write`
and `sd_softdevice_disable`; there is still no source-only app image.

The pinned Nordic fstorage backend requires an SoC completion event for
each accepted flash operation while the BLE manager is enabled. The pinned
Cordio `pal_flash.c` controls external QSPI flash on the Nordic development
board and cannot implement R1's internal NVMC storage. An internal-flash
adapter must arbitrate with Cordio radio procedures, preserve the source
buffer until completion, protect code and bootloader pages, and publish the
real result before this boundary can be considered complete.

## Controller shutdown

The Nordic handler calls `sd_softdevice_disable` inside a critical region,
so Cordio reset cannot be awaited there. A source-owned Nordic request
observer now defers the disable request, posts `DmDevReset`, and resumes the
request after `DM_RESET_CMPL_IND`. The final disable call checks that reset
completed. On the WSF task's return from dispatch, it stops the
Cordio-owned RTC1, radio, TIMER0/TIMER1 and CCM/AAR interrupts, releases
Cordio's own HFCLK/LFCLK references, and suspends WSF dispatch. R1's RTC0
FreeRTOS tick retains its separate LFCLK reference.

The `DmDevReset` API does not report message-allocation failure, and this
sequence has not been exercised on R1 hardware. Re-enabling Cordio in the
same process is not implemented. These limits remain before firmware can
be considered fully operational.

`build/sources-r1-cordio-shutdown-hw-20261112/report.json` compiles
1,352/1,352 opt-in application and 86/86 bootloader units without failures
or duplicate strong symbols. The strict link at
`build/r1-cordio-shutdown-hw-strict-20261112/report.json` has **2**
reachable imports, zero archive members or region overflow, 19,382 bytes
of lower BLE flash headroom, 525 bytes of lower BLE RAM headroom and 2,500
bytes of upper application RAM headroom. Only internal flash erase and
write remain unresolved; the source-only application image is not linked.

## Internal flash and split source images

The R1 source profile now implements internal `sd_flash_page_erase` and
`sd_flash_write` against the nRF52840 NVMC. It accepts only the recovered
FDS and `device_flash` region (`0xD1000..0xF7FFF`) after checking the 4 KiB
FICR page size, 256-page flash size and `0xF8000` UICR bootloader address.
The application, Cordio and bootloader flash regions are protected from
these API calls. With BLE enabled, one operation is retained until an
actual SoC completion event is queued. Writes use four words per reserved
baseband slot. Erases use 1 ms partial erase steps, verify the entire page
after at least 90 steps, and fail after 160 steps if it is still not
erased. A 2.5 ms background slot is requested for each step; Cordio can
place it between radio procedures. The worker holds Cordio's generic
baseband clock through controller shutdown even when no BLE procedure is
active, and the Nordic
shutdown observer waits for fstorage to drain. With the BLE manager off,
NVMC operations use the synchronous path and emit no SoC event. This
follows the [nRF52840 NVMC partial erase contract](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/nvmc.html),
which requires cumulative erase time and notes that flash code execution
halts during an NVMC step.

The strict source link now succeeds with **zero undefined references** and
zero archive members. `tools/build/r1_application_link.py` exports and
validates `cordio.bin` at `0x1000` and `application.bin` at `0x27000`
separately, instead of treating their concatenation as a single
application-region binary. Receipt
`build/r1-cordio-flash-lifetime-strict-20261112/report.json` records
137,574 Cordio bytes (SHA-256
`e8126b06aecc0959ce5a315893f75b241168abd7dad1bbbb3334690cea01ed0c`)
and 695,804 application bytes (SHA-256
`92cb3a5e7b00cba22385fb99152f8a6ec4062c0143d75b38223028ae2f1495e2`).
The lower BLE flash has 18,074 bytes of headroom, lower RAM 525 bytes,
upper application RAM 2,420 bytes, and upper flash 512 bytes. The full
source build at `build/sources-r1-cordio-flash-lifetime-20261112/report.json`
compiles 1,353/1,353 opt-in application and 86/86 bootloader units with no
failures or duplicate strong symbols. `make sources-check` reports zero
unbuilt R1 units.

These images have **not** been executed on R1 hardware. The background
slot must be measured with real BLE connection schedules, partial erase
timing, fstorage completion and power interruption. A saturated schedule
may delay storage indefinitely. The bootloader's separate normal-function
build still requires source-backed Nordic BLE services. Local IRK persistence and
same-process BLE re-enable also remain open. The split images are not a
complete installable firmware bundle or evidence of stock byte identity.

## Bootloader handoff to the split application

The source-built BLE image begins at `0x1000`, but that address contains
Cordio code rather than a vector table. The bootloader's SDK handoff used
`MBR_SIZE` (`0x1000`) as its entry point, which is correct only when the
stock S140 image forwards boot to the application. The single replacement
at `r1/src/bootloader/runtime/app_start.c` now keeps that stock handoff in
the default profile and selects the actual application vector at `0x27000`
in the normal-function source profile. It installs that vector in VTOR
before the final C handoff, matching the application's source-owned vector
bridge. This removes a deterministic bad jump in the source profile; it
does not make that profile bootable yet.

`build/r1-boot-handoff-stock-final-20261112/report.json` compiles all
86 bootloader units with no failures or duplicate strong symbols, and
`build/r1-boot-handoff-stock-final-strict-20261112/report.json` links a
23,024-byte bootloader image with a valid vector and RAM layout. The
normal-function build at
`build/r1-boot-handoff-source-final-20261112/report.json` also compiles
86/86 units, but its strict link still reports 30 unresolved Nordic/MBR
services at
`build/r1-boot-handoff-source-final-strict-20261112/report.json`.
The bootloader has no independent source-backed BLE runtime. A controller
tied to the upper application cannot serve DFU safely while that
application is being replaced.

Disassembly of the linked source application ELF identifies 255 direct
branches from the lower BLE region (`<0x27000`) into 27 functions in the
upper application region. Of those, 190 target `memset`, `memcpy` or
`memcmp`; the rest include FreeRTOS allocation and critical-section calls,
Nordic clock and ECB helpers, `nrf_sdh_request_continue`, fstorage, and
the application task creator. This is a direct branch audit only; data
references and indirect calls were not counted. It shows that the current
Cordio lower image is not independently executable during a bootloader DFU.
The lower RAM region reaches `0x200064A8`, while the stock bootloader RAM
begins at `0x20005978`. The strict source BLE bootloader link now selects
`0x200064A8` as its RAM origin; the stock link retains `0x20005978`.
Receipts `build/r1-boot-ram-profile-cordio-20261112/report.json` and
`build/r1-boot-ram-profile-stock-20261112/report.json` verify those bounds.
The source bootloader still fails on BLE service imports; this layout
change only removes the static RAM overlap.

The source linker now places the existing C owners of `memcpy`, `memset`,
`memcmp`, `strlen`, `strcpy` and the EABI memory adapters in the lower BLE
region. Re-linking the same compiled C units at
`build/r1-mbr-integrated-app-final-20261112/report.json` passes
with zero undefined references and zero archive members: lower BLE grows
to 138,522 bytes with 17,126 bytes of flash headroom, while the upper
application shrinks to 694,844 bytes. The direct lower-to-upper branch
audit falls from 255 calls into 27 targets to 54 calls into 21 targets.
The remaining targets are Nordic clock/ECB services and application-owned
FreeRTOS, BLE event, fstorage and GATT helpers. Those calls still prevent
the installed lower BLE image from running independently during DFU.

The Nordic ECB helper and the clock manager, nrfx clock backend and
critical-region owner are now also placed in lower flash and RAM. A fresh
source application link at
`build/r1-cordio-initdata-verified-20261112/report.json` passes with zero
undefined references and zero archive members. Its lower image is 140,070
bytes, with 15,578 flash bytes and 138 RAM bytes left in the current
regions. The linker places 270 bytes of initialized Cordio tables in lower
RAM and their load image in lower flash. The application reset copies that
section after clearing lower BSS, and the strict exporter verifies its
bytes in `cordio.bin` (SHA-256 of the data section:
`251c6559f8c52250065c96038d380f5bbc1f15c47e2a2ed6853f3edc79f1d527`).
The upper application image is 693,340 bytes with 2,808 RAM bytes of
headroom.

An `--emit-relocs` diagnostic link from the same C objects found **zero**
direct references from upstream Cordio code to upper application flash or
RAM. The lower image still has 44 relocations into upper flash and 285
into upper RAM, all owned by application BLE adapters. This is stronger
than a branch-only count but does not cover calls through runtime function
pointers. The bootloader now initializes lower BSS and data from the
installed image before BLE setup. It still needs its own service adapter
that avoids executing the upper application during DFU.

The first installed lower image with this interface included a C-defined
48-byte region descriptor in its code section. The source bootloader's MBR `INIT_SD` path
scans lower flash for its magic and validates the version, image and RAM
bounds before zeroing lower RAM and copying the initialized data image.
The scanner rejects absent or ambiguous valid descriptors; application
reset initializes the same region from linker symbols. The strict export
at `build/r1-cordio-descriptor-final-20261112/report.json` verifies one
discoverable descriptor at `0x23218`, its 12 words against the linked
BSS/data ranges, and both split images. The lower image is 140,118 bytes,
with 15,530 bytes of flash headroom and 138 bytes of lower RAM headroom;
the upper application is 693,340 bytes. This validates cross-image
metadata, not bootloader execution of Cordio.

At that stage, the source bootloader's per-payload report at
`build/r1-boot-cordio-descriptor-source-rtc0-20261112/report.json`
compiles 88/88 C units with no failures or duplicate strong symbols. Its
strict link at
`build/r1-boot-cordio-descriptor-source-strict-20261112/report.json`
had **29** unresolved BLE and flash services. The default R1
profile compiles 974/974 application, 88/88 bootloader and 1/1 MBR units
at `build/sources-r1-cordio-descriptor-default-20261112/report.json`;
its application, bootloader and MBR strict links all pass. Those default
application and bootloader links still use stock S140/MBR interfaces at
runtime, so they do not complete the source-only boot path.

## Source-owned first page and staged bootloader copy

`r1/src/mbr/runtime.c` now builds as a separate C payload for
`0x0000..0x0FFF`, with its own vector and no link to S140, the application
or the bootloader. The first source bootloader `sd_mbr_command` implementation
validated a staged bootloader source and wrote a copy record into the
reserved MBR parameter page at `0xFE000`, programming its magic word last.
After reset, the first-page code validates the record, erases and copies
the bootloader pages, checks every copied word, invalidates the record,
and jumps through the bootloader vector. If power is interrupted mid-copy,
the record remains valid and the first page replays the copy from the
staging source. `INIT_SD` initializes the descriptor-checked lower BLE RAM;
`COMPARE` and IRQ vector selection have direct C implementations. Other
MBR commands, including SoftDevice copy, are still unsupported.

The current full source-profile report
`build/sources-r1-mbr-integrated-20261112/report.json` compiles
1,353/1,353 application, 87/87 bootloader and 1/1 MBR units without a
failed compilation or duplicate strong symbol. The strict application
link at `build/r1-mbr-integrated-application-strict-20261112/report.json`
still has zero undefined references and zero archive members. The new
`tools/build/r1_mbr_link.py` strict link checks the source-only 4 KiB MBR
page, vector, config words at `0xFF8`, erased gap and absence of ELF
relocations. Its receipt at
`build/r1-mbr-integrated-mbr-strict-20261112/report.json` passes and
records SHA-256
`ed09411dd7597d95340cc025529e3a7ae0e6ded9ffbf3ce7b2b000016f68148e`.
At that stage, the normal-function bootloader had **29** unresolved Nordic BLE and
flash service imports at
`build/r1-mbr-integrated-boot-strict-20261112/report.json`.

The default profile also compiles cleanly at
`build/sources-r1-mbr-default-20261112/report.json`: 974/974 application,
87/87 bootloader and 1/1 MBR units, with no failed compilation or duplicate
strong symbol. Its strict application and bootloader links pass at
`build/r1-mbr-default-application-strict-20261112/report.json` and
`build/r1-mbr-default-boot-strict-20261112/report.json`. This default
application/bootloader profile still relies on installed stock S140/MBR
services at runtime; those green links do not close the source-only path.

This MBR path has not been exercised on hardware, including an interrupted
copy, watchdog reset and BLE DFU session. The MBR record trusts that DFU
authenticated the source before staging it; the record checksum covers
metadata, not image contents. Source BLE still requires an independent
bootloader service runtime. The source bootloader RAM origin is above
Cordio's lower RAM, but this layout has not been exercised on hardware.
This is a candidate first page, not an installable whole-device image or
byte-identical MBR.

## Checked lower controller entry points

At this earlier stage the shared-region descriptor was ABI version 3 (64 bytes). Alongside
the BSS/data layout it carries four C function addresses: controller
bootstrap, WSF timer update, one WSF dispatch pass and `LlSetBdAddr`. The application
linker verifies that each address is a Thumb entry inside the lower code
before the descriptor. The source bootloader checks the same bounds before
it initializes lower RAM and stores the descriptor for its C wrappers.
`r1_cordio_flash_register()` now runs from the application's BLE enable
path after controller bootstrap; the shared controller bootstrap no longer
calls that application-specific flash service. Its remaining direct imports
all resolve inside lower flash in the linked image. The source bootloader's
`sd_ble_gap_addr_set` validates the DFU random-static address, calls the
lower `LlSetBdAddr` entry, and records it for later `sd_ble_gap_addr_get`.

The source-profile receipt
`build/r1-cordio-gap-app-20261112/report.json` passes a strict
application link with zero undefined references and archive members. Its
descriptor is unique at `0x23218`, contains lower entry addresses
`0x1f675`, `0x19cc5`, `0x199e5` and `0x13765`, and leaves 15,514 bytes lower flash
headroom and 138 bytes lower RAM headroom. The source MBR link also passes
at `build/r1-cordio-gap-mbr-20261112/report.json`. The source
bootloader still lacks 28 BLE/flash APIs and cannot complete DFU. The
descriptor does not supply a bootloader host, event bridge, flash scheduler
or bare-metal WSF ownership; its wrappers must not be treated as a
working BLE stack until those pieces are implemented and tested.

The final source-profile compile at
`build/r1-cordio-gap-source-20261112/report.json` compiles 1,354
application, 88 bootloader and one MBR unit without failures or duplicate
strong symbols. The strict source bootloader receipt
`build/r1-cordio-gap-boot-20261112/report.json` lists the remaining 28
Nordic BLE/event/flash imports. `make sources-check` passes, and the full
default-profile `make sources` receipt at
`build/r1-cordio-gap-make-sources-20261112/report.json` reports zero
compilation failures and zero duplicate strong symbols in every G2 and R1
payload, with no manifest change during the build. Default R1 application,
bootloader and MBR strict links pass at
`build/r1-cordio-gap-default-app-20261112/`,
`build/r1-cordio-gap-default-boot-20261112/` and
`build/r1-cordio-gap-default-mbr-20261112/`.

## Source DFU manager and first-page staging ABI

At the earlier source DFU manager stage the lower-region descriptor was ABI
version 7 (100 bytes). It
exports checked C entry points for the shared controller, WSF dispatch,
factory-address update, clock/radio/timer/CCM/RTC1 IRQ handlers, and the
bootloader's one-link DFU resource manager. The bootloader's six relevant
vectors use one C dispatcher that reads the active exception number and
forwards to the validated lower entry. Its `sd_softdevice_enable` and
`sd_ble_cfg_set` are C wrappers around lower-flash implementations.
The lower manager validates the recovered RC clock profile, starts the
source clock driver and records the SDK's one-link BLE configuration.
Direct imports of that manager all resolve in lower flash. A DFU host,
Nordic BLE event bridge and radio-safe flash scheduler are still missing.

The source MBR now contains a tagged C stage command at `0x800`, verified
by `tools/build/r1_mbr_link.py`. The bootloader checks the tag at `0x7fc`
before invoking it. That first-page command validates the copy source,
programs the replay record at `0xFE000` and resets; the MBR reset path
performs the copy. This frees bootloader flash while keeping the copy
service in source code independent of the bootloader region being erased.
The stage and interrupted-copy paths remain untested on hardware.

The application receipt for that stage is
`build/r1-mbr-stage-entry-app-20261112/report.json`: zero undefined
references or archive members, a unique descriptor at `0x2338c`, 15,106
bytes lower-flash headroom and 130 bytes lower-RAM headroom. The standalone
MBR link passes at `build/r1-mbr-stage-entry-mbr-20261112/report.json`,
including its tag, stage entry, erased gaps and relocation-free page.
`build/r1-mbr-stage-entry-boot-20261112/report.json` records **26**
remaining source bootloader BLE/event/flash imports and 368 bytes of
24 KiB bootloader flash headroom. The default application, bootloader
and MBR strict links also pass from
`build/r1-mbr-stage-entry-default-20261112/report.json`; that profile
still requires stock S140 services at runtime.

## Lower RAM reservation for the DFU host

The source Cordio WSF heap now reserves 14,336 bytes instead of 16,384.
The existing ARM structure calculation accounts for 5,196 bytes of WSF
buffer pools and 5,768 bytes of link-layer state. The new compile-time
bound retains at least 3,072 bytes beyond those calculated allocations,
and `r1_cordio_controller_bootstrap()` checks the actual pool and controller
allocations before accepting either. The heap is a single lower-RAM BSS
array; no executable or initialized stock data was substituted.

`build/r1-dfu-heap-budget-source-20261112/report.json` compiles all 1,355
source application units, 89 bootloader units and the source MBR without
failure or duplicate strong symbols. The strict source application link at
`build/r1-dfu-heap-budget-app-20261112/report.json` has no undefined
references or archive members, 15,106 bytes of lower-flash headroom and
2,178 bytes of lower-RAM headroom. The source MBR receipt at
`build/r1-dfu-heap-budget-mbr-20261112/report.json` still validates the
tagged stage entry. The source bootloader receipt at
`build/r1-dfu-heap-budget-boot-20261112/report.json` still lists the same
26 unresolved Nordic BLE/event/flash calls, with 368 bytes of bootloader
flash headroom. The heap estimate is not a hardware measurement; its
runtime allocation guards and BLE DFU path remain unexercised on device.

The first link after the heap change still placed the lower-flash GAP
service's attribute tables at `0x2000658c..0x20006698` and BSS near
`0x20038c20`, both owned by the upper application. The Cordio linker
script now places that service's data and BSS, plus the advertising set's
state, in lower RAM. The strict relink at
`build/r1-dfu-lower-gap-state-app-20261112/report.json` confirms all of
those sections below `0x200064a8`, with 1,776 bytes lower-RAM and 3,224
bytes upper-RAM headroom, zero undefined references and no archive members.
This makes their state available to lower-region initialization. The
application host callback still calls upper event code, and the GATT
database uses the application's allocator. The DFU service therefore still
needs independent host callbacks, event delivery and GATT allocation before
the bootloader may expose the remaining Nordic APIs.

The repository-wide `make sources` receipt at
`build/r1-dfu-heap-budget-make-sources-20261112/report.json` has zero
failed compilations and duplicate strong symbols in every G2 and R1
payload. The default-profile R1 application, bootloader and MBR strict
links pass at `build/r1-dfu-heap-budget-default-app-20261112/`,
`build/r1-dfu-heap-budget-default-boot-20261112/` and
`build/r1-dfu-heap-budget-default-mbr-20261112/`. Those default images
still rely on the stock S140 interface. The source-only bootloader still
has 26 unresolved imports; neither profile has been flashed in this work.

## Fixed lower-flash ABI and bootloader service calls

The next descriptor revision was ABI version 10, 128 bytes, pinned at `0x1000`
immediately after the source MBR page. Its recorded `code_end` and lower
data bounds are checked before the bootloader initializes RAM. All 19
service and IRQ entry words are validated in one C loop against the lower
code range. The strict application link at
`build/r1-dfu-adv-v10-app-20261112/report.json` confirms the descriptor
at `0x1000`, every target in lower code, zero undefined references, no
archive members, 14,812 bytes lower-flash and 1,776 bytes lower-RAM
headroom. The lower GAP identity and advertising state is lower-owned;
the bootloader now forwards device name set/get, preferred connection
parameters, and legacy advertising configure/start/stop to their C
implementations. This reduces its unresolved imports from 26 to 20.

The bootloader's SDK main loop is now selected from
`r1/src/bootloader/runtime/nrf_bootloader.c`. In the source profile it
advances WSF once after each application-scheduler pass, then polls the
Nordic stack observers for BLE and SoC events. It uses the
descriptor-validated lower timer and dispatcher entries. The default
profile retains its previous loop. The source boot receipt at
`build/r1-dfu-wsf-loop-boot-20261112/report.json` has 20 remaining
BLE/event/flash imports and 400 bytes of bootloader flash headroom. The
default bootloader strict link passes at
`build/r1-dfu-wsf-loop-default-boot-20261112/report.json`. The current
repository-wide source manifest check passes, with zero unbuilt R1 source
files. A DFU-specific host, BLE event
queue and radio-safe flash scheduler remain required before BLE DFU can
operate.

ABI version 11 was 132 bytes. The source SoC event queue then
uses Cordio's lower C critical-section owner, and its eight event words
and indices live in lower RAM rather than the application's BSS. The
bootloader forwards `sd_evt_get` through the checked descriptor, so a
flash completion event published by the eventual DFU flash service can
reach Nordic's polling observers without FreeRTOS. The strict application
link at `build/r1-dfu-soc-event-v11-app-20261112/report.json` validates
the descriptor at `0x1000`, zero undefined references and archive members,
14,808 bytes lower-flash and 1,736 bytes lower-RAM headroom. The source
bootloader has 19 unresolved BLE/flash APIs and 368 bytes flash headroom
at `build/r1-dfu-soc-event-v11-boot-20261112/report.json`; the source MBR
link also passes. The queue's producer has no bootloader flash service
yet, and BLE DFU remains unavailable.

The source bootloader now owns a four-slot, bounded BLE event queue in its
upper RAM. Its C `sd_ble_evt_get` checks Nordic's four-byte event-buffer
alignment, reports the required length without consuming a peek or an
undersized event, and releases each event after copying it. The lower DFU host will
call `r1_bootloader_ble_event_publish` when its event adapter is installed;
there is no event producer yet. The source bootloader compile at
`build/r1-dfu-ble-event-queue-source-20261112/report.json` has 90 of 90
units compiled without failures or duplicate strong symbols, and its
strict-link receipt lists **18** remaining BLE/flash imports with 272 bytes
flash headroom. `make sources-check` and the default-profile bootloader
strict link pass; a complete DFU session is still unimplemented.

The first-page source MBR now has a second tagged C entry at `0x900` for
Cordio descriptor validation and lower-RAM initialization. The bootloader
checks its tag at `0x8fc` before calling it, then records the validated
descriptor for later service and IRQ forwarding. The MBR checks the
descriptor's flash/RAM bounds and every Thumb service entry before it
zeros lower RAM and copies lower initialized data. The strict MBR receipt
at `build/r1-dfu-mbr-init-mbr-20261112/report.json` verifies both fixed
entries, both tags, erased gaps, the configuration words and a relocation-free
4 KiB page. The corresponding source application link passes at
`build/r1-dfu-mbr-init-app-20261112/report.json`. The bootloader receipt at
`build/r1-dfu-mbr-init-boot-20261112/report.json` still has 18 unresolved
BLE/flash imports, but its 24 KiB flash headroom increased from 272 to
560 bytes. The first-page initialization has not been exercised on device.
The default-profile application, bootloader and MBR strict links also pass
from `build/r1-dfu-mbr-init-default-source-20261112/report.json`.

The source-profile receipts at that stage were
`build/r1-dfu-current-20261112/report.json` and the strict links under
`build/r1-dfu-current-{app,boot,mbr}-20261112/`. All 1,355 application,
90 bootloader and one MBR C units compile without failures or duplicate
strong symbols. The application and MBR strict links pass; the bootloader
still has the 18 BLE/flash imports listed above, with 560 bytes of boot
flash headroom. A host-side C harness under ignored `build/` exercised
the bootloader BLE event queue's peek, short-buffer, FIFO, full-queue and
wraparound behavior. The repository-wide `make sources` receipt at
`build/r1-dfu-ble-event-queue-make-sources-20261112/report.json` has zero
failed compilations or duplicate strong symbols in every R1 and G2 payload.
`make sources-check` passes with zero unbuilt R1 source files. These checks
do not exercise the BLE producer, DFU transfer, or source boot on hardware.

## Source DFU flash scheduling in lower Cordio memory

Descriptor ABI version 12 is 148 bytes and adds four checked entries for
the source DFU flash service. Its C state and code live in lower Cordio RAM
and flash. The bootloader registers it after controller bootstrap and runs
its scheduler service after each WSF dispatch pass. `sd_flash_page_erase`
and `sd_flash_write` now forward to this service. Erases use bounded partial
NVMC steps; writes use four-word baseband slots; completion is published to
the lower SoC queue for Nordic's flash observer. The service rejects lower
controller flash, the running bootloader, and out-of-range writes. It allows
the upper application region and the two DFU metadata pages at `0xfe000`
and `0xff000`. A lower-controller update still needs a separate staged
copy design because writing its executing code is unsafe.

`build/r1-dfu-flash-source-20261112/report.json` compiles 1,356 source
application units, 90 bootloader units and the C MBR with zero failures or
duplicate strong symbols. Strict links at
`build/r1-dfu-flash-{app,boot,mbr}-20261112/` validate the 148-byte
descriptor and 4 KiB MBR. The application links with no undefined symbols
or archive members; lower flash has 13,872 bytes and lower RAM 1,656 bytes
headroom. The bootloader still fails its strict link on 16 BLE and shutdown
APIs, with 496 bytes of boot flash headroom. No flash operation or DFU
transfer has been exercised on R1 hardware.

An ignored host C harness at `build/r1-dfu-flash-test/` compiles the actual
flash range predicate and checks the lower-controller, application,
bootloader, parameter-page and settings-page boundaries. The default-profile
application, bootloader and MBR also pass strict links at
`build/r1-dfu-flash-default-{app,boot,mbr}-20261112/`.

The lower GAP service now accepts a host-selected CCC event sink. The
application host installs its existing Nordic event bridge before the GAP
attributes are initialized; the later DFU host installs a bootloader
event sink instead. The advertising DM configure/start/stop and TX-power
commands also moved from the application host unit into the lower
advertising unit, whose timeout and connection-handle callbacks are now
host-selected. This removes application host calls from the DFU advertising
configure/start/stop path. The source compile receipt at
`build/r1-dfu-adv-lower-fix-source-20261112/report.json` has zero failed
units or duplicate strong symbols. Its strict application link at
`build/r1-dfu-adv-lower-fix-app-20261112/report.json` verifies the 148-byte
descriptor, zero undefined symbols, no archive members, 13,632 bytes lower
flash headroom and 1,648 bytes lower RAM headroom. The strict MBR link
passes. The bootloader still lacks 16 BLE and shutdown APIs; there is no
DFU host or BLE event producer yet.

At that stage, the source DFU host lived under `r1/src/application/ble/cordio_dfu_host.c`
in lower flash and RAM. It installs Cordio's peripheral DM, L2CAP, ATT and
SMP handlers, then accepts a bootloader-owned BLE event publisher. Its first
event path converts connection, disconnection, ATT MTU, CCC writes and
advertising timeouts into Nordic event records. The source-only
`sd_ble_enable` checks the DFU resource request, starts the controller and
host, and waits for Cordio's reset completion. Bootloader startup dispatch
was moved into the lower C service to conserve boot flash. The host does
not yet supply DFU characteristic writes, GATT operations, security replies
or shutdown, so this is not an operating DFU transport.

Descriptor ABI version 14 was 164 bytes. Its source compile receipt
at `build/r1-dfu-host-lower-enable-fixed-source-20261112/report.json` has
1,357 application, 90 bootloader and one MBR C units compiled with zero
failures or duplicate strong symbols. Strict links at
`build/r1-dfu-host-lower-enable-fixed-{app,boot,mbr}-20261112/` verify the
application and MBR, the descriptor at `0x1000`, no application undefined
symbols or archive members, 12,504 bytes lower-flash and 1,624 bytes
lower-RAM headroom. The bootloader still has 15 unresolved BLE/GATT/security
and shutdown APIs, with 320 bytes boot-flash headroom. The source host has
not been run on R1 hardware.

At that stage, descriptor ABI version 16 was 184 bytes. The DFU host now owns
one-link connection state and translates Cordio connection-parameter,
data-length and PHY completion events. Its C GAP services handle disconnect,
connection-parameter updates, data-length updates and PHY updates; the
bootloader forwards those four Nordic calls through checked descriptor
entries. The ATT MTU callback records a pending reply, and the source
`sd_ble_gatts_exchange_mtu_reply` acknowledges the Cordio response that
was already sent. The source compile at
`build/r1-dfu-gap-mtu-source-20261112/report.json` has 1,357 application,
90 bootloader and one MBR C units compiled without failures or duplicate
strong symbols. Strict links at `build/r1-dfu-gap-mtu-{app,boot,mbr}-20261112/`
validate the application and MBR. The bootloader still has ten unresolved
security, GATT, user-memory and shutdown APIs and 208 bytes of flash
headroom; it does not link. The application has 11,780 bytes of lower-flash
and 1,624 bytes of lower-RAM headroom. Source DFU has not been run on hardware.

The first-page source MBR now has a third tagged C entry at `0xb00` for
non-initialization commands: staged bootloader copy, word comparison and
interrupt-forward address selection. The bootloader keeps `INIT_SD` locally
because it records the validated lower descriptor there, and forwards the
other commands to the tagged MBR entry. The strict MBR link at
`build/r1-dfu-mbr-command-mbr-20261112/report.json` verifies all three
entries and tags, erased gaps, both configuration words and no relocations
within its 4 KiB page. The source compile and strict application link pass
at `build/r1-dfu-mbr-command-source-20261112/report.json` and
`build/r1-dfu-mbr-command-app-20261112/report.json`. This recovered 128
bytes in the 24 KiB bootloader; its strict link still has ten unresolved
BLE/security/GATT/shutdown APIs and 336 bytes of flash headroom.

The repository-wide `make sources` receipt at
`build/r1-dfu-host-make-sources-20261112/report.json` has zero failed
compilations and duplicate strong symbols in all G2 and default-profile
R1 payloads, with both device manifests unchanged during their builds.
The default-profile R1 application, bootloader and MBR strict links
also pass at `build/r1-dfu-mbr-command-default-{app,boot,mbr}-20261112/`.

## Complete C source link for the R1 images

Descriptor ABI version 22 is 220 bytes. Its lower-flash DFU host binds the
shared ATT database to a bounded 4 KiB bootloader-owned RAM arena and a
bootloader BLE event publisher. The lower GATT adapter now takes host-selected
connection, UUID-encoding and TX-event callbacks, so the same C service
registration, authorized-write, CCC restore and HVX implementation serves the
application and DFU bootloader. The DFU host also supplies one-link security
rejection and key-miss replies, value reads, and bounded disconnect and
advertising-stop dispatch. Its shutdown path checks for idle radio activity,
disables the controller peripherals and releases the LF clock. The SDK's
unbonded Service Changed UUID value request is translated to its assigned
CCC handle 11 in this DFU path.

`build/r1-dfu-verified-source-20261112/report.json` compiles all 1,358
application, 90 bootloader and one MBR manifest units with zero failed units
or duplicate strong symbols. Every R1 source-manifest unit is a `.c` file.
The strict source application, bootloader and MBR links all pass at
`build/r1-dfu-verified-{app,boot,mbr}-20261112/`. The application has zero
undefined references and zero archive members, a validated 220-byte
descriptor at `0x1000`, 9,706 bytes of lower-flash headroom and 1,014 bytes
of lower-RAM headroom. The bootloader image is 24,512 bytes within its 24 KiB
partition, with zero undefined references and 64 bytes of flash headroom.
The source MBR passes its 4 KiB page, three tagged entry, erased-gap and
relocation-free checks. The bootloader ATT arena is at `0x20008ac0`, after
the lower RAM limit and before its heap. An ignored host harness at
`build/r1-dfu-arena-test.c` passed allocation, alignment, coalescing and
bounds checks under AddressSanitizer and UndefinedBehaviorSanitizer.

`tools/build/r1_source_firmware_regions.py` verifies those three link
receipts and the source hashes, then emits the C MBR, lower Cordio region,
application, bootloader and two UICR words in sparse Intel HEX. The receipt
at `build/r1-dfu-verified-code-hex-final-20261112/report.json` records 1,427
participating C sources and six non-overlapping regions. A readback parser
verified every HEX checksum, region hash and exact sparse byte count.
The HEX omits DFU settings, persisted FDS/FAL data and package metadata.
The root `make r1-source-firmware` target runs the source-profile compile,
three strict links and sparse export in sequence; each output path must be
fresh. Its end-to-end receipt is under
`build/r1-source-firmware-target-20261112/`.

The descriptor-rooted lower call audit at
`build/r1-dfu-lower-reloc-audit-20261112.json` traversed 356 lower functions
from 39 unique code roots. It found zero direct upper-application branches
and zero upper flash/RAM relocations in that reachable set. The entire lower
code section still has 209 upper-image relocations in application-only
adapters; indirect callback targets and runtime behavior are outside this
static audit. These receipts establish a C source build with linked R1
application, bootloader and MBR images. They do not establish stock byte
identity or a working over-the-air DFU session on hardware; no R1 device
was flashed or exercised for this change.

The repository-wide `make sources` receipt at
`build/r1-dfu-verified-make-sources-20261112/report.json` has zero failed
units and zero duplicate strong symbols in every G2 and default R1 payload.
`make sources-check` reports zero unbuilt R1 source files. The default-profile
application, bootloader and MBR strict links also pass at
`build/r1-dfu-verified-default-{app,boot,mbr}-20261112/`. The source-only
`make r1-source-firmware` run passed end to end at
`build/r1-source-firmware-target-20261112/`.
