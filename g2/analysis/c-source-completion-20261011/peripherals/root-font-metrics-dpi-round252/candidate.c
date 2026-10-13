#include <stdint.h>
/* Arithmetic contract native526ba4..526be4, not whole metrics function. */
void font_metrics_dpi_252(uint32_t *out,const uint32_t *request){
 int32_t dx=(int32_t)request[3],dy=(int32_t)request[4];
 out[0]=dx?(uint32_t)((int32_t)((uint32_t)dx*request[1]+36u)/72):request[1];
 out[1]=dy?(uint32_t)((int32_t)((uint32_t)dy*request[2]+36u)/72):request[2];
}
