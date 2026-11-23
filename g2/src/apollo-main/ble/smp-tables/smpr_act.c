/* Pinned Cordio legacy responder SMP actions. */
#define smpCb audio_ble_smp_handler_state
/* Stock builds this unit with the G2 product trace cascade: smprActProcPairReq 0x5e38f8 emits
 * SMP_TRACE_ERR0("pScr already allocated") (elog line 98 = vendor line 98, file string 0x5e3d38).
 * This unit's profile has no WSF trace, so route that one macro through wsf_trace_g2.h here. */
#define G2_CORDIO_STOCK_FILE "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\smp\\smpr_act.c"
#include "wsf_types.h"
#include "wsf_trace.h"
#include "../../../../config-recovered/cordio/g2-config/wsf_trace_g2.h"
#undef SMP_TRACE_ERR0
#define SMP_TRACE_ERR0(msg) G2_WSF_TRACE("SMP", "ERR", msg)
#include "../../../../../third-party/local-vendor/sources/AmbiqSuite_R3.2.0/third_party/cordio/ble-host/sources/stack/smp/smpr_act.c"
