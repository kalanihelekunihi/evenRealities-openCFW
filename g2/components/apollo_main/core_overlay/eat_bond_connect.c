/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the pathless G2 eAT bond/connect handlers. */

#include <stdint.h>

#include "eat_bond_connect.h"

#ifndef OPEN_CFW_EAT_CLEAN_BOND_RESPONSE_ADDRESS
#define OPEN_CFW_EAT_CLEAN_BOND_RESPONSE_ADDRESS 0x007850d0u
#endif
#ifndef OPEN_CFW_EAT_KEEP_CONNECT_RESPONSE_ADDRESS
#define OPEN_CFW_EAT_KEEP_CONNECT_RESPONSE_ADDRESS 0x0077553cu
#endif

#ifndef OPEN_CFW_EAT_CLEAN_BOND
void open_cfw_retained_eat_clean_bond(void);
#define OPEN_CFW_EAT_CLEAN_BOND() open_cfw_retained_eat_clean_bond()
#endif

#ifndef OPEN_CFW_EAT_KEEP_CONNECT
void open_cfw_retained_eat_keep_connect(int enabled);
#define OPEN_CFW_EAT_KEEP_CONNECT(enabled) \
    open_cfw_retained_eat_keep_connect((enabled))
#endif

#ifndef OPEN_CFW_EAT_OUTPUT
void open_cfw_retained_eat_output(const char *response);
#define OPEN_CFW_EAT_OUTPUT(response) open_cfw_retained_eat_output((response))
#endif

#define OPEN_CFW_EAT_CLEAN_BOND_RESPONSE \
    ((const char *)(uintptr_t)OPEN_CFW_EAT_CLEAN_BOND_RESPONSE_ADDRESS)
#define OPEN_CFW_EAT_KEEP_CONNECT_RESPONSE \
    ((const char *)(uintptr_t)OPEN_CFW_EAT_KEEP_CONNECT_RESPONSE_ADDRESS)

#if defined(OPEN_CFW_EAT_CLEAN_BOND_ONLY)
#define OPEN_CFW_EAT_SELECTOR 1
#elif defined(OPEN_CFW_EAT_KEEP_CONNECT_ONLY)
#define OPEN_CFW_EAT_SELECTOR 2
#else
#define OPEN_CFW_EAT_SELECTOR 0
#endif

#if OPEN_CFW_EAT_SELECTOR == 0 || OPEN_CFW_EAT_SELECTOR == 1
int open_cfw_eat_clean_bond_handler(void)
{
    OPEN_CFW_EAT_CLEAN_BOND();
    OPEN_CFW_EAT_OUTPUT(OPEN_CFW_EAT_CLEAN_BOND_RESPONSE);
    return 0;
}
#endif

#if OPEN_CFW_EAT_SELECTOR == 0 || OPEN_CFW_EAT_SELECTOR == 2
int open_cfw_eat_keep_connect_handler(void)
{
    OPEN_CFW_EAT_KEEP_CONNECT(1);
    OPEN_CFW_EAT_OUTPUT(OPEN_CFW_EAT_KEEP_CONNECT_RESPONSE);
    return 0;
}
#endif
