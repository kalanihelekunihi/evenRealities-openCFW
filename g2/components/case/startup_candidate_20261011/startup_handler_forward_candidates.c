/* SPDX-License-Identifier: MIT
 * Four exact CASE vector forwarding bodies. Destination handlers retain
 * separate typed hardware/event contracts.
 */
#include <stdint.h>
extern void case_irq_child_4330(uint32_t state); /* stock 0x08004330 */
extern void case_irq_child_5a52(uint32_t state); /* stock 0x08005a52 */
extern void case_irq_child_5c90(uint32_t state); /* stock 0x08005c90 */
extern void case_irq_child_5f50(uint32_t state); /* stock 0x08005f50 */
void case_vector_irq_06c4(void){case_irq_child_4330(0x200008e4u);}
void case_vector_irq_6e08(void){case_irq_child_5a52(0x20000948u);}
void case_vector_irq_84b0(void){case_irq_child_5c90(0x20000f4cu);}
void case_vector_irq_8f98(void){case_irq_child_5f50(0x20000e24u);}
