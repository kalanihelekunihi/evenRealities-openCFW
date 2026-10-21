/* SPDX-License-Identifier: MIT
 * Reconstructed instructions at stock 0x41B8EC..0x41B8F4.
 * Callable only in offline fixture until hardware execution authorized.
 */
.syntax unified
.thumb
.text
.global opencfw_boot_control_critical_save
.type opencfw_boot_control_critical_save,%function
.thumb_func
opencfw_boot_control_critical_save:
    mrs r0, primask
    cpsid i
    bx lr
.size opencfw_boot_control_critical_save, .-opencfw_boot_control_critical_save
