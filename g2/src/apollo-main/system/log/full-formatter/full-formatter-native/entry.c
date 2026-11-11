/* Main 0x481836 candidate: adapted from pinned IAR Bootloader source;
 * identical 1270-instruction core topology except 23 relocated BL sites. */
/* IAR formatter entry: a 192-byte scratch frame on the stack (digit buffers
 * and record at fixed offsets, see engine.c) handed to the core. */
#include "engine.h"
int32_t g2_main_iar_format_core(g2_main_format_put callback,void *context,const char *format,uint32_t **cursor,unsigned mode,uint8_t *frame);
int32_t g2_iar_general_format(g2_main_format_put put,void *context,const char *format,uint32_t **cursor,unsigned mode){
 uint8_t frame[192] __attribute__((aligned(8)));
 return g2_main_iar_format_core(put,context,format,cursor,mode,frame);
}
