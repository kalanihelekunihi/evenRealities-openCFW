/* Native radio request send 0x52e0d2. Descriptor layout at 0x55cf40
 * follows the retained 0x30-byte native stack object. */
#include <stdint.h>

extern int32_t audio_ble_radio_begin_select_52e072(void *);
extern uint32_t audio_ble_radio_tx_space_52df50(void *);
extern void audio_ble_radio_tx_release_52e058(void *);
extern int32_t audio_ble_radio_io_mode_52dd1c(void);
extern void audio_ble_radio_serial_put_52dc98(uint32_t);
extern int32_t audio_ble_vendor_send_55cf40(uint32_t,void *);
extern void audio_ble_radio_context_init_52e0a2(void *);
extern void audio_ble_hci_boot_log_4733ee(const void *,...);
extern const uint8_t audio_ble_radio_send_log_71b740[]; /* native 0x52ed30 pointer */
extern const uint8_t audio_ble_radio_send_oversize_log_730e54[]; /* native 0x52ede0 pointer */

static uint32_t word(const void *p) {uint32_t v;__builtin_memcpy(&v,p,4u);return v;}

int32_t audio_ble_radio_exchange_begin_52e0d2(void *context,const void *command,
                                                uint32_t length) {
    int32_t result=audio_ble_radio_begin_select_52e072(context);
    if(result!=0)return result;
    if(length>=0x104u) {
        result=9;
        audio_ble_hci_boot_log_4733ee(audio_ble_radio_send_oversize_log_730e54);
    } else {
        uint8_t payload[260];
        uint8_t scratch[16];
        uint8_t descriptor[0x30];
        uint32_t sent=0u;
        while(sent<length) {
            uint32_t space=(uint8_t)audio_ble_radio_tx_space_52df50(context);
            if(space==0u) {
                result=8;
                audio_ble_radio_tx_release_52e058(context);
                break;
            }
            uint32_t count=length-sent;
            if(count>space)count=space;
            if(count!=0u) {
                __builtin_memcpy(payload,(const uint8_t *)command+sent,count);
                sent+=count;
                if(audio_ble_radio_io_mode_52dd1c()==0) {
                    __builtin_memset(descriptor,0,sizeof(descriptor));
                    /* native descriptor: count+0x10, type+0x14,
                     * payload+0x18, scratch+0x1c, zeroed flags. */
                    __builtin_memcpy(descriptor+0x10u,&count,4u);
                    descriptor[0x14u]=2u;
                    uint32_t pointer=(uint32_t)(uintptr_t)payload;
                    __builtin_memcpy(descriptor+0x18u,&pointer,4u);
                    pointer=(uint32_t)(uintptr_t)scratch;
                    __builtin_memcpy(descriptor+0x1cu,&pointer,4u);
                    int32_t vendor=audio_ble_vendor_send_55cf40(word((uint8_t *)context+4u),descriptor);
                    if(vendor!=0) {
                        result=11;
                        audio_ble_hci_boot_log_4733ee(audio_ble_radio_send_log_71b740,
                                                      vendor,word(context));
                    }
                } else {
                    for(uint32_t i=0;i<count;i++)
                        audio_ble_radio_serial_put_52dc98(payload[i]);
                }
            }
            audio_ble_radio_tx_release_52e058(context);
        }
    }
    audio_ble_radio_context_init_52e0a2(context);
    return result;
}
