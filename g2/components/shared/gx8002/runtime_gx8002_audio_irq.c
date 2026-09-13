/* SPDX-License-Identifier: MIT */
/* Recovered audio input IRQ, package17e5c..180e4. Not yet qualified.
 * SDK callback types; register access order follows stock, including the
 * bounded status polling and unconditional final FFT-VAD callback. */
#include <stdint.h>
#include <stddef.h>
#include <gx_audio_in/gx_audio_in_v2.h>
extern void *memset(void *,int,size_t);
typedef struct {
    uint32_t input,output;
    GX_AUDIO_IN_CONFIG_CB config;
    GX_AUDIO_IN_RECORD_CB record;
    GX_AUDIO_IN_UPDATE_CB update;
    GX_AUDIO_IN_ENGVAD_CB engvad;
    GX_AUDIO_IN_FFTVAD_CB fftvad;
} audio_runtime;
extern volatile audio_runtime open_cfw_gx8002_audio_runtime;
_Static_assert(sizeof(audio_runtime)==28,"audio runtime ABI");
#define REG(offset) (*(volatile uint32_t *)(uintptr_t)(0xa0a00000u+(offset)))
static inline unsigned pending(unsigned bit)
{
    return ((REG(0x100)>>bit)&1u) && ((REG(0x104)>>bit)&1u);
}
int open_cfw_gx8002_audio_irq(int irq,void *private_data)
{
    (void)irq;(void)private_data;
    volatile audio_runtime *state=&open_cfw_gx8002_audio_runtime;
    if (!(REG(0x104)&(1u<<24)))
        if (!(REG(0x104)&(1u<<24))) (void)REG(0x104);
    unsigned mask=0;
    if (pending(18)) { REG(0x104)=1u<<18;mask=1; }
    if (pending(19)) { mask|=2;REG(0x104)=1u<<19; }
    if (pending(20)) { mask|=4;REG(0x104)=1u<<20; }
    if (mask) { GX_AUDIO_IN_ENGVAD_CB cb=state->engvad;if(cb) (void)cb(mask); }
    unsigned addresses[3];memset(addresses,0,sizeof(addresses));
    mask=pending(0);addresses[0]=REG(0x124);
    if (pending(1)) mask|=2;
    addresses[1]=REG(0x148);
    if (pending(2)) mask|=4;
    addresses[2]=REG(0x168);
    if(mask) {
        GX_AUDIO_IN_RECORD_CB cb=state->record;if(cb) (void)cb(mask,addresses);
        if(mask&1) REG(0x104)=1;
        if(mask&2) REG(0x104)=2;
        if(mask&4) REG(0x104)=4;
    }
    memset(addresses,0,sizeof(addresses));mask=0;
    if(pending(3)) {addresses[0]=REG(0x128);mask=1;}
    if(pending(4)) {addresses[1]=REG(0x14c);mask|=2;}
    if(pending(5)) {addresses[2]=REG(0x16c);mask|=4;}
    if(mask) {
        GX_AUDIO_IN_UPDATE_CB cb=state->update;if(cb) (void)cb(mask,addresses);
        if(mask&1) REG(0x104)=8;
        if(mask&2) REG(0x104)=16;
        if(mask&4) REG(0x104)=32;
    }
    mask=0;
    if(pending(16)) {REG(0x104)=1u<<16;mask=1;}
    if(pending(17)) {mask|=2;REG(0x104)=1u<<17;}
    GX_AUDIO_IN_FFTVAD_CB cb=state->fftvad;if(cb) (void)cb(mask);
    return 0;
}
