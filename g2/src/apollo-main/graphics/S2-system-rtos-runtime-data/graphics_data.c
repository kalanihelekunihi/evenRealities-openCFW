/* NemaGFX platform HAL state used by graphics/u-03/nema_hal_gpu_irq.c
 * (product HAL code; the NemaGFX library itself is licence-blocked and not
 * integrated). Zero-initialised. */
#include <stdint.h>

void *volatile g2_nema_irq_semaphore;                /* RAM 0x20074814 binary semaphore */
void (*volatile g2_nema_irq_callback)(uint32_t cl_id); /* RAM 0x20074818 completion callback */
