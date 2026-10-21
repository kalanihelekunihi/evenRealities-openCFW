/* Native HCI register 0x5367f0, callback wrapper 0x536814,
 * HciCoreHandler 0x530cb2, and WSF message wrappers 0x4bf9ec/0x4bf9b0. */
#include <stdint.h>

extern uint8_t audio_ble_hci_stack_state_20073870[]; /* live 0x20073870 */
extern void *audio_wsf_queue_dequeue(void *); /* selected 0x538c4a */
extern void g2_wsf_candidate_buffer_free_word(uint32_t); /* selected 0x5304d4 */
extern void audio_ble_hci_event_process(void *); /* native 0x56b390 */
extern void audio_ble_hci_reset_sequence(void *); /* native 0x569b56 */
extern void *audio_ble_hci_acl_reassemble(void *); /* native 0x52a962 */
extern void audio_ble_hci_command_timeout(void *); /* native 0x52aee6 */

static uint32_t word(const uint8_t *p) {
    uint32_t v; __builtin_memcpy(&v,p,4u); return v;
}
static void put(uint8_t *p,const void *v) {
    __builtin_memcpy(p,&v,4u);
}
void audio_ble_l2c_hci_register(void (*acl)(void),void (*flow)(void)) {
    put(audio_ble_hci_stack_state_20073870+0x10u,(const void *)acl);
    put(audio_ble_hci_stack_state_20073870+0x14u,(const void *)flow);
}
void *audio_ble_wsf_message_dequeue(void *queue,uint8_t *handler) {
    uint8_t *header=(uint8_t *)audio_wsf_queue_dequeue(queue);
    if(header==0)return 0;
    *handler=header[4];
    return header+8u;
}
void audio_ble_wsf_message_free(void *message) {
    g2_wsf_candidate_buffer_free_word((uint32_t)(uintptr_t)message-8u);
}
uint32_t audio_ble_hci_core_handler(uint32_t events,void *event,
                                    uint32_t unused,uint32_t scratch) {
    (void)unused;
    uint32_t local=scratch;
    uint8_t *state=audio_ble_hci_stack_state_20073870;
    if(event==0) {
        if((events&1u)!=0u) {
            uint8_t handler;
            void *message;
            while((message=audio_ble_wsf_message_dequeue(state,&handler))!=0) {
                local=(local&~0xffu)|handler;
                if(handler==4u) {
                    audio_ble_hci_event_process(message);
                    if(state[0x21u]!=0u)
                        audio_ble_hci_reset_sequence(message);
                    audio_ble_wsf_message_free(message);
                } else if(handler==2u) {
                    void *assembled=audio_ble_hci_acl_reassemble(message);
                    if(assembled!=0) {
                        void (*callback)(void *)=(void (*)(void *))(uintptr_t)word(state+0x10u);
                        callback(assembled);
                    }
                } else {
                    uint32_t callback=word(state+0x18u);
                    if(callback==0u)audio_ble_wsf_message_free(message);
                    else ((void (*)(void *))(uintptr_t)callback)(message);
                }
            }
        }
    } else if(((const uint8_t *)event)[2]==1u)
        audio_ble_hci_command_timeout(event);
    return local;
}
void audio_ble_handler_536814(uint32_t events,void *event,
                              uint32_t unused,uint32_t scratch) {
    (void)audio_ble_hci_core_handler((uint8_t)events,event,unused,scratch);
}
