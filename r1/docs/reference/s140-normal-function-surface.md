# R1 S140 and MBR C function surface

The pinned Nordic SDK supports `SVCALL_AS_NORMAL_FUNCTION`: its SoftDevice
declarations become ordinary external C calls. An initial ignored probe
recompiled the 40 SVC-bearing application units and ten SVC-bearing
bootloader units with that macro using their recorded compiler commands.
The application then had 61 distinct `sd_*` imports;
the bootloader has 35, of which `sd_mbr_command` is bootloader-only. Their
union is **62 C interfaces**. The application still has two `SVC 0`
instructions for FreeRTOS first-task startup and its DFU service path; the
bootloader has none. The SDK macro therefore removes the 54 Nordic
S140/MBR supervisor-call numbers in the current linked units, but does not
implement the services or eliminate every architectural SVC.

The stock-compatible `nordic_gap_address.c` alias could not compile when
the SVC body became an external declaration. It now forwards through the
normal C function in this mode and retains the original alias otherwise.
Probe receipts are under ignored `build/r1-svc-normal-c-probe/`, including
`compile-results.json`, `boot-compile-results.json`, object response files,
and `sd-interfaces.json`. The complete normal-function build is reproducible
with `python3 tools/build/sources.py build --device r1 --normal-svc --out build/<fresh-directory>`.
The optional `--cordio-rtc0` flag reserves RTC1 for Cordio and moves the R1
FreeRTOS tick to RTC0. Its current ignored receipt is
`build/sources-r1-cordio-ble50-final-profile-20261111/report.json`: all 1,422
units compile (1,336 application, 86 bootloader), and both payloads compose
with zero duplicate strong symbols. The application has **48** `sd_*`
imports, the bootloader **31**, and their union **49**. The RTC0 variant
includes the R1-owned Cordio RTC1 PAL and 362 opt-in application C units in
the same manifest composition; no IRQ handler remains unresolved. The
integrated ExactLE host profile selects Bluetooth 5.0 and disables the
sample-board UART HCI transport;
its R1-owned CHCI source compiles without that external transport. The
opt-in linker layout also places Cordio code and BSS in the reclaimed S140
regions and the R1 reset code zeros that BSS. The normal-function
application still contains two
`SVC 0` instructions; the bootloader contains none.
This is a source-level interface inventory, not
an R1 firmware image or a Cordio protocol implementation. Event formats,
SoftDevice state, BLE timing, flash/MBR behavior and hardware validation
remain required.

The first C SoC provider, `r1/src/application/ble/soc_power_c.c`, implements
`sd_power_dcdc_mode_set`, `sd_power_gpregret_set/clr` and
`sd_power_system_off` only when the
normal-function mode is selected. DC/DC mode 0 or 1 writes REG1 through the
pinned Nordic power HAL; other values return `NRF_ERROR_INVALID_PARAM`.
GPREGRET ID 0 or 1 uses the HAL's corresponding eight-bit register; set and
clear preserve the previous interrupt mask around read-modify-write. An
invalid ID returns `NRF_ERROR_INVALID_PARAM` without touching either
register. System-off calls the pinned HAL, whose MMIO write and low-power
loop do not return in the ordinary case; the provider returns the SDK's
unexpected-return error if the HAL does return. The ARM compile defines
these symbols only in normal-function mode. A host fake-register check covers
both registers, set/clear masks, interrupt-mask restoration, valid DC/DC
modes, invalid inputs and the system-off call path. Adding the object to the
normal-mode application closes four imports with no duplicate strong symbol,
leaving **57** `sd_*` imports in the application and **58** in the app/boot
union. These checks do not confirm physical regulator, retention or
system-off behavior.

The source-only `r1/src/application/ble/soc_ecb_c.c` provides
`sd_ecb_block_encrypt` in normal-function mode through the pinned
tiny-aes-c AES-128 block implementation. It clears the temporary expanded
key schedule before return. A host test passed the FIPS-197
AES-128 example and the zero-key/zero-block vector. The ARM normal-mode
object composes with the application and removes that import. **56** `sd_*`
imports remain in the application and **57** in the app/boot union. The
stock-compatible build excludes this provider. Software encryption timing
and concurrent radio behavior remain unverified.

