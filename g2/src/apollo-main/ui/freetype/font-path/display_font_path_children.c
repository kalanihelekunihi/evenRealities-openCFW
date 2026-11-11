/* Native pathname compare/duplicate and LVGL list append children. */
#include <stdint.h>
extern uint32_t g2_log_module_length(const char *); /* selected 0x44a43c */
extern void *audio_uart_lv_malloc(uint32_t); /* 0x44f718 */
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t); /* selected 0x439be4 */
/* strcmp 0x46cacc: audio_uart_font_path_compare is an alias of
 * string_compare_46cacc (runtime/a-11-string/string_compare_46cacc.c). */
int32_t audio_uart_font_path_compare(const char *left,const char *right);
