/* SPDX-License-Identifier: MIT */
#include "pt_protocol_production_entry.h"

#include <stdint.h>

static unsigned int postprocess_calls;

static int backend(enum open_cfw_pt_platform_operation op,
                   uintptr_t a0, uintptr_t a1, uintptr_t a2, uintptr_t a3,
                   uintptr_t a4,
                   void *context)
{
    (void)a1; (void)a2; (void)a3; (void)a4; (void)context;
    if (op == OPEN_CFW_PT_OP_GET_PRODUCT_MODE) {
        *(uint8_t *)a0 = 2U;
        return 0;
    }
    if (op == OPEN_CFW_PT_OP_POST_RESPONSE) {
        if (a0 == 0U || a1 < 5U || a2 == 0U || a3 < 5U) return -1;
        ++postprocess_calls;
        return 0;
    }
    return -1;
}

int main(void)
{
    struct open_cfw_pt_platform_backend port = {backend, 0};
    struct open_cfw_pt_platform_backend invalid_port = {0, 0};
    uint8_t request[5] = {0x01U, 0U, 0U, 0U, 1U};
    uint8_t response[256] = {0};
    uint8_t length = 0U;
    open_cfw_pt_protocol_production_reset();
    if (open_cfw_pt_protocol_production_entry(request, 5U, response, &length) != OPEN_CFW_PT_HANDLER_FAILED) return 1;
    if (open_cfw_pt_protocol_production_install(0) != OPEN_CFW_PT_INVALID_ARGUMENT) return 2;
    if (open_cfw_pt_protocol_production_install(&port) != 0) return 3;
    if (open_cfw_pt_protocol_production_entry(0, 5U, response, &length) != OPEN_CFW_PT_INVALID_ARGUMENT || length != 0U) return 4;
    if (open_cfw_pt_protocol_production_entry(request, 5U, response, &length) != 0) return 5;
    if (length < 6U || response[0] != 0x5AU || response[1] != 0xA5U || response[2] != 0xFFU) return 6;
    if (open_cfw_pt_protocol_production_postprocess(
            request, 5U, response, length) != 0 ||
        postprocess_calls != 1U) return 12;
    if (open_cfw_pt_protocol_production_install(&invalid_port) != OPEN_CFW_PT_INVALID_ARGUMENT) return 7;
    if (open_cfw_pt_protocol_production_entry(request, 5U, response, &length) != OPEN_CFW_PT_HANDLER_FAILED) return 8;
    if (open_cfw_pt_protocol_production_install(&port) != 0) return 9;
    open_cfw_pt_protocol_production_reset();
    if (open_cfw_pt_protocol_production_entry(request, 5U, response, &length) != OPEN_CFW_PT_HANDLER_FAILED) return 10;
    if (open_cfw_pt_protocol_production_postprocess(
            request, 5U, response, length) != OPEN_CFW_PT_HANDLER_FAILED)
        return 13;
    if (open_cfw_pt_protocol_production_bootstrap() != 0) return 11;
    open_cfw_pt_protocol_production_reset();
    return 0;
}
