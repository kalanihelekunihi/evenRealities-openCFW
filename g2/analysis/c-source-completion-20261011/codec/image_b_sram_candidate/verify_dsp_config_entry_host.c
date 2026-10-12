#include <assert.h>
#include <stdint.h>
#include <stdio.h>
volatile uint32_t gx8002_image_b_dsp_config_2002d7a4[4];
extern uint32_t gx8002_image_b_dsp_config_copy_1000deb4(const uint32_t *);
extern uint32_t gx8002_image_b_dsp_transform_entry_1000de94(const void *, void *, uint32_t);
static const void *seen_context;static void *seen_samples;static uint32_t seen_phase;static unsigned calls;
uint32_t gx8002_image_b_dsp_transform_1000d2a4(const void *context,void *samples,uint32_t phase){seen_context=context;seen_samples=samples;seen_phase=phase;calls++;return 0x87654321u;}
int main(void){uint32_t src[4]={1,2,3,4};assert(gx8002_image_b_dsp_config_copy_1000deb4(src)==0);for(int i=0;i<4;i++)assert(gx8002_image_b_dsp_config_2002d7a4[i]==src[i]);assert(gx8002_image_b_dsp_transform_entry_1000de94(src,&src[1],7)==0);assert(calls==1&&seen_context==src&&seen_samples==&src[1]&&seen_phase==7);puts("2/2 DSP config and forwarding fixtures");}
