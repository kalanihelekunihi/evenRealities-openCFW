/* Native 0x5cb6c/0x5cb4c and boot wrapper0x4e1e4; recovered linker ranges.
 * Callbacks have no input contract; their return status is discarded. */
#include <stdint.h>
typedef uint32_t (*r1_init_fn)(void);
extern uint32_t r1_named_adc_register_all(void),r1_internal_flash_device_registration(void);
extern uint32_t r1_twi_primary_device_binding_configuration(void),r1_twi_secondary_device_binding_configuration(void);
extern uint32_t r1_named_gpio_register_all(void),r1_native_output_gpio_registration(void),r1_native_rtc_register(void);
extern uint32_t r1_stock_i2c2_register(void),r1_stock_i2c3_register(void),r1_stock_i2c4_register(void),r1_stock_i2c5_register(void);
extern uint32_t r1_yhm2710_stacmd_binding_configuration(void),r1_native_named_wdt_register(void);
const r1_init_fn r1_device_initcalls[13] __attribute__((section(".r1.init.devices")))={
 r1_named_adc_register_all,r1_internal_flash_device_registration,
 r1_twi_primary_device_binding_configuration,r1_twi_secondary_device_binding_configuration,
 r1_named_gpio_register_all,r1_native_output_gpio_registration,r1_native_rtc_register,
 r1_stock_i2c2_register,r1_stock_i2c3_register,r1_stock_i2c4_register,r1_stock_i2c5_register,
 r1_yhm2710_stacmd_binding_configuration,r1_native_named_wdt_register
};
extern const r1_init_fn r1_init_early_start[],r1_init_early_stop[],r1_init_board_start[],r1_init_board_stop[],r1_init_post_start[],r1_init_post_stop[];
static void walk(uintptr_t cursor,uintptr_t end) {
 for (;cursor<end;cursor+=4) {
  /* Native tests the slot address, not the function word. Do not add a
   * null-function guard: a zero callback in a nonzero slot faults. */
  if (cursor) (void)(*(r1_init_fn const volatile *)cursor)();
 }
}
void r1_module_init_table_run(void) {
 walk((uintptr_t)r1_init_early_start,(uintptr_t)r1_init_early_stop);
 walk((uintptr_t)r1_init_board_start,(uintptr_t)r1_init_board_stop);
 walk((uintptr_t)r1_device_initcalls,(uintptr_t)(r1_device_initcalls+13));
}
void r1_module_post_init_run(void) {walk((uintptr_t)r1_init_post_start,(uintptr_t)r1_init_post_stop);}
void r1_native_boot_initcall_dispatch(void) {
 __asm volatile("cpsid i" ::: "memory");
 r1_module_init_table_run();
 __asm volatile("cpsie i" ::: "memory");
 r1_module_post_init_run();
}
