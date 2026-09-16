// SPDX-License-Identifier: MIT
// Reconstructed top-level DRC initializer (stock package 0x470c4..0x4728c).
#include <stdint.h>
#include <stddef.h>

struct drc_header {
    uint32_t sample_rate, frame_count;
    uint32_t reserved8, reserved12, reserved16, reserved20;
    void *stage1, *stage2, *stage3, *stage4;
};
_Static_assert(sizeof(struct drc_header) == 40, "stock DRC header");

extern void *open_cfw_gx8002_memset(void *, int, unsigned);
extern void *open_cfw_gx8002_drc_stage1_initialize(void *, float,float,float,float,float,float);
extern void *open_cfw_gx8002_drc_stage2_initialize(void *, float,float,float,float,float,float,float);
extern void *open_cfw_gx8002_drc_stage3_initialize(void *, float,float,float,float,float,float,float);
extern void *open_cfw_gx8002_drc_stage4_initialize(void *, float,float,float,float,float);
extern void open_cfw_gx8002_drc_stage4_set_gain(void *, float);

struct drc_parameters {
    float p_fb8,p_fbc,p_fc0,p_fc4,p_fc8,p_fcc,p_fd0,p_fd4,p_fd8,p_fdc,p_fe0,
          p_fe4,p_fe8,p_fec,p_ff0,p_ff4,p_ff8,p_ffc,p_17000,p_17004,p_17008;
};
__attribute__((section(".drc_parameters")))
volatile struct drc_parameters open_cfw_gx8002_drc_parameters = {
    .p_fb8=.05f, .p_fbc=5.f, .p_fc0=15.f, .p_fc4=20.f, .p_fc8=.2f,
    .p_fcc=-36.5f, .p_fd0=.01f, .p_fd4=.01f, .p_fd8=5.f, .p_fdc=40.f,
    .p_fe0=.02f, .p_fe4=-40.f, .p_fe8=.005f, .p_fec=5.f, .p_ff0=.1f,
    .p_ff4=-15.f, .p_ff8=.01f, .p_ffc=-10.f, .p_17000=.005f,
    .p_17004=.02f, .p_17008=-50.f
};
__attribute__((section(".drc_stage1_control")))
volatile uint32_t open_cfw_gx8002_drc_stage1_control_bits;

__attribute__((section(".drc_stage1_size")))
unsigned open_cfw_gx8002_drc_stage1_size(void *unused, unsigned include) { (void)unused; return include ? 48u : 0u; }
__attribute__((section(".drc_stage2_size")))
unsigned open_cfw_gx8002_drc_stage2_size(void *unused, unsigned include) { (void)unused; return include ? 52u : 0u; }
__attribute__((section(".drc_stage3_size")))
unsigned open_cfw_gx8002_drc_stage3_size(void *unused, unsigned include) { (void)unused; return include ? 64u : 0u; }

__attribute__((section(".drc_initialize")))
struct drc_header *open_cfw_gx8002_drc_initialize(uint32_t sample_rate, uint32_t frame_count,
                                                   struct drc_header *memory) {
    volatile struct drc_header *h = memory;
    open_cfw_gx8002_memset(memory, 0, 40);
    if (!h) return memory;
    h->sample_rate = sample_rate;
    h->frame_count = frame_count;
    h->reserved8 = h->reserved12 = h->reserved16 = h->reserved20 = 0;
    uint8_t *cursor = (uint8_t *)memory + 40;
    h->stage1 = open_cfw_gx8002_drc_stage1_initialize(cursor, -15.f, 5.f, .005f, .1f,
                                                       (float)open_cfw_gx8002_drc_stage1_control_bits,
                                                       (float)h->sample_rate);
    cursor += open_cfw_gx8002_drc_stage1_size(h->stage1, 2);
    h->stage2 = open_cfw_gx8002_drc_stage2_initialize(cursor, .05f, .2f, 5.f, 20.f, -36.5f,
                                                       15.f, (float)h->sample_rate);
    cursor += open_cfw_gx8002_drc_stage2_size(h->stage2, 2);
    h->stage3 = open_cfw_gx8002_drc_stage3_initialize(cursor, .01f, .01f, .02f, 5.f, 40.f,
                                                       -40.f, (float)h->sample_rate);
    cursor += open_cfw_gx8002_drc_stage3_size(h->stage3, 2);
    h->stage4 = open_cfw_gx8002_drc_stage4_initialize(cursor, .005f, .02f, .01f, -50.f,
                                                       (float)h->sample_rate);
    open_cfw_gx8002_drc_stage4_set_gain(h->stage4, -10.f);
    return memory;
}
