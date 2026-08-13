/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 buck/LDO override initialization adaptation from
 * AmbiqSuite SDK 5.1.0. Reviewed stock and SDK evidence is recorded in
 * EVIDENCE.md.
 */

typedef __UINTPTR_TYPE__ open_cfw_pwrctrl_buck_ldo_uintptr;

#define OPEN_CFW_PWRCTRL_BUCK_LDO_VRCTRL 0x40020060U

#define OPEN_CFW_PWRCTRL_BUCK_LDO_SIMOBUCK_OVER 0x00010000U
#define OPEN_CFW_PWRCTRL_BUCK_LDO_SIMOBUCK_PDNB 0x00020000U
#define OPEN_CFW_PWRCTRL_BUCK_LDO_SIMOBUCK_RSTB 0x00040000U
#define OPEN_CFW_PWRCTRL_BUCK_LDO_SIMOBUCK_ACTIVE 0x00080000U

#define OPEN_CFW_PWRCTRL_BUCK_LDO_CORE_OVER 0x00000001U
#define OPEN_CFW_PWRCTRL_BUCK_LDO_CORE_ACTIVE_GROUP 0x0000000EU
#define OPEN_CFW_PWRCTRL_BUCK_LDO_CORE_COLD_START 0x00000010U

#define OPEN_CFW_PWRCTRL_BUCK_LDO_MEM_OVER 0x00000020U
#define OPEN_CFW_PWRCTRL_BUCK_LDO_MEM_ACTIVE_GROUP 0x000001C0U
#define OPEN_CFW_PWRCTRL_BUCK_LDO_MEM_COLD_START 0x00000200U

#ifndef OPEN_CFW_PWRCTRL_BUCK_LDO_READ32
#define OPEN_CFW_PWRCTRL_BUCK_LDO_READ32(address) \
    (*(const volatile unsigned int *)( \
        open_cfw_pwrctrl_buck_ldo_uintptr)(address))
#endif

#ifndef OPEN_CFW_PWRCTRL_BUCK_LDO_WRITE32
#define OPEN_CFW_PWRCTRL_BUCK_LDO_WRITE32(address, value) \
    (*(volatile unsigned int *)( \
        open_cfw_pwrctrl_buck_ldo_uintptr)(address) = (value))
#endif

static void
open_cfw_pwrctrl_buck_ldo_update(
    unsigned int set_mask,
    unsigned int clear_mask
)
{
    unsigned int value = OPEN_CFW_PWRCTRL_BUCK_LDO_READ32(
        OPEN_CFW_PWRCTRL_BUCK_LDO_VRCTRL
    );

    value = (value | set_mask) & ~clear_mask;
    OPEN_CFW_PWRCTRL_BUCK_LDO_WRITE32(
        OPEN_CFW_PWRCTRL_BUCK_LDO_VRCTRL,
        value
    );
}

/*
 * ABI-compatible source replacement for AmbiqSuite's private
 * buck_ldo_override_init at 0x0047FE12...0x0047FE67.
 */
__attribute__((used, noinline))
void open_cfw_pwrctrl_buck_ldo_override_init(void)
{
    /*
     * SIMOBUCKOVER is deliberately written after the three SIMOBUCK state
     * fields. The override does not take effect until deep sleep.
     */
    open_cfw_pwrctrl_buck_ldo_update(
        OPEN_CFW_PWRCTRL_BUCK_LDO_SIMOBUCK_PDNB,
        0U
    );
    open_cfw_pwrctrl_buck_ldo_update(
        OPEN_CFW_PWRCTRL_BUCK_LDO_SIMOBUCK_RSTB,
        0U
    );
    open_cfw_pwrctrl_buck_ldo_update(
        OPEN_CFW_PWRCTRL_BUCK_LDO_SIMOBUCK_ACTIVE,
        0U
    );
    open_cfw_pwrctrl_buck_ldo_update(
        OPEN_CFW_PWRCTRL_BUCK_LDO_SIMOBUCK_OVER,
        0U
    );

    /*
     * Apollo510 runs CoreLDO and MemLDO in parallel with SIMOBUCK. For each
     * LDO, disable cold start, establish active/early/power-up state, and set
     * its override bit last.
     */
    open_cfw_pwrctrl_buck_ldo_update(
        0U,
        OPEN_CFW_PWRCTRL_BUCK_LDO_CORE_COLD_START
    );
    open_cfw_pwrctrl_buck_ldo_update(
        OPEN_CFW_PWRCTRL_BUCK_LDO_CORE_ACTIVE_GROUP,
        0U
    );
    open_cfw_pwrctrl_buck_ldo_update(
        OPEN_CFW_PWRCTRL_BUCK_LDO_CORE_OVER,
        0U
    );

    open_cfw_pwrctrl_buck_ldo_update(
        0U,
        OPEN_CFW_PWRCTRL_BUCK_LDO_MEM_COLD_START
    );
    open_cfw_pwrctrl_buck_ldo_update(
        OPEN_CFW_PWRCTRL_BUCK_LDO_MEM_ACTIVE_GROUP,
        0U
    );
    open_cfw_pwrctrl_buck_ldo_update(
        OPEN_CFW_PWRCTRL_BUCK_LDO_MEM_OVER,
        0U
    );
}

#undef OPEN_CFW_PWRCTRL_BUCK_LDO_WRITE32
#undef OPEN_CFW_PWRCTRL_BUCK_LDO_READ32
