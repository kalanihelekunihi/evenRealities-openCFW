/* SPDX-License-Identifier: MIT
 * Exact-address GPIO aliases. All four candidate call sites discard R0, so
 * their declarations use the selected void-return ABI. Physical pin behavior
 * remains a hardware validation boundary.
 */
#include "../glue/case_gpio_control_contract.h"

void case_binary_local_control_a(uint32_t enable){case_control_a(enable);}
void case_binary_local_control_b(uint32_t enable){case_control_b(enable);}
void case_binary_56_clear_a(uint32_t enable){case_control_a(enable);}
void case_binary_56_clear_b(uint32_t enable){case_control_b(enable);}
void case_legacy_gpio_bit4(uint32_t enable){case_control_b(enable);}
