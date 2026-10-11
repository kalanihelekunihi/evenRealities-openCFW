/* Native FT_Get_Font_Format 0x524b64. ROM0x78aa84 owns the parameter name. */
#include <stdint.h>
static const char font_format_key[]="font-format";
const char *audio_uart_font_get_format(void *face) {
    if(face==0) return 0;
    uint8_t *driver=(uint8_t *)(uintptr_t)*(uint32_t *)(void *)((uint8_t *)face+0x60u);
    uint8_t *clazz=(uint8_t *)(uintptr_t)*(uint32_t *)(void *)driver;
    typedef const char *(*request_fn)(void *,const char *);
    request_fn request=(request_fn)(uintptr_t)*(uint32_t *)(void *)(clazz+0x20u);
    if(request==0) return 0;
    return request(driver,font_format_key);
}
