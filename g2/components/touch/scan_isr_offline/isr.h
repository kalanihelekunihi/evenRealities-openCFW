#ifndef TOUCH_SCAN_ISR_OFFLINE_H
#define TOUCH_SCAN_ISR_OFFLINE_H
#include <stdint.h>
void touch_clear_busy(uint8_t *);
void touch_transfer_active(uint32_t,uint32_t,uint8_t *);
/* LP count must be nonzero; result buffer must hold slots*cycles u16. */
void touch_transfer_low_power(uint32_t,uint32_t,uint8_t *);
void touch_scan_slots(uint32_t,uint32_t,uint8_t *);
void touch_scan_isr(uint8_t *);
/* Additive offline binding replaces stock ISR metadata with native function.
 * Distinct addresses are compared as logical entry identities, never bytes. */
uint32_t touch_prepare_scan_isr_bound(uint8_t *);
void touch_interrupt_dispatch(uint32_t,uint8_t *);
void touch_msclp_interrupt(volatile uint32_t *,uint8_t *);
void touch_project_msclp_irq(void);
#endif
