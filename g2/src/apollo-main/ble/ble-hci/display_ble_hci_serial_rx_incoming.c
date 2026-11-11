/* Native hciTrSerialRxIncoming 0x530186 and its size/dispatch children.
 * State slots are authenticated ROM pointees into live product RAM. */
#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_stock_ram_20074648[] __asm__("g2_stock_ram_20074648");
extern unsigned char g2ref_g2_stock_ram_20074f30[] __asm__("g2_stock_ram_20074f30");
extern unsigned char g2ref_g2_stock_ram_20074fc8[] __asm__("g2_stock_ram_20074fc8");
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
        uint8_t state=B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074fc8+0x6u));
        if(state==0u) {
            B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074fc8+0x7u))=c;
            H(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30))=0u;
            B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074fc8+0x6u))=1u;
            B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074fc8+0x5u))=1u;
            src++;consumed++;remaining--;
        } else if(state==1u) {
            uint32_t header_length;
            uint8_t type=B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074fc8+0x7u));
            if(type==4u)header_length=2u;
            else if(type==2u)header_length=4u;
            else {B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074fc8+0x6u))=0u;return count;}
            if(H(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30))!=header_length) {
                B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074648+0x4u)+H(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30)))=c;
                H(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30))++;
                src++;consumed++;remaining--;
            }
            if(H(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30))==header_length) {
                uint32_t payload=0u;
                if(type==4u)payload=B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074648+0x5u));
                else payload=(uint32_t)B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074648+0x6u))|((uint32_t)B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074648+0x7u))<<8u);
                if(type==2u && payload<=audio_ble_hci_get_max_rx_acl_len_530d4c())
                    W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074648+0x8u))=(uint32_t)(uintptr_t)audio_ble_hci_msg_data_alloc(
                        (uint16_t)(payload+header_length),0u);
                else if(type==4u && payload<0x100u)
                    W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074648+0x8u))=(uint32_t)(uintptr_t)audio_wsf_msg_alloc(
                        (uint16_t)(payload+header_length));
                if(W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074648+0x8u))==0u) {B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074fc8+0x6u))=0u;return count;}
                W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074648+0xcu))=W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074648+0x8u));
                for(uint32_t i=0;i<header_length;i++) {
                    B(W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074648+0xcu)))=B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074648+0x4u)+i);
                    W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074648+0xcu))++;
                }
                H(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30))=(uint16_t)payload;
                B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074fc8+0x6u))=payload==0u?3u:2u;
            }
        } else if(state==2u) {
            B(W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074648+0xcu)))=c;
            W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074648+0xcu))++;
            H(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30))--;
            if(H(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30))==0u)B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074fc8+0x6u))=3u;
            src++;consumed++;remaining--;
        }
        if(B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074fc8+0x6u))==3u) {
            B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074fc8+0x5u))=0u;
            if(W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074648+0x8u))!=0u)
                audio_ble_hci_core_recv_530c88(B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074fc8+0x7u)),
                    (void *)(uintptr_t)W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074648+0x8u)));
            B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074fc8+0x6u))=0u;
        }
    }
}
