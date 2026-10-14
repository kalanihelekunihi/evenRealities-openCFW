/* Target ABI check only; this object does not define hciCb or product RAM. */
#include <stddef.h>
#include "wsf_types.h"
#include "hci_main.h"
_Static_assert(sizeof(wsfQueue_t) == 8u, "rxQueue size");
_Static_assert(offsetof(hciCb_t, rxQueue) == 0u, "rxQueue");
_Static_assert(offsetof(hciCb_t, evtCback) == 8u, "event callback");
_Static_assert(offsetof(hciCb_t, secCback) == 12u, "security callback");
_Static_assert(offsetof(hciCb_t, aclCback) == 16u, "ACL callback");
_Static_assert(offsetof(hciCb_t, flowCback) == 20u, "flow callback");
_Static_assert(offsetof(hciCb_t, isoCback) == 24u, "ISO callback");
_Static_assert(offsetof(hciCb_t, isoFlowCback) == 28u, "ISO flow callback");
_Static_assert(offsetof(hciCb_t, handlerId) == 32u, "handler ID");
_Static_assert(offsetof(hciCb_t, resetting) == 33u, "reset flag");
_Static_assert(sizeof(hciCb_t) == 36u, "control block extent");
