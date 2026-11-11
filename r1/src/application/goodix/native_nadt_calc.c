#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include "goodix_nadt.h"
#include "native_nadt_state.h"
#include "native_nadt_public_view.h"

extern double r1_native_round(double);
extern double r1_native_sqrt(double);
extern float r1_native_roundf(float);
extern float r1_native_sqrtf(float);

/* These scratch banks are shared by the one native NADT context. The stream
 * history and persistent counters remain in the native initializer's owner. */
static goodix_primitives_nadt_primary_workspace primary_scratch;
static goodix_primitives_nadt_auxiliary_workspace auxiliary_scratch;
static goodix_primitives_nadt_alternate_workspace alternate_scratch;

typedef struct {
    goodix_primitives_nadt_stream_state *stream;
    const goodix_primitives_nadt_primary_configuration *primary;
    goodix_primitives_nadt_auxiliary_configuration auxiliary;
    goodix_primitives_nadt_alternate_configuration alternate;
    bool failed;
} r1_nadt_callbacks;

static volatile uint8_t *native_bytes(void)
{
    return (volatile uint8_t *)&r1_goodix_native_nadt_state;
}

static uint16_t configuration_half(size_t offset)
{
    const volatile uint8_t *const configuration =
        r1_goodix_native_nadt_configuration;
    return (uint16_t)((uint16_t)configuration[offset] |
        ((uint16_t)configuration[offset + 1u] << 8u));
}

static uint32_t configuration_word(size_t offset)
{
    return (uint32_t)configuration_half(offset) |
        ((uint32_t)configuration_half(offset + 2u) << 16u);
}

static float configuration_float(size_t offset)
{
    const uint32_t bits = configuration_word(offset);
    float value;
    memcpy(&value, &bits, sizeof(value));
    return value;
}

static uint8_t classify_primary(void *opaque, const void *primary,
    const void *secondary, int32_t count)
{
    r1_nadt_callbacks *const callbacks = opaque;
    if (callbacks->failed) return 0u;
    /* The stock callback accepts histories shorter than the typed 23-sample
     * filter. Preserve its current classification here; short-history
     * workspace writes still need reconstruction (see NADT root review). */
    if (count < 23) {
        return (uint8_t)callbacks->stream->classifier.current_result;
    }
    goodix_primitives_nadt_alternate_state alternate;
    if (!r1_goodix_nadt_alternate_state_load(native_bytes(), &alternate)) {
        callbacks->failed = true;
        return 0u;
    }
    const int32_t previous = callbacks->stream->classifier.current_result;
    uint8_t classified = (uint8_t)previous;
    if (!goodix_primitives_nadt_primary_signal_classify(
            primary, secondary, (size_t)count, callbacks->primary,
            &callbacks->stream->classifier, &primary_scratch,
            &alternate.autocorrelation, r1_native_roundf, NULL,
            &classified)) {
        callbacks->failed = true;
        return 0u;
    }
    /* Primary writes mode 1 when it first raises classification 3. The
     * shared mode byte is otherwise left for auxiliary/alternate writers. */
    if ((classified & 3u) == 3u && previous != 3 &&
            callbacks->stream->classifier.classification_latched) {
        native_bytes()[1u] = 1u;
    }
    alternate.mode = native_bytes()[1u];
    r1_goodix_nadt_alternate_state_store(native_bytes(), &alternate);
    return classified;
}

static int32_t classify_auxiliary(void *opaque, uint16_t counter)
{
    r1_nadt_callbacks *const callbacks = opaque;
    if (callbacks->failed) return 0;
    goodix_primitives_nadt_auxiliary_state state;
    if (!r1_goodix_nadt_auxiliary_state_load(native_bytes(), &state)) {
        callbacks->failed = true;
        return 0;
    }
    if (state.processing) return state.current_result;
    uint32_t classified = (uint32_t)state.current_result;
    if (!goodix_primitives_nadt_auxiliary_state_classify(
            r1_goodix_native_nadt_workspace.third,
            callbacks->stream->secondary_history_count,
            &callbacks->auxiliary, counter != 0u, &state,
            &auxiliary_scratch, NULL, r1_native_sqrtf, &classified)) {
        callbacks->failed = true;
        return 0;
    }
    r1_goodix_nadt_auxiliary_state_store(native_bytes(), &state);
    return (int32_t)classified;
}

static int32_t classify_alternate(void *opaque)
{
    r1_nadt_callbacks *const callbacks = opaque;
    if (callbacks->failed) return 0;
    goodix_primitives_nadt_alternate_state state;
    if (!r1_goodix_nadt_alternate_state_load(native_bytes(), &state)) {
        callbacks->failed = true;
        return 0;
    }
    if (state.processing) return state.current_result;
    int32_t classified = state.current_result;
    if (!goodix_primitives_nadt_alternate_state_classify(
            r1_goodix_native_nadt_workspace.third,
            callbacks->stream->secondary_history_count,
            &callbacks->alternate, &state, &alternate_scratch, NULL,
            &classified)) {
        callbacks->failed = true;
        return 0;
    }
    r1_goodix_nadt_alternate_state_store(native_bytes(), &state);
    return classified;
}

