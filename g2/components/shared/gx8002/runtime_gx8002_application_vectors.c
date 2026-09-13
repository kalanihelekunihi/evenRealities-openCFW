/* SPDX-License-Identifier: MIT
 * Application SRAM vector layout: reset, 31 core exceptions, 32 IRQs.
 * Targets retain their independently reconstructed entry-point ownership.
 */
typedef void (*handler)(void);
extern void open_cfw_gx8002_application_reset(void);
extern void open_cfw_gx8002_exception_entry(void);
extern void open_cfw_gx8002_irq_entry(void);
const handler open_cfw_gx8002_application_vectors[64] = {
    [0] = open_cfw_gx8002_application_reset,
    [1 ... 31] = open_cfw_gx8002_exception_entry,
    [32 ... 63] = open_cfw_gx8002_irq_entry,
};
_Static_assert(sizeof(open_cfw_gx8002_application_vectors) == 256, "vector ABI");
