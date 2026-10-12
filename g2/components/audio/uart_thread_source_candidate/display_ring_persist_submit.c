/* Native 0x48ea66. Disassembly proves entry R3 is saved/restored only;
 * both appended fourth words are explicitly derived from the clock calls. */
#include <stdint.h>
extern volatile uint8_t audio_uart_ring_persist_early_pending; /* RAM 0x20075034 */
extern uint32_t audio_uart_ring_persist_early_check_47dcb4(uint8_t *);
extern uint32_t audio_uart_ring_persist_clock_snapshot_47dc74(void);
extern void audio_uart_ring_persist_append_48e9be(uint32_t,uint32_t,const uint32_t *,uint32_t);
void audio_uart_ring_persist_submit_48ea66(uint32_t key,uint32_t count,const void *payload) {
    uint8_t early=0u;
    uint32_t early_stamp=audio_uart_ring_persist_early_check_47dcb4(&early);
    uint32_t now=audio_uart_ring_persist_clock_snapshot_47dc74();
    if(early!=0u && audio_uart_ring_persist_early_pending==0u) {
        audio_uart_ring_persist_early_pending=1u;
        uint32_t preface[2]={now,early_stamp};
        audio_uart_ring_persist_append_48e9be(0xffff81u,2u,preface,early_stamp);
    }
    uint32_t stamp=early!=0u?early_stamp:now;
    audio_uart_ring_persist_append_48e9be(key,count,(const uint32_t *)payload,stamp);
}
