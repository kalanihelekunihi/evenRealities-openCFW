/*
 * openR1 checked GH3X2X democode ABI bridge.
 *
 * The executable Goodix algorithm census and goodix_mem implementation now
 * compile from owner-authorized transparent C and are retained in the target
 * image. Those recovered routines expose narrow typed contracts, however,
 * while the public democode drives a large global frame/result ABI. Until a
 * this adapter maps the enabled function IDs, frame layouts, lifetimes, and
 * result sinks onto an R1-owned provider contract. No vendor algorithm archive
 * is linked.
 *
 * The bridge fails closed using the democode's own error codes and never
 * fabricates sensor or biometric data. An unbound/unsupported provider returns
 * GH3X2X_RET_RESOURCE_ERROR. Provider results are copied only after their
 * update flag, bit mask, population count, and bounded 16-word payload agree.
 * Version getters retain the democode's "no_ver" marker when unavailable.
 *   - The frame/transport hooks of the excluded PC-tool upload protocol
 *     drop their payloads; GH3X2X_UprotocolPacketFormat reports a
 *     zero-length packet.
 *   - The ACC/PPG timestamp-sync helpers retain the matched public democode
 *     behavior: empty hooks and a constant-one frame-data flag.
 *
 * This file is compiled only where the pinned vendor tree is available
 * (host vendor-goodix-test and the Nordic SDK/Zephyr images); it includes vendor
 * headers so the stub signatures are checked against the real prototypes.
 */

#include "gh_drv.h"
#include "gh3x2x_demo_algo_call.h"
#include "gh_uprotocol.h"

#include "r1_gh3x2x_algo_bridge.h"
#include "r1_gh3x2x_primitive_adapter.h"

#include <string.h>

_Static_assert(GH3X2X_FUNC_OFFSET_MAX == R1_GH3X2X_ALGO_FUNCTION_COUNT,
               "Goodix function count drift");
_Static_assert(GH3X2X_ALGO_RESULT_MAX_NUM == R1_GH3X2X_ALGO_RESULT_COUNT,
               "Goodix result count drift");
_Static_assert(GH3X2X_FUNC_OFFSET_HR == R1_GH3X2X_ALGO_FUNCTION_HR,
               "Goodix HR function offset drift");
_Static_assert(GH3X2X_FUNC_OFFSET_HRV == R1_GH3X2X_ALGO_FUNCTION_HRV,
               "Goodix HRV function offset drift");
_Static_assert(GH3X2X_FUNC_OFFSET_HSM == R1_GH3X2X_ALGO_FUNCTION_HSM,
               "Goodix HSM function offset drift");
_Static_assert(GH3X2X_FUNC_OFFSET_SPO2 == R1_GH3X2X_ALGO_FUNCTION_SPO2,
               "Goodix SpO2 function offset drift");

static r1_gh3x2x_algo_provider g_algo_provider;
static const STGh3x2xFrameInfo *const *g_algo_frames;
static GU32 g_algo_initialized;
static r1_gh3x2x_algo_result_observer_fn g_result_observer;
static void *g_result_observer_context;
static r1_gh3x2x_algo_frame_observer_fn g_frame_observer;
static void *g_frame_observer_context;

#if (defined(__GNUC__) || defined(__clang__)) && !defined(__APPLE__)
#define R1_GH3X2X_RETAINED_API                                             \
    __attribute__((section(".openr1_goodix_api"), used))
#else
#define R1_GH3X2X_RETAINED_API
#endif

static void gh3x2x_bridge_clear_bytes(void *destination, GU32 length) {
    GU8 *bytes = (GU8 *)destination;
    for (GU32 index = 0u; index < length; ++index) {
        bytes[index] = 0u;
    }
}

R1_GH3X2X_RETAINED_API void r1_gh3x2x_algo_unbind_provider(void) {
    gh3x2x_bridge_clear_bytes(&g_algo_provider,
                              (GU32)sizeof(g_algo_provider));
    g_algo_initialized = 0u;
}

