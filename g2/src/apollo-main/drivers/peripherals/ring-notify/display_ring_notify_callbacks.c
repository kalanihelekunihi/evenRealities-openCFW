/* Native delayed callback entries 0x47257c, 0x472588, 0x4a285c,
 * and ring-enable-pair 0x4c5032. */
#include <stdint.h>
extern void audio_uart_ring_master_set_phy_event_4a2254(uint32_t);
extern uint32_t Thread_SendEvtToRingTask(uint32_t); /* selected 0x4c543e */
extern void audio_uart_ring_publish_link_ready_4a271e(void);
void audio_uart_ring_pair_enable_effect_472630(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="task.ring";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\threads\\thread_ring.c";
static const char fn[]="_ring_enable_pair";
static const char message[]="RING_EnablePairEvt";
static const char short_message[]="[task.ring]RING_EnablePairEvt";
void audio_uart_ring_pair_enable_delayed_47257c(void) {
    audio_uart_ring_master_set_phy_event_4a2254(0u);
}
void audio_uart_ring_pair_disable_delayed_472588(void) {
    (void)Thread_SendEvtToRingTask(0x800u);
}
void audio_uart_ring_status_delayed_4a285c(void) {
    audio_uart_ring_publish_link_ready_4a271e();
}
void audio_uart_ring_service_disc_followup_4c5032(void) {
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,fn,265u,message);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10000000u,short_message,short_message);
    audio_uart_ring_pair_enable_effect_472630();
}
void audio_uart_ring_pair_enable_effect_472630(void) {
    (void)Thread_SendEvtToRingTask(0x40u);
}
