/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room Touch application core. Object storage and every resident or
 * platform operation are supplied explicitly by the caller.
 */
#include <stddef.h>
#include <stdint.h>

#include "runtime_touch_application_core.h"

enum {
    OPEN_CFW_TOUCH_SAMPLE_STRIDE = 10,
    OPEN_CFW_TOUCH_REFERENCE_HZ = 1000000,
};

static uint32_t divide_u32(uint32_t numerator, uint32_t denominator)
{
    uint32_t quotient = 0U;
    uint32_t remainder = 0U;
    uint32_t bit = 32U;

    while (bit != 0U) {
        --bit;
        remainder = (remainder << 1U) | ((numerator >> bit) & 1U);
        if (remainder >= denominator) {
            remainder -= denominator;
            quotient |= UINT32_C(1) << bit;
        }
    }
    return quotient;
}

void open_cfw_touch_application_1b6c_update(
    uint32_t index, void *object,
    const open_cfw_touch_application_core_provider *provider)
{
    open_cfw_touch_application_record_view *record;
    uint32_t sample_index;
    uint32_t coefficient_stride;

    if (object == NULL || provider == NULL || provider->record_at == NULL) {
        return;
    }
    record = provider->record_at(provider->provider_context, index, object);
    if (record == NULL || record->lifecycle == 7U || record->samples == NULL ||
            record->coefficients == NULL) {
        return;
    }
    coefficient_stride = record->flags & 0x0FU;
    for (sample_index = 0U; sample_index < record->sample_count;
            ++sample_index) {
        uint8_t *sample = &record->samples[
            sample_index * OPEN_CFW_TOUCH_SAMPLE_STRIDE];
        uint8_t *coefficients = &record->coefficients[
            sample_index * coefficient_stride * 2U];
        uint8_t *mode_byte = NULL;

        if ((record->flags & UINT16_C(0x0300)) == UINT16_C(0x0200) &&
                record->mode_bytes != NULL) {
            mode_byte = &record->mode_bytes[sample_index];
        }
        if ((record->flags & UINT16_C(0x0010)) != 0U &&
                provider->apply_four != NULL) {
            provider->apply_four(provider->provider_context, record,
                                 sample, coefficients);
            coefficients += 4U;
        }
        if ((record->flags & UINT16_C(0x0080)) != 0U &&
                provider->apply_two != NULL) {
            provider->apply_two(provider->provider_context, record,
                                sample, coefficients, mode_byte);
            coefficients += 2U;
        }
        if ((record->flags & UINT16_C(0x0400)) != 0U &&
                provider->apply_final != NULL) {
            provider->apply_final(provider->provider_context, record,
                                  sample, coefficients);
        }
    }
}

uint32_t open_cfw_touch_application_2638_dispatch(
    uint32_t index, void *object,
    const open_cfw_touch_application_core_provider *provider)
{
    open_cfw_touch_application_record_view *record;
    uint32_t coefficient_stride;
    uint32_t result = 0U;
    uint32_t sample_index;

    if (object == NULL || provider == NULL || provider->record_at == NULL ||
            provider->prepare_sample == NULL ||
            provider->process_sample == NULL ||
            provider->finish_sample == NULL) {
        return 0U;
    }
    record = provider->record_at(provider->provider_context, index, object);
    if (record == NULL || record->samples == NULL || record->auxiliary == NULL ||
            record->coefficients == NULL) {
        return 0U;
    }
    coefficient_stride = record->flags & 0x0FU;
    for (sample_index = 0U; sample_index < record->sample_count;
            ++sample_index) {
        uint8_t *sample = &record->samples[
            sample_index * OPEN_CFW_TOUCH_SAMPLE_STRIDE];
        uint8_t *coefficients = &record->coefficients[
            sample_index * coefficient_stride * 2U];
        uint8_t *mode_byte = NULL;

        if ((record->flags & UINT16_C(0x0300)) == UINT16_C(0x0200) &&
                record->mode_bytes != NULL) {
            mode_byte = &record->mode_bytes[sample_index];
        }
        provider->prepare_sample(provider->provider_context, record, sample,
                                 coefficients, mode_byte);
        result |= provider->process_sample(
            provider->provider_context, record->algorithm, sample,
            &record->auxiliary[sample_index], object);
        provider->finish_sample(
            provider->provider_context, record->algorithm, sample);
    }
    return result;
}

uint32_t open_cfw_touch_application_18a8_process(
    uint32_t index, void *object,
    const open_cfw_touch_application_core_provider *provider)
{
    open_cfw_touch_application_record_view *record;
    uint32_t result;

    if (index > 2U || object == NULL || provider == NULL ||
            provider->record_at == NULL || provider->object_exists == NULL ||
            provider->update_pointer == NULL) {
        return 1U;
    }
    record = provider->record_at(provider->provider_context, index, object);
    if (record == NULL || record->lifecycle == 7U) {
        return 1U;
    }
    if (provider->object_exists(provider->provider_context, index, object) == 0U) {
        return 8U;
    }
    provider->update_pointer(provider->provider_context, index, object);
    result = open_cfw_touch_application_2638_dispatch(index, object, provider);
    if (record->mode != 1U) {
        result |= 1U;
    } else if (provider->selection_update != NULL) {
        provider->selection_update(
            provider->provider_context, record, object);
    }
    return result;
}

uint32_t open_cfw_touch_application_17f4_run(
    void *object, volatile uint32_t *control_flags, uint8_t *busy,
    uint32_t timebase_hz,
    const open_cfw_touch_application_run_provider *provider)
{
    uint32_t result;
    uint32_t retry_count;
    uint32_t index;

    if (object == NULL || control_flags == NULL || busy == NULL ||
            provider == NULL || provider->notify == NULL ||
            provider->preflight == NULL || provider->stage_a == NULL ||
            provider->stage_b == NULL || provider->stage_c == NULL ||
            provider->retry_budget == NULL || provider->poll == NULL ||
            provider->update_pointer == NULL || provider->update_all == NULL ||
            provider->shutdown == NULL) {
        return UINT32_C(0xFFFFFFFF);
    }
    *control_flags |= UINT32_C(0x00008000);
    *busy = 0U;
    provider->notify(provider->provider_context, 1U, object);
    result = provider->preflight(provider->provider_context, object);
    if (result == 0U) {
        result |= provider->stage_a(provider->provider_context, object);
        result |= provider->stage_b(provider->provider_context, object);
        result |= provider->stage_c(provider->provider_context, object);
        retry_count = provider->retry_budget(
            provider->provider_context, OPEN_CFW_TOUCH_REFERENCE_HZ,
            divide_u32(timebase_hz, OPEN_CFW_TOUCH_REFERENCE_HZ), 5U);
        while (provider->poll(provider->provider_context, object) != 0U) {
            if (retry_count == 0U) {
                result = 4U;
                break;
            }
            --retry_count;
        }
        *busy = 1U;
        provider->notify(provider->provider_context, 1U, object);
        for (index = 0U; index < 3U; ++index) {
            provider->update_pointer(
                provider->provider_context, index, object);
        }
    }
    provider->update_all(provider->provider_context, object);
    provider->shutdown(provider->provider_context, object);
    *control_flags &= UINT32_C(0xFFFF7FFF);
    return result;
}