R1_GH3X2X_RETAINED_API void r1_gh3x2x_algo_bind_provider(
    const r1_gh3x2x_algo_provider *provider) {
    r1_gh3x2x_algo_unbind_provider();
    if (provider != GH3X2X_PTR_NULL) {
        g_algo_provider = *provider;
    }
}

R1_GH3X2X_RETAINED_API bool r1_gh3x2x_algo_provider_bound(void) {
    return g_algo_provider.process != GH3X2X_PTR_NULL &&
           g_algo_provider.supported_functions != 0u;
}

R1_GH3X2X_RETAINED_API void r1_gh3x2x_algo_unbind_result_observer(void) {
    g_result_observer = GH3X2X_PTR_NULL;
    g_result_observer_context = GH3X2X_PTR_NULL;
}

R1_GH3X2X_RETAINED_API void r1_gh3x2x_algo_bind_result_observer(
    r1_gh3x2x_algo_result_observer_fn observer, void *context) {
    g_result_observer = observer;
    g_result_observer_context = observer != GH3X2X_PTR_NULL
        ? context : GH3X2X_PTR_NULL;
}

R1_GH3X2X_RETAINED_API bool r1_gh3x2x_algo_result_observer_bound(void) {
    return g_result_observer != GH3X2X_PTR_NULL;
}

R1_GH3X2X_RETAINED_API void r1_gh3x2x_algo_unbind_frame_observer(void) {
    g_frame_observer = GH3X2X_PTR_NULL;
    g_frame_observer_context = GH3X2X_PTR_NULL;
}

R1_GH3X2X_RETAINED_API void r1_gh3x2x_algo_bind_frame_observer(
    r1_gh3x2x_algo_frame_observer_fn observer, void *context) {
    g_frame_observer = observer;
    g_frame_observer_context = observer != GH3X2X_PTR_NULL
        ? context : GH3X2X_PTR_NULL;
}

R1_GH3X2X_RETAINED_API bool r1_gh3x2x_algo_frame_observer_bound(void) {
    return g_frame_observer != GH3X2X_PTR_NULL;
}

static GU8 gh3x2x_bridge_population(GU16 value) {
    GU8 count = 0u;
    while (value != 0u) {
        count = (GU8)(count + (GU8)(value & 1u));
        value = (GU16)(value >> 1u);
    }
    return count;
}

static int32_t gh3x2x_bridge_signed_word(uint32_t value) {
    int32_t result;
    _Static_assert(sizeof(result) == sizeof(value),
                   "Goodix raw sample word width drift");
    memcpy(&result, &value, sizeof(result));
    return result;
}

static uint8_t gh3x2x_bridge_gain_code(uint32_t agc) {
    return (uint8_t)(agc & UINT32_C(0x0f));
}

static uint16_t gh3x2x_bridge_drive_current(uint32_t agc) {
    return (uint16_t)(((agc >> 8u) & UINT32_C(0xff)) +
                      ((agc >> 16u) & UINT32_C(0xff)));
}

static bool gh3x2x_bridge_input_frame_valid(
    const r1_gh3x2x_algo_frame *frame, uint8_t expected_offset) {
    return frame != GH3X2X_PTR_NULL &&
        frame->function_offset == expected_offset &&
        frame->function_mask == ((uint32_t)1u << expected_offset) &&
        frame->raw_values != GH3X2X_PTR_NULL &&
        frame->channel_count != 0u;
}

static void gh3x2x_bridge_input_base(
    const r1_gh3x2x_algo_frame *frame, uint8_t sleep_flag,
    r1_gh3x2x_algo_input *output) {
    gh3x2x_bridge_clear_bytes(output, (GU32)sizeof(*output));
    output->frame_id = (uint8_t)frame->frame_count;
    output->total_channel_count = R1_GH3X2X_ALGO_PRIMARY_CHANNELS;
    output->sleep_flag = sleep_flag;
    output->bit_count = 24u;
    output->chip_type = 1u;
    output->data_type = 0u;
    for (size_t axis = 0u; axis < R1_GH3X2X_ALGO_AXIS_COUNT; ++axis) {
        output->acceleration[axis] = frame->acceleration[axis];
    }
}

