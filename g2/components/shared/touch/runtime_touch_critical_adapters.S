/*
 * SPDX-License-Identifier: Apache-2.0
 * Isolated namespaced adaptation of Infineon mtb-pdl-cat2
 * drivers/source/COMPONENT_CM0P/TOOLCHAIN_GCC_ARM/cy_syslib_gcc.S at commit
 * 35f1714623cfea682d5e285af80d50416b4c7bbc.
 */
.syntax unified
.thumb
.cpu cortex-m0plus

.global open_cfw_touch_enter_critical
.type open_cfw_touch_enter_critical, %function
.thumb_func
open_cfw_touch_enter_critical:
    mrs r0, primask
    cpsid i
    bx lr
.size open_cfw_touch_enter_critical, .-open_cfw_touch_enter_critical

.global open_cfw_touch_exit_critical
.type open_cfw_touch_exit_critical, %function
.thumb_func
open_cfw_touch_exit_critical:
    msr primask, r0
    bx lr
.size open_cfw_touch_exit_critical, .-open_cfw_touch_exit_critical
