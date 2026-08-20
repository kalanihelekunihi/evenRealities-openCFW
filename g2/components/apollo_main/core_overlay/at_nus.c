/* Clean-room reconstruction of the pathless stock AT^NUS command handler. */

#include <stdint.h>

#ifndef OPEN_CFW_AT_NUS_RESPONSE_ADDRESS
#define OPEN_CFW_AT_NUS_RESPONSE_ADDRESS 0x0078a370u
#endif
#ifndef OPEN_CFW_AT_NUS_OUTPUT
void open_cfw_retained_at_nus_output(const char *response);
#define OPEN_CFW_AT_NUS_OUTPUT(response) \
    open_cfw_retained_at_nus_output((response))
#endif

#define OPEN_CFW_AT_NUS_RESPONSE \
    ((const char *)(uintptr_t)OPEN_CFW_AT_NUS_RESPONSE_ADDRESS)

int open_cfw_at_nus_handler(void)
{
    OPEN_CFW_AT_NUS_OUTPUT(OPEN_CFW_AT_NUS_RESPONSE);
    return 1;
}