R1_GH3X2X_RETAINED_API bool r1_gh3x2x_algo_prepare_hr_mapped_input(
    const r1_gh3x2x_algo_frame *frame,
    const uint8_t channel_map[R1_GH3X2X_ALGO_INPUT_CHANNELS],
    uint8_t scene, uint8_t sleep_flag, r1_gh3x2x_algo_input *output) {
    if (output == GH3X2X_PTR_NULL || channel_map == GH3X2X_PTR_NULL ||
        !gh3x2x_bridge_input_frame_valid(
            frame, R1_GH3X2X_ALGO_FUNCTION_HR)) {
        return false;
    }
    r1_gh3x2x_algo_input prepared;
    gh3x2x_bridge_input_base(frame, sleep_flag, &prepared);
    prepared.scene = scene;
    for (size_t index = 0u;
         index < R1_GH3X2X_ALGO_INPUT_CHANNELS; ++index) {
        const uint8_t source = channel_map[index];
        if (source == UINT8_MAX) {
            continue;
        }
        if (source >= frame->channel_count) {
            return false;
        }
        prepared.channel_values[index] =
            gh3x2x_bridge_signed_word(frame->raw_values[source]);
        prepared.enable_flags[index >> 3u] |=
            (uint8_t)(1u << (7u - (index & 7u)));
    }
    *output = prepared;
    return true;
}

R1_GH3X2X_RETAINED_API bool r1_gh3x2x_algo_hr_default_channel_map(
    uint8_t output[R1_GH3X2X_ALGO_INPUT_CHANNELS]) {
    if (output == GH3X2X_PTR_NULL) {
        return false;
    }
    static const uint8_t recovered[R1_GH3X2X_ALGO_INPUT_CHANNELS] = {
        0u, 1u, 2u, 3u,
        UINT8_MAX, UINT8_MAX, UINT8_MAX, UINT8_MAX,
        UINT8_MAX, UINT8_MAX, UINT8_MAX, UINT8_MAX,
    };
    memcpy(output, recovered, sizeof(recovered));
    return true;
}

R1_GH3X2X_RETAINED_API bool r1_gh3x2x_algo_prepare_hr_input(
    const r1_gh3x2x_algo_frame *frame, uint8_t sleep_flag,
    r1_gh3x2x_algo_input *output) {
    uint8_t channel_map[R1_GH3X2X_ALGO_INPUT_CHANNELS];
    (void)r1_gh3x2x_algo_hr_default_channel_map(channel_map);
    return r1_gh3x2x_algo_prepare_hr_mapped_input(
        frame, channel_map, 0u, sleep_flag, output);
}

R1_GH3X2X_RETAINED_API bool r1_gh3x2x_algo_prepare_hrv_input(
    const r1_gh3x2x_algo_frame *frame, uint8_t last_hr,
    uint8_t sleep_flag, r1_gh3x2x_algo_input *output) {
    if (output == GH3X2X_PTR_NULL ||
        !gh3x2x_bridge_input_frame_valid(
            frame, R1_GH3X2X_ALGO_FUNCTION_HRV) ||
        frame->agc_values == GH3X2X_PTR_NULL ||
        frame->channel_count < R1_GH3X2X_ALGO_PRIMARY_CHANNELS) {
        return false;
    }
    r1_gh3x2x_algo_input prepared;
    gh3x2x_bridge_input_base(frame, sleep_flag, &prepared);
    prepared.last_hr = last_hr;
    for (size_t index = 0u;
         index < R1_GH3X2X_ALGO_PRIMARY_CHANNELS; ++index) {
        prepared.channel_values[index] =
            gh3x2x_bridge_signed_word(frame->raw_values[index]);
        prepared.gain_codes[index] =
            gh3x2x_bridge_gain_code(frame->agc_values[index]);
        prepared.drive_currents[index] =
            gh3x2x_bridge_drive_current(frame->agc_values[index]);
        prepared.enable_flags[index >> 3u] |=
            (uint8_t)(1u << (7u - (index & 7u)));
    }
    *output = prepared;
    return true;
}

