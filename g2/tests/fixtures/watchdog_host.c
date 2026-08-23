#include "watchdog_host.h"

unsigned int open_cfw_test_watchdog_selector_calls;
unsigned int open_cfw_test_watchdog_selector_argument;
unsigned int open_cfw_test_watchdog_provider_calls;
unsigned char open_cfw_test_watchdog_selector_value;

void open_cfw_test_watchdog_reset(unsigned char selector_value)
{
    open_cfw_test_watchdog_selector_calls = 0u;
    open_cfw_test_watchdog_selector_argument = 0xffffffffu;
    open_cfw_test_watchdog_provider_calls = 0u;
    open_cfw_test_watchdog_selector_value = selector_value;
}

const unsigned char *open_cfw_test_watchdog_selector(unsigned int selector)
{
    ++open_cfw_test_watchdog_selector_calls;
    open_cfw_test_watchdog_selector_argument = selector;
    return &open_cfw_test_watchdog_selector_value;
}

void open_cfw_test_watchdog_enable_provider(void)
{
    ++open_cfw_test_watchdog_provider_calls;
}
