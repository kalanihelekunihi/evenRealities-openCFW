/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_PRODUCTION_TEST_SCREEN_H
#define OPEN_CFW_PRODUCTION_TEST_SCREEN_H

#include <stdint.h>

#define OPEN_CFW_PRODUCTION_TEST_CONSTRUCT_EVENT 2U
#define OPEN_CFW_PRODUCTION_TEST_EXIT_EVENT 3U

int open_cfw_production_test_common_data_handler(
    const void *context,
    const void *data,
    uint32_t length
);
int open_cfw_production_test_predicate(void);
int open_cfw_production_test_screen_event(
    uint32_t event,
    const void *argument_1,
    const void *argument_2,
    void *parent
);

#endif
