/* SPDX-License-Identifier: MIT */
/* Exact observed accesses, including the unusual absolute read addresses.
 * Their hardware role remains unqualified; do not substitute MMIO-base offsets.
 */
typedef __UINTPTR_TYPE__ uintptr_t;
struct open_cfw_dw_spi_irq_context {
    unsigned int reserved;
    volatile unsigned int *registers;
};
int open_cfw_gx8002_dw_spi_irq(int irq, void *data)
{
    (void)irq;
    volatile struct open_cfw_dw_spi_irq_context *context = data;
    volatile unsigned int *registers = context->registers;
    unsigned int status = registers[12];
    if (status & 2u)
        (void)*(volatile unsigned int *)(uintptr_t)0x38u;
    if (status & 8u)
        (void)*(volatile unsigned int *)(uintptr_t)0x3cu;
    return 0;
}
