/* Native radio transmit-space query 0x52df50. The 0x52ec80 ROM slot
 * authenticates error string 0x6ff930; live busy/MMIO remain external. */
#include <stdint.h>

extern volatile uint8_t audio_ble_hci_radio_dispatch_cell_20074f4f;
extern int32_t g2_gpio_hal_write(uint32_t,uint32_t);
extern void audio_ble_hci_boot_delay_491102(uint32_t);
extern int32_t audio_ble_radio_io_mode_52dd1c(void);
extern int32_t audio_ble_vendor_send_55cf40(uint32_t,void *);
extern void audio_ble_radio_serial_put_52dc98(uint32_t);
extern uint32_t audio_ble_radio_serial_get_52dcde(void);
extern void audio_ble_hci_boot_log_4733ee(const void *,...);
extern const uint8_t audio_ble_radio_tx_space_log_6ff930[];

static uint32_t word(const void *p) {uint32_t v;__builtin_memcpy(&v,p,4u);return v;}
static void put(void *p,uint32_t v) {__builtin_memcpy(p,&v,4u);}

uint32_t audio_ble_radio_tx_space_52df50(void *context) {
    volatile uint32_t *const hardware=(volatile uint32_t *)(uintptr_t)0x40010410u;
    audio_ble_hci_radio_dispatch_cell_20074f4f=1u;
    uint8_t command[2]={0x42u,0u};
    (void)g2_gpio_hal_write(0x95u,0u);
    for(uint32_t poll=0;poll<12000u&&(*hardware&0x00200000u)==0u;poll++)
        audio_ble_hci_boot_delay_491102(100u);
    if((*hardware&0x00200000u)==0u)return 0u;
    uint8_t response[2];
    for(uint32_t attempt=0;attempt<10u;attempt++) {
        (void)g2_gpio_hal_write(0x95u,0u);
        if(audio_ble_radio_io_mode_52dd1c()==0) {
            uint8_t descriptor[0x30];
            __builtin_memset(descriptor,0,sizeof(descriptor));
            put(descriptor+0x10u,2u);
            descriptor[0x14u]=2u;
            put(descriptor+0x18u,(uint32_t)(uintptr_t)command);
            put(descriptor+0x1cu,(uint32_t)(uintptr_t)response);
            int32_t error=audio_ble_vendor_send_55cf40(word((uint8_t *)context+4u),descriptor);
            if(error!=0) {
                audio_ble_hci_boot_log_4733ee(audio_ble_radio_tx_space_log_6ff930,
                                              error,word(context));
                return 0u;
            }
            if(response[0]==0xc0u&&response[1]!=0u)return response[1];
            (void)g2_gpio_hal_write(0x95u,1u);
        } else {
            audio_ble_radio_serial_put_52dc98(command[0]);
            response[1]=(uint8_t)audio_ble_radio_serial_get_52dcde();
            if(response[1]!=0u)return response[1];
        }
    }
    return response[1];
}
