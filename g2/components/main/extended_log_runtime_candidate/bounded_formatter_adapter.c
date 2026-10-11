/* Experimental four-word 0x44b76c interface for the selected bounded
 * integer/string formatter. Only its documented syntax domain is supported. */
#include <stdint.h>
#include <stdarg.h>
extern int32_t g2_log_candidate_common_format(uint32_t destination,
                                               uint32_t capacity,
                                               uint32_t format,
                                               uint32_t arguments);
/* Product/general formatter contract for syntax outside the measured subset. */
extern int32_t g2_log_general_vformat(char *destination,uint32_t capacity,
                                      const char *format,va_list arguments);
static int admitted(const char *p) {
    if(!p) return 0;
    while(*p) {
        if(*p++!='%') continue;
        if(!*p) return 1; /* authenticated final literal percent */
        if(*p=='%') {p++;continue;}
        while(*p=='-' || *p=='#' || *p=='0') p++;
        unsigned width=0;
        while(*p>='0' && *p<='9') {
            width=width*10u+(unsigned)(*p++-'0');
            if(width>24u) return 0;
        }
        int precision=0;
        if(*p=='.') {
            precision=1;p++;
            if(*p=='*') p++;
            else while(*p>='0' && *p<='9') p++;
        }
        unsigned length=0;
        if(*p=='l') {length=1;p++;if(*p=='l') {length=2;p++;}}
        else if(*p=='z') {length=1;p++;}
        const char c=*p++;
        if(!c) return 0;
        if(length==2) {if(c!='d' && c!='u') return 0;}
        else if(length==1) {if(c!='d' && c!='u' && c!='x' && c!='X') return 0;}
        else if(c!='d' && c!='u' && c!='x' && c!='X' && c!='p' && c!='s' && c!='c') return 0;
        if(precision && c!='s') return 0;
    }
    return 1;
}
int32_t g2_log_vformat_bounded_candidate(char *destination,uint32_t capacity,
                                          const char *format,va_list arguments) {
    _Static_assert(sizeof(va_list)==4,"ARM32 va_list word ABI");
    if(!admitted(format))
        return g2_log_general_vformat(destination,capacity,format,arguments);
    uint32_t argument_word;
    __builtin_memcpy(&argument_word,&arguments,sizeof(argument_word));
    return g2_log_candidate_common_format((uint32_t)(uintptr_t)destination,
                                          capacity,(uint32_t)(uintptr_t)format,
                                          argument_word);
}
