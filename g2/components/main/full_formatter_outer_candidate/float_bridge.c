/* Convert Main formatter's isolated float record into the shared output
 * segments. No product decimal separator or FP result is synthesized. */
#include "format_part.h"
#include "../../bootloader/initializer_callbacks/iar_format_native/record.h"
#include <stdint.h>
#include <stddef.h>

extern int g2_main_float_render_internal(format_record *,unsigned,uint32_t **,
                                          uint8_t *);
int32_t g2_iar_main_float_format(g2_format_part *out,uint32_t flags,
                                 uint32_t width,uint32_t precision_word,
                                 int32_t precision,int32_t signed_width,
                                 uint8_t conversion,uint32_t **cursor) {
    (void)width;(void)precision_word;
    uint8_t frame[232]={0};
    uint8_t scratch[128]={0};
    format_record record={0};
    record.scratch=(uint32_t)(uintptr_t)scratch;
    record.digits=record.scratch;
    record.flags=(uint16_t)flags;
    record.width=signed_width;
    record.precision=precision;
    int32_t result=g2_main_float_render_internal(&record,conversion,cursor,frame);
    if(result)return result;
    if(record.prefix_count>sizeof(out->prefix) ||
       record.digit_count>sizeof(out->body) ||
       record.trailer_count>sizeof(out->suffix))return -1;
    for(uint32_t i=0;i<record.prefix_count;i++)out->prefix[i]=scratch[i];
    const uint8_t *digits=(const uint8_t *)(uintptr_t)record.digits;
    for(uint32_t i=0;i<record.digit_count;i++)out->body[i]=digits[i];
    for(uint32_t i=0;i<record.trailer_count;i++)out->suffix[i]=digits[record.digit_count+i];
    out->prefix_len=record.prefix_count;
    out->body_len=record.digit_count;
    out->suffix_len=record.trailer_count;
    out->lead_zero=record.leading_zeros;
    out->mid_zero=record.middle_zeros;
    out->trail_zero=record.trailing_zeros;
    return 0;
}
