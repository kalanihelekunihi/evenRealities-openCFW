/* SPDX-License-Identifier: MIT
 * Source-owned 256-word Boot vector table from locked f89a4c46.
 * Entries are typed handler symbols or reserved zero slots (indices left out
 * below); no native code bytes are embedded. External IRQ handlers remain
 * hardware-qualified.
 */
#include <stdint.h>

typedef void (*opencfw_boot_vector_t)(void);

extern void opencfw_boot_fault_loop(void);
extern void opencfw_boot_gpio_irq0(void);
extern void opencfw_boot_gpio_irq1(void);
extern void opencfw_boot_gpio_irq2(void);
extern void opencfw_boot_iom4_irq_dispatch(void);
extern void opencfw_boot_mspi_irq(void);
extern void opencfw_boot_nmi_loop(void);
extern void opencfw_boot_pendsv_entry(void);
extern void opencfw_boot_reserved_loop(void);
extern void opencfw_boot_reset_entry(void);
extern void opencfw_boot_spot_timer_irq(void);
extern void opencfw_boot_stimer_irq(void);
extern void opencfw_boot_svc_entry(void);
extern void opencfw_boot_systick_entry(void);
extern void opencfw_boot_uart_irq1(void);
extern void opencfw_boot_uart_irq2(void);
extern void opencfw_boot_uart_irq3(void);

__attribute__((section(".boot_vectors"), used, aligned(4)))
const opencfw_boot_vector_t opencfw_boot_vectors[256] = {
    [0] = (opencfw_boot_vector_t)(uintptr_t)0x2007fb00u, /* initial MSP */
    [1] = opencfw_boot_reset_entry,
    [2] = opencfw_boot_nmi_loop,
    [3] = opencfw_boot_fault_loop,
    [4] = opencfw_boot_fault_loop,
    [5] = opencfw_boot_fault_loop,
    [6] = opencfw_boot_fault_loop,
    [7] = opencfw_boot_fault_loop,
    [11] = opencfw_boot_svc_entry,
    [12] = opencfw_boot_reserved_loop,
    [14] = opencfw_boot_pendsv_entry,
    [15] = opencfw_boot_systick_entry,
    [16 ... 25] = opencfw_boot_reserved_loop,
    [26] = opencfw_boot_iom4_irq_dispatch,
    [27 ... 31] = opencfw_boot_reserved_loop,
    [32] = opencfw_boot_uart_irq1,
    [33] = opencfw_boot_uart_irq2,
    [34] = opencfw_boot_uart_irq3,
    [35 ... 36] = opencfw_boot_reserved_loop,
    [37] = opencfw_boot_mspi_irq,
    [38 ... 47] = opencfw_boot_reserved_loop,
    [48] = opencfw_boot_stimer_irq,
    [49 ... 71] = opencfw_boot_reserved_loop,
    [72] = opencfw_boot_gpio_irq0,
    [73] = opencfw_boot_gpio_irq1,
    [74] = opencfw_boot_gpio_irq2,
    [75 ... 97] = opencfw_boot_reserved_loop,
    [98] = opencfw_boot_spot_timer_irq,
    [99 ... 150] = opencfw_boot_reserved_loop,
};
