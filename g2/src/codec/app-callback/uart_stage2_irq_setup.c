/* SPDX-License-Identifier: MIT
 * Stage-2 VIC registration 0x100030cc/0x100030e8 and CPU interrupt
 * save/restore 0x10003110/0x1000311c. Native instruction bytes for
 * the latter are mfcr r0,cr<0,0>; psrclr ie and mtcr r0,cr<0,0>.
 */
#include <stdint.h>

/* Stock 0x100030CC (csi_vic_enable_irq) */
void gx8002_uart_stage2_vic_enable_30cc(uint32_t irq)
{
    volatile uint32_t *const enable =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xe000e100);
    enable[(irq & 0x3fu) >> 5] = 1u << (irq & 31u);
}

void gx8002_uart_stage2_irq_register_30e8(uint32_t irq,
                                            uintptr_t callback,
                                            uintptr_t context)
{
    if (irq >= 32u || callback == 0) return;
    volatile uint32_t *const slots =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2000984c);
    slots[irq * 2u] = (uint32_t)callback;
    slots[irq * 2u + 1u] = (uint32_t)context;
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0xe000e100) = 1u << irq;
}

__attribute__((naked)) uint32_t gx8002_uart_stage2_irq_save_3110(void)
{
    __asm__ volatile("mfcr r0, cr<0, 0>\n"
                     "psrclr ie\n"
                     "jmp r15\n");
}

__attribute__((naked)) void gx8002_uart_stage2_irq_restore_311c(
    uint32_t state __attribute__((unused)))
{
    __asm__ volatile("mtcr r0, cr<0, 0>\n"
                     "jmp r15\n");
}

/* The native branch to 0x10003024 retains original r1/r2 at the call.
 * Disassembly at 0x10002f80-82 sets only r0 to the descriptor address.
 */
extern uint32_t gx8002_uart_stage2_uart_irq_setup_3024(
    volatile uint32_t *descriptor, uint32_t buffer, uint32_t transfer_bytes);

uint32_t gx8002_uart_stage2_uart_start_2f34(uint32_t port,
                                               uint32_t buffer,
                                               uint32_t transfer_bytes,
                                               uint32_t completion_callback,
                                               uint32_t callback_arg)
{
    volatile uint32_t *const descriptor =
        (volatile uint32_t *)(uintptr_t)
        (UINT32_C(0x2000908c) + (port << 7));
    if (buffer == 0 || completion_callback == 0) return UINT32_MAX;
    descriptor[0x58 / 4] = completion_callback;
    descriptor[0x40 / 4] = 2;
    descriptor[0x60 / 4] = buffer;
    descriptor[0x64 / 4] = transfer_bytes;
    descriptor[0x5c / 4] = callback_arg;
    descriptor[0x68 / 4] = UINT32_MAX;
    volatile uint32_t *const uart =
        (volatile uint32_t *)(uintptr_t)descriptor[1];
    if (descriptor[0x2c / 4] != 0) {
        uart[0xa8 / 4] = 1;
        return gx8002_uart_stage2_uart_irq_setup_3024(descriptor,
                                                         buffer, transfer_bytes);
    }
    uint32_t saved = gx8002_uart_stage2_irq_save_3110();
    uart[1] = uart[1] | 1u;
    gx8002_uart_stage2_irq_restore_311c(saved);
    return 0;
}
