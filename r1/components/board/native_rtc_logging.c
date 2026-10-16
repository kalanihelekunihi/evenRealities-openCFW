/* Native RTC structured logging; mode is re-read at each native decision. */
#include <stdarg.h>
#include <stdint.h>
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern const char *nrf_strerror_get(uint32_t);
const char r1_rtc_log_enabled[] __attribute__((section(".r1.rtc.log.enabled")))="[RING]Enabled.";
const char r1_rtc_log_tick[] __attribute__((section(".r1.rtc.log.tick")))="[RING]Tick events enabled.";
const char r1_rtc_log_function[] __attribute__((section(".r1.rtc.log.function")))="[RING]Function: %s, error code: %s.";
void r1_rtc_log_info(const char *format,...) {
    if (format[0]=='F') {
        va_list args;va_start(args,format);const char *name=va_arg(args,const char *);uint32_t error=va_arg(args,uint32_t);va_end(args);
        if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) {
            const char *description=nrf_strerror_get(error);
            r1_structured_log_format(0x0c800000,r1_rtc_log_function,r1_rtc_log_function,name,description);
        }
    } else if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) {
        const char *text=format[0]=='E'?r1_rtc_log_enabled:r1_rtc_log_tick;
        r1_structured_log_format(0x0c000000,text,text);
    }
    (void)r1_structured_log_mode_get();
}