R1_GH3X2X_RETAINED_API bool r1_gh3x2x_algo_prepare_spo2_input(
    const r1_gh3x2x_algo_frame *frame,
    const uint8_t channel_map[R1_GH3X2X_ALGO_INPUT_CHANNELS],
    uint8_t sleep_flag, r1_gh3x2x_algo_input *output) {
    if (output == GH3X2X_PTR_NULL || channel_map == GH3X2X_PTR_NULL ||
        !gh3x2x_bridge_input_frame_valid(
            frame, R1_GH3X2X_ALGO_FUNCTION_SPO2) ||
        frame->agc_values == GH3X2X_PTR_NULL) {
        return false;
    }
    r1_gh3x2x_algo_input prepared;
    gh3x2x_bridge_input_base(frame, sleep_flag, &prepared);
    for (size_t index = 0u;
         index < R1_GH3X2X_ALGO_INPUT_CHANNELS; ++index) {
        const uint8_t source = channel_map[index];
        if (source == UINT8_MAX) {
            continue;
        }
        if (source >= frame->channel_count) {
            return false;
        }
        prepared.channel_values[index] =
            gh3x2x_bridge_signed_word(frame->raw_values[source]);
        prepared.gain_codes[index] =
            gh3x2x_bridge_gain_code(frame->agc_values[source]);
        prepared.drive_currents[index] =
            gh3x2x_bridge_drive_current(frame->agc_values[source]);
        prepared.enable_flags[index >> 3u] |=
            (uint8_t)(1u << (7u - (index & 7u)));
    }
    *output = prepared;
    return true;
}

R1_GH3X2X_RETAINED_API bool r1_gh3x2x_algo_spo2_default_channel_map(
    uint8_t output[R1_GH3X2X_ALGO_INPUT_CHANNELS]) {
    if (output == GH3X2X_PTR_NULL) {
        return false;
    }
    static const uint8_t recovered[R1_GH3X2X_ALGO_INPUT_CHANNELS] = {
        UINT8_MAX, UINT8_MAX, UINT8_MAX, UINT8_MAX,
        1u, UINT8_MAX, UINT8_MAX, UINT8_MAX,
        0u, UINT8_MAX, UINT8_MAX, UINT8_MAX,
    };
    memcpy(output, recovered, sizeof(recovered));
    return true;
}

R1_GH3X2X_RETAINED_API bool r1_gh3x2x_algo_bind_hr_primitive_input(
    r1_gh3x2x_algo_input *input, const uint8_t *filter_code,
    size_t filter_code_count,
    goodix_primitives_hba_process_input *primitive) {
    if (input == GH3X2X_PTR_NULL || filter_code == GH3X2X_PTR_NULL ||
        filter_code_count == 0u || primitive == GH3X2X_PTR_NULL ||
        input->total_channel_count != R1_GH3X2X_ALGO_PRIMARY_CHANNELS) {
        return false;
    }
    const goodix_primitives_hba_process_input prepared = {
        .channel_values = input->channel_values,
        .channel_value_count = R1_GH3X2X_ALGO_INPUT_CHANNELS,
        .enable_flags = input->enable_flags,
        .enable_flag_count = R1_GH3X2X_ALGO_INPUT_ENABLE_BYTES,
        .gain_codes = input->gain_codes,
        .gain_code_count = R1_GH3X2X_ALGO_INPUT_CHANNELS,
        .drive_currents = input->drive_currents,
        .drive_current_count = R1_GH3X2X_ALGO_INPUT_CHANNELS,
        .channel_count = R1_GH3X2X_ALGO_PRIMARY_CHANNELS,
        .accelerometer = {
            input->acceleration[0], input->acceleration[1],
            input->acceleration[2],
        },
        .mode = input->sleep_flag,
        .filter_code = filter_code,
        .filter_code_count = filter_code_count,
    };
    *primitive = prepared;
    return true;
}

