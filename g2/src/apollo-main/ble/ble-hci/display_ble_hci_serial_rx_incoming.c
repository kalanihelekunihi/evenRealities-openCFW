/* Native hciTrSerialRxIncoming 0x530186 and its size/dispatch children.
 * State slots are authenticated ROM pointees into live product RAM. */
#include <stdint.h>
extern void *audio_ble_hci_msg_data_alloc(uint16_t,uint8_t); /* 0x4bf990 */
extern void *audio_wsf_msg_alloc(uint16_t); /* 0x4bf99e */
extern void audio_wsf_msg_enqueue(void *,uint8_t,void *); /* WsfMsgEnq */
extern void audio_ble_wsf_set_event(uint32_t,uint32_t); /* 0x52b91e */
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define H(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
extern uint16_t audio_ble_hci_get_max_rx_acl_len_530d4c(void); /* opencfw U5: now provided by the Cordio unit */
extern void audio_ble_hci_core_recv_530c88(uint8_t type,void *message); /* opencfw U5: now provided by the Cordio unit */
uint32_t audio_ble_hci_serial_rx_incoming_530186(const void *input,uint16_t count) {
    const uint8_t *src=(const uint8_t *)input;
    uint16_t remaining=count,consumed=0u;
    for(;;) {
        if(remaining==0u)return consumed;
        uint8_t c=*src;
        uint8_t state=B(0x20074fceu);
        if(state==0u) {
            B(0x20074fcfu)=c;
            H(0x20074f30u)=0u;
            B(0x20074fceu)=1u;
            B(0x20074fcdu)=1u;
            src++;consumed++;remaining--;
        } else if(state==1u) {
            uint32_t header_length;
            uint8_t type=B(0x20074fcfu);
            if(type==4u)header_length=2u;
            else if(type==2u)header_length=4u;
            else {B(0x20074fceu)=0u;return count;}
            if(H(0x20074f30u)!=header_length) {
                B(0x2007464cu+H(0x20074f30u))=c;
                H(0x20074f30u)++;
                src++;consumed++;remaining--;
            }
            if(H(0x20074f30u)==header_length) {
                uint32_t payload=0u;
                if(type==4u)payload=B(0x2007464du);
                else payload=(uint32_t)B(0x2007464eu)|((uint32_t)B(0x2007464fu)<<8u);
                if(type==2u && payload<=audio_ble_hci_get_max_rx_acl_len_530d4c())
                    W(0x20074650u)=(uint32_t)(uintptr_t)audio_ble_hci_msg_data_alloc(
                        (uint16_t)(payload+header_length),0u);
                else if(type==4u && payload<0x100u)
                    W(0x20074650u)=(uint32_t)(uintptr_t)audio_wsf_msg_alloc(
                        (uint16_t)(payload+header_length));
                if(W(0x20074650u)==0u) {B(0x20074fceu)=0u;return count;}
                W(0x20074654u)=W(0x20074650u);
                for(uint32_t i=0;i<header_length;i++) {
                    B(W(0x20074654u))=B(0x2007464cu+i);
                    W(0x20074654u)++;
                }
                H(0x20074f30u)=(uint16_t)payload;
                B(0x20074fceu)=payload==0u?3u:2u;
            }
        } else if(state==2u) {
            B(W(0x20074654u))=c;
            W(0x20074654u)++;
            H(0x20074f30u)--;
            if(H(0x20074f30u)==0u)B(0x20074fceu)=3u;
            src++;consumed++;remaining--;
        }
        if(B(0x20074fceu)==3u) {
            B(0x20074fcdu)=0u;
            if(W(0x20074650u)!=0u)
                audio_ble_hci_core_recv_530c88(B(0x20074fcfu),
                    (void *)(uintptr_t)W(0x20074650u));
            B(0x20074fceu)=0u;
        }
    }
}
