/* Independent integer postprocessing7c4e..7c9a. FIFO input is external. */
#include <stdint.h>
#include "max_raw.h"
uint32_t touch_saturated_max(uint32_t fifo,uint32_t scan_ctl,uint32_t clock_source,uint32_t method,uint32_t chop){
 uint32_t divider=(scan_ctl>>16)&0xfff,kref=divider+1;
 uint32_t epi=((clock_source&3)==2?96u:2u)*((divider+4)>>2);
 if(((clock_source&3)==2 && (method==1 || method==10)) || !(kref&1))epi--;
 uint32_t value=(fifo-epi)*chop;
 uint32_t result=value<65536?value:65535;
 return result?result:1;
}
/* Recovered wrapper5cac: the injected scan adapter is an explicit external
 * dependency; neither analog measurement nor scan failure values invented. */
uint32_t touch_max_raw_init(uint32_t id,uint8_t *context,touch_saturated_scan scan){
 uint8_t *w=(uint8_t *)(*(uint32_t *)(context+12)+id*144u),*c=*(uint8_t **)w;
 if(!(c[35]&8))return 0;
 uint32_t value=0,status=scan(&value,id,*(uint16_t *)(w+128),0,context);
 *(uint16_t *)(c+4)=(uint16_t)(value<65536?value:65535);return status;
}
