/* SPDX-License-Identifier: MIT
 * Native CASE 0x08003656: USB reset power-management command wrapper.
 */
#include <stdint.h>
extern uint32_t case_init_pmic_write(uint32_t register_id,uint32_t value);
void case_boot_usb_reset_gls_box(void)
{
    (void)case_init_pmic_write(0xa2u,1u);
}
