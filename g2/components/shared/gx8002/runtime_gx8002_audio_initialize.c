/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <stddef.h>
#include <gx_audio_in/gx_audio_in_v2.h>
/* gx_irq.h signature, kept local because its legacy types.h conflicts
 * with this toolchain stdint.h (int32_t is int versus long). */
extern void gx_request_irq(int,int (*)(int,void *),void *);
extern void open_cfw_gx8002_platform_gate(uint32_t,uint32_t);
extern int open_cfw_gx8002_audio_reset(void);
extern void *memset(void *,int,size_t);
extern int open_cfw_gx8002_audio_irq(int,void *);
typedef struct {
    uint32_t input,output;
    GX_AUDIO_IN_CONFIG_CB config;
    GX_AUDIO_IN_RECORD_CB record;
    GX_AUDIO_IN_UPDATE_CB update;
    GX_AUDIO_IN_ENGVAD_CB engvad;
    GX_AUDIO_IN_FFTVAD_CB fftvad;
} audio_runtime;
extern volatile audio_runtime open_cfw_gx8002_audio_runtime;
_Static_assert(sizeof(audio_runtime)==28,"Audio state ABI");
_Static_assert(sizeof(GX_AUDIO_IN_CONFIG)==20,"Audio config ABI");
static inline void field(volatile uint32_t *reg,unsigned int bit,unsigned int value)
{
    uint32_t word=*reg;
    *reg=(word&~(1u<<bit))|((value&1u)<<bit);
}
/* Recovered package 0xdd70. Preserve initialization before null rejection,
 * callback publication order, and input/output snapshots after configuration. */
int open_cfw_gx8002_audio_initialize(GX_AUDIO_IN_CONFIG config)
{
    volatile audio_runtime *state=&open_cfw_gx8002_audio_runtime;
    volatile uint32_t *registers=(volatile uint32_t *)(uintptr_t)0xa0a00000u;
    open_cfw_gx8002_platform_gate(3,1);
    memset((void *)state,0,sizeof(*state));
    (void)open_cfw_gx8002_audio_reset();
    field(registers,31,1);
    field(registers,29,1);
    registers[0x10c/4]=0;
    if (!config.config_callback) return -1;
    state->config=config.config_callback;
    if (config.update_callback) state->update=config.update_callback;
    if (config.record_callback) state->record=config.record_callback;
    if (config.engvad_callback) state->engvad=config.engvad_callback;
    if (config.fftvad_callback) state->fftvad=config.fftvad_callback;
    (void)config.config_callback();
    (void)gx_request_irq(2,open_cfw_gx8002_audio_irq,0);
    if (config.record_callback) {
        uint32_t output=state->output;
        if (output&1) field(registers+0x100/4,0,1);
        if (output&2) field(registers+0x100/4,1,1);
        if (output&4) field(registers+0x100/4,2,1);
    }
    uint32_t input=state->input;
    if (input&1) {
        field(registers+0xc/4,9,1);
        field(registers,7,0);
    }
    if (input&2) {
        if ((registers[0x28/4]&15)<2) field(registers+0x28/4,9,1);
        if ((registers[0x2c/4]&15)<2) field(registers+0x2c/4,9,1);
        field(registers,15,0);
    }
    if (input&4) {
        if ((registers[0x48/4]&15)<8) field(registers+0x48/4,9,1);
        if ((registers[0x4c/4]&15)<8) field(registers+0x4c/4,9,1);
        field(registers+1,31,0);
    }
    return 0;
}
