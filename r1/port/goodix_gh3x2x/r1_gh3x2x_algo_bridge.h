#ifndef R1_GH3X2X_ALGO_BRIDGE_H
#define R1_GH3X2X_ALGO_BRIDGE_H

/*
 * Transparent, vendor-header-free provider contract for the GH3X2X
 * democode algorithm-call ABI.
 *
 * The pinned democode owns FIFO parsing and its STGh3x2xFrameInfo globals.
 * r1_gh3x2x_stubs.c validates and normalizes those globals into the bounded
 * views below.  Reconstructed algorithms can therefore be composed without
 * depending on the vendor global layout, and test/target providers cannot
 * overrun the democode's fixed 16-word result record.
 */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define R1_GH3X2X_ALGO_FUNCTION_COUNT 20u
#define R1_GH3X2X_ALGO_RESULT_COUNT 16u
#define R1_GH3X2X_ALGO_AXIS_COUNT 3u
#define R1_GH3X2X_ALGO_INPUT_CHANNELS 12u
#define R1_GH3X2X_ALGO_INPUT_ENABLE_BYTES 2u
#define R1_GH3X2X_ALGO_PRIMARY_CHANNELS 4u
/* Pinned public-democode function offsets. */
#define R1_GH3X2X_ALGO_FUNCTION_HR 1u
#define R1_GH3X2X_ALGO_FUNCTION_HRV 2u
#define R1_GH3X2X_ALGO_FUNCTION_HSM 3u
#define R1_GH3X2X_ALGO_FUNCTION_SPO2 6u

typedef struct {
    uint32_t function_mask;
    uint8_t function_offset;
    uint8_t channel_count;
    uint16_t sample_rate_hz;
    const uint8_t *channel_map;
    const uint32_t *raw_values;
    const uint32_t *agc_values;
    const uint32_t *frame_flags;
    size_t frame_flag_count;
    int16_t acceleration[R1_GH3X2X_ALGO_AXIS_COUNT];
    uint32_t frame_count;
} r1_gh3x2x_algo_frame;

typedef struct {
    bool updated;
    uint8_t value_count;
    uint16_t value_mask;
    int32_t values[R1_GH3X2X_ALGO_RESULT_COUNT];
} r1_gh3x2x_algo_result;

/* Exact provider-independent superset of the records assembled by the
 * recovered HR (0x0002C944), HRV (0x0002CAD8), and SpO2 (0x0002CFE8)
 * wrappers. It preserves all three four-channel groups, AGC values, and
 * MSB-first enable flags without exposing vendor globals. */
typedef struct {
    uint8_t frame_id;
    uint8_t total_channel_count;
    uint8_t sleep_flag;
    uint8_t bit_count;
    uint8_t chip_type;
    uint8_t data_type;
    uint8_t enable_flags[R1_GH3X2X_ALGO_INPUT_ENABLE_BYTES];
    int32_t channel_values[R1_GH3X2X_ALGO_INPUT_CHANNELS];
    uint8_t gain_codes[R1_GH3X2X_ALGO_INPUT_CHANNELS];
    uint16_t drive_currents[R1_GH3X2X_ALGO_INPUT_CHANNELS];
    int32_t acceleration[R1_GH3X2X_ALGO_AXIS_COUNT];
    uint8_t last_hr;
    uint8_t scene;
} r1_gh3x2x_algo_input;

/* Mapped HR and SpO2 use their recovered 12-slot maps; 0xFF disables a slot
 * and every other index must name a bounded raw frame word. HRV copies the
 * first four frame/AGC words and carries the last accepted HR. All helpers
 * leave output untouched on failure. */
bool r1_gh3x2x_algo_prepare_hr_input(
    const r1_gh3x2x_algo_frame *frame, uint8_t sleep_flag,
    r1_gh3x2x_algo_input *output);
bool r1_gh3x2x_algo_prepare_hr_mapped_input(
    const r1_gh3x2x_algo_frame *frame,
    const uint8_t channel_map[R1_GH3X2X_ALGO_INPUT_CHANNELS],
    uint8_t scene, uint8_t sleep_flag, r1_gh3x2x_algo_input *output);
