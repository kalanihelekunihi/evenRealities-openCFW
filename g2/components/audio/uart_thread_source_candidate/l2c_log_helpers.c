/* Native 0x4c9c50 live trace-enable getter and 0x44b610 bounded comparison. */
#include <stdint.h>
extern volatile uint8_t audio_l2c_log_enabled_cell; /* RAM 0x2007502f */
uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void) {return audio_l2c_log_enabled_cell;}
int32_t audio_l2c_strncmp(const char *a,const char *b,uint32_t count) {
    for(uint32_t i=0;i<count;i++) {
        uint8_t x=(uint8_t)a[i],y=(uint8_t)b[i];
        if(x!=y) return x<y?-1:1;
        if(x==0u) return 0;
    }
    return 0;
}
