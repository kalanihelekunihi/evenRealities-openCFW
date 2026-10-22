/* Native pathname compare/duplicate and LVGL list append children. */
#include <stdint.h>
extern uint32_t g2_log_module_length(const char *); /* selected 0x44a43c */
extern void *audio_uart_lv_malloc(uint32_t); /* 0x44f718 */
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t); /* selected 0x439be4 */
int32_t audio_uart_font_path_compare(const char *left,const char *right) {
    for(;;) {
        uint32_t a=(uint8_t)*left;
        uint32_t b=(uint8_t)*right;
        if(a==0u||a!=b) return (int32_t)(a-b);
        ++left;++right;
    }
}
