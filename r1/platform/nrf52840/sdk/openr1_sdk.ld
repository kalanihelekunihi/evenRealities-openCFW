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
  /* Every recovered module is a deliberate firmware-bundle payload.  The SDK
   * build uses -ffunction-sections plus --gc-sections, so merely compiling an
   * implementation is not enough: consume its text/constant sections here
   * before nrf_common.ld's generic .text rule can discard an unbound API. */
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
    KEEP(*goodix_primitives.c.o(.text .text.* .rodata .rodata.*))
    KEEP(*goodix_heap.c.o(.text .text.* .rodata .rodata.*))
    KEEP(*gomore_primitives.c.o(.text .text.* .rodata .rodata.*))
    KEEP(*gomore_tensor_runtime.c.o(.text .text.* .rodata .rodata.*))
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
  } > FLASH
} INSERT AFTER .text;

INCLUDE "nrf_common.ld"

/* GNU names expected by the authenticated CmBacktrace provider. */
PROVIDE(_sstack = __StackLimit);
PROVIDE(_estack = __StackTop);
PROVIDE(_stext = ORIGIN(FLASH));
PROVIDE(_etext = __etext);
