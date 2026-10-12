#include <assert.h>
#include <stdint.h>
#include <stdio.h>
extern uint32_t opencfw_em9305_init_transition_report_316908_body(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint8_t*);
static unsigned value;
uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t p){uint8_t*b=(uint8_t*)p;assert(b[0]==0&&b[1]==0&&b[2]==5&&b[3]==value&&b[4]==value&&b[9]==(uint8_t)(value+1)&&b[35]==(uint8_t)(value+2));unsigned low=0x12340000|value;for(unsigned j=0;j<4;j++)assert(b[10+j]==(uint8_t)(low>>(j*8)));assert(b[14]==0xcd&&b[15]==0xab);assert(b[36]==255&&b[37]==255&&b[38]==0xa5&&b[39]==0x5a);for(unsigned j=16;j<35;j++)assert(b[j]==0);return 0x456;}
int main(void){for(unsigned n=0;n<256;n++){value=n;uint8_t frame[40];for(unsigned j=0;j<40;j++)frame[j]=0xcc;frame[38]=0xa5;frame[39]=0x5a;assert(opencfw_em9305_init_transition_report_316908_body(n+2,n,n+1,0x12340000|n,0xabcd,frame)==0x456);}puts("PASS256 report-frame paths with actual selected fill/serializer");}
