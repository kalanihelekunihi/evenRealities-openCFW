/* Native hciEvtCmdStatusFailure 0x56b100 and hciCmdRecvCmpl 0x52aef8. */
#include <stdint.h>
extern uint8_t audio_ble_hci_stack_state_20073870[]; /* live */
extern uint8_t audio_ble_hci_cmd_state_20073a90[]; /* live */
extern void *audio_wsf_buffer_alloc(uint16_t); /* selected WsfBufAlloc */
extern void g2_wsf_candidate_buffer_free_word(uint32_t); /* selected WsfBufFree */
extern void WsfTimerStop(void *); /* selected */
extern void audio_ble_hci_cmd_send(uint32_t); /* native hciCmdSend */
static uint32_t pointer(const uint8_t *p) {uint32_t v;__builtin_memcpy(&v,p,4u);return v;}
void audio_ble_hci_cmd_status_failure(uint32_t status,uint32_t opcode) {
    if((uint16_t)opcode!=0x2026u || (uint8_t)status!=0x12u)return;
    uint8_t *event=(uint8_t *)audio_wsf_buffer_alloc(4u);
    if(event==0)return;
    event[0]=0u;event[1]=0u;event[2]=0x26u;event[3]=0x12u;
    uint32_t callback=pointer(audio_ble_hci_stack_state_20073870+0x0cu);
    ((void (*)(void *))(uintptr_t)callback)(event);
    g2_wsf_candidate_buffer_free_word((uint32_t)(uintptr_t)event);
}
void audio_ble_hci_cmd_receive_complete(uint32_t ignored) {
    (void)ignored;
    WsfTimerStop(audio_ble_hci_cmd_state_20073a90);
    audio_ble_hci_cmd_state_20073a90[0x1au]=1u;
    audio_ble_hci_cmd_send(0u);
}
