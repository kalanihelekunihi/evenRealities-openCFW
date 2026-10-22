/* SPDX-License-Identifier: MIT
 * Field-wise native source initializer 0x10026c74..0x10026d7c. The two
 * keyword records have 0x58 stride and are used by LvpPrintMaxKwsList.
 * Function/name identities in the sample registration are C relocations.
 * Final 0x2002 runtime alias and scatter placement remain unqualified.
 */
#include "resident_sample_product_data.h"

extern uint32_t gx8002_xip_sample_app_init_10208e4c(void);
extern uint32_t gx8002_xip_sample_event_10208f04(const uint32_t *);
extern uint32_t gx8002_xip_i2s_request_tick_102091bc(void);
extern uint32_t gx8002_xip_app_gpio_resume_10208dec(const char *);
extern uint32_t gx8002_xip_app_gpio_suspend_10208dcc(const char *);

static const char sample_name[]
    __attribute__((section(".gx8002.sample_name.b649"), used)) = "sample app";
static const char suspend_name[]
    __attribute__((section(".gx8002.sample_name.b654"), used)) = "SampleAppSuspend";
static const char resume_name[]
    __attribute__((section(".gx8002.sample_name.b665"), used)) = "SampleAppResume";

/* Stock 0x10026C74 (s_recv_header_data_count) */
uint32_t gx8002_uart_receive_config_words_26c74[2]
    __attribute__((section(".gx8002.uart_rx_config.26c74"), used,
                   aligned(4))) = {4u, 4u};

/* Stock 0x10026C7C (gx8002_wakeword_parameters) */
struct gx8002_kws_keyword_record gx8002_kws_keywords_26c7c[2]
    __attribute__((section(".gx8002.kws_keywords.26c7c"), used,
                   aligned(4))) = {
    {.phrase = "hey_even", .field_28 = {54u,54u},
     .field_48 = 2u, .threshold_tenths = 0x237u,
     .result_code = 100u, .field_54 = 1u},
    {.phrase = "hi_even", .field_28 = {54u,54u},
     .field_48 = 2u, .threshold_tenths = 0x1ccu,
     .result_code = 101u, .field_54 = 1u},
};

/* Stock 0x10026D2C (gx8002_max_decoder_state) */
uint32_t gx8002_sample_prestate_26d2c
    __attribute__((section(".gx8002.sample_prestate.26d2c"), used,
                   aligned(4))) = 1u;

/* Stock 0x10026D3C (gx8002_sample_application) */
/* Stock 0x10026D38 (gx8002_app_core_ops) */
/* Stock 0x10026D30 (gx8002_event_state) */
struct gx8002_sample_registration gx8002_sample_registration_26d30
    __attribute__((section(".gx8002.sample_registration.26d30"), used,
                   aligned(4))) = {
    .state = UINT32_MAX,
    .enabled = 1u,
    .callbacks = gx8002_sample_registration_26d30.entries,
    .entries = {
        (uintptr_t)sample_name,
        (uintptr_t)&gx8002_xip_sample_app_init_10208e4c,
        (uintptr_t)&gx8002_xip_sample_event_10208f04,
        (uintptr_t)&gx8002_xip_i2s_request_tick_102091bc,
        (uintptr_t)&gx8002_xip_app_gpio_resume_10208dec,
        (uintptr_t)suspend_name,
        (uintptr_t)&gx8002_xip_app_gpio_suspend_10208dcc,
        (uintptr_t)resume_name,
    },
};

/* Stock 0x10026D5C (gx8002_app_reply_state) */
struct gx8002_initialized_request gx8002_request_initial_26d5c
    __attribute__((section(".gx8002.request_initial.26d5c"), used,
                   aligned(4))) = {
    .request = {.prefix = UINT32_C(0x58585542)},
};
