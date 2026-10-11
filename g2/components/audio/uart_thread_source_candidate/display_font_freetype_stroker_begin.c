/* Native FT_Stroker_BeginSubPath 0x5694e0. */
#include <stdint.h>
int32_t audio_uart_font_stroker_begin(void *stroker,const void *point,uint8_t open) {
    if(stroker==0||point==0) return 6;
    uint8_t *s=(uint8_t *)stroker;
    s[20u]=1u;
    *(uint32_t *)(void *)(s+8u)=*(const uint32_t *)point;
    *(uint32_t *)(void *)(s+12u)=*(const uint32_t *)(const void *)((const uint8_t *)point+4u);
    s[21u]=open;
    uint8_t join=s[42u];
    s[40u]=(join!=0u||(open!=0u&&s[41u]==0u))?1u:0u;
    *(uint32_t *)(void *)(s+28u)=*(const uint32_t *)point;
    *(uint32_t *)(void *)(s+32u)=*(const uint32_t *)(const void *)((const uint8_t *)point+4u);
    *(uint32_t *)s=0u;
    return 0;
}
