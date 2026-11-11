#include <stdint.h>
#include <stddef.h>
#include <stdarg.h>
/* Observed cold RW bytes at 0x20007cec; startup-verified, not yet image-integrated. */
__attribute__((section(".r1.gomore.log.configuration"),used))
volatile uint8_t r1_gomore_log_configuration[12]={0};
extern void __aeabi_memclr(void *,size_t);
extern char *r1_native_strcat(char *,const char *);
extern int r1_native_vsnprintf(char *,size_t,const char *,va_list);
struct __attribute__((packed,may_alias)) log_word {uint32_t value;};
struct __attribute__((packed,may_alias)) log_half {uint16_t value;};
static uint32_t word(uint32_t offset){return ((volatile struct log_word *)(r1_gomore_log_configuration+offset))->value;}
static uint16_t half(uint32_t offset){return ((volatile struct log_half *)(r1_gomore_log_configuration+offset))->value;}
static uint32_t shift(uint32_t count){count&=255u;return count<32u?1u<<count:0;}
struct log_frame {char message[256];uint32_t sentinel;va_list arguments;};
_Static_assert(offsetof(struct log_frame,sentinel)==256,"native suffix sentinel");
_Static_assert(offsetof(struct log_frame,arguments)==260,"native frame view");
void r1_gomore_log_native(uint32_t level,uint32_t category,const char *format,...)
{
    struct log_frame frame;
    /* The suffix may extend into the sentinel. Use the whole object's byte
     * representation so those accesses stay within the containing object. */
    char *message=(char *)&frame;
    va_start(frame.arguments,format);
    __aeabi_memclr(message,256);
    if (word(4) && r1_gomore_log_configuration[0] && (shift(level)&word(8)) && (shift(category)&half(2))) {
        (void)r1_native_strcat(message,"[GoMoRe]");
        uint32_t formatted=(uint32_t)r1_native_vsnprintf(message+8,248,format,frame.arguments);
        frame.sentinel=0;
        if (formatted<248) (void)r1_native_strcat(message,"\r\n");
        typedef void (*emit_fn)(const char *,const char *);
        ((emit_fn)(uintptr_t)word(4))("%s",message);
    }
    va_end(frame.arguments);
}
