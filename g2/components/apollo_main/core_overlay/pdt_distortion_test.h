/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_PDT_DISTORTION_TEST_H
#define OPEN_CFW_PDT_DISTORTION_TEST_H

#include <stdint.h>

#define OPEN_CFW_PDT_DISTORTION_CONSTRUCT_EVENT 2U
#define OPEN_CFW_PDT_DISTORTION_EXIT_EVENT 3U

void open_cfw_pdt_distortion_zero_styles(
    void *object, uint32_t value, uint32_t selector
);
int open_cfw_pdt_distortion_common_data_handler(
    const void *context, const void *data, uint32_t length
);
int open_cfw_pdt_distortion_predicate(void);
int open_cfw_pdt_distortion_screen_event(
    uint32_t event, const void *argument_1, const void *argument_2,
    void *parent
);

#endif