goodix_nadt_ret goodix_nadt_calc(goodix_nadt_input_rawdata *raw,
    goodix_nadt_result *result)
{
    if (raw == NULL || result == NULL) return GX_ALGO_NADT_RWONG_INPUT;
    volatile uint8_t *const native = native_bytes();
    native[3u] = 0u;
    if (native[0u] != 0xbfu) {
        r1_goodix_native_nadt_state.values[0] = 0u;
        r1_goodix_native_nadt_state.counters[2] = 0u;
        r1_goodix_native_nadt_state.counters[3] = 0u;
        native[11u] = 0u;
        ((volatile goodix_nadt_result *)result)->nadt_out =
            (int32_t)r1_goodix_native_nadt_state.values[1];
        native[3u] = GX_ALGO_NADT_UNINIT;
        return GX_ALGO_NADT_UNINIT;
    }
    if (r1_goodix_native_nadt_state.allocation != NULL) {
        memset(r1_goodix_native_nadt_state.allocation, 0, 52u);
    }
    result->nadt_out_flag = 0;
    const uint16_t sample_rate = configuration_half(0u);
    const uint16_t cadence_divisor = (uint16_t)(sample_rate / 25u);
    const uint16_t next_cadence =
        (uint16_t)(r1_goodix_native_nadt_state.counters[1] + 1u);
    if (cadence_divisor != 0u && next_cadence % cadence_divisor != 0u) {
        r1_goodix_native_nadt_state.counters[1] = next_cadence;
        result->nadt_out = (int32_t)r1_goodix_native_nadt_state.values[1];
        return GX_ALGO_NADT_SUCCESS;
    }

    goodix_primitives_nadt_stream_state stream;
    goodix_primitives_nadt_window_configuration window;
    goodix_primitives_nadt_sample_preparation_state preparation;
    uint8_t *const tail = r1_goodix_native_nadt_workspace.final;
    if (!r1_goodix_nadt_stream_state_load(native, tail, &stream) ||
            !r1_goodix_nadt_window_configuration_load(tail,
                r1_goodix_native_nadt_configuration, &window)) {
        native[3u] = 1u;
        return (goodix_nadt_ret)1;
    }
    r1_goodix_nadt_preparation_state_load(native, &preparation);
    goodix_primitives_nadt_sample_preparation_input sample;
    if (!r1_goodix_nadt_public_sample_view(raw, &sample)) {
        native[3u] = 1u;
        return GX_ALGO_NADT_RWONG_INPUT;
    }
    const goodix_nadt_input_unique *const unique =
        (const goodix_nadt_input_unique *)raw->pst_module_unique;
    int32_t *const integrity_values = raw->data_type != 0u
        ? unique->ch_ipd : raw->ppg_rawdata;
    const size_t stride = raw->total_ch_num;
    if (goodix_primitives_integrity_invalid((uint32_t)integrity_values[0]) ||
            goodix_primitives_integrity_invalid(
                (uint32_t)integrity_values[stride]) ||
            goodix_primitives_integrity_invalid(
                (uint32_t)integrity_values[stride * 2u])) {
        integrity_values[0] = INT32_C(9000000);
        integrity_values[1] = INT32_C(9000000);
        integrity_values[2] = INT32_C(9000000);
    }
    const goodix_primitives_nadt_stream_input input = {
        .sample = &sample,
        .axis_x = raw->acc_x,
        .axis_y = raw->acc_y,
        .axis_z = raw->acc_z,
        .profile = unique == NULL ? 0u : unique->ppg_colour_flg,
        .classifier_suppressed = raw->sleep_flg != 0u,
    };
    goodix_primitives_nadt_primary_configuration primary;
    if (!r1_goodix_nadt_primary_configuration_load(tail,
            r1_goodix_native_nadt_configuration,
            r1_goodix_nadt_primary_boundary_coefficients,
            GOODIX_PRIMITIVES_NADT_PRIMARY_BOUNDARY_COEFFICIENTS,
            &primary)) {
        native[3u] = 1u;
        return (goodix_nadt_ret)1;
    }
    r1_nadt_callbacks callbacks = {
        .stream = &stream,
        .primary = &primary,
    };
    if (!r1_goodix_nadt_auxiliary_configuration_load(
            r1_goodix_native_nadt_configuration, &callbacks.auxiliary) ||
            !r1_goodix_nadt_alternate_configuration_load(
                r1_goodix_native_nadt_configuration, &callbacks.alternate)) {
        native[3u] = 1u;
        return (goodix_nadt_ret)1;
    }
    const goodix_primitives_nadt_window_plan window_plan = {
        .classify_primary = classify_primary,
        .primary_context = &callbacks,
        .classify_auxiliary = classify_auxiliary,
        .auxiliary_context = &callbacks,
        .classify_alternate = classify_alternate,
        .alternate_context = &callbacks,
        .square_root = r1_native_sqrt,
    };
    struct r1_goodix_native_nadt_workspace *const workspace =
        &r1_goodix_native_nadt_workspace;
    goodix_primitives_nadt_optical_transform optical = {
        .numerators = workspace->filter.numerator,
        .numerator_count = 6u,
        .denominators = workspace->filter.denominator,
        .denominator_count = 6u,
        .input_histories = workspace->filter.primary,
        .input_history_count = 4u,
        .output_histories = workspace->filter.secondary,
        .output_history_count = 4u,
        .correction_threshold = workspace->filter.scale,
    };
    const uint16_t rate = configuration_half(0u);
    const uint32_t threshold_bits =
        configuration_word(0x0cu) + configuration_word(0x10u);
    int32_t threshold_sum;
    memcpy(&threshold_sum, &threshold_bits, sizeof(threshold_sum));
    const goodix_primitives_nadt_stream_plan plan = {
        .sample_rate = rate,
        .primary_baseline = INT32_C(0x800000),
        .low_primary_threshold = threshold_sum / 2,
        .ratio_threshold = configuration_float(0x1cu),
        .strong_ratio_threshold = configuration_float(0x20u),
        .window_configuration = &window,
        .window_plan = &window_plan,
        .preparation_state = &preparation,
        .optical_transform = &optical,
        .round_provider = r1_native_round,
        .square_root = r1_native_sqrt,
    };
    const uint16_t cadence = (uint16_t)(rate / 25u);
    const bool processed = cadence != 0u &&
        (uint16_t)(stream.cadence_counter + 1u) % cadence == 0u;
    const goodix_primitives_nadt_stream_workspace_view borrowed =
        r1_goodix_native_nadt_workspace_view();
    goodix_primitives_nadt_stream_output output;
    goodix_primitives_nadt_window_diagnostics window_diagnostics = {0};
    const uint32_t history_lane = native[13u] > 3u ? 3u : native[13u];
    const uint8_t prior_low_primary = native[12u];
    if (!goodix_primitives_nadt_stream_process_view(&input, &plan, &stream,
            &borrowed, &window_diagnostics, &output) || callbacks.failed) {
        native[3u] = 1u;
        return (goodix_nadt_ret)1;
    }
    r1_goodix_nadt_stream_state_store(native, tail, &stream);
    /* Stock finalizes the raw classifier word, before its result flag is
     * packed for the public output. The mode byte can also be written by a
     * classifier callback, so copy it from native state here. */
    if (stream.classifier.current_result == 2 ||
            stream.classifier.current_result == 3) {
        native[9u] = native[1u];
        if (output.sample_prepared) output.quality = native[1u];
        native[44u] = 0u;
        native[45u] = 0u;
        native[46u] = 0u;
        native[47u] = 0u;
    }
    /* Stock 0x6e2fa..0x6e376 keeps signed maxima and minima for the
     * centered primary and raw secondary samples in four lane banks. */
    const uint32_t primary_bits =
        (uint32_t)raw->ppg_rawdata[1] - UINT32_C(0x800000);
    const uint32_t secondary_bits = (uint32_t)raw->ppg_rawdata[2];
    int32_t primary_sample, secondary_sample;
    memcpy(&primary_sample, &primary_bits, sizeof(primary_sample));
    memcpy(&secondary_sample, &secondary_bits, sizeof(secondary_sample));
    /* The native bank receives this sample's count before the 25-sample
     * reset clears state +12. */
    const uint8_t low_primary_for_history = output.window_ready
        ? (uint8_t)(prior_low_primary +
            (primary_sample < plan.low_primary_threshold ? 1u : 0u))
        : native[12u];
    native[60u + history_lane] = low_primary_for_history;
    int32_t *const history = (int32_t *)workspace->history;
    if (output.history_ordinal == 1u) {
        history[history_lane] = primary_sample;
        history[4u + history_lane] = primary_sample;
        history[8u + history_lane] = secondary_sample;
        history[12u + history_lane] = secondary_sample;
    } else {
        if (history[history_lane] < primary_sample)
            history[history_lane] = primary_sample;
        if (history[4u + history_lane] > primary_sample)
            history[4u + history_lane] = primary_sample;
        if (history[8u + history_lane] < secondary_sample)
            history[8u + history_lane] = secondary_sample;
        if (history[12u + history_lane] > secondary_sample)
            history[12u + history_lane] = secondary_sample;
    }
    r1_goodix_nadt_window_configuration_store(tail, &window);
    r1_goodix_nadt_preparation_state_store(native, &preparation);
    if (stream.initialized) result->nadt_out_flag = output.window_ready ? 1 : 0;
    result->nadt_out = output.classification;
    if (processed) result->nadt_confi = output.quality;
    if (r1_goodix_native_nadt_state.allocation != NULL) {
        uint8_t *const allocation = r1_goodix_native_nadt_state.allocation;
        allocation[0] = (uint8_t)stream.classifier.current_result;
        if (output.window_ready) {
            allocation[1] = window_diagnostics.high_variation ? 1u : 0u;
            allocation[2] = window_diagnostics.primary_classification;
            allocation[3] = window_diagnostics.auxiliary_classification;
            allocation[4] = window_diagnostics.alternate_classification;
        }
    }
    return (goodix_nadt_ret)output.status;
}
