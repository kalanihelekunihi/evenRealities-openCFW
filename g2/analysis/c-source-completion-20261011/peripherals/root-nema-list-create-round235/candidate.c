#include <stdint.h>
extern void audio_uart_nema_buffer_create_514070(uint32_t *,uint32_t,uint32_t);
/* Native514278..5142ee: buffer descriptor, signed capacity, full60byte list. */
void audio_uart_nema_cl_create_sized_514278(void *out,uint32_t bytes) {
 uint32_t descriptor[4];
 audio_uart_nema_buffer_create_514070(descriptor,0u,bytes);
 uint32_t row[15];
 row[0]=descriptor[0];row[1]=descriptor[1];row[2]=descriptor[2];row[3]=descriptor[3];
 row[4]=(uint32_t)(((int32_t)descriptor[0]/8)*2);
 row[5]=0;row[6]=0;row[7]=UINT32_MAX;
 row[8]=0;row[9]=0;row[10]=0;row[11]=0;row[12]=0;
 row[13]=UINT32_MAX;row[14]=UINT32_MAX;
 uint32_t *destination=out;
 for(uint32_t i=0;i<15;i++)destination[i]=row[i];
}