R1_GH3X2X_RETAINED_API bool r1_gh3x2x_algo_bind_hrv_primitive_input(
    r1_gh3x2x_algo_input *input,
    goodix_primitives_hrv_process_input *primitive) {
    if (input == GH3X2X_PTR_NULL || primitive == GH3X2X_PTR_NULL ||
        input->total_channel_count != R1_GH3X2X_ALGO_PRIMARY_CHANNELS) {
        return false;
    }
    const goodix_primitives_hrv_process_input prepared = {
        .channel_values = input->channel_values,
        .channel_value_count = R1_GH3X2X_ALGO_PRIMARY_CHANNELS,
        .presence_bytes = input->enable_flags,
        .presence_byte_count = 1u,
        .gain_codes = input->gain_codes,
        .gain_code_count = R1_GH3X2X_ALGO_PRIMARY_CHANNELS,
        .drive_currents = input->drive_currents,
        .drive_current_count = R1_GH3X2X_ALGO_PRIMARY_CHANNELS,
        .channel_count = R1_GH3X2X_ALGO_PRIMARY_CHANNELS,
        .last_hr = input->last_hr,
        .axis_x = input->acceleration[0],
        .axis_y = input->acceleration[1],
        .axis_z = input->acceleration[2],
    };
    *primitive = prepared;
    return true;
}

R1_GH3X2X_RETAINED_API bool r1_gh3x2x_algo_bind_spo2_primitive_input(
    r1_gh3x2x_algo_input *input,
    goodix_primitives_spo2_calc_input *primitive) {
    if (input == GH3X2X_PTR_NULL || primitive == GH3X2X_PTR_NULL ||
        input->total_channel_count != R1_GH3X2X_ALGO_PRIMARY_CHANNELS) {
        return false;
    }
    const goodix_primitives_spo2_calc_input prepared = {
        .frame_id = input->frame_id,
        .total_channel_count = input->total_channel_count,
        .enable_flags = input->enable_flags,
        .enable_flag_count = R1_GH3X2X_ALGO_INPUT_ENABLE_BYTES,
        .channel_values = input->channel_values,
        .channel_value_count = R1_GH3X2X_ALGO_INPUT_CHANNELS,
        .gain_codes = input->gain_codes,
        .gain_code_count = R1_GH3X2X_ALGO_INPUT_CHANNELS,
        .drive_currents = input->drive_currents,
        .drive_current_count = R1_GH3X2X_ALGO_INPUT_CHANNELS,
        .acceleration = {
            input->acceleration[0], input->acceleration[1],
            input->acceleration[2],
        },
        .sleep_flag = input->sleep_flag,
        .bit_count = input->bit_count,
        .chip_type = input->chip_type,
        .data_type = input->data_type,
    };
    *primitive = prepared;
    return true;
}

static bool gh3x2x_bridge_frame(GU8 offset,
                                r1_gh3x2x_algo_frame *normalized,
                                STGh3x2xAlgoResult **result) {
    if (normalized == GH3X2X_PTR_NULL ||
        offset >= R1_GH3X2X_ALGO_FUNCTION_COUNT ||
        g_algo_frames == GH3X2X_PTR_NULL ||
        g_algo_frames[offset] == GH3X2X_PTR_NULL) {
        return false;
    }
    const STGh3x2xFrameInfo *frame = g_algo_frames[offset];
    if (frame->pstFunctionInfo == GH3X2X_PTR_NULL ||
        frame->pchChnlMap == GH3X2X_PTR_NULL ||
        frame->punFrameRawdata == GH3X2X_PTR_NULL ||
        frame->punFrameAgcInfo == GH3X2X_PTR_NULL ||
        frame->punFrameFlag == GH3X2X_PTR_NULL ||
        frame->punFrameCnt == GH3X2X_PTR_NULL ||
        frame->pusFrameGsensordata == GH3X2X_PTR_NULL ||
        frame->pstFunctionInfo->uchChnlNum > frame->uchFuntionChnlLimit ||
        frame->pstFunctionInfo->uchChnlNum == 0u ||
        frame->unFunctionID != ((GU32)1u << offset)) {
        return false;
    }

    normalized->function_mask = frame->unFunctionID;
    normalized->function_offset = offset;
    normalized->channel_count = frame->pstFunctionInfo->uchChnlNum;
    normalized->sample_rate_hz = frame->pstFunctionInfo->usSampleRate;
    normalized->channel_map = frame->pchChnlMap;
    normalized->raw_values = frame->punFrameRawdata;
    normalized->agc_values = frame->punFrameAgcInfo;
    normalized->frame_flags = frame->punFrameFlag;
    normalized->frame_flag_count = 8u;
    for (GU8 axis = 0u; axis < R1_GH3X2X_ALGO_AXIS_COUNT; ++axis) {
        normalized->acceleration[axis] = frame->pusFrameGsensordata[axis];
    }
    normalized->frame_count = *frame->punFrameCnt;
    if (result != GH3X2X_PTR_NULL) {
        if (frame->pstAlgoResult == GH3X2X_PTR_NULL) {
            return false;
        }
        *result = frame->pstAlgoResult;
    }
    return true;
}

