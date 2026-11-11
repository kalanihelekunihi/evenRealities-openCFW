/* These SDK users share the recovered multi-range iterator implementation.
 * Descriptor and cursor layout must agree even when compiled by Clang/GCC. */
#include "section_legacy_abi.h"
_Static_assert(NRF_SDH_REQ_OBSERVER_PRIO_LEVELS == 2 &&
               NRF_SDH_STATE_OBSERVER_PRIO_LEVELS == 2 &&
               NRF_SDH_STACK_OBSERVER_PRIO_LEVELS == 2 &&
               NRF_SDH_SOC_OBSERVER_PRIO_LEVELS == 2,
               "configured SoftDevice observer priority ranges");
/* Three is the current SDK candidate configuration, not a stock inventory claim. */
_Static_assert(NRF_PWR_MGMT_CONFIG_HANDLER_PRIORITY_COUNT == 3,
               "configured power observer priority ranges");
