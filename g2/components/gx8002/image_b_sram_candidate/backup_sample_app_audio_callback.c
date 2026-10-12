/* Image-B sample app audio callback 0x1000bef4..0x1000c093.
 * Source model follows the native 64-bit wrap counters, 6144-step timing
 * arithmetic, diagnostic branch, frame-window selection, and final state
 * writes. MMIO at A0A00148/A0B80010 and audio output are real external
 * hardware contracts. This unit remains experimental until bounded native
 * instruction/effect comparison covers the arithmetic branches. */
#include <stdint.h>

extern int gx8002_image_b_heap_log_10009934(const char *, ...);
extern uint32_t gx8002_image_b_audio_out_push_frame_10006b60(
    uint32_t, uint32_t);

static volatile uint32_t *const callback_state =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002d360);
static volatile uint32_t *const callback_flags =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0x20016f6c);
static volatile uint32_t *const audio_handle =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002d798);

static uint64_t pair(uint32_t low, uint32_t high)
{
    return ((uint64_t)high << 32) | low;
}

/* Native divu at 0x1000bfc2: preserve its instruction behavior even for a
 * zero divisor, which ordinary C division would leave undefined. */
static uint32_t native_unsigned_divide(uint32_t numerator, uint32_t divisor)
{
    uint32_t result;
    __asm__ volatile ("divu %0, %1, %2"
                      : "=r"(result) : "r"(numerator), "r"(divisor));
    return result;
}

void gx8002_image_b_sample_app_audio_callback_1000bef4(
    uint32_t start, uint32_t end)
{
    uint32_t timestamp = *(volatile uint32_t *)(uintptr_t)UINT32_C(0xa0a00148);
    uint32_t prior_timestamp_high = callback_state[3];
    uint32_t audio_clock = *(volatile uint32_t *)(uintptr_t)UINT32_C(0xa0b80010);
    uint32_t timestamp_high = (uint32_t)((int32_t)timestamp >> 31);
    uint32_t audio_high = (uint32_t)((int32_t)audio_clock >> 31);
    uint32_t prior_audio_low = callback_state[0];
    uint32_t prior_audio_high = callback_state[1];
    uint64_t now_timestamp = pair(timestamp, timestamp_high);
    uint64_t now_audio = pair(audio_clock, audio_high);

    int timestamp_wrapped = timestamp_high < prior_timestamp_high;
    if (timestamp_high == prior_timestamp_high)
        timestamp_wrapped = timestamp < callback_state[2];
    uint32_t timestamp_wrap_low = callback_state[4];
    uint32_t timestamp_wrap_high = callback_state[5];
    uint64_t timestamp_wraps = pair(timestamp_wrap_low, timestamp_wrap_high);
    if (timestamp_wrapped) {
        ++timestamp_wraps;
        callback_state[4] = (uint32_t)timestamp_wraps;
        callback_state[5] = (uint32_t)(timestamp_wraps >> 32);
    }
    int audio_wrapped = audio_high < prior_audio_high;
    if (audio_high == prior_audio_high)
        audio_wrapped = audio_clock < prior_audio_low;
    uint32_t audio_wrap_low = callback_state[6];
    uint32_t audio_wrap_high = callback_state[7];
    uint64_t audio_wraps = pair(audio_wrap_low, audio_wrap_high);
    if (audio_wrapped) {
        ++audio_wraps;
        callback_state[6] = (uint32_t)audio_wraps;
        callback_state[7] = (uint32_t)(audio_wraps >> 32);
    }
    uint64_t expanded_timestamp = timestamp_wraps * UINT64_C(6144) +
        now_timestamp;
    uint64_t expanded_audio = audio_wraps * UINT64_C(6144) + now_audio;
    uint32_t difference = (uint32_t)(expanded_timestamp - expanded_audio);
    callback_state[8] = difference;

    if (callback_flags[0] != 0u) {
        callback_state[9] = difference;
        callback_flags[0] = 0u;
        (void)gx8002_image_b_heap_log_10009934(
            "ddd %d, %lld, %lld\n", difference,
            (long long)expanded_timestamp, (long long)expanded_audio);
    }
    int32_t count = (int32_t)callback_flags[1];
    if (count < 1000) {
        callback_flags[1] = (uint32_t)(count + 1);
    } else {
        callback_flags[1] = 0u;
        (void)gx8002_image_b_heap_log_10009934("%d,", timestamp);
        (void)gx8002_image_b_heap_log_10009934(
            "%ld;", callback_state[4], callback_state[5]);
        (void)gx8002_image_b_heap_log_10009934("%d,", audio_clock);
        (void)gx8002_image_b_heap_log_10009934(
            "%ld@\n", callback_state[6], callback_state[7]);
        (void)gx8002_image_b_heap_log_10009934(
            "%d$\n", callback_state[9] - callback_state[8]);
    }

    uint32_t frame[2];
    frame[0] = end + 1u;
    frame[1] = (end + end + 1u) - start;
    uint32_t frame_limit = callback_state[10];
    if (frame[1] >= frame_limit) {
        frame[0] = 0u;
        frame[1] = end - start;
    }
    uint32_t current_difference = callback_state[8];
    uint32_t baseline = callback_state[9];
    int32_t baseline_delta = (int32_t)(baseline - current_difference);
    if ((int32_t)(64u - frame_limit) < baseline_delta &&
        baseline_delta < (int32_t)(frame_limit - 64u)) {
        goto submit_frame;
    }

    uint32_t span = end - start;
    (void)gx8002_image_b_heap_log_10009934("%d&\n", callback_state[8]);
    uint32_t divisor = span + 1u;
    uint32_t quotient = native_unsigned_divide(timestamp, divisor);
    uint32_t position = quotient * divisor;
    frame[0] = position;
    frame[1] = span + position;
    if (frame[1] >= frame_limit) {
        frame[0] = 0u;
        frame[1] = span;
    }
    (void)gx8002_image_b_heap_log_10009934(
        "%d,%d\n", timestamp, position);
    callback_flags[0] = 1u;

submit_frame:
    callback_state[2] = timestamp;
    callback_state[3] = (uint32_t)((int32_t)timestamp >> 31);
    callback_state[0] = audio_clock;
    callback_state[1] = (uint32_t)((int32_t)audio_clock >> 31);
    (void)gx8002_image_b_audio_out_push_frame_10006b60(
        *audio_handle, (uint32_t)(uintptr_t)frame);
}
