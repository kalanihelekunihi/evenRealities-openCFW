/* Main 0x481836 candidate: adapted from pinned IAR Bootloader source;
 * identical 1270-instruction core topology except 23 relocated BL sites. */
#include <stdint.h>
typedef struct {uint32_t low,high,context,digits,scratch,prefix_count,digit_count,trailer_count,leading_zeros,middle_zeros,trailing_zeros,count;int32_t precision,width;uint16_t flags;uint8_t length,mode;} format_record;
int g2_main_format_float_render(format_record *,unsigned,uint32_t **,uint8_t *);
