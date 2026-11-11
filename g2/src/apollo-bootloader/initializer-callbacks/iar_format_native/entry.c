/* IAR formatter entry: a 192-byte scratch frame on the stack (digit buffers
 * and record at fixed offsets, see engine.c) handed to the core. */
#include "engine.h"
int32_t opencfw_iar_format_core(opencfw_format_put callback,void *context,const char *format,uint32_t **cursor,unsigned mode,uint8_t *frame);
int32_t opencfw_iar_format_engine(opencfw_format_put put,void *context,const char *format,uint32_t **cursor,unsigned mode){
 uint8_t frame[192] __attribute__((aligned(8)));
 return opencfw_iar_format_core(put,context,format,cursor,mode,frame);
}

/* Stock entry names that branch straight to the provider above. */
__typeof__(opencfw_iar_format_engine) opencfw_boot_format_engine __attribute__((alias("opencfw_iar_format_engine")));
