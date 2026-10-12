#include <stdint.h>
extern uint8_t audio_uart_display_lv_root[];
extern void *audio_uart_lv_cache_add_4d4eea(void *,const void *,void *);
extern void *audio_uart_font_cache_info(void *);
extern char *audio_uart_font_path_duplicate(const char *);
/* Full native48911a..489168; key source type is a byte at offset8. */
void *audio_uart_lv_decoder_add_cache_48911a(void *decoder,const void *key,void *decoded,void *user_data)
{
    void *cache=(void *)(uintptr_t)*(volatile uint32_t *)(void *)(audio_uart_display_lv_root+0x134u);
    void *entry=audio_uart_lv_cache_add_4d4eea(cache,key,0);
    if(entry==0) return 0;
    volatile uint32_t *data=audio_uart_font_cache_info(entry);
    data[3]=(uint32_t)(uintptr_t)decoded;
    if(((volatile uint8_t *)data)[8]==1u)
        data[1]=(uint32_t)(uintptr_t)audio_uart_font_path_duplicate((const char *)(uintptr_t)data[1]);
    data[5]=(uint32_t)(uintptr_t)user_data;
    data[4]=(uint32_t)(uintptr_t)decoder;
    return entry;
}
