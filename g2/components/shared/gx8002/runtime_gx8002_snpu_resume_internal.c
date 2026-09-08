/* SPDX-License-Identifier: MIT */
/* Recovered internal resume sequence. Only observed offsets are described;
 * the opaque gap is not source-owned driver state. */
#include <stdint.h>
#include <stddef.h>
struct open_cfw_snpu_resume_view {
    volatile uint32_t state;
    unsigned char unmodeled_004[0x5bc];
    volatile uint32_t field_5c0;
    void *volatile registers;
    void *volatile reset_registers;
    unsigned char unmodeled_5cc[4];
    volatile uint32_t field_5d0;
};
extern struct open_cfw_snpu_resume_view open_cfw_gx8002_snpu_resume_state;
_Static_assert(offsetof(struct open_cfw_snpu_resume_view, registers)==0x5c4,"register pointer offset");
_Static_assert(offsetof(struct open_cfw_snpu_resume_view, reset_registers)==0x5c8,"reset pointer offset");
_Static_assert(offsetof(struct open_cfw_snpu_resume_view, field_5d0)==0x5d0,"state field offset");
extern void gx_clock_set_module_snpu_enable(int);
extern int open_cfw_gx8002_npu_is_enabled(void *);
extern void open_cfw_gx8002_npu_disable(void *);
extern int open_cfw_gx8002_npu_all_idle(void *);
extern void open_cfw_gx8002_npu_reset(void *);
extern void open_cfw_gx8002_npu_regs_init(void);
int open_cfw_gx8002_snpu_resume_internal(void)
{
    open_cfw_gx8002_snpu_resume_state.state=0;
    open_cfw_gx8002_snpu_resume_state.field_5c0=0;
    open_cfw_gx8002_snpu_resume_state.field_5d0=0;
    gx_clock_set_module_snpu_enable(1);
    if (open_cfw_gx8002_npu_is_enabled(open_cfw_gx8002_snpu_resume_state.registers)) {
        open_cfw_gx8002_npu_disable(open_cfw_gx8002_snpu_resume_state.registers);
        while (!open_cfw_gx8002_npu_all_idle(open_cfw_gx8002_snpu_resume_state.registers)) {
            /* The original waits indefinitely and reloads the pointer. */
        }
    }
    open_cfw_gx8002_npu_reset(open_cfw_gx8002_snpu_resume_state.reset_registers);
    open_cfw_gx8002_npu_regs_init();
    return 0;
}
