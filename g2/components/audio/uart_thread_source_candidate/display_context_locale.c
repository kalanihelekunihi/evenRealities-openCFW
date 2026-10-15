/* Apollo display context registry 0x460090/0x4600b4 and locale 0x471164. */
#include <stdint.h>

extern const void *audio_uart_display_context_list_cell; /* RAM 0x200746c8 */
extern const void *audio_uart_display_context_active_cell; /* RAM 0x200746cc */
extern volatile uint32_t audio_uart_display_locale_index; /* RAM 0x20000030 */
extern int32_t audio_uart_font_path_compare(const char *,const char *); /* 0x46cacc */

int32_t audio_uart_display_context_set(const void *registry)
{
    if(registry==0) return -1;
    const void *const *entries=(const void *const *)registry;
    if(entries[0]==0) return -1;
    audio_uart_display_context_list_cell=registry;
    audio_uart_display_context_active_cell=entries[0];
    return 0;
}

const char *audio_uart_display_layer_init(void)
{
    static const char english[]="en-GB";
    static const char chinese[]="zh-CN";
    static const char hong_kong[]="zh-HK";
    static const char german[]="de";
    static const char french[]="fr";
    static const char spanish[]="es";
    static const char italian[]="it";
    static const char japanese[]="ja";
    switch(audio_uart_display_locale_index) {
    case 1u:return german;
    case 2u:return french;
    case 3u:return spanish;
    case 4u:return italian;
    case 5u:return japanese;
    case 6u:return chinese;
    case 7u:return hong_kong;
    default:return english;
    }
}

int32_t audio_uart_display_context_commit(const char *locale)
{
    const void *const *entries=(const void *const *)audio_uart_display_context_list_cell;
    if(entries==0) return -1;
    for(uint16_t index=0;entries[index]!=0;index=(uint16_t)(index+1u)) {
        const char *name=*(const char *const *)entries[index];
        if(audio_uart_font_path_compare(name,locale)==0) {
            audio_uart_display_context_active_cell=entries[index];
            return 0;
        }
    }
    return -1;
}
