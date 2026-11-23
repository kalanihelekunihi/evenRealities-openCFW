/* Pinned Cordio secure-connection common SMP actions. */
#define smpCb audio_ble_smp_handler_state
/* Stock builds this unit with the Cordio byte-array traces on: SMP_TRACE_128/256 expand to
 * smpLogByteArray (stock 0x56d478, C smpLogByteArray_56d478); stock has 12 such calls in this
 * unit's range (BL scan of the stock image, 2026-11-22). The G2 flags leave WSF_TRACE_ENABLED
 * off, so force the two macros here; smp_sc_main.h's include guard keeps these definitions. */
#include <string.h>
#include "wsf_types.h"
#include "wsf_buf.h"
#include "wsf_msg.h"
#include "wsf_trace.h"
#include "util/bstream.h"
#include "util/calc128.h"
#include "util/wstr.h"
#include "smp_api.h"
#include "smp_main.h"
#include "smp_sc_main.h"
void smpLogByteArray_56d478(char *str, uint8_t *pArray, uint8_t len);
#undef SMP_TRACE_128
#undef SMP_TRACE_256
#define SMP_TRACE_128(msg, ptr) smpLogByteArray_56d478(msg, ptr, 16)
#define SMP_TRACE_256(msg, ptr) smpLogByteArray_56d478(msg, ptr, 32)
#include "../../../../../third-party/local-vendor/sources/AmbiqSuite_R3.2.0/third_party/cordio/ble-host/sources/stack/smp/smp_sc_act.c"
