/* Native compiler strncpy helper 0x44b5a0, source-equivalent byte semantics. */
#include <stdint.h>
void *audio_settings_copy_text(void *destination,const void *source,uint32_t count) {
    uint8_t *out=(uint8_t *)destination;
    const uint8_t *in=(const uint8_t *)source;
    uint32_t i=0;
    for(;i<count;i++) {
        uint8_t value=in[i];
        out[i]=value;
        if(value==0u) {
            i++;
            break;
        }
    }
    for(;i<count;i++) out[i]=0u;
    return destination;
}
