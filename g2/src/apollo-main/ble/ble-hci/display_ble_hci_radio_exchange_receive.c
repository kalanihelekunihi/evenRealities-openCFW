/* Native radio exchange receive 0x52e1ea. Product busy cell at 0x20074f4f
 * and status MMIO at 0x40010410 are live runtime inputs. */
#include <stdint.h>

extern volatile uint8_t audio_ble_hci_radio_dispatch_cell_20074f4f;
extern int32_t audio_ble_radio_begin_select_52e072(void *);
extern int32_t audio_ble_radio_io_mode_52dd1c(void);
extern void audio_ble_radio_context_init_52e0a2(void *);
extern void audio_ble_radio_serial_put_52dc98(uint32_t);
extern uint32_t audio_ble_radio_serial_get_52dcde(void);
extern int32_t audio_ble_vendor_send_55cf40(uint32_t,void *);
extern int32_t audio_ble_vendor_receive_55cc1c(uint32_t,void *);
extern int32_t g2_gpio_hal_write(uint32_t,uint32_t);
extern void audio_ble_hci_boot_log_4733ee(const void *,...);
extern const uint8_t audio_ble_radio_busy_log_768ae4[];
extern const uint8_t audio_ble_radio_header_log_6f7d84[];
extern const uint8_t audio_ble_radio_length_log_71b778[];
extern const uint8_t audio_ble_radio_bulk_log_71b7b0[];

static uint32_t word(const void *p) {uint32_t v;__builtin_memcpy(&v,p,4u);return v;}
static void put(void *p,uint32_t v) {__builtin_memcpy(p,&v,4u);}

int32_t audio_ble_radio_exchange_receive_52e1ea(void *context,void *output,
                                                  uint32_t *received) {
    volatile uint32_t *const hardware=(volatile uint32_t *)(uintptr_t)0x40010410u;
    uint8_t request[2]={0x81u,0u};
    if(audio_ble_hci_radio_dispatch_cell_20074f4f!=0u) {
        audio_ble_hci_boot_log_4733ee(audio_ble_radio_busy_log_768ae4);
        return 3;
    }
    if((*hardware&0x00200000u)==0u)return 7;
    int32_t result=audio_ble_radio_begin_select_52e072(context);
    if(result!=0)return result;
    uint8_t *dst=(uint8_t *)output;
    do {
        if(audio_ble_radio_io_mode_52dd1c()==0) {
            uint8_t header[2]; /* vendor callback fills this on successful read */
            uint8_t descriptor[0x30];
            for(uint32_t attempt=0;attempt<10u;attempt++) {
                (void)g2_gpio_hal_write(0x95u,0u);
                __builtin_memset(descriptor,0,sizeof(descriptor));
                put(descriptor+0x10u,2u);
                descriptor[0x14u]=2u;
                put(descriptor+0x18u,(uint32_t)(uintptr_t)request);
                put(descriptor+0x1cu,(uint32_t)(uintptr_t)header);
                int32_t vendor=audio_ble_vendor_send_55cf40(word((uint8_t *)context+4u),descriptor);
                if(vendor!=0) {
                    (void)g2_gpio_hal_write(0x95u,1u);
                    result=10;
                    break;
                }
                if(header[0]==0xc0u && header[1]!=0u)break;
                (void)g2_gpio_hal_write(0x95u,1u);
            }
            uint32_t amount=header[1];
            if(header[0]!=0xc0u||amount==0u) {
                (void)g2_gpio_hal_write(0x95u,1u);
                audio_ble_hci_boot_log_4733ee(audio_ble_radio_header_log_6f7d84,
                                              0x3b4u,(int8_t)header[0],amount);
                result=6;
                break;
            }
            if((*hardware&0x00200000u)!=0u) {
                if(0x103u<*received+amount) {
                    (void)g2_gpio_hal_write(0x95u,1u);
                    audio_ble_hci_boot_log_4733ee(audio_ble_radio_length_log_71b778,
                                                  (int8_t)header[0],amount);
                    result=9;
                    break;
                }
                __builtin_memset(descriptor,0,sizeof(descriptor));
                put(descriptor+4u,0u);
                put(descriptor+0x10u,amount);
                descriptor[0x14u]=1u;
                put(descriptor+0x1cu,(uint32_t)(uintptr_t)(dst+*received));
                int32_t vendor=audio_ble_vendor_receive_55cc1c(word((uint8_t *)context+4u),descriptor);
                if(vendor!=0) {
                    (void)g2_gpio_hal_write(0x95u,1u);
                    audio_ble_hci_boot_log_4733ee(audio_ble_radio_bulk_log_71b7b0,vendor);
                    result=11;
                    break;
                }
                *received+=amount;
            }
        } else {
            (void)g2_gpio_hal_write(0x95u,0u);
            audio_ble_radio_serial_put_52dc98(0x81u);
            uint32_t amount=(uint8_t)audio_ble_radio_serial_get_52dcde();
            if(amount==0u||amount==0xffu) {
                (void)g2_gpio_hal_write(0x95u,1u);
                audio_ble_hci_boot_log_4733ee(audio_ble_radio_header_log_6f7d84,
                                              0x35eu,0u,amount);
                result=6;
                break;
            }
            if((*hardware&0x00200000u)!=0u) {
                if(0x103u<*received+amount) {
                    (void)g2_gpio_hal_write(0x95u,1u);
                    audio_ble_hci_boot_log_4733ee(audio_ble_radio_length_log_71b778,0u,amount);
                    result=9;
                    break;
                }
                for(uint32_t i=0;i<amount;i++)dst[*received+i]=(uint8_t)audio_ble_radio_serial_get_52dcde();
                *received+=amount;
            }
        }
        (void)g2_gpio_hal_write(0x95u,1u);
    } while((*hardware&0x00200000u)!=0u);
    audio_ble_radio_context_init_52e0a2(context);
    return result;
}
