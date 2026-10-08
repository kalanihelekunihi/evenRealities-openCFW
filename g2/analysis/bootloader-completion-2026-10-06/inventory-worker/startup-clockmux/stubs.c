/* Link-only child symbols; Unicorn intercepts these entry points as explicit cuts. */
#include <stdint.h>
#include <stddef.h>
void opencfw_hal_delay_us(uint32_t x) {(void)x;}
uint32_t opencfw_hal_status_poll(uint32_t a, uintptr_t b, uint32_t c, uint32_t d, uint32_t e) {(void)a;(void)b;(void)c;(void)d;(void)e;return 0;}
uint64_t opencfw_legacy_gpio_mode(uint32_t a, uint8_t *b) {(void)a;(void)b;return 0;}
uint32_t opencfw_power_register_read(uint32_t a, uint32_t *b) {(void)a;(void)b;return 0;}
uint32_t opencfw_bl_power_register_update(uint32_t a, uint32_t b) {(void)a;(void)b;return 0;}
uint32_t opencfw_bl_mspi_mode_enter(uint32_t a) {(void)a;return 0;}
uint32_t opencfw_bl_mspi_mode_leave(uint32_t a) {(void)a;return 0;}
uint64_t opencfw_low_power_prepare(void) {return 0;}
uint64_t opencfw_low_power_finish(void) {return 0;}
uint32_t opencfw_cache_invalidate(const volatile void *a, uint32_t b) {(void)a;(void)b;return 0;}
