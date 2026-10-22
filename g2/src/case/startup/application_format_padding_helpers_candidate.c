/* SPDX-License-Identifier: MIT
 * Native CASE 0x08009638 and 0x08009658 formatter padding leaves.
 * The callback return value is ignored by both native routines.
 */
#include <stdint.h>

typedef int32_t (*case_format_emit_t)(int32_t,void *);

/* Stock 0x08009638 (case_emit_left_padding) */
int32_t case_format_space_padding(int32_t width,uint32_t flags,void *context,
                                  case_format_emit_t emit)
{
    int32_t written=0;
    if((flags&(1u<<13))!=0u)
        while(width>0){--width;(void)emit(0x20,context);++written;}
    return written;
}

/* Stock 0x08009658 (case_emit_right_padding) */
int32_t case_format_field_padding(int32_t width,uint32_t flags,void *context,
                                  case_format_emit_t emit)
{
    int32_t written=0;
    int32_t character=(flags&(1u<<16))!=0u?0x30:0x20;
    if((flags&(1u<<13))==0u)
        while(width>0){--width;(void)emit(character,context);++written;}
    return written;
}
