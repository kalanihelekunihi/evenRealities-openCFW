/* SPDX-License-Identifier: MIT
 * Native CASE protocol command templates 0x08001d04 and 0x08001e4c.
 * The call sites set side/mode payload fields and calculate checksums.
 */
#include <stdint.h>
const uint8_t case_boot_transport_action_template[8]={
    0x13u,0u,0u,1u,0u,0u,0u,0u
};
const uint8_t case_policy_ota_probe_template[12]={
    0x5bu,0u,0u,5u,0u,0u,0u,0u,0u,0u,0u,0u
};
_Static_assert(sizeof(case_boot_transport_action_template)==8u,"action packet extent");
_Static_assert(sizeof(case_policy_ota_probe_template)==12u,"OTA packet extent");
