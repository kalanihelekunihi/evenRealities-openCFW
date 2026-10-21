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
/* Original wrapper 0x0800a7d2, retained instruction sequence in the frame
 * dispatch closure. Kernel primitives remain explicit unresolved providers. */
extern uint32_t xEventGroupGetBitsFromISR(void *);
extern int32_t xEventGroupClearBitsFromISR(void *, uint32_t);
extern uint32_t xEventGroupClearBits(void *, uint32_t);
uint32_t case_clear_event(void *event, uint32_t flags) {
 if (!event || (flags & 0xff000000u)) return 0xfffffffcu;
 uint32_t ipsr;
 __asm volatile("mrs %0, ipsr" : "=r"(ipsr));
 if (!ipsr) return xEventGroupClearBits(event, flags);
 uint32_t prior=xEventGroupGetBitsFromISR(event);
 if (xEventGroupClearBitsFromISR(event, flags)==0) return 0xfffffffdu;
 return prior;
}
