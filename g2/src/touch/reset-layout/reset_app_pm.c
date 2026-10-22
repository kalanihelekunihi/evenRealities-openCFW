/* SPDX-License-Identifier: MIT
 * Native application PM descriptor RAM200004cc, ROMb598; native callback3620
 * is literally MOVS r0,#0; BX lr. Its parameters are zeroed RAM200009c0.
 * Threshold RAM200004e8 is read as a halfword by deferred processing and
 * written as a halfword by command7. The next two padding bytes remain open.
 */
#include "../pm-callbacks/callbacks.h"
#include <stddef.h>
/* Stock 0x00003620 (not in touch.tsv: application PM callback) */
__attribute__((noinline)) uint32_t touch_app_pm_callback(touch_pm_params *params,uint32_t mode)
{
    (void)params;(void)mode;return 0;
}
touch_pm_params touch_app_pm_params
    __attribute__((section(".touch_bss.app_pm_params"),used));
touch_pm_callback touch_reset_app_pm_descriptor
    __attribute__((section(".touch_init.app_pm_descriptor"),used)) = {
    .callback=touch_app_pm_callback,.type=1u,.skip=0u,
    .params=&touch_app_pm_params,.prev=NULL,.next=NULL,.order=2u,
};
uint16_t touch_application_threshold
    __attribute__((section(".touch_init.app_threshold"),used))=1000u;
_Static_assert(sizeof(touch_pm_callback)==28,"PM descriptor ABI");
_Static_assert(sizeof(touch_pm_params)==8,"PM params ABI");
