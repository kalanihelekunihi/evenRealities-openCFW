/* SPDX-License-Identifier: MIT
 * Four exact CASE vector forwarding bodies. Destination handlers retain
 * separate typed hardware/event contracts.
 */
#include <stdint.h>
extern void case_irq_child_4330(uint32_t state); /* stock 0x08004330 */
extern void case_irq_child_5a52(uint32_t state); /* stock 0x08005a52 */
extern void case_irq_child_5c90(uint32_t state); /* stock 0x08005c90 */
extern void case_irq_child_5f50(uint32_t state); /* stock 0x08005f50 */
/* Stock 0x080006C4 (case_forward_resource) */
void case_vector_irq_06c4(void){case_irq_child_4330(0x200008e4u);}
/* Stock 0x08006E08 (case_forward_resource) */
void case_vector_irq_6e08(void){case_irq_child_5a52(0x20000948u);}
/* Stock 0x080084B0 (case_forward_resource) */
void case_vector_irq_84b0(void){case_irq_child_5c90(0x20000f4cu);}
/* Stock 0x08008F98 (case_forward_resource) */
void case_vector_irq_8f98(void){case_irq_child_5f50(0x20000e24u);}