bool r1_gh3x2x_algo_prepare_hrv_input(
    const r1_gh3x2x_algo_frame *frame, uint8_t last_hr,
    uint8_t sleep_flag, r1_gh3x2x_algo_input *output);
bool r1_gh3x2x_algo_prepare_spo2_input(
    const r1_gh3x2x_algo_frame *frame,
    const uint8_t channel_map[R1_GH3X2X_ALGO_INPUT_CHANNELS],
    uint8_t sleep_flag, r1_gh3x2x_algo_input *output);
/* Exact one-time R1 HBA map written by 0x0002A630: the first four lanes map
 * directly and all remaining lanes are disabled. */
bool r1_gh3x2x_algo_hr_default_channel_map(
    uint8_t output[R1_GH3X2X_ALGO_INPUT_CHANNELS]);
/* Exact one-time R1 SpO2 map written by 0x0002ACF4: IR source 1 occupies the
 * middle group and red source 0 the final group; every other lane is 0xFF. */
bool r1_gh3x2x_algo_spo2_default_channel_map(
    uint8_t output[R1_GH3X2X_ALGO_INPUT_CHANNELS]);

/* Receives only provider results that passed the bridge's update, count,
 * mask, and fixed-capacity checks. The view is valid for the duration of the
 * call; observers must copy anything they retain. */
typedef void (*r1_gh3x2x_algo_result_observer_fn)(
    void *context, const r1_gh3x2x_algo_frame *frame,
    const r1_gh3x2x_algo_result *result);

/* The retail R1 product dispatcher consumes the first raw word of each HSM
 * (function mask 0x08) frame even though the Goodix algorithm table has no
 * HSM executor. This observer exposes that checked frame boundary without
 * pretending HSM has an algorithm result. The view is call-scoped. */
typedef void (*r1_gh3x2x_algo_frame_observer_fn)(
    void *context, const r1_gh3x2x_algo_frame *frame);

typedef struct {
    void *context;
    /* supported_functions is a bitmap using the democode's function IDs. */
    uint32_t supported_functions;
    bool (*initialize)(void *context, const r1_gh3x2x_algo_frame *frame);
    bool (*process)(void *context, const r1_gh3x2x_algo_frame *frame,
                    r1_gh3x2x_algo_result *result);
    bool (*deinitialize)(void *context, uint32_t function_mask,
                         uint8_t function_offset);
    /* Writes a NUL-terminated string and returns true when available. */
    bool (*version)(void *context, uint8_t function_offset,
                    char *destination, size_t destination_size);
    void (*sensor_enable)(void *context, bool accelerometer, bool capacitive,
                          bool temperature);
    bool (*write_virtual_register)(void *context, uint16_t address,
                                   uint16_t value);
} r1_gh3x2x_algo_provider;

/* Copy-bind provider state. NULL restores the closed state. */
void r1_gh3x2x_algo_bind_provider(
    const r1_gh3x2x_algo_provider *provider);
void r1_gh3x2x_algo_unbind_provider(void);
bool r1_gh3x2x_algo_provider_bound(void);
/* The result observer is independent of the algorithm provider so the R1
 * product layer can consume licensed or reconstructed provider output without
 * becoming part of the provider ABI. NULL restores the closed state. */
void r1_gh3x2x_algo_bind_result_observer(
    r1_gh3x2x_algo_result_observer_fn observer, void *context);
void r1_gh3x2x_algo_unbind_result_observer(void);
bool r1_gh3x2x_algo_result_observer_bound(void);
/* Independent observer for validated HSM raw frames. NULL closes the seam. */
void r1_gh3x2x_algo_bind_frame_observer(
    r1_gh3x2x_algo_frame_observer_fn observer, void *context);
void r1_gh3x2x_algo_unbind_frame_observer(void);
bool r1_gh3x2x_algo_frame_observer_bound(void);

#endif
