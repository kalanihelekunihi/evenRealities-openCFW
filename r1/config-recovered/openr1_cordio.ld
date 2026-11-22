/* Source-built R1 controller layout. The first flash page belongs to the
 * separate C MBR payload; no stock S140 image may be installed with this layout.
 * Include the unchanged upper application layout and place Cordio sections
 * into the reclaimed lower flash and RAM regions. */
MEMORY
{
  BLE_FLASH (rx)  : ORIGIN = 0x00001000, LENGTH = 0x00026000
  BLE_RAM   (rwx) : ORIGIN = 0x20000000, LENGTH = 0x000064a8
}

/* The WSF heap is initialized by r1_cordio_wsf_heap_init(). */
SECTIONS
{
  .r1_cordio_heap (NOLOAD) : ALIGN(8)
  {
    KEEP(*(.bss.r1_cordio_heap))
  } > BLE_RAM
} INSERT BEFORE .bss;

/* Match encoded source basenames. A broad path wildcard can accidentally
 * match the name of a build output directory and capture the whole app. */
SECTIONS
{
  .r1_cordio_code : ALIGN(4)
  {
    /* The bootloader reads the ABI at the first word of lower flash. */
    KEEP(*r1__src__application__ble__cordio_region_descriptor.c.o(.r1_cordio_descriptor))
    /* Cordio must retain its ordinary C memory primitives when the upper
     * application is absent during DFU. Keep their single source owners. */
    *third-party__upstream__musl-memory-1.2.5__memcpy.c.o(.text .text.* .rodata .rodata.*)
    *third-party__upstream__musl-memory-1.2.5__memset.c.o(.text .text.* .rodata .rodata.*)
    *third-party__upstream__musl-memory-1.2.5__strlen.c.o(.text .text.* .rodata .rodata.*)
    *r1__src__application__runtime__native_memory_compare.c.o(.text .text.* .rodata .rodata.*)
    *r1__src__application__runtime__memory_eabi.c.o(.text .text.* .rodata .rodata.*)
    *r1__src__application__runtime__native_libc_sequences.c.o(.text.strcpy .rodata.strcpy)
    /* PAL AES uses this C nRF ECB owner; its state must live with Cordio. */
    *__modules__nrfx__hal__nrf_ecb.c.o(.text .text.* .rodata .rodata.*)
    /* Cordio's clock PAL uses the C Nordic clock manager and nrfx backend. */
    *__components__libraries__util__app_util_platform.c.o(.text .text.* .rodata .rodata.*)
    *__integration__nrfx__legacy__nrf_drv_clock.c.o(.text .text.* .rodata .rodata.*)
    *__modules__nrfx__drivers__src__nrfx_clock.c.o(.text .text.* .rodata .rodata.*)
    *__upstream__cordio__*.o(.text .text.* .rodata .rodata.*)
    *r1__src__application__ble__cordio_*.o(.text .text.* .rodata .rodata.*)
    *r1__src__application__ble__r1_gap_event_bridge.c.o(.text .text.* .rodata .rodata.*)
    *r1__src__application__ble__r1_adv_bridge.c.o(.text .text.* .rodata .rodata.*)
    *r1__src__application__ble__r1_gap_service_cordio.c.o(.text .text.* .rodata .rodata.*)
    *r1__src__application__ble__r1_gap_identity_bridge.c.o(.text .text.* .rodata .rodata.*)
    *r1__src__application__ble__r1_gatts_*.o(.text .text.* .rodata .rodata.*)
    *r1__src__application__ble__r1_ble_option_cordio.c.o(.text .text.* .rodata .rodata.*)
    *r1__src__application__ble__r1_soc_event_cordio.c.o(.text .text.* .rodata .rodata.*)
    *r1__src__application__ble__r1_security_cordio.c.o(.text .text.* .rodata .rodata.*)
    *r1__src__application__ble__r1_user_mem_cordio.c.o(.text .text.* .rodata .rodata.*)
    *r1__src__application__ble__r1_flash_cordio.c.o(.text .text.* .rodata .rodata.*)
    *r1__src__application__ble__r1_wsf_task.c.o(.text .text.* .rodata .rodata.*)
    __r1_cordio_code_end = .;
  } > BLE_FLASH
} INSERT BEFORE .text;

/* Reset_Handler zeros NOBITS and copies the lower data load image before
 * controller initialization. The source bootloader needs the same sequence. */
SECTIONS
{
  .r1_cordio_bss (NOLOAD) : ALIGN(8)
  {
    __r1_cordio_bss_start = .;
    *__upstream__cordio__*.o(.bss .bss.* COMMON)
    *__modules__nrfx__hal__nrf_ecb.c.o(.bss .bss.* COMMON)
    *__components__libraries__util__app_util_platform.c.o(.bss .bss.* COMMON)
    *__integration__nrfx__legacy__nrf_drv_clock.c.o(.bss .bss.* COMMON)
    *__modules__nrfx__drivers__src__nrfx_clock.c.o(.bss .bss.* COMMON)
    /* The r1_gap_event_bridge ring uses the upper application's .bss. */
    *r1__src__application__ble__cordio_*.o(.bss .bss.* COMMON)
    /* GAP attributes and advertising-set state are shared with DFU. Keep
     * them below the upper application's RAM origin so the source bootloader
     * can initialize them through the lower-region descriptor. */
    *r1__src__application__ble__r1_gap_service_cordio.c.o(.bss .bss.* COMMON)
    *r1__src__application__ble__r1_adv_bridge.c.o(.bss .bss.* COMMON)
    *r1__src__application__ble__r1_soc_event_cordio.c.o(.bss .bss.* COMMON)
    *r1__src__application__ble__r1_gatts_database_cordio.c.o(.bss .bss.* COMMON)
    *r1__src__application__ble__r1_gatts_api_bridge.c.o(.bss .bss.* COMMON)
    __r1_cordio_bss_end = .;
  } > BLE_RAM
  .r1_cordio_data : ALIGN(4)
  {
    __r1_cordio_data_start = .;
    *__upstream__cordio__*.o(.data .data.*)
    *r1__src__application__ble__r1_gap_service_cordio.c.o(.data .data.*)
    *r1__src__application__ble__r1_adv_bridge.c.o(.data .data.*)
    *r1__src__application__ble__r1_gatts_database_cordio.c.o(.data .data.*)
    *r1__src__application__ble__r1_gatts_api_bridge.c.o(.data .data.*)
    __r1_cordio_data_end = .;
  } > BLE_RAM AT > BLE_FLASH
  __r1_cordio_data_load = LOADADDR(.r1_cordio_data);
} INSERT BEFORE .bss;

INCLUDE "r1/config-recovered/openr1_sdk.ld"
