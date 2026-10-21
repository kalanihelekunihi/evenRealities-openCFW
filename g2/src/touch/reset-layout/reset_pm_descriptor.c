/* SPDX-License-Identifier: MIT
 * Reset-copied DeepSleep callback descriptor at SRAM 0x20000850.
 * The callback and descriptor field layout are independently reconstructed
 * in the Touch PM components; its params object lives in zeroed SRAM.
 */
#include "../pm-callbacks/callbacks.h"
#include "../ilo-pm/pm.h"
#include <stddef.h>
#include <stdint.h>
_Static_assert(sizeof(touch_pm_callback)==28,"PM descriptor ABI");
_Static_assert(offsetof(touch_pm_callback,order)==24,"PM order field");

touch_pm_callback touch_reset_ilo_pm_descriptor
    __attribute__((section(".touch_init.pm_descriptor"),used)) = {
    .callback=(uint32_t (*)(touch_pm_params *,uint32_t))touch_ilo_deep_sleep_callback,
    .type=1u,
    .skip=0u,
    .params=(touch_pm_params *)(uintptr_t)0x20000cccu,
    .prev=NULL,
    .next=NULL,
    .order=0xffu,
};
