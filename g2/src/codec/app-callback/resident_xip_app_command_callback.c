/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x10209430..0x102096a2. All eleven command
 * comparisons, original call order, request fields, and stock strings.
 * Tokenization, hardware and request consumption use separately typed
 * source/ABI contracts. Payload and product-state validity are native
 * runtime preconditions.
 */
#include "request.h"
#include "resident_sample_product_data.h"

extern uint32_t gx8002_xip_tws_publish_10206c24(const char *, ...);
extern uint32_t gx8002_xip_audio_vad_query_10207404(void *);
extern uint32_t gx8002_xip_gsensor_workstate_10206908(void);
extern char *gx8002_xip_strtok_1020995c(char *, const char *);
extern uint32_t gx8002_xip_gpio_set_direction_10205f24(uint32_t, uint32_t);
extern void gx8002_xip_multiboot_switch_10207a80(void);
extern uint32_t gx8002_xip_audio_set_rough_gain_102043ac(uint32_t, uint32_t);
extern int32_t gx8002_xip_padmux_set_102065dc(uint32_t, uint32_t);
extern uint32_t gx8002_xip_audio_channel_field_102049b0(uint32_t, uint32_t);

static volatile uint8_t *const application =
    (volatile uint8_t *)(uintptr_t)UINT32_C(0x2002e8f0);
static g2_codec_request *const reply =
    &gx8002_request_initial_26d5c.request;

static uint16_t command(const uint8_t *message)
{
    return *(const uint16_t *)(const void *)(message + 4u);
}

static uint32_t payload_length(const uint8_t *message)
{
    return *(const uint32_t *)(const void *)(message + 0x18u);
}

static const uint8_t *payload(const uint8_t *message)
{
    return *(const uint8_t *const *)(const void *)(message + 0x10u);
}

extern uint32_t g2_codec_event_dispatch(uint32_t, uint32_t, uint32_t);

