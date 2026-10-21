/* Stock Main 0x47dd08: pack the first three decimal version components. */
#include <stdint.h>

const volatile char audio_tracepoint_version_string_78c740[]
    __attribute__((section(".rodata.opencfw.tracepoint.version"),used))="2.2.6.10";

uint32_t audio_tracepoint_version_47dd08(void) {
    const volatile char *p=audio_tracepoint_version_string_78c740;
    uint32_t values[3]={0u,0u,0u};
    uint32_t count=0u;
    while(*p!=0 && count<3u) {
        if((uint32_t)(*p-'0')<10u) {
            uint32_t value=0u;
            do {
                uint32_t digit=(uint32_t)(*p-'0');
                if(value>429496729u || (value==429496729u && digit>5u))
                    value=0xffffffffu;
                else if(value!=0xffffffffu)
                    value=value*10u+digit;
                p++;
            } while((uint32_t)(*p-'0')<10u);
            values[count++]=value;
        } else p++;
    }
    return (values[0]<<16)|(values[1]<<8)|values[2];
}