static bool gh3x2x_bridge_mask_valid(GU32 functions) {
    const GU32 known = ((GU32)1u << R1_GH3X2X_ALGO_FUNCTION_COUNT) - 1u;
    return functions != 0u && (functions & ~known) == 0u;
}

/* Marker written by the real algo-call layer when a version is absent. */
static void gh3x2x_stub_write_no_ver(GCHAR version[150]) {
    static const GCHAR marker[] = "no_ver";
    GU8 index = 0u;
    if (version == GH3X2X_PTR_NULL) {
        return;
    }
    while (marker[index] != '\0') {
        version[index] = marker[index];
        ++index;
    }
    version[index] = '\0';
}

/* --- Algorithm-call ABI entry points --- */

GS8 GH3X2X_AlgoInit(GU32 unFunctionID) {
    if (!gh3x2x_bridge_mask_valid(unFunctionID)) {
        return GH3X2X_RET_PARAMETER_ERROR;
    }
    GS8 status = GH3X2X_RET_OK;
    GU32 initialized_now = 0u;
    for (GU8 offset = 0u; offset < R1_GH3X2X_ALGO_FUNCTION_COUNT; ++offset) {
        const GU32 function = (GU32)1u << offset;
        if ((unFunctionID & function) == 0u ||
            (g_algo_initialized & function) != 0u) {
            continue;
        }
        if (offset != R1_GH3X2X_ALGO_FUNCTION_HSM &&
            (g_algo_provider.initialize == GH3X2X_PTR_NULL ||
             (g_algo_provider.supported_functions & function) == 0u)) {
            status = GH3X2X_RET_RESOURCE_ERROR;
            goto rollback;
        }
        r1_gh3x2x_algo_frame frame;
        if (!gh3x2x_bridge_frame(offset, &frame, GH3X2X_PTR_NULL)) {
            status = GH3X2X_RET_GENERIC_ERROR;
            goto rollback;
        }
        if (offset == R1_GH3X2X_ALGO_FUNCTION_HSM) {
            initialized_now |= function;
            continue;
        }
        if (!g_algo_provider.initialize(g_algo_provider.context, &frame)) {
            status = GH3X2X_RET_GENERIC_ERROR;
            goto rollback;
        }
        initialized_now |= function;
    }
    g_algo_initialized |= initialized_now;
    return GH3X2X_RET_OK;

rollback:
    if (g_algo_provider.deinitialize != GH3X2X_PTR_NULL) {
        for (GU8 rollback_offset = 0u;
             rollback_offset < R1_GH3X2X_ALGO_FUNCTION_COUNT;
             ++rollback_offset) {
            const GU32 rollback_function = (GU32)1u << rollback_offset;
            if (rollback_offset != R1_GH3X2X_ALGO_FUNCTION_HSM &&
                (initialized_now & rollback_function) != 0u) {
                (void)g_algo_provider.deinitialize(
                    g_algo_provider.context, rollback_function,
                    rollback_offset);
            }
        }
    }
    return status;
}

