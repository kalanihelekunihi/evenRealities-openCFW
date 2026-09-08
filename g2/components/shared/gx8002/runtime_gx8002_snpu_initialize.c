/* SPDX-License-Identifier: MIT */
/* Candidate caller recovery. External view describes observed offsets only;
 * unmodeled fields are not understood or source-owned state. */
#include <stdint.h>
#include <stddef.h>
struct open_cfw_snpu_initialize_view {
    volatile uint32_t state;
    unsigned char unmodeled_004[0x5ac];
    volatile uint32_t field_5b0;
    volatile uint32_t field_5b4;
    unsigned char unmodeled_5b8[12];
    void *volatile registers;
    void *volatile reset_registers;
    void *volatile field_5cc;
};
extern struct open_cfw_snpu_initialize_view open_cfw_gx8002_snpu_initialize_state;
_Static_assert(offsetof(struct open_cfw_snpu_initialize_view, registers)==0x5c4,"register offset");
_Static_assert(offsetof(struct open_cfw_snpu_initialize_view, field_5b4)==0x5b4,"state offset");
extern void open_cfw_gx8002_snpu_device_init(void *);
extern void open_cfw_gx8002_snpu_tcb_init(void);
typedef int (*open_cfw_snpu_irq_handler)(int,void *);
extern void open_cfw_gx8002_snpu_request_irq(open_cfw_snpu_irq_handler,void *);
extern int open_cfw_gx8002_snpu_isr(int,void *);
int open_cfw_gx8002_snpu_initialize(void)
{
    open_cfw_gx8002_snpu_device_init((void *)(uintptr_t)UINT32_C(0xa0c00000));
    open_cfw_gx8002_snpu_initialize_state.registers=(void *)(uintptr_t)UINT32_C(0xa0c00000);
    open_cfw_gx8002_snpu_initialize_state.reset_registers=(void *)(uintptr_t)UINT32_C(0xa0300000);
    open_cfw_gx8002_snpu_initialize_state.field_5cc=(void *)(uintptr_t)UINT32_C(0xa0c00190);
    open_cfw_gx8002_snpu_initialize_state.field_5b4=0;
    open_cfw_gx8002_snpu_initialize_state.field_5b0=0;
    open_cfw_gx8002_snpu_tcb_init();
    open_cfw_gx8002_snpu_request_irq(open_cfw_gx8002_snpu_isr,NULL);
    open_cfw_gx8002_snpu_initialize_state.state=2;
    return 0;
}
