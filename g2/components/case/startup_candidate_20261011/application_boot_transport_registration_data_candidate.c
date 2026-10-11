/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800d26c..0x0800d37f transport registration descriptors.
 * Field positions are read by native 0xaa48/0xa93c; names are protocol task
 * labels, expressed as strings rather than copied executable/image bytes.
 */
#include "application_boot_transport_registration_data_candidate.h"
_Static_assert(sizeof(TimerSpec)==16u,"timer descriptor extent");
_Static_assert(sizeof(WorkerSpec)==36u,"worker descriptor extent");
_Static_assert(sizeof(EventSpec)==36u,"event descriptor extent");
_Static_assert(sizeof(Registry)==0x114u,"registration block extent");

const Registry case_boot_transport_registration_storage={
    .timers={
        {"clearLedTimer",0u,0u,0u},
        {"startLedTimer",0u,0u,0u},
        {"showErrorLedTimer",0u,0u,0u},
        {"agingTimer",0u,0u,0u},
        {"setAgingStatusTimer",0u,0u,0u},
        {"powerOnTimer",0u,0u,0u},
    },
    .workers={
        {"pwrManagerTask",0u,0u,0u,0u,0x200u,12u,0u,0u},
        {"defaultTask",0u,0u,0u,0u,0x200u,9u,0u,0u},
        {"ledTask",0u,0u,0u,0u,0x200u,8u,0u,0u},
        {"glsDetectTask",0u,0u,0u,0u,0x200u,11u,0u,0u},
    },
    .event={"appEvent",0u,0u,0u,0x200u,1u,0u,3u,0u},
};
