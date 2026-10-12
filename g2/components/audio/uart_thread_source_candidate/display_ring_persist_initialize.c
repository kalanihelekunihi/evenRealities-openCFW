/* Native persistence queue initialization 0x48eac8. Native 0x47dce4 is
 * exactly MRS PRIMASK; CPSID i, and this body restores with MSR PRIMASK. */
#include <stdint.h>
extern volatile uint8_t audio_uart_ring_persist_initialized; /* RAM 0x20075032 */
extern volatile uint8_t audio_uart_ring_persist_has_tail; /* RAM 0x20075033 */
extern uint8_t audio_uart_ring_persist_queue_state[24u]; /* RAM 0x200771f4 */
extern uint32_t audio_uart_ring_persist_validate_48e900(void);
extern void audio_uart_ring_persist_reset_48e99c(void);
extern uint32_t audio_uart_ring_persist_read_clock_47dcec(void);
extern uint32_t audio_uart_ring_persist_read_version_47dd08(void);
extern void audio_uart_ring_persist_submit_48ea66(uint32_t,uint32_t,const void *);
void audio_uart_ring_persist_initialize_48eac8(void) {
    uint32_t saved;
    __asm__ volatile("mrs %0, primask\n\tcpsid i" : "=r"(saved) :: "memory");
    if(audio_uart_ring_persist_initialized!=0u) {
        __asm__ volatile("msr primask, %0" :: "r"(saved) : "memory");
        return;
    }
    if(audio_uart_ring_persist_validate_48e900()!=0u) {
        const uint32_t *q=(const uint32_t *)(const void *)audio_uart_ring_persist_queue_state;
        audio_uart_ring_persist_has_tail=(uint8_t)(q[4]!=q[2]);
    } else {
        audio_uart_ring_persist_reset_48e99c();
    }
    audio_uart_ring_persist_initialized=1u;
    __asm__ volatile("msr primask, %0" :: "r"(saved) : "memory");
    uint32_t metadata[2]={audio_uart_ring_persist_read_clock_47dcec(),
                          audio_uart_ring_persist_read_version_47dd08()};
    audio_uart_ring_persist_submit_48ea66(0xffff80u,2u,metadata);
}
