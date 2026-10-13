#include <stdint.h>
/* Native514e0c..514e50: sparse path bounds reset, no NULL guard in native. */
void audio_uart_nema_vg_path_bounds_reset_514e0c(void *path) {
 volatile uint32_t *p=path;
 p[4]=0x477fff00u;p[5]=0x477fff00u;p[6]=0xc77fff00u;p[7]=0xc77fff00u;
 p[20]=0u;p[21]=0u;p[9]=0u;p[8]=0u;p[11]=0u;p[10]=0u;
 p[13]=0u;p[12]=0u;p[15]=0u;p[14]=0u;p[22]=0u;p[23]=0u;
 p[16]=0x477fff00u;p[17]=0x477fff00u;p[18]=0xc77fff00u;p[19]=0xc77fff00u;
}
