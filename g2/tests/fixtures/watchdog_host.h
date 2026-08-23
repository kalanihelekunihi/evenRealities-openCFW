#ifndef OPEN_CFW_WATCHDOG_HOST_H
#define OPEN_CFW_WATCHDOG_HOST_H

extern unsigned int open_cfw_test_watchdog_selector_calls;
extern unsigned int open_cfw_test_watchdog_selector_argument;
extern unsigned int open_cfw_test_watchdog_provider_calls;
extern unsigned char open_cfw_test_watchdog_selector_value;

void open_cfw_test_watchdog_reset(unsigned char selector_value);
const unsigned char *open_cfw_test_watchdog_selector(unsigned int selector);
void open_cfw_test_watchdog_enable_provider(void);

#define OPEN_CFW_WATCHDOG_SELECTOR(selector) \
    open_cfw_test_watchdog_selector((selector))
#define OPEN_CFW_WATCHDOG_ENABLE_PROVIDER() \
    open_cfw_test_watchdog_enable_provider()

#endif