`r1/src/application/ble/uuid_registry_c.c` implements
`sd_ble_uuid_vs_add` and `sd_ble_uuid_encode` for both R1 payloads in
normal-function mode. It uses the application SDK's two vendor UUID slots
and the bootloader SDK's one slot, ignores bytes 12 and 13 when matching a
base, returns an existing type for duplicate bases, and substitutes the
16-bit value during little-endian encoding. Host checks cover both
capacities, duplicate and overflow cases, encoding, invalid inputs, and
interrupt-mask restoration; both capacities also pass ASan/UBSan runs.
The provider has no GATT or Cordio binding yet. It closes two application
imports and one bootloader import; the remaining union is **55** `sd_*`
interfaces.

`r1/src/application/ble/soc_vector_base_c.c` replaces
`sd_softdevice_vector_table_base_set` in both normal-function payloads. It
updates Cortex-M4 VTOR with interrupts masked and architecture barriers,
then restores the caller's interrupt mask. With no S140/MBR vector relay,
the hardware vector register must select the active application or DFU table.
The application and bootloader both compile the provider; each loses one
unresolved import, bringing their unresolved `sd_*` union to **54**. The
default images remain byte-for-byte unchanged. This direct vector ownership
still needs validation as part of a complete source-built boot path.

`r1/src/application/ble/gap_factory_address_c.c` provides the initial
`sd_ble_gap_addr_get` identity in both normal-function payloads. It reads the
nRF52840's factory `FICR.DEVICEADDR` in BLE little-endian order and sets the
random-static high bits. The R1 port of Cordio's `pal_cfg.c` uses the same
helper to initialize its controller address; the pinned sample had instead
used the separate `FICR.DEVICEID`. A host fake-FICR check covers byte order,
address type and null-pointer status, and the ARM source compositions lose
one import per payload. The current unresolved `sd_*` union is **53**. The
address has not been read from R1 hardware, and controller bootstrap remains
unimplemented.

The Cordio variant now compiles the pinned `nrf_drv_clock.c` with
`SOFTDEVICE_PRESENT` undefined for that one SDK unit. Its direct nrfx path
keeps `POWER_CLOCK_IRQn` active and requests HFCLK through the hardware clock
driver. The SoftDevice observer path instead disables that IRQ during enable
and routes HFCLK through `sd_clock_hfclk_request`, `release`, and
`is_running`. The conditional compile removes all three application imports;
the stock profile still compiles the unmodified SDK behavior. This does not
establish the Cordio startup order, IRQ timing, or radio arbitration on R1.

`r1/src/application/ble/soc_app_evt_wait_c.c` is the single shared C
provider of `sd_app_evt_wait` for both normal-function payloads. It executes
CMSIS `__WFE()` and returns `NRF_SUCCESS`, following the pinned Nordic
`nrf_soc_nosd/nrf_soc.c` behavior. This closes one import in each payload;
the default SVC builds omit the definition. The ARM compositions pass, but
sleep and wake behavior has not been validated on R1 hardware.

The current Cordio variant uses an R1-sized WSF heap and a three-peripheral-link
resource profile. A compile-time assertion in the R1 SDK bootstrap unit
checks the recovered three-link, zero-central, 247-byte-MTU settings; the
Cordio compilation profile itself still uses the pinned sample SDK header.
The [Cordio memory evidence](cordio-nrf52840-source-candidate.md) separates
the 5,196-byte WSF buffer-pool requirement from unmeasured controller state.