GS8 GH3X2X_AlgoDeinit(GU32 unFunctionID) {
    if (!gh3x2x_bridge_mask_valid(unFunctionID)) {
        return GH3X2X_RET_PARAMETER_ERROR;
    }
    for (GU8 offset = 0u; offset < R1_GH3X2X_ALGO_FUNCTION_COUNT; ++offset) {
        const GU32 function = (GU32)1u << offset;
        if ((unFunctionID & function) != 0u &&
            (g_algo_initialized & function) != 0u) {
            if (offset == R1_GH3X2X_ALGO_FUNCTION_HSM) {
                g_algo_initialized &= ~function;
                continue;
            }
            if (g_algo_provider.deinitialize == GH3X2X_PTR_NULL) {
                return GH3X2X_RET_RESOURCE_ERROR;
            }
            if (!g_algo_provider.deinitialize(g_algo_provider.context,
                                              function, offset)) {
                return GH3X2X_RET_GENERIC_ERROR;
            }
            g_algo_initialized &= ~function;
        }
    }
    return GH3X2X_RET_OK;
}

GS8 GH3X2X_AlgoCalculate(GU32 unFunctionID) {
    if (!gh3x2x_bridge_mask_valid(unFunctionID)) {
        return GH3X2X_RET_PARAMETER_ERROR;
    }
    if ((unFunctionID & g_algo_initialized) != unFunctionID) {
        return GH3X2X_RET_RESOURCE_ERROR;
    }
    for (GU8 offset = 0u; offset < R1_GH3X2X_ALGO_FUNCTION_COUNT; ++offset) {
        const GU32 function = (GU32)1u << offset;
        if ((unFunctionID & function) == 0u) {
            continue;
        }
        r1_gh3x2x_algo_frame frame;
        if (offset == R1_GH3X2X_ALGO_FUNCTION_HSM) {
            if (!gh3x2x_bridge_frame(offset, &frame, GH3X2X_PTR_NULL)) {
                return GH3X2X_RET_GENERIC_ERROR;
            }
            if (g_frame_observer != GH3X2X_PTR_NULL) {
                g_frame_observer(g_frame_observer_context, &frame);
            }
            continue;
        }
        if (g_algo_provider.process == GH3X2X_PTR_NULL ||
            (g_algo_provider.supported_functions & function) == 0u) {
            return GH3X2X_RET_RESOURCE_ERROR;
        }
        r1_gh3x2x_algo_result result;
        STGh3x2xAlgoResult *vendor_result = GH3X2X_PTR_NULL;
        gh3x2x_bridge_clear_bytes(&result, (GU32)sizeof(result));
        if (!gh3x2x_bridge_frame(offset, &frame, &vendor_result) ||
            !g_algo_provider.process(g_algo_provider.context, &frame,
                                     &result)) {
            return GH3X2X_RET_GENERIC_ERROR;
        }
        if ((!result.updated && (result.value_count != 0u ||
                                 result.value_mask != 0u)) ||
            result.value_count > R1_GH3X2X_ALGO_RESULT_COUNT ||
            result.value_count !=
                gh3x2x_bridge_population(result.value_mask)) {
            return GH3X2X_RET_PARAMETER_ERROR;
        }
        gh3x2x_bridge_clear_bytes(vendor_result,
                                  (GU32)sizeof(*vendor_result));
        if (result.updated) {
            vendor_result->uchUpdateFlag = 1u;
            vendor_result->uchResultNum = result.value_count;
            vendor_result->usResultBit = result.value_mask;
            for (GU8 index = 0u; index < result.value_count; ++index) {
                vendor_result->snResult[index] = result.values[index];
            }
            if (g_result_observer != GH3X2X_PTR_NULL) {
                g_result_observer(
                    g_result_observer_context, &frame, &result);
            }
        }
    }
    return GH3X2X_RET_OK;
}

void GH3X2X_AlgoSensorEnable(GU8 uchAlgoGsensorEnable, GU8 uchAlgoCapEnable,
                             GU8 uchAlgoTempEnable) {
    if (g_algo_provider.sensor_enable != GH3X2X_PTR_NULL) {
        g_algo_provider.sensor_enable(g_algo_provider.context,
                                      uchAlgoGsensorEnable != 0u,
                                      uchAlgoCapEnable != 0u,
                                      uchAlgoTempEnable != 0u);
    }
}

