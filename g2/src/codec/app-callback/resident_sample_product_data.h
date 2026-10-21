/* SPDX-License-Identifier: MIT
 * Image-A initialized sample/KWS data: source 0x10026c74..0x10026d7c,
 * native runtime alias 0x20026c74..0x20026d7c after the stage load.
 */
#ifndef GX8002_RESIDENT_SAMPLE_PRODUCT_DATA_H
#define GX8002_RESIDENT_SAMPLE_PRODUCT_DATA_H

#include "request.h"

struct gx8002_kws_keyword_record {
    char phrase[40];
    uint16_t field_28[2];
    uint32_t reserved_2c[7];
    uint32_t field_48;
    uint32_t threshold_tenths;
    uint32_t result_code;
    uint32_t field_54;
};
_Static_assert(sizeof(struct gx8002_kws_keyword_record) == 88,
               "native keyword stride");

struct gx8002_sample_registration {
    uint32_t state;
    uint32_t enabled;
    const void *callbacks;
    uintptr_t entries[8];
};
_Static_assert(sizeof(struct gx8002_sample_registration) == 44,
               "native sample registration extent");

struct gx8002_initialized_request {
    g2_codec_request request;
    uint32_t reserved_tail;
};
_Static_assert(sizeof(struct gx8002_initialized_request) == 32,
               "native request initializer extent");

extern uint32_t gx8002_uart_receive_config_words_26c74[2];
extern struct gx8002_kws_keyword_record gx8002_kws_keywords_26c7c[2];
extern uint32_t gx8002_sample_prestate_26d2c;
extern struct gx8002_sample_registration gx8002_sample_registration_26d30;
extern struct gx8002_initialized_request gx8002_request_initial_26d5c;

#endif
