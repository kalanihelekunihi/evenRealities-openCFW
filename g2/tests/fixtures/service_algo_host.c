/* SPDX-License-Identifier: MIT */
#include <assert.h>
#include <stdint.h>

static int16_t left_buffer[800];
static int16_t right_buffer[800];
static int16_t mono_buffer[800];
static uint64_t left_energy;
static uint64_t right_energy;
static uint64_t window_index;
static uint64_t energy_window[10];

#define OPEN_CFW_SERVICE_ALGO_LEFT_BUFFER left_buffer
#define OPEN_CFW_SERVICE_ALGO_RIGHT_BUFFER right_buffer
#define OPEN_CFW_SERVICE_ALGO_MONO_BUFFER mono_buffer
#define OPEN_CFW_SERVICE_ALGO_LEFT_ENERGY left_energy
#define OPEN_CFW_SERVICE_ALGO_RIGHT_ENERGY right_energy
#define OPEN_CFW_SERVICE_ALGO_WINDOW_INDEX window_index
#define OPEN_CFW_SERVICE_ALGO_ENERGY_WINDOW energy_window
#include "../../components/apollo_main/core_overlay/service_algo.c"

int main(void)
{
    int16_t stereo[1600];
    int16_t shifted_left[64] = {0};
    int16_t shifted_right[64] = {0};
    int16_t *buffer = 0;
    uint32_t size = 0;
    uint16_t ssr = 0;
    int16_t angle = 0;
    double radians = 1.0;
    double delay = 1.0;
    double correlation = 0.0;
    double rms = 0.0;
    unsigned int index;

    open_cfw_service_algo_front_buffer_get(&buffer, &size);
    assert(buffer == mono_buffer);
    assert(size == 1600u);
    assert(algo_front_data_preprocess(stereo, 3196u) == -1);
    for (index = 0u; index < 800u; ++index) {
        stereo[index * 2u] = 100;
        stereo[index * 2u + 1u] = -100;
    }
    assert(algo_front_data_preprocess(stereo, sizeof(stereo)) == 0);
    assert(left_buffer[799] == 100 && right_buffer[799] == -100);
    assert(mono_buffer[799] == 0);
    assert(left_energy == 10000u && right_energy == 10000u);
    assert(SVC_SSRProcess(stereo, sizeof(stereo)) == 10001u);
    assert(open_cfw_service_algo_energy_window_update(left_buffer, 1600u) == 0);
    assert(energy_window[0] == 10000u && window_index == 1u);
    for (index = 1u; index < 10u; ++index) energy_window[index] = 10000u;
    assert(SVC_SSRProcess(stereo, sizeof(stereo)) == 1u);
    assert(open_cfw_service_algo_process(stereo, sizeof(stereo), &ssr, &angle) == 0);
    assert(ssr == 1u);

    open_cfw_service_algo_cross_correlation(
        left_buffer, left_buffer, 800, 10, 16000.0, 0.14, 343.0,
        0.0, 0.0, &radians, &delay, &correlation, &rms
    );
    assert(radians > -0.0002 && radians < 0.0002);
    assert(delay == 0.0);
    assert(correlation > 0.0);
    assert(rms > 99.9 && rms < 100.1);
    assert(open_cfw_service_algo_quiet_nan() !=
        open_cfw_service_algo_quiet_nan());

    /* A right-channel sample delayed by three slots must report +3/sample_rate. */
    shifted_left[11] = 1000;
    shifted_right[14] = 1000;
    open_cfw_service_algo_cross_correlation(
        shifted_left, shifted_right, 64, 10, 1000.0, 0.5, 100.0,
        0.0, 1.0, &radians, &delay, &correlation, &rms
    );
    assert(delay > 0.002999 && delay < 0.003001);
    assert(radians > 0.643 && radians < 0.645);
    assert(correlation > 20.0);
    assert(rms > 124.9 && rms < 125.1);

    /* Threshold and invalid-input paths must fail closed without stale output. */
    radians = 1.0;
    delay = 1.0;
    correlation = 1.0;
    rms = 1.0;
    open_cfw_service_algo_cross_correlation(
        shifted_left, shifted_right, 64, 10, 1000.0, 0.5, 100.0,
        126.0, 1.0, &radians, &delay, &correlation, &rms
    );
    assert(radians != radians && delay != delay);
    assert(correlation == 0.0);
    assert(rms > 124.9 && rms < 125.1);
    open_cfw_service_algo_cross_correlation(
        0, shifted_right, 64, 10, 1000.0, 0.5, 100.0,
        0.0, 0.0, &radians, &delay, &correlation, &rms
    );
    assert(radians != radians && delay != delay);
    assert(correlation == 0.0 && rms == 0.0);
    assert(open_cfw_service_algo_process(stereo, sizeof(stereo), 0, &angle) == -1);
    assert(open_cfw_service_algo_process(stereo, sizeof(stereo), &ssr, 0) == -1);

    /* The ten-entry energy history is a ring, including the wrap boundary. */
    window_index = 9u;
    assert(open_cfw_service_algo_energy_window_update(shifted_left, 128u) == 0);
    assert(window_index == 0u && energy_window[9] == 15625u);
    assert(open_cfw_service_algo_energy_window_update(shifted_left, 128u) == 0);
    assert(window_index == 1u && energy_window[0] == 15625u);
    assert(open_cfw_service_algo_energy_window_update(0, 128u) == -1);
    assert(open_cfw_service_algo_energy_window_update(shifted_left, 127u) == -1);
    return 0;
}
