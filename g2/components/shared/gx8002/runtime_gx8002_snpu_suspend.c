/* SPDX-License-Identifier: MIT */
/* Reconstructed stock SNPU suspend call/state sequence. SDK object relocation
 * names identify helpers; no binary code is used as firmware payload.
 * The incomplete layout below describes observed offsets only, not ownership
 * or understanding of the intervening state. Candidate pending qualification. */
#include <stdint.h>
#include <stddef.h>
struct open_cfw_gx8002_snpu_suspend_view {
    volatile uint32_t state;
    unsigned char unmodeled[0x5c0];
    void *volatile registers;
};
extern struct open_cfw_gx8002_snpu_suspend_view open_cfw_gx8002_snpu_state;
_Static_assert(offsetof(struct open_cfw_gx8002_snpu_suspend_view, registers) == 0x5c4, "SNPU register pointer offset");
extern int open_cfw_gx8002_npu_is_enabled(void *);
extern void open_cfw_gx8002_npu_disable(void *);
extern int open_cfw_gx8002_npu_all_idle(void *);
extern void gx_clock_set_module_snpu_enable(int);
int open_cfw_gx8002_snpu_suspend(void)
{
    void *registers = open_cfw_gx8002_snpu_state.registers;
    if (registers == NULL)
        return -1;
    if (open_cfw_gx8002_snpu_state.state == 2)
        return 0;
    if (open_cfw_gx8002_npu_is_enabled(registers)) {
        open_cfw_gx8002_npu_disable(open_cfw_gx8002_snpu_state.registers);
        while (!open_cfw_gx8002_npu_all_idle(open_cfw_gx8002_snpu_state.registers)) {
            /* Preserve stock's unbounded wait and live pointer reload. */
        }
    }
    gx_clock_set_module_snpu_enable(0);
    open_cfw_gx8002_snpu_state.state = 2;
    return 0;
}
