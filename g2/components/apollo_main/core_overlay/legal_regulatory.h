/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_LEGAL_REGULATORY_H
#define OPEN_CFW_LEGAL_REGULATORY_H

#include <stdint.h>

struct open_cfw_legal_regulatory_event;
int open_cfw_legal_regulatory_ui_event_handler(
    uint32_t event_id,
    const struct open_cfw_legal_regulatory_event *event,
    uint32_t event_size,
    uintptr_t context);

#endif
