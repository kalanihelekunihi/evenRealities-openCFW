/* Native radio context check 0x52e4b4. ROM 0x52f090 authenticates
 * expected response word 0x0101ff04; 0x52eba4 -> status 0x40010410. */
#include <stdint.h>

extern void audio_ble_radio_context_setup_52e49a(uint32_t);
extern int32_t g2_gpio_hal_write(uint32_t,uint32_t);
extern void audio_ble_hci_radio_reset_4910f4(uint32_t);
extern void audio_ble_hci_boot_delay_491102(uint32_t);
extern int32_t audio_ble_radio_exchange_receive_52e1ea(void *,void *,uint32_t *);
extern void audio_ble_hci_boot_log_4733ee(const void *,...);
extern volatile uint32_t audio_ble_hci_radio_detect_word_20074228;
extern const uint8_t audio_ble_hci_radio_detect_log_774b04[];
extern const uint8_t audio_ble_hci_radio_detect_mismatch_log_7515cc[];
extern const uint8_t audio_ble_hci_radio_detect_bytes_log_711d58[];

static uint32_t word(const uint8_t *p) {uint32_t v;__builtin_memcpy(&v,p,4u);return v;}

int32_t audio_ble_radio_context_check_52e4b4(void *context) {
    uint8_t response[16];
    __builtin_memset(response,0,sizeof(response));
    uint32_t received=0u;
    if(context==0)return 12;
    audio_ble_radio_context_setup_52e49a(1u);
    (void)g2_gpio_hal_write(0x5du,0u);
    audio_ble_hci_radio_reset_4910f4(1u);
    (void)g2_gpio_hal_write(0x5du,1u);
    volatile uint32_t *const hardware=(volatile uint32_t *)(uintptr_t)0x40010410u;
    uint32_t ticks=0u;
    while((*hardware&0x00200000u)!=0u) {
        if(ticks==30000u)return 4;
        audio_ble_hci_boot_delay_491102(1u);
        ++ticks;
    }
    ticks=0u;
    while((*hardware&0x00200000u)==0u) {
        if(ticks==30000u)break;
        audio_ble_hci_boot_delay_491102(1u);
        ++ticks;
    }
    audio_ble_radio_context_setup_52e49a(0u);
    if(ticks==30000u)return 5;
    int32_t result=audio_ble_radio_exchange_receive_52e1ea(context,response,&received);
    if(result!=0)return result;
    if(word(response)==0x0101ff04u) {
        audio_ble_hci_boot_log_4733ee(audio_ble_hci_radio_detect_log_774b04);
        return 0;
    }
    audio_ble_hci_radio_detect_word_20074228=word(response);
    audio_ble_hci_boot_log_4733ee(audio_ble_hci_radio_detect_mismatch_log_7515cc,0x452u);
    audio_ble_hci_boot_log_4733ee(audio_ble_hci_radio_detect_bytes_log_711d58,
                                  response[0],response[1],response[2],response[3],response[4]);
    return 5;
}