The opt-in `cordio-rtc0` variant now provides `sd_ble_cfg_set`,
`sd_ble_enable` and `sd_ble_version_get` from C in
`r1/src/application/ble/cordio_softdevice_config.c`.
The provider validates the seven recovered resource settings and linker RAM
base, then calls the Cordio controller bootstrap. Its strict link retains 38
reachable Nordic imports; the remaining S140 services, events and lifecycle
still need real providers. See the Cordio candidate reference for receipts.
The variant also creates a static FreeRTOS task to service WSF timers and
events after bootstrap. Its dispatch timing and stack margin remain untested
on hardware.
It also provides the manager's `sd_softdevice_enable` stage, validating the
recovered RC LFCLK contract and preparing the SDK event IRQ. Disable and the
fault callback route remain open.
The Cordio host now registers DM, L2CAP, ATT client/server and SMP handlers
with a 247-byte ATT MTU. It starts the HCI reset sequence and waits for DM
reset completion before `sd_ble_enable` reports success. Connection, security
and ATT callbacks still await the Nordic event adapter; the lower BLE RAM
layout has 549 bytes of static headroom after retaining these handlers.

All 1,296 manifest units are `.c` files. That does not make the image free
of handwritten assembly: six linked `r1/src` files use ARM inline assembly
for delay timing, exception entry, integer flags, division-by-zero behavior
or a fixed Goodix ABI frame. The pinned FreeRTOS Cortex-M port also contains
active inline assembly for task startup and context switching. A newlib
ctype source contains assembly only inside a host-only conditional branch.
These are separate source-replacement boundaries for a strict C-only goal;
the normal-function compile verifies that the current C compiler accepts
them, not that the firmware is pure C.

## Original C interface surface before the providers above

- `sd_app_evt_wait`
- `sd_ble_cfg_set`
- `sd_ble_enable`
- `sd_ble_evt_get`
- `sd_ble_gap_addr_get`
- `sd_ble_gap_addr_set`
- `sd_ble_gap_adv_addr_get`
- `sd_ble_gap_adv_set_configure`
- `sd_ble_gap_adv_start`
- `sd_ble_gap_adv_stop`
- `sd_ble_gap_appearance_get`
- `sd_ble_gap_appearance_set`
- `sd_ble_gap_authenticate`
- `sd_ble_gap_conn_param_update`
- `sd_ble_gap_data_length_update`
- `sd_ble_gap_device_identities_set`
- `sd_ble_gap_device_name_get`
- `sd_ble_gap_device_name_set`
- `sd_ble_gap_disconnect`
- `sd_ble_gap_phy_update`
- `sd_ble_gap_ppcp_set`
- `sd_ble_gap_privacy_get`
- `sd_ble_gap_privacy_set`
- `sd_ble_gap_sec_info_reply`
- `sd_ble_gap_sec_params_reply`
- `sd_ble_gap_tx_power_set`
- `sd_ble_gap_whitelist_set`
- `sd_ble_gattc_char_value_by_uuid_read`
- `sd_ble_gattc_exchange_mtu_request`
- `sd_ble_gattc_read`
- `sd_ble_gatts_attr_get`
- `sd_ble_gatts_characteristic_add`
- `sd_ble_gatts_descriptor_add`
- `sd_ble_gatts_exchange_mtu_reply`
- `sd_ble_gatts_hvx`
- `sd_ble_gatts_initial_user_handle_get`
- `sd_ble_gatts_rw_authorize_reply`
- `sd_ble_gatts_service_add`
- `sd_ble_gatts_service_changed`
- `sd_ble_gatts_sys_attr_get`
- `sd_ble_gatts_sys_attr_set`
- `sd_ble_gatts_value_get`
- `sd_ble_opt_set`
- `sd_ble_user_mem_reply`
- `sd_ble_uuid_encode`
- `sd_ble_uuid_vs_add`
- `sd_ble_version_get`
- `sd_clock_hfclk_is_running`
- `sd_clock_hfclk_release`
- `sd_clock_hfclk_request`
- `sd_ecb_block_encrypt`
- `sd_evt_get`
- `sd_flash_page_erase`
- `sd_flash_write`
- `sd_mbr_command`
- `sd_power_dcdc_mode_set`
- `sd_power_gpregret_clr`
- `sd_power_gpregret_set`
- `sd_power_system_off`
- `sd_softdevice_disable`
- `sd_softdevice_enable`
- `sd_softdevice_vector_table_base_set`
