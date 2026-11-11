SEARCH_DIR(.)
GROUP(-lgcc -lc -lnosys)

MEMORY
{
  /* Keep the recovered three-page FDS range below the 36-page device_flash. */
  FLASH (rx)  : ORIGIN = 0x00027000, LENGTH = 0x000aa000
  RAM   (rwx) : ORIGIN = 0x200064a8, LENGTH = 0x00039b58
}

SECTIONS
{
  .fs_data :
  {
    PROVIDE(__start_fs_data = .);
    KEEP(*(.fs_data))
    PROVIDE(__stop_fs_data = .);
  } > RAM
} INSERT AFTER .data;

SECTIONS
{
  .openr1_noinit (NOLOAD) : ALIGN(4)
  {
    KEEP(*(.openr1_noinit*))
  } > RAM
} INSERT AFTER .bss;

SECTIONS
{
  /* Explicitly retained modules supply firmware-bundle entry points and
   * resident data. The SDK uses -ffunction-sections and --gc-sections, so
   * source compilation alone does not retain an unbound API. The two large
   * algorithm libraries below instead retain their reachable sections and
   * source-owned API records, avoiding uncalled code in flash. */
  .openr1_reconstructed_code :
  {
    /* nrf_common.ld normally places this first inside .text.  Because this
     * retained section must precede its catch-all .text rule, consume the
     * vector table here first so the application still begins with MSP/reset. */
    KEEP(*(.isr_vector))
    KEEP(*rtc_device.c.o(.text .text.* .rodata .rodata.*))
    KEEP(*generic_device_registry.c.o(.text .text.* .rodata .rodata.*))
    KEEP(*software_twi.c.o(.text .text.* .rodata .rodata.*))
    KEEP(*sensor_stream.c.o(.text .text.* .rodata .rodata.*))
    KEEP(*time_calendar.c.o(.text .text.* .rodata .rodata.*))
    KEEP(*r1_model_data.c.o(.text .text.* .rodata .rodata.*))
    KEEP(*quantized_runtime.c.o(.text .text.* .rodata .rodata.*))
    KEEP(*gxt310.c.o(.text .text.* .rodata .rodata.*))
    KEEP(*qma6100.c.o(.text .text.* .rodata .rodata.*))
    KEEP(*yhm2710.c.o(.text .text.* .rodata .rodata.*))
    /* These large C libraries are compiled as complete source units. Their
     * called functions and referenced data remain live through relocations;
     * retaining every uncalled helper exhausts application flash. */
    *goodix_primitives.c.o(.text .text.* .rodata .rodata.*)
    KEEP(*goodix_heap.c.o(.text .text.* .rodata .rodata.*))
    *gomore_primitives.c.o(.text .text.* .rodata .rodata.*)
    KEEP(*gomore_tensor_runtime.c.o(.text .text.* .rodata .rodata.*))
    KEEP(*goodix_hba_config.c.o(.text .text.* .rodata .rodata.*))
    KEEP(*goodix_hrv_config.c.o(.text .text.* .rodata .rodata.*))
    KEEP(*goodix_spo2_config_for_gh3x2x-v2.23_7ecd2a.c.o(.text .text.* .rodata .rodata.*))
    KEEP(*r1_gh3x2x_provider_composer.c.o(.text .text.* .rodata .rodata.*))
    KEEP(*r1_gh3x2x_reconstructed_roots.c.o(.text .text.* .rodata .rodata.*))
    KEEP(*(.openr1_goodix_api))
  } > FLASH
} INSERT BEFORE .text;

SECTIONS
{
  .sdh_req_observers :
  {
    PROVIDE(__start_sdh_req_observers = .);
    KEEP(*(SORT(.sdh_req_observers*)))
    PROVIDE(__stop_sdh_req_observers = .);
  } > FLASH
  .sdh_state_observers :
  {
    PROVIDE(__start_sdh_state_observers = .);
    KEEP(*(SORT(.sdh_state_observers*)))
    PROVIDE(__stop_sdh_state_observers = .);
  } > FLASH
  .sdh_stack_observers :
  {
    PROVIDE(__start_sdh_stack_observers = .);
    KEEP(*(SORT(.sdh_stack_observers*)))
    PROVIDE(__stop_sdh_stack_observers = .);
  } > FLASH
  .sdh_ble_observers :
  {
    PROVIDE(__start_sdh_ble_observers = .);
    KEEP(*(SORT(.sdh_ble_observers*)))
    PROVIDE(__stop_sdh_ble_observers = .);
  } > FLASH
  .sdh_soc_observers :
  {
    PROVIDE(__start_sdh_soc_observers = .);
    KEEP(*(SORT(.sdh_soc_observers*)))
    PROVIDE(__stop_sdh_soc_observers = .);
  } > FLASH
  .openr1_motion_api :
  {
    KEEP(*(.openr1_motion_api))
  } > FLASH
  .openr1_storage_api :
  {
    KEEP(*(.openr1_storage_api))
    KEEP(*(.openr1_analog_api))
    KEEP(*(.openr1_health_api))
    KEEP(*(.openr1_event_api))
    KEEP(*(.openr1_protocol_api))
    KEEP(*(.openr1_frontier_api))
    KEEP(*(.openr1_touch_audit_api))
    KEEP(*(.openr1_health_db_api))
    KEEP(*(.openr1_twi_sync_api))
    KEEP(*(.openr1_retained_log_api))
    KEEP(*(.openr1_reset_trace_api))
    KEEP(*(.openr1_reset_reason_api))
    KEEP(*(.openr1_clock_api))
    KEEP(*(.openr1_rtc_api))
  } > FLASH
} INSERT AFTER .text;

INCLUDE "nrf_common.ld"

/* The source application's MSP is the linker RAM top. Keep enough room for
 * reset and interrupt nesting even as reconstructed static data grows. */
ASSERT(SIZEOF(.stack_dummy) >= 0x2000,
       "application MSP stack reservation is below 8 KiB")

/* The source reset copies every initialized RAM section through the dynamic
 * log registry. These assertions reject a registry with a disconnected load
 * image before the firmware can be considered bootable. */
__r1_data_init_end__ = ADDR(.log_dynamic_data) + SIZEOF(.log_dynamic_data);
ASSERT(LOADADDR(.log_dynamic_data) == __etext +
       (ADDR(.log_dynamic_data) - __data_start__),
       "log dynamic data is outside the reset copy image")
ASSERT(LOADADDR(.fs_data) == __etext + (ADDR(.fs_data) - __data_start__),
       "FDS data is outside the reset copy image")
ASSERT(__r1_data_init_end__ <= __bss_start__,
       "initialized data overlaps bss")

/* GNU names expected by the authenticated CmBacktrace provider. */
PROVIDE(_sstack = __StackLimit);
PROVIDE(_estack = __StackTop);
PROVIDE(_stext = ORIGIN(FLASH));
PROVIDE(_etext = __etext);
/* The selected R1 CmBacktrace configuration names these same GNU bounds.
 * Its provider takes their addresses, not values stored at those addresses. */
PROVIDE(r1_cmb_stack_start = _sstack);
PROVIDE(r1_cmb_stack_end = _estack);
PROVIDE(r1_cmb_code_start = _stext);
PROVIDE(r1_cmb_code_end = _etext);
/* app_util.h declares the vector anchor as one uint32_t. The C source owns
 * the full table under a distinct typed name; bind that SDK anchor here. */
__isr_vector = r1_application_vectors;
