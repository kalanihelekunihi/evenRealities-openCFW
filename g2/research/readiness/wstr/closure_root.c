#include <stdint.h>
#include "wstr.h"

volatile uint8_t open_cfw_wstr_sink[8];

__attribute__((used))
void open_cfw_wstr_closure_root(void)
{
    static const uint8_t source[8] = {0, 1, 2, 3, 4, 5, 6, 7};
    WStrReverseCpy((uint8_t *)open_cfw_wstr_sink, source, sizeof(source));
    WStrReverse((uint8_t *)open_cfw_wstr_sink, sizeof(open_cfw_wstr_sink));
}
