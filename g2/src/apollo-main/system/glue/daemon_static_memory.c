#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_stock_ram_2003fa98[] __asm__("g2_stock_ram_2003fa98");
extern unsigned char g2ref_g2_stock_ram_20071ea0[] __asm__("g2_stock_ram_20071ea0");

/* Stock 0x4d3610 writes the timer-daemon TCB, stack and depth to three
 * caller-provided output cells. The original body has no null checks. */
void audio_daemon_get_static_memory(void **tcb, void **stack, uint32_t *depth) {
    *tcb = (void *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20071ea0);
    *stack = (void *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_stock_ram_2003fa98);
    *depth = 4096u;
}
