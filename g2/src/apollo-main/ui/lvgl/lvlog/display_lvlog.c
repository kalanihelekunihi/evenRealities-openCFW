/* LVGL platform log wrapper native 0x44d25c. Native buffer sizes and
 * format are retained; general formatter grammar remains its own gate. */
#include <stdint.h>
#include <stdarg.h>
extern uint8_t audio_uart_display_lv_state[]; /* RAM0x2006f548 */
/* Native 0x44d2f0 loads RAM 0x20002bec and indexes by signed level*4.
 * This wrapper admits levels 2..5, requiring at least six pointer slots.
 * Startup ownership and the actual pointer values remain unresolved. */
extern const char *audio_uart_lv_level_names[6]; /* RAM0x20002bec */
extern uint32_t audio_uart_lv_tick(void); /* 0x473482 */
extern int32_t g2_log_vformat(char *,uint32_t,const char *,va_list); /* 0x44b76c */
int32_t g2_audio_dump_snprintf(char *,uint32_t,const char *,...); /* 0x44b728 */
static const char line_format[]="[%s]\t(%u.%03u, +%u)\t %s: %s %s:%d\n";
typedef void (*lv_sink)(uint32_t,const char *);
int32_t g2_audio_dump_snprintf(char *destination,uint32_t capacity,
                                const char *format,...) {
    va_list args;
    va_start(args,format);
    int32_t n=g2_log_vformat(destination,capacity,format,args);
    va_end(args);
    return n;
}
/* 0x44d25c is upstream lv_log_add (lvgl/src/misc/lv_log.c, same lv_global
 * offsets 0x16c/0x170 as stock); the hand copy was removed. */
