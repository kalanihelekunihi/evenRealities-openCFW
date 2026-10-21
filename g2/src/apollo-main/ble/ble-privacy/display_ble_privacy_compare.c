/* Native 0x4d294a compares the six-byte peer address via 0x4751c8. */
#include <stdint.h>
uint32_t audio_ble_privacy_compare_address(const uint8_t *a,const uint8_t *b) {
    for(uint32_t i=0;i<6u;i++) if(a[i]!=b[i]) return 0u;
    return 1u;
}
