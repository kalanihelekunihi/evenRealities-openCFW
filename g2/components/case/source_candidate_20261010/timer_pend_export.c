/* Export the independently compared deferred producer under the stock name.
 * The verified source file remains byte-for-byte unchanged.
 */
#define case_pend_from_isr xTimerPendFunctionCallFromISR
#include "../deferred_event_offline/deferred.c"
