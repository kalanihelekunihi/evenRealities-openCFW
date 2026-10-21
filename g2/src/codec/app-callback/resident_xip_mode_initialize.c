/* SPDX-License-Identifier: MIT
 * XIP 0x102085a4 mode initialization and source-owned typed replacements
 * for the two five-word descriptors at 0x1020b1c4/0x1020b204 and their
 * two-pointer selector at 0x1020b1bc. Final XIP placement is unresolved.
 */
#include <stdint.h>

extern uint32_t gx8002_xip_idle_initialize_10208634(uint32_t argument);
extern void gx8002_xip_idle_done_10208624(void);
extern void gx8002_xip_idle_tick_1020861c(void);
extern void gx8002_xip_idle_buffer_initialize_10208620(void);
extern uint32_t gx8002_xip_tws_initialize_10208670(uint32_t argument);
extern void gx8002_xip_tws_done_1020864c(void);
extern void gx8002_resident_tws_tick_26358(void);
extern void gx8002_xip_tws_buffer_initialize_10208644(void);

struct gx8002_xip_mode_descriptor {
    uint32_t id;
    uint32_t (*initialize)(uint32_t);
    void (*done)(void);
    void (*tick)(void);
    void (*buffer_initialize)(void);
};
_Static_assert(sizeof(struct gx8002_xip_mode_descriptor) == 20,
               "native mode descriptor ABI");

const struct gx8002_xip_mode_descriptor gx8002_xip_idle_descriptor = {
    0u, gx8002_xip_idle_initialize_10208634,
    gx8002_xip_idle_done_10208624, gx8002_xip_idle_tick_1020861c,
    gx8002_xip_idle_buffer_initialize_10208620,
};
const struct gx8002_xip_mode_descriptor gx8002_xip_tws_descriptor = {
    1u, gx8002_xip_tws_initialize_10208670,
    gx8002_xip_tws_done_1020864c, gx8002_resident_tws_tick_26358,
    gx8002_xip_tws_buffer_initialize_10208644,
};
const struct gx8002_xip_mode_descriptor *const gx8002_xip_mode_table[2] = {
    &gx8002_xip_idle_descriptor, &gx8002_xip_tws_descriptor,
};

uint32_t gx8002_xip_lvp_init_mode_102085a4(uint32_t requested)
{
    volatile uint32_t *const state =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002e6e4);
    state[0] = 1u;
    state[1] = 0u;
    if (requested == gx8002_xip_tws_descriptor.id) state[1] = 1u;
    /* All other inputs, including the idle ID, retain native slot zero. */
    /* Native reloads the selector after each indirect callback. */
    gx8002_xip_mode_table[state[1]]->buffer_initialize();
    (void)gx8002_xip_mode_table[state[1]]->initialize(0xffffu);
    return gx8002_xip_mode_table[state[1]]->id;
}
