/* Native locale dispatch wrappers 0x4d58ae/0x4d58c2 and range error
 * writer 0x439cb2.  The literal at 0x4d43ac points to the live locale
 * vtable at RAM 0x200044c0; its callback initialization is not inferred. */
#include <stdint.h>
extern uint8_t audio_uart_ring_locale_dispatch_200044c0[];
extern volatile uint32_t audio_uart_ring_errno_20074f14;
typedef int32_t (*locale_character_fn)(uint32_t);
static locale_character_fn locale_method(unsigned offset) {
    uintptr_t target=*(volatile const uintptr_t *)(const void *)(audio_uart_ring_locale_dispatch_200044c0+offset);
    return (locale_character_fn)target;
}
int32_t audio_uart_ring_locale_space_4d58ae(uint32_t value) {
    return locale_method(0x20u)(value);
}
int32_t audio_uart_ring_locale_lower_4d58c2(uint32_t value) {
    return locale_method(0x28u)(value);
}
void audio_uart_ring_errno_range_set_439cb2(void) {
    audio_uart_ring_errno_20074f14=0x22u;
}
