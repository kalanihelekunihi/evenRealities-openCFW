/* Native R1 structured-log record packing, recovered from 0x46FD4.
 * This is the stock compact wire schema, not a printf implementation. */
#include <stdint.h>
#include <stddef.h>
#include <stdarg.h>
#include <string.h>
extern volatile uint8_t r1_structured_log_mode;
volatile uint8_t r1_structured_log_level __attribute__((section(".r1.log.level"),aligned(1)))=3;
volatile uint8_t r1_structured_log_sequence __attribute__((section(".r1.log.sequence"),aligned(1)));
extern uint32_t osKernelGetTickCount(void);
extern uint32_t r1_structured_log_clock_available(void);
extern uint32_t r1_structured_log_timestamp_adapter(void);
extern uint32_t r1_structured_log_local_timestamp(void);
extern uint32_t r1_log_double_to_float_bits(uint64_t bits);
extern void r1_structured_log_cache_append(const void *record,uint32_t bytes);
static int digit(uint8_t ch) { return (uint32_t)(ch-'0')<10; }
void r1_structured_log_encode_format(uint32_t header,const char *text,va_list arguments) {
    struct { uint32_t prefix,time,header;uint8_t payload[32]; } record={0};
    uint32_t severity=(header>>26)&7u;
    if (r1_structured_log_mode & 4u) { if (severity>5) return; }
    else if ((r1_structured_log_mode & 1u) && r1_structured_log_level<severity) return;
    uint8_t sequence=r1_structured_log_sequence;
    r1_structured_log_sequence=(uint8_t)(sequence+1);
    record.prefix=UINT32_C(0xdc000000)+((osKernelGetTickCount()%1000)<<16)+((uint32_t)sequence<<8)+0x7b;
    record.time=r1_structured_log_clock_available() ? r1_structured_log_local_timestamp() : r1_structured_log_timestamp_adapter();
    record.header=header;
    const uint8_t *p=(const uint8_t *)text;
    uint32_t used=0,processed=0;
    uint32_t requested=(header>>22)&15u;
    while (*p && processed<requested) {
        if (*p=='%') {
            ++p;
            if (*p=='0' || *p=='-' || *p=='+' || *p==' ' || *p=='#') {
                do { ++p; } while (digit(*p));
            } else while (digit(*p)) ++p;
            if (*p=='.') {
                ++p;
                if (*p=='*') { ++p;(void)va_arg(arguments,uint32_t); }
                else while (digit(*p)) ++p;
            }
            int wide=0;
            if (*p=='l') { ++p;if (*p=='l') { ++p;wide=1; } }
            else if (*p=='h') { ++p;if (*p=='h') ++p; }
            uint8_t conversion=*p;
            if (!conversion) break;
            if (conversion=='%') { ++p;continue; }
            if (conversion=='s') {
                const char *value=va_arg(arguments,const char *);
                if (used+16<=32) {
                    size_t length=value ? strlen(value) : 0;
                    size_t keep=length<16 ? length : 16;
                    if (keep) memcpy(record.payload+used,value+length-keep,keep);
                    if (keep<16) memset(record.payload+used+keep,0,16-keep);
                    used+=16;
                }
            } else if (conversion=='f' || conversion=='F') {
                uint64_t bits=va_arg(arguments,uint64_t);
                if (used+4<=32) {
                    uint32_t value=r1_log_double_to_float_bits(bits);
                    memcpy(record.payload+used,&value,4);used+=4;
                }
            } else {
                int integer=conversion=='i'||conversion=='d'||conversion=='c'||conversion=='X'||conversion=='o'||conversion=='p'||conversion=='u'||conversion=='x';
                uint32_t value=(wide && integer) ? (uint32_t)va_arg(arguments,uint64_t) : va_arg(arguments,uint32_t);
                if (used+4<=32) { memcpy(record.payload+used,&value,4);used+=4; }
            }
            processed=(processed+1)&255u;
        }
        ++p;
        if (used>31) break;
    }
    record.header=(header & UINT32_C(0xfc3fffff)) | (processed<<22);
    r1_structured_log_cache_append(&record,12+used);
}
