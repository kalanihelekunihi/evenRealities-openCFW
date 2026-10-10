/* Exact CASE wrapper address 0x0800a888 is shared by frame callback and
 * binary forwarding. The independent implementation is case_event_flags_set.
 * Source callers use the recovered 32-bit ARM ABI with an address in r0. */
#include <stdint.h>
extern uint32_t case_event_flags_set(void *, uint32_t);
uint32_t case_event_post(uint32_t event, uint32_t flags) {
 return case_event_flags_set((void *)(uintptr_t)event, flags);
}
uint32_t case_forward_event(void *event, uint32_t flags) {
 return case_event_flags_set(event, flags);
}
/* Original CASE target 0x08005f42 is exactly `bx lr` (weak error callback). */
void HAL_UART_ErrorCallback(void *uart) { (void)uart; }
