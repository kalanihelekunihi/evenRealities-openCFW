/* Native hciDrvWrite 0x4b4a02, ring ownership and command framing. */
#include <stdint.h>
extern uint8_t audio_ble_hci_radio_scheduler_state[]; /* live ring 0x20073ba8 */
extern volatile uint8_t audio_ble_hci_driver_handler_id; /* live 0x20074fcb */
extern void audio_ble_hci_error_check_4b47ae(uint32_t);
extern uint32_t audio_ble_hci_ring_commit_530084(void *,const void *,uint32_t);
extern void audio_ble_wsf_set_event(uint32_t,uint32_t); /* native 0x52b91e */
static uint32_t word(const uint8_t *p) {uint32_t v;__builtin_memcpy(&v,p,4u);return v;}
static void put(uint8_t *p,uint32_t v) {__builtin_memcpy(p,&v,4u);}
uint32_t audio_ble_hci_driver_write(uint32_t packet_type,uint16_t length,const void *bytes) {
    uint8_t *ring=audio_ble_hci_radio_scheduler_state;
    if(word(ring+8u)==word(ring+12u)) {
        audio_ble_hci_error_check_4b47ae(0x09000000u);
    } else if(length<0x103u) {
        uint8_t *out=(uint8_t *)(uintptr_t)(word(ring+20u)+word(ring));
        put(out,(uint32_t)length+1u);
        out[4u]=(uint8_t)packet_type;
        const uint8_t *input=(const uint8_t *)bytes;
        for(uint32_t i=0;i<length;i++)out[5u+i]=input[i];
        (void)audio_ble_hci_ring_commit_530084(ring,0,1u);
        audio_ble_wsf_set_event(audio_ble_hci_driver_handler_id,1u);
    } else {
        audio_ble_hci_error_check_4b47ae(0x09000001u); /* native ROM 0x4b4da0 */
    }
    return length;
}
