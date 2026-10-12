#include <stdint.h>
extern uint32_t g2_log_module_length(const char *); /* selected44a43c */
extern int32_t audio_uart_font_path_compare(const char *,const char *); /* selected46cacc */
/* Full native454768..454770. */
uint32_t audio_uart_lv_string_length_454768(const char *source)
{
    return g2_log_module_length(source);
}
/* Full native4547be..4547c6. */
int32_t audio_uart_lv_string_compare_4547be(const char *a,const char *b)
{
    return audio_uart_font_path_compare(a,b);
}
/* Full native4c70e4..4c7116. Index0 deliberately excluded by native loop. */
const char *audio_uart_lv_fs_extension_4c70e4(const char *source)
{
    static const char empty[]="";
    uint32_t i=audio_uart_lv_string_length_454768(source);
    while(i != 0u) {
        if((uint8_t)source[i]==46u) return source+i+1u;
        if((uint8_t)source[i]==47u || (uint8_t)source[i]==92u) return empty;
        --i;
    }
    return empty;
}
