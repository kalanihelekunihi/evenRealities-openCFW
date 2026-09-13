/* SPDX-License-Identifier: MIT */
/* Recovered from codec package 0x16744; SDK gx_pmu_ctrl.h defines the
 * command word's low four trim bits and enable bit. Unlike stock, initialize
 * all 27 reserved bits rather than passing uninitialized stack contents.
 * Experimental: reserved-bit hardware behavior has not been qualified.
 */
extern int gx_pmu_ctrl_set(unsigned command, const void *parameter);

int open_cfw_gx8002_digital_voltage(unsigned voltage)
{
    if (voltage == ~0u)
        return -1;
    {
        unsigned command_word = (voltage & 15u) | 16u;
        (void)gx_pmu_ctrl_set(8u, &command_word);
    }
    return 0;
}