void GH3X2X_AlgoVersion(GU8 uchFunctionID, GCHAR version[150]) {
    if (version == GH3X2X_PTR_NULL ||
        uchFunctionID >= R1_GH3X2X_ALGO_FUNCTION_COUNT ||
        g_algo_provider.version == GH3X2X_PTR_NULL ||
        (g_algo_provider.supported_functions &
         ((GU32)1u << uchFunctionID)) == 0u ||
        !g_algo_provider.version(g_algo_provider.context, uchFunctionID,
                                 (char *)version, 150u)) {
        gh3x2x_stub_write_no_ver(version);
    } else {
        version[149] = '\0';
    }
}

void GH3X2X_AlgoCallConfigInit(
    const STGh3x2xFrameInfo *const pstGh3x2xFrameInfo[],
    GU8 uchAlgoCfgIndex) {
    g_algo_frames = pstGh3x2xFrameInfo;
    UNUSED_VAR(uchAlgoCfgIndex);
}

void GH3X2X_WriteAlgConfigWithVirtualReg(GU16 usVirtualRegAddr,
                                         GU16 usVirtualRegValue) {
    if (g_algo_provider.write_virtual_register != GH3X2X_PTR_NULL) {
        (void)g_algo_provider.write_virtual_register(
            g_algo_provider.context, usVirtualRegAddr, usVirtualRegValue);
    }
}

/* --- ACC/PPG timestamp sync helpers (algorithm-call layer, absent) --- */

void GH3X2X_TimestampSyncAccInit(void) {
}

void GH3X2X_TimestampSyncPpgInit(GU32 unFunctionID) {
    UNUSED_VAR(unFunctionID);
}

void GH3X2X_TimestampSyncSetPpgIntFlag(GU8 uchPpgIntFlag) {
    UNUSED_VAR(uchPpgIntFlag);
}

void GH3X2X_TimestampSyncFillAccSyncBuffer(GU32 unTimeStamp, GS16 usAccX,
                                           GS16 usAccY, GS16 usAccZ) {
    UNUSED_VAR(unTimeStamp);
    UNUSED_VAR(usAccX);
    UNUSED_VAR(usAccY);
    UNUSED_VAR(usAccZ);
}

void GH3X2X_TimestampSyncFillPpgSyncBuffer(
    GU32 unTimeStamp, const STGh3x2xFrameInfo *const pstFrameInfo) {
    UNUSED_VAR(unTimeStamp);
    UNUSED_VAR(pstFrameInfo);
}

GU8 GH3X2X_TimestampSyncGetFrameDataFlag(void) {
    /* Exact public-democode/recovered body at 0x0002AE00. */
    return 1u;
}

/* --- PC-tool upload protocol (module/gh_protocol, kernel/gh_demo_protocol;
 *      excluded from the openR1 build: no external command surface) --- */

GU8 GH3X2X_UprotocolPacketFormat(GU8 uchCmd, GU8 *puchPacketBuffer,
                                 GU8 *puchPayloadData,
                                 GU8 uchPayloadDataLen) {
    UNUSED_VAR(uchCmd);
    UNUSED_VAR(puchPacketBuffer);
    UNUSED_VAR(puchPayloadData);
    UNUSED_VAR(uchPayloadDataLen);
    return 0u; /* zero-length packet: nothing to transmit */
}

void Gh2x2xUploadDataToMaster(const STGh3x2xFrameInfo *const pstFrameInfo,
                              GU16 usFrameCnt, GU16 usFrameNum,
                              GU8 *puchTagArray) {
    UNUSED_VAR(pstFrameInfo);
    UNUSED_VAR(usFrameCnt);
    UNUSED_VAR(usFrameNum);
    UNUSED_VAR(puchTagArray);
}

void Gh3x2xDemoSendProtocolData(GU8 *puchProtocolDataBuffer,
                                GU16 usProtocolDataLen) {
    UNUSED_VAR(puchProtocolDataBuffer);
    UNUSED_VAR(usProtocolDataLen);
}

void GH3X2X_GetVersion(GU8 uchGetVersionType, GCHAR pszVersionString[150]) {
    UNUSED_VAR(uchGetVersionType);
    gh3x2x_stub_write_no_ver(pszVersionString);
}
