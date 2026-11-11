/* Logger-disabled first-party stop coordination, no timer in selected exit contract. */
#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_audio_ble_rx_thread_state[] __asm__("audio_ble_rx_thread_state"); /* Fix 45: stock owner (owner.py) */
extern unsigned char g2ref_audio_ble_tx_thread_state[] __asm__("audio_ble_tx_thread_state"); /* Fix 45: stock owner (owner.py) */
extern unsigned char g2ref_audio_ble_wsf_thread_state[] __asm__("audio_ble_wsf_thread_state"); /* Fix 45: stock owner (owner.py) */
extern unsigned char g2ref_audio_display_driver_manager[] __asm__("audio_display_driver_manager"); /* Fix 45: stock owner (owner.py) */
extern unsigned char g2ref_audio_uart_ring_thread_manager[] __asm__("audio_uart_ring_thread_manager"); /* Fix 45: stock owner (owner.py) */
extern unsigned char g2ref_g2_ble_production_context[] __asm__("g2_ble_production_context"); /* Fix 45: stock owner (owner.py) */
extern unsigned char g2ref_g2_hub_thread_desc[] __asm__("g2_hub_thread_desc"); /* Fix 45: stock owner (owner.py) */
extern unsigned char g2ref_g2_input_thread_desc[] __asm__("g2_input_thread_desc"); /* Fix 45: stock owner (owner.py) */
extern unsigned char g2ref_g2_notif_thread_context[] __asm__("g2_notif_thread_context"); /* Fix 45: stock owner (owner.py) */
extern unsigned char g2ref_audio_uart_thread_manager_state[] __asm__("audio_uart_thread_manager_state");
extern unsigned char g2ref_g2_audio_dispatch_state[] __asm__("g2_audio_dispatch_state");
extern uint32_t audio_flags_set(void*,uint32_t);
extern void audio_ack_index(uint32_t),audio_queue_delete_peer(void*),audio_delay(uint32_t);
extern uint32_t audio_event_wait(void*,uint32_t,uint32_t,uint32_t);
/* Stock 0x004C96B6 (thread_manager_stop_fanout) */
uint32_t audio_stop_fanout(uint32_t reason){
 const uint32_t ctx[10]={((uint32_t)(uintptr_t)g2ref_g2_notif_thread_context+0x0u),((uint32_t)(uintptr_t)g2ref_audio_uart_ring_thread_manager+0x0u),((uint32_t)(uintptr_t)g2ref_g2_ble_production_context+0x0u),((uint32_t)(uintptr_t)g2ref_audio_ble_rx_thread_state+0x0u),((uint32_t)(uintptr_t)g2ref_audio_ble_tx_thread_state+0x0u),((uint32_t)(uintptr_t)g2ref_audio_ble_wsf_thread_state+0x0u),((uint32_t)(uintptr_t)g2ref_g2_audio_dispatch_state+0x0u),((uint32_t)(uintptr_t)g2ref_g2_input_thread_desc+0x0u),((uint32_t)(uintptr_t)g2ref_g2_hub_thread_desc+0x0u),((uint32_t)(uintptr_t)g2ref_audio_display_driver_manager+0x0u)};
 const uint32_t bits[10]={2,0x40,0x800,0x80,0x100,0x200,8,0x10,0x20,0x1000};uint32_t want=0;
 for(uint32_t i=0;i<10;i++){if((reason&0x20)&&i>=3&&i<=5)continue;want|=bits[i];audio_flags_set(*(void**)(ctx[i]+8),0x800000);}
 return want;
}
void audio_stop_one(void *thread,uint32_t index){
 audio_flags_set(thread,0x800000);audio_event_wait(*(void**)((uint32_t)(uintptr_t)g2ref_audio_uart_thread_manager_state+0x1cu),1u<<index,1,20000);
}
void audio_exit_no_timer(void){
 audio_ack_index(3);void *q=*(void**)((uint32_t)(uintptr_t)g2ref_g2_audio_dispatch_state+0xcu);
 if(q){audio_queue_delete_peer(q);*(void**)((uint32_t)(uintptr_t)g2ref_g2_audio_dispatch_state+0xcu)=0;}
 for(;;)audio_delay(0xffffffffu);
}
