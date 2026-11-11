#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_audio_uart_thread_manager_state[] __asm__("audio_uart_thread_manager_state");

/* Original 0x4c9c3c: post bit (1 << index) to the retained manager
 * event group through osEventFlagsSet. The stop-handshake receipt shows
 * this is an audio acknowledgment before timer and queue cleanup. */
extern uint32_t osEventFlagsSet(void *group, uint32_t bits);

void audio_ack_index(uint32_t index) {
    uint32_t amount = (uint8_t)index;
    uint32_t bits = amount < 32u ? (1u << amount) : 0u;
    void *group = *(void *volatile *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_audio_uart_thread_manager_state+0x1cu);
    (void)osEventFlagsSet(group, bits);
}

void audio_exit_request(uint32_t index) __attribute__((alias("audio_ack_index")));
