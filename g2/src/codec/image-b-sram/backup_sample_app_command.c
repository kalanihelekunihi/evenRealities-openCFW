/* Image-B LVP_APP UART command callback 0x1000c1f8..0x1000c3c1.
 * Branches and stores follow authenticated CK804EF disassembly of the
 * sealed stage2 image. Hardware, logger, and tokenizer effects remain
 * delegated to their separately selected source providers. */
#include <stdint.h>
#include <stddef.h>

extern int gx8002_image_b_heap_log_10009934(const char *, ...);
extern uint32_t gx8002_image_b_audio_vad_policy_1000a470(void);
extern uint32_t gx8002_image_b_gsensor_workstate_100089e8(void);
extern uint32_t gx8002_image_b_channel_gain_10005920(uint32_t, uint32_t);
extern char *gx8002_image_b_tokenize_100112d4(char *, const char *);
extern int32_t gx8002_image_b_audio_uart_packet_send_1000b54c(uint8_t *);
extern void gx8002_image_b_boot_slot_toggle_1000aad0(void);

static uint16_t get16(const uint8_t *p, uint32_t offset)
{
    return *(const uint16_t *)(const void *)(p + offset);
}
static uint32_t get32(const uint8_t *p, uint32_t offset)
{
    return *(const uint32_t *)(const void *)(p + offset);
}
static void put16(volatile uint8_t *p, uint32_t offset, uint16_t value)
{
    *(volatile uint16_t *)(volatile void *)(p + offset) = value;
}
static void put32(volatile uint8_t *p, uint32_t offset, uint32_t value)
{
    *(volatile uint32_t *)(volatile void *)(p + offset) = value;
}

static volatile uint8_t *const state =
    (volatile uint8_t *)(uintptr_t)UINT32_C(0x2002d3a0);
static volatile uint8_t *const packet =
    (volatile uint8_t *)(uintptr_t)UINT32_C(0x20016f98);

static void send_packet(uint16_t command, uint32_t payload, uint32_t length)
{
    put16(packet, 4u, command);
    packet[7] = 1u;
    put32(packet, 0x10u, payload);
    put32(packet, 0x18u, length);
    (void)gx8002_image_b_audio_uart_packet_send_1000b54c(
        (uint8_t *)(uintptr_t)packet);
}

int gx8002_image_b_sample_app_command_1000c1f8(const uint8_t *event)
{
    (void)gx8002_image_b_heap_log_10009934(
        "[%s]%d\n", "_uartRecvCallback", 106);
    uint16_t key = get16(event, 4u);
    if (key == 368u) {
        (void)gx8002_image_b_heap_log_10009934("receive misc test cmd\n");
        uint32_t status = *(volatile uint32_t *)(volatile void *)(state + 0u);
        if (status == 0u) {
            status = gx8002_image_b_audio_vad_policy_1000a470();
            put32(state, 0u, status);
        }
        put16(state, 4u, status != 0u ? 1u : 0u);
        send_packet(624u, UINT32_C(0x2002d3a4), 2u);
    } else if (key == 369u) {
        (void)gx8002_image_b_heap_log_10009934("receive gsensor test cmd\n");
        (void)gx8002_image_b_gsensor_workstate_100089e8();
        put16(state, 4u, 0u);
        send_packet(625u, UINT32_C(0x2002d3a4), 2u);
    } else if (key == 258u) {
        (void)gx8002_image_b_heap_log_10009934("receive version req\n");
        char version[8] = "0.0.2.3";
        for (uint32_t i = 0u; i < 4u; ++i) {
            char *token = gx8002_image_b_tokenize_100112d4(
                i == 0u ? version : NULL, ".");
            /* Native dereferences each token without a null guard. */
            state[11u - i] = (uint8_t)(token[0] - '0');
        }
        state[12] = state[11];
        state[13] = state[10];
        state[14] = state[9];
        state[15] = state[8];
        send_packet(514u, UINT32_C(0x2002d3ac), 4u);
    } else if (key == 264u) {
        (void)gx8002_image_b_heap_log_10009934(
            "receive  switch wakeup model cmd\n");
        put16(state, 4u, 0u);
        send_packet(520u, UINT32_C(0x2002d3a4), 2u);
        gx8002_image_b_boot_slot_toggle_1000aad0();
    } else if (key == 267u) {
        uint32_t length = get32(event, 0x18u);
        uint32_t last = *(volatile uint32_t *)(volatile void *)(state + 0x10u);
        if (length != 0u) {
            const uint8_t *payload =
                (const uint8_t *)(uintptr_t)get32(event, 0x10u);
            for (uint32_t i = 0u; i < length; ++i) {
                last = payload[i];
                (void)gx8002_image_b_heap_log_10009934("0x%x \n", last);
                put32(state, 0x10u, last);
            }
        }
        if (last >= 49u) {
            (void)gx8002_image_b_heap_log_10009934(
                "set pga gain %d fail，gain range 0~48\n", last);
            put16(state, 4u, 0u);
        } else if (gx8002_image_b_channel_gain_10005920(2u, last) == 0u) {
            (void)gx8002_image_b_heap_log_10009934(
                "set pga gain %d success\n",
                *(volatile uint32_t *)(volatile void *)(state + 0x10u));
            put16(state, 4u, 1u);
        } else {
            (void)gx8002_image_b_heap_log_10009934(
                "set pga gain %d fail\n",
                *(volatile uint32_t *)(volatile void *)(state + 0x10u));
            put16(state, 4u, 0u);
        }
        send_packet(523u, UINT32_C(0x2002d3a4), 2u);
    }
    return 0;
}