uint32_t gx8002_xip_app_command_callback_persistent_10209430(
    const uint8_t *message)
{
    if (command(message) == 0x170u) {
        (void)gx8002_xip_tws_publish_10206c24("receive misc test cmd\n");
        volatile uint32_t *const cached =
            (volatile uint32_t *)(void *)(application + 0x28u);
        if (*cached == 0u)
            *cached = gx8002_xip_audio_vad_query_10207404((void *)0);
        (void)g2_codec_event_dispatch(0u, 0x70u, *cached != 0u);
    }
    if (command(message) == 0x171u) {
        (void)gx8002_xip_tws_publish_10206c24(
            "receive gsensor test cmd\n");
        (void)gx8002_xip_gsensor_workstate_10206908();
        (void)g2_codec_event_dispatch(0u, 0x71u, 0u);
    }
    if (command(message) == 0x102u) {
        (void)gx8002_xip_tws_publish_10206c24("receive version req\n");
        char version[8] = "0.0.2.3";
        application[0x2fu] = (uint8_t)(*gx8002_xip_strtok_1020995c(
            version, ".") - '0');
        application[0x2eu] = (uint8_t)(*gx8002_xip_strtok_1020995c(
            (char *)0, ".") - '0');
        application[0x2du] = (uint8_t)(*gx8002_xip_strtok_1020995c(
            (char *)0, ".") - '0');
        uint8_t last = (uint8_t)(*gx8002_xip_strtok_1020995c(
            (char *)0, ".") - '0');
        application[0x2cu] = last;
        application[0x30u] = application[0x2fu];
        application[0x31u] = application[0x2eu];
        application[0x32u] = application[0x2du];
        application[0x33u] = last;
        reply->request_code = 0x202u;
        reply->flag = 1u;
        reply->payload = (const uint8_t *)(const void *)(application + 0x30u);
        reply->count = 4u;
        (void)g2_codec_request_consume(reply);
    }
    if (command(message) == 0x107u) {
        (void)gx8002_xip_tws_publish_10206c24(
            "receive switch bf req\n");
        (void)g2_codec_event_dispatch(0u, 7u, 1u);
        (void)gx8002_xip_gpio_set_direction_10205f24(0u, 0u);
        (void)gx8002_xip_gpio_set_direction_10205f24(1u, 0u);
        gx8002_xip_multiboot_switch_10207a80();
    }
    if (command(message) == 0x109u) {
        (void)gx8002_xip_tws_publish_10206c24("open vad reporting\n");
        (void)g2_codec_event_dispatch(0u, 9u, 1u);
        *(volatile uint16_t *)(void *)(application + 0x34u) = 1u;
    }
    if (command(message) == 0x10au) {
        (void)gx8002_xip_tws_publish_10206c24("close vad reporting\n");
        (void)g2_codec_event_dispatch(0u, 10u, 1u);
        *(volatile uint16_t *)(void *)(application + 0x34u) = 0u;
    }
    if (command(message) == 0x10bu) {
        const uint8_t *const bytes = payload(message);
        for (uint32_t i = 0u; i < payload_length(message); ++i) {
            (void)gx8002_xip_tws_publish_10206c24("0x%x \n", bytes[i]);
            *(volatile uint32_t *)(void *)(application + 0x38u) = bytes[i];
        }
        uint32_t gain = *(volatile uint32_t *)(void *)(application + 0x38u);
        uint32_t accepted = 0u;
        if (gain < 49u) {
            uint32_t result = gx8002_xip_audio_set_rough_gain_102043ac(
                2u, gain);
            gain = *(volatile uint32_t *)(void *)(application + 0x38u);
            if (result == 0u) {
                (void)gx8002_xip_tws_publish_10206c24(
                    "set pga gain %d success\n", gain);
                accepted = 1u;
            } else {
                (void)gx8002_xip_tws_publish_10206c24(
                    "set pga gain %d fail\n", gain);
            }
        } else {
            (void)gx8002_xip_tws_publish_10206c24(
                "set pga gain %d fail，gain range 0~48\n", gain);
        }
        (void)g2_codec_event_dispatch(0u, 11u, accepted);
    }
    if (command(message) == 0x10cu) {
        (void)gx8002_xip_tws_publish_10206c24("receive open dmic req\n");
        (void)gx8002_xip_tws_publish_10206c24("dmic init master\n");
        (void)gx8002_xip_padmux_set_102065dc(0u, 7u);
        (void)gx8002_xip_padmux_set_102065dc(1u, 9u);
        (void)g2_codec_event_dispatch(0u, 12u, 1u);
    }
    if (command(message) == 0x10du) {
        (void)gx8002_xip_tws_publish_10206c24("receive close dmic req\n");
        (void)gx8002_xip_tws_publish_10206c24("dmic close master\n");
        (void)gx8002_xip_padmux_set_102065dc(0u, 1u);
        (void)gx8002_xip_padmux_set_102065dc(1u, 1u);
        (void)gx8002_xip_gpio_set_direction_10205f24(0u, 0u);
        (void)gx8002_xip_gpio_set_direction_10205f24(1u, 0u);
        (void)g2_codec_event_dispatch(0u, 13u, 1u);
    }
    if (command(message) == 0x10eu) {
        (void)gx8002_xip_tws_publish_10206c24(
            "receive set pdm ch delay req\n");
        uint8_t one = 1u;
        (void)gx8002_xip_audio_channel_field_102049b0(0u, 1u);
        reply->request_code = command(message);
        reply->flag = 1u;
        reply->payload = &one;
        reply->count = 1u;
        (void)g2_codec_request_consume(reply);
    }
    if (command(message) == 0x10fu) {
        (void)gx8002_xip_tws_publish_10206c24(
            "receive set i2s status req\n");
        *(volatile uint32_t *)(void *)(application + 0x3cu) = 1u;
        application[0x40u] = payload(message)[0];
        (void)gx8002_xip_tws_publish_10206c24(
            "i2s_mode_state %d\n", application[0x40u]);
    }
    return 0u;
}
