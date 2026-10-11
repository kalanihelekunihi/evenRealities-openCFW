/* LVGL platform log wrapper native 0x44d25c. Native buffer sizes and
 * format are retained; general formatter grammar remains its own gate. */
#include <stdint.h>
#include <stdarg.h>
extern uint8_t audio_uart_display_lv_state[]; /* RAM0x2006f548 */
extern const char *audio_uart_lv_level_names[]; /* RAM0x20002bec */
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
void audio_uart_lvgl_log(uint32_t level,const char *file,uint32_t line,
                          const char *function,const char *format,...) {
    if(level<2u||level>=6u) return;
    uint32_t i=0u;
    const volatile char *count_file=(const volatile char *)file;
    while(count_file[i]!=0) ++i;
    while(i!=0u) {
        if(file[i]=='/'||file[i]=='\\') {++i;break;}
        --i;
    }
    uint32_t tick=audio_uart_lv_tick();
    uint8_t *s=audio_uart_display_lv_state;
    uint32_t callback=*(uint32_t *)(void *)(s+0x16cu);
    if(callback!=0u) {
        char body[256],output[512];
        va_list args;
        va_start(args,format);
        (void)g2_log_vformat(body,sizeof(body),format,args);
        va_end(args);
        (void)g2_audio_dump_snprintf(output,sizeof(output),line_format,
             audio_uart_lv_level_names[level],tick/1000u,tick%1000u,
             tick-*(uint32_t *)(void *)(s+0x170u),function,body,file+i,line);
        ((lv_sink)(uintptr_t)callback)(level,output);
    }
    *(uint32_t *)(void *)(s+0x170u)=tick;
}
