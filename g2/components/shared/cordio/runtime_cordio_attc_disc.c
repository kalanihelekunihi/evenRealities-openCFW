/* SPDX-License-Identifier: Apache-2.0 */

#include "runtime_cordio_attc_disc.h"

#if !defined(OPEN_CFW_ATTC_DISC_UUID_COMPARE_ONLY) && \
    !defined(OPEN_CFW_ATTC_DISC_VERIFY_ONLY) && \
    !defined(OPEN_CFW_ATTC_DISC_DESCRIPTORS_ONLY) && \
    !defined(OPEN_CFW_ATTC_DISC_DESCRIPTOR_PAIR_ONLY) && \
    !defined(OPEN_CFW_ATTC_DISC_DESCRIPTOR_ONLY) && \
    !defined(OPEN_CFW_ATTC_DISC_CHAR_DECL_ONLY) && \
    !defined(OPEN_CFW_ATTC_DISC_CHARACTERISTIC_ONLY) && \
    !defined(OPEN_CFW_ATTC_DISC_CONFIG_NEXT_ONLY) && \
    !defined(OPEN_CFW_ATTC_DISC_INCLUDED_SERVICE_ONLY) && \
    !defined(OPEN_CFW_ATTC_DISC_SERVICE_START_ONLY) && \
    !defined(OPEN_CFW_ATTC_DISC_SERVICE_COMPLETE_ONLY) && \
    !defined(OPEN_CFW_ATTC_DISC_CHAR_START_ONLY) && \
    !defined(OPEN_CFW_ATTC_DISC_CHAR_COMPLETE_ONLY) && \
    !defined(OPEN_CFW_ATTC_DISC_INC_START_ONLY) && \
    !defined(OPEN_CFW_ATTC_DISC_INC_COMPLETE_ONLY) && \
    !defined(OPEN_CFW_ATTC_DISC_CONFIG_START_ONLY) && \
    !defined(OPEN_CFW_ATTC_DISC_CONFIG_COMPLETE_ONLY) && \
    !defined(OPEN_CFW_ATTC_DISC_CONFIG_RESUME_ONLY)
#define OPEN_CFW_ATTC_DISC_BUILD_ALL 1
#endif

#ifdef OPEN_CFW_ATTC_DISC_PRODUCTION
#define OPEN_CFW_ATTC_DISC_CHARACTERISTIC_UUID ((uint8_t *)0x0078F53EU)
#else
#define OPEN_CFW_ATTC_DISC_CHARACTERISTIC_UUID \
    open_cfw_cordio_attc_discovery_characteristic_uuid
#endif

static __attribute__((unused)) uint16_t open_cfw_cordio_attc_disc_u16(
    const uint8_t *value
)
{
    return (uint16_t)value[0] | ((uint16_t)value[1] << 8);
}

static __attribute__((unused)) void open_cfw_cordio_attc_disc_zero(
    uint16_t *handles, uint8_t count
)
{
    while (count != 0U) {
        *handles++ = 0U;
        count--;
    }
}

static __attribute__((unused)) uint8_t open_cfw_cordio_attc_disc_valid(
    struct open_cfw_cordio_attc_discovery_control_block *control
)
{
    return (uint8_t)(control != NULL && control->characteristics != NULL
        && control->handles != NULL);
}

#if defined(OPEN_CFW_ATTC_DISC_BUILD_ALL) || defined(OPEN_CFW_ATTC_DISC_UUID_COMPARE_ONLY)
__attribute__((used, noinline)) uint8_t
open_cfw_cordio_attc_discovery_uuid_compare(
    struct open_cfw_cordio_attc_discovery_characteristic *characteristic,
    uint8_t *uuid, uint8_t settings
)
{
    uint8_t index, length;
    if (characteristic == NULL || characteristic->uuid == NULL || uuid == NULL) {
        return 0U;
    }
    if ((characteristic->settings & OPEN_CFW_ATTC_DISC_UUID128) == settings) {
        length = settings == 0U ? OPEN_CFW_ATTC_DISC_UUID16_LENGTH
            : OPEN_CFW_ATTC_DISC_UUID128_LENGTH;
        for (index = 0U; index < length; index++) {
            if (characteristic->uuid[index] != uuid[index]) {
                return 0U;
            }
        }
        return 1U;
    }
    if (settings == OPEN_CFW_ATTC_DISC_UUID128
        && (characteristic->settings & OPEN_CFW_ATTC_DISC_UUID128) == 0U) {
        return open_cfw_cordio_att_uuid_compare_16_to_128(
            characteristic->uuid, uuid
        );
    }
    return 0U;
}
#endif

#if defined(OPEN_CFW_ATTC_DISC_BUILD_ALL) || defined(OPEN_CFW_ATTC_DISC_VERIFY_ONLY)
__attribute__((used, noinline)) uint8_t open_cfw_cordio_attc_discovery_verify(
    struct open_cfw_cordio_attc_discovery_control_block *control
)
{
    uint8_t index;
    if (!open_cfw_cordio_attc_disc_valid(control)) {
        return OPEN_CFW_ATTC_DISC_ERROR_INVALID_RESPONSE;
    }
    for (index = 0U; index < control->characteristic_count; index++) {
        if (control->characteristics[index] == NULL) {
            return OPEN_CFW_ATTC_DISC_ERROR_INVALID_RESPONSE;
        }
        if ((control->characteristics[index]->settings
                & OPEN_CFW_ATTC_DISC_REQUIRED) != 0U
            && control->handles[index] == 0U) {
            return OPEN_CFW_ATTC_DISC_ERROR_REQUIRED_NOT_FOUND;
        }
    }
    return OPEN_CFW_ATTC_DISC_SUCCESS;
}
#endif

#if defined(OPEN_CFW_ATTC_DISC_BUILD_ALL) || defined(OPEN_CFW_ATTC_DISC_DESCRIPTORS_ONLY)
__attribute__((used, noinline)) uint8_t
open_cfw_cordio_attc_discovery_descriptors(
    uint8_t connection_id,
    struct open_cfw_cordio_attc_discovery_control_block *control
)
{
    uint16_t start_handle, end_handle;
    if (!open_cfw_cordio_attc_disc_valid(control)
        || control->characteristic_index > control->characteristic_count) {
        return OPEN_CFW_ATTC_DISC_ERROR_INVALID_RESPONSE;
    }
    while (control->characteristic_index < control->characteristic_count) {
        uint8_t index = control->characteristic_index;
        struct open_cfw_cordio_attc_discovery_characteristic *item =
            control->characteristics[index];
        if (item == NULL) {
            return OPEN_CFW_ATTC_DISC_ERROR_INVALID_RESPONSE;
        }
        if ((item->settings & OPEN_CFW_ATTC_DISC_DESCRIPTOR) != 0U) {
            if (index == 0U || control->handles[index-1U] == 0U) {
                return OPEN_CFW_ATTC_DISC_ERROR_INVALID_RESPONSE;
            }
            start_handle = (uint16_t)(control->handles[index-1U] + 1U);
            end_handle = control->handles[index];
            control->handles[index] = 0U;
            if (start_handle != 0U && start_handle <= end_handle) {
                open_cfw_cordio_attc_find_information_request(
                    connection_id, start_handle, end_handle, 1U
                );
                return OPEN_CFW_ATTC_DISC_CONTINUING;
            }
            do {
                control->characteristic_index++;
                if (control->characteristic_index >=
                    control->characteristic_count) {
                    break;
                }
                item = control->characteristics[
                    control->characteristic_index];
                if (item == NULL) {
                    return OPEN_CFW_ATTC_DISC_ERROR_INVALID_RESPONSE;
                }
            } while ((item->settings & OPEN_CFW_ATTC_DISC_DESCRIPTOR) != 0U);
        } else {
            control->characteristic_index++;
        }
    }
    return open_cfw_cordio_attc_discovery_verify(control);
}
#endif

#if defined(OPEN_CFW_ATTC_DISC_BUILD_ALL) || defined(OPEN_CFW_ATTC_DISC_DESCRIPTOR_PAIR_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_attc_discovery_process_descriptor_pair(
    struct open_cfw_cordio_attc_discovery_control_block *control,
    uint8_t settings, uint8_t *pair
)
{
    uint16_t handle;
    uint8_t index;
    if (!open_cfw_cordio_attc_disc_valid(control) || pair == NULL) {
        return;
    }
    handle = open_cfw_cordio_attc_disc_u16(pair);
    pair += 2U;
    for (index = control->characteristic_index;
         index < control->characteristic_count; index++) {
        struct open_cfw_cordio_attc_discovery_characteristic *item =
            control->characteristics[index];
        if (item == NULL
            || (item->settings & OPEN_CFW_ATTC_DISC_DESCRIPTOR) == 0U) {
            break;
        }
        if (control->handles[index] == 0U
            && open_cfw_cordio_attc_discovery_uuid_compare(
                item, pair, settings)) {
            control->handles[index] = handle;
            break;
        }
    }
}
#endif

#if defined(OPEN_CFW_ATTC_DISC_BUILD_ALL) || defined(OPEN_CFW_ATTC_DISC_DESCRIPTOR_ONLY)
__attribute__((used, noinline)) uint8_t
open_cfw_cordio_attc_discovery_process_descriptor(
    struct open_cfw_cordio_attc_discovery_control_block *control,
    struct open_cfw_cordio_att_event *event
)
{
    uint8_t *input, settings, pair_length;
    uint16_t remaining;
    if (!open_cfw_cordio_attc_disc_valid(control) || event == NULL
        || control->characteristic_index >= control->characteristic_count) {
        return OPEN_CFW_ATTC_DISC_ERROR_INVALID_RESPONSE;
    }
    if (event->header.status == 0U) {
        if (event->value == NULL || event->value_length < 1U) {
            return OPEN_CFW_ATTC_DISC_ERROR_INVALID_RESPONSE;
        }
        input = event->value;
        if (*input++ == OPEN_CFW_ATTC_DISC_FIND_FORMAT_UUID16) {
            settings = 0U;
            pair_length = OPEN_CFW_ATTC_DISC_FIND_PAIR_UUID16;
        } else if (event->value[0] ==
            OPEN_CFW_ATTC_DISC_FIND_FORMAT_UUID128) {
            settings = OPEN_CFW_ATTC_DISC_UUID128;
            pair_length = OPEN_CFW_ATTC_DISC_FIND_PAIR_UUID128;
        } else {
            return OPEN_CFW_ATTC_DISC_ERROR_INVALID_RESPONSE;
        }
        remaining = (uint16_t)(event->value_length-1U);
        if (remaining == 0U || remaining % pair_length != 0U) {
            return OPEN_CFW_ATTC_DISC_ERROR_INVALID_RESPONSE;
        }
        while (remaining != 0U) {
            open_cfw_cordio_attc_discovery_process_descriptor_pair(
                control, settings, input
            );
            input += pair_length;
            remaining = (uint16_t)(remaining-pair_length);
        }
    }
    if (event->header.status != 0U || event->continuing == 0U) {
        do {
            control->characteristic_index++;
            if (control->characteristic_index >=
                control->characteristic_count) {
                break;
            }
            if (control->characteristics[
                    control->characteristic_index] == NULL) {
                return OPEN_CFW_ATTC_DISC_ERROR_INVALID_RESPONSE;
            }
        } while ((control->characteristics[control->characteristic_index]
                ->settings & OPEN_CFW_ATTC_DISC_DESCRIPTOR) != 0U);
        if (event->header.parameter > 0xFFU) {
            return OPEN_CFW_ATTC_DISC_ERROR_INVALID_RESPONSE;
        }
        return open_cfw_cordio_attc_discovery_descriptors(
            (uint8_t)event->header.parameter, control
        );
    }
    return OPEN_CFW_ATTC_DISC_CONTINUING;
}
#endif

#if defined(OPEN_CFW_ATTC_DISC_BUILD_ALL) || defined(OPEN_CFW_ATTC_DISC_CHAR_DECL_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_attc_discovery_process_characteristic_declaration(
    struct open_cfw_cordio_attc_discovery_control_block *control,
    uint8_t settings, uint8_t *declaration
)
{
    uint16_t declaration_handle, value_handle;
    uint8_t index;
    if (!open_cfw_cordio_attc_disc_valid(control) || declaration == NULL) {
        return;
    }
    declaration_handle = open_cfw_cordio_attc_disc_u16(declaration);
    value_handle = open_cfw_cordio_attc_disc_u16(declaration+3U);
    if (control->end_handle_index != OPEN_CFW_ATTC_DISC_INDEX_NONE) {
        if (control->end_handle_index >= control->characteristic_count
            || declaration_handle == 0U) {
            control->end_handle_index = OPEN_CFW_ATTC_DISC_INDEX_NONE;
            return;
        }
        control->handles[control->end_handle_index] =
            (uint16_t)(declaration_handle-1U);
        control->end_handle_index = OPEN_CFW_ATTC_DISC_INDEX_NONE;
    }
    if (value_handle <= declaration_handle
        || value_handle > control->service_end_handle) {
        return;
    }
    for (index = 0U; index < control->characteristic_count; index++) {
        struct open_cfw_cordio_attc_discovery_characteristic *item =
            control->characteristics[index];
        if (item == NULL) {
            return;
        }
        if (control->handles[index] == 0U
            && open_cfw_cordio_attc_discovery_uuid_compare(
                item, declaration+5U, settings)) {
            control->handles[index] = value_handle;
            if ((uint8_t)(index+1U) < control->characteristic_count
                && control->characteristics[index+1U] != NULL
                && (control->characteristics[index+1U]->settings
                    & OPEN_CFW_ATTC_DISC_DESCRIPTOR) != 0U) {
                control->end_handle_index = (uint8_t)(index+1U);
            }
            break;
        }
    }
}
#endif

#if defined(OPEN_CFW_ATTC_DISC_BUILD_ALL) || defined(OPEN_CFW_ATTC_DISC_CHARACTERISTIC_ONLY)
__attribute__((used, noinline)) uint8_t
open_cfw_cordio_attc_discovery_process_characteristic(
    struct open_cfw_cordio_attc_discovery_control_block *control,
    struct open_cfw_cordio_att_event *event
)
{
    uint8_t *input, pair_length, settings;
    uint16_t remaining;
    if (!open_cfw_cordio_attc_disc_valid(control) || event == NULL) {
        return OPEN_CFW_ATTC_DISC_ERROR_INVALID_RESPONSE;
    }
    if (event->header.status == 0U) {
        if (event->value == NULL || event->value_length < 1U) {
            return OPEN_CFW_ATTC_DISC_ERROR_INVALID_RESPONSE;
        }
        input = event->value;
        pair_length = *input++;
        if (pair_length == OPEN_CFW_ATTC_DISC_CHAR_PAIR_UUID16) {
            settings = 0U;
        } else if (pair_length == OPEN_CFW_ATTC_DISC_CHAR_PAIR_UUID128) {
            settings = OPEN_CFW_ATTC_DISC_UUID128;
        } else {
            return OPEN_CFW_ATTC_DISC_ERROR_INVALID_RESPONSE;
        }
        remaining = (uint16_t)(event->value_length-1U);
        if (remaining == 0U || remaining % pair_length != 0U) {
            return OPEN_CFW_ATTC_DISC_ERROR_INVALID_RESPONSE;
        }
        while (remaining != 0U) {
            open_cfw_cordio_attc_discovery_process_characteristic_declaration(
                control, settings, input
            );
            input += pair_length;
            remaining = (uint16_t)(remaining-pair_length);
        }
    }
    if (event->header.status != 0U || event->continuing == 0U) {
        if (control->end_handle_index != OPEN_CFW_ATTC_DISC_INDEX_NONE) {
            if (control->end_handle_index >= control->characteristic_count) {
                return OPEN_CFW_ATTC_DISC_ERROR_INVALID_RESPONSE;
            }
            control->handles[control->end_handle_index] =
                control->service_end_handle;
        }
        control->characteristic_index = 0U;
        if (event->header.parameter > 0xFFU) {
            return OPEN_CFW_ATTC_DISC_ERROR_INVALID_RESPONSE;
        }
        return open_cfw_cordio_attc_discovery_descriptors(
            (uint8_t)event->header.parameter, control
        );
    }
    return OPEN_CFW_ATTC_DISC_CONTINUING;
}
#endif

#if defined(OPEN_CFW_ATTC_DISC_BUILD_ALL) || defined(OPEN_CFW_ATTC_DISC_CONFIG_NEXT_ONLY)
__attribute__((used, noinline)) uint8_t
open_cfw_cordio_attc_discovery_configuration_next(
    uint8_t connection_id,
    struct open_cfw_cordio_attc_discovery_control_block *control
)
{
    if (!open_cfw_cordio_attc_disc_valid(control)
        || (control->configuration_count != 0U
            && control->configuration == NULL)
        || control->characteristic_index > control->configuration_count) {
        return OPEN_CFW_ATTC_DISC_ERROR_INVALID_RESPONSE;
    }
    while (control->characteristic_index < control->configuration_count) {
        struct open_cfw_cordio_attc_discovery_configuration *item =
            &control->configuration[control->characteristic_index];
        if (item->handle_index >= control->characteristic_count) {
            return OPEN_CFW_ATTC_DISC_ERROR_INVALID_RESPONSE;
        }
        if (control->handles[item->handle_index] != 0U) {
            if (item->value_length != 0U) {
                if (item->value == NULL) {
                    return OPEN_CFW_ATTC_DISC_ERROR_INVALID_RESPONSE;
                }
                open_cfw_cordio_attc_write_request(
                    connection_id, control->handles[item->handle_index],
                    item->value_length, (uint8_t *)item->value
                );
            } else {
                open_cfw_cordio_attc_read_request(
                    connection_id, control->handles[item->handle_index]
                );
            }
            return OPEN_CFW_ATTC_DISC_CONTINUING;
        }
        control->characteristic_index++;
    }
    return OPEN_CFW_ATTC_DISC_SUCCESS;
}
#endif

#if defined(OPEN_CFW_ATTC_DISC_BUILD_ALL) || defined(OPEN_CFW_ATTC_DISC_INCLUDED_SERVICE_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_attc_discovery_process_included_service(
    struct open_cfw_cordio_attc_discovery_control_block *control,
    uint8_t settings, uint8_t *declaration
)
{
    uint16_t handle;
    uint8_t index;
    if (!open_cfw_cordio_attc_disc_valid(control) || declaration == NULL) {
        return;
    }
    handle = open_cfw_cordio_attc_disc_u16(declaration);
    if (handle < control->service_start_handle
        || handle > control->service_end_handle) {
        return;
    }
    for (index = 0U; index < control->characteristic_count; index++) {
        if (control->characteristics[index] == NULL) {
            return;
        }
        if (control->handles[index] == 0U
            && open_cfw_cordio_attc_discovery_uuid_compare(
                control->characteristics[index], declaration+6U, settings)) {
            control->handles[index] = handle;
            return;
        }
    }
}
#endif

#if defined(OPEN_CFW_ATTC_DISC_BUILD_ALL) || defined(OPEN_CFW_ATTC_DISC_SERVICE_START_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_attc_discover_service(
    uint8_t connection_id,
    struct open_cfw_cordio_attc_discovery_control_block *control,
    uint8_t uuid_length, uint8_t *uuid
)
{
    (void)control;
    if (uuid != NULL && (uuid_length == 2U || uuid_length == 16U)) {
        open_cfw_cordio_attc_find_by_type_value_request(
            connection_id, OPEN_CFW_ATTC_DISC_HANDLE_START,
            OPEN_CFW_ATTC_DISC_HANDLE_MAX,
            OPEN_CFW_ATTC_DISC_PRIMARY_SERVICE_UUID,
            uuid_length, uuid, 0U
        );
    }
}
#endif

#if defined(OPEN_CFW_ATTC_DISC_BUILD_ALL) || defined(OPEN_CFW_ATTC_DISC_SERVICE_COMPLETE_ONLY)
__attribute__((used, noinline)) uint8_t
open_cfw_cordio_attc_complete_service_discovery(
    struct open_cfw_cordio_attc_discovery_control_block *control,
    struct open_cfw_cordio_att_event *event
)
{
    if (control == NULL || event == NULL) {
        return OPEN_CFW_ATTC_DISC_ERROR_INVALID_RESPONSE;
    }
    if (event->header.event != OPEN_CFW_ATTC_DISC_EVENT_FIND_TYPE) {
        return OPEN_CFW_ATTC_DISC_ERROR_UNDEFINED;
    }
    if (event->header.status != 0U) {
        return event->header.status;
    }
    if (event->value == NULL || event->value_length < 4U) {
        return event->value_length == 0U ? OPEN_CFW_ATTC_DISC_ERROR_NOT_FOUND
            : OPEN_CFW_ATTC_DISC_ERROR_INVALID_RESPONSE;
    }
    control->service_start_handle = open_cfw_cordio_attc_disc_u16(event->value);
    control->service_end_handle = open_cfw_cordio_attc_disc_u16(event->value+2U);
    if (control->service_start_handle == 0U
        || control->service_end_handle < control->service_start_handle) {
        return OPEN_CFW_ATTC_DISC_ERROR_INVALID_RESPONSE;
    }
    return OPEN_CFW_ATTC_DISC_SUCCESS;
}
#endif

#if defined(OPEN_CFW_ATTC_DISC_BUILD_ALL) || defined(OPEN_CFW_ATTC_DISC_CHAR_START_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_attc_start_characteristic_discovery(
    uint8_t connection_id,
    struct open_cfw_cordio_attc_discovery_control_block *control
)
{
    if (open_cfw_cordio_attc_disc_valid(control)
        && control->service_start_handle != 0U
        && control->service_start_handle <= control->service_end_handle) {
        control->characteristic_index = 0U;
        control->end_handle_index = OPEN_CFW_ATTC_DISC_INDEX_NONE;
        open_cfw_cordio_attc_read_by_type_request(
            connection_id, control->service_start_handle,
            control->service_end_handle, 2U,
            OPEN_CFW_ATTC_DISC_CHARACTERISTIC_UUID, 1U
        );
    }
}
#endif

#if defined(OPEN_CFW_ATTC_DISC_BUILD_ALL) || defined(OPEN_CFW_ATTC_DISC_CHAR_COMPLETE_ONLY)
__attribute__((used, noinline)) uint8_t
open_cfw_cordio_attc_complete_characteristic_discovery(
    struct open_cfw_cordio_attc_discovery_control_block *control,
    struct open_cfw_cordio_att_event *event
)
{
    uint8_t status;
    if (!open_cfw_cordio_attc_disc_valid(control) || event == NULL) {
        return OPEN_CFW_ATTC_DISC_ERROR_INVALID_RESPONSE;
    }
    if (event->header.event == OPEN_CFW_ATTC_DISC_EVENT_READ_TYPE) {
        status = open_cfw_cordio_attc_discovery_process_characteristic(
            control, event
        );
    } else if (event->header.event == OPEN_CFW_ATTC_DISC_EVENT_FIND_INFO) {
        status = open_cfw_cordio_attc_discovery_process_descriptor(
            control, event
        );
    } else {
        return OPEN_CFW_ATTC_DISC_ERROR_UNDEFINED;
    }
    if (status != OPEN_CFW_ATTC_DISC_SUCCESS
        && status != OPEN_CFW_ATTC_DISC_CONTINUING) {
        open_cfw_cordio_attc_disc_zero(
            control->handles, control->characteristic_count
        );
    }
    return status;
}
#endif

#if defined(OPEN_CFW_ATTC_DISC_BUILD_ALL) || defined(OPEN_CFW_ATTC_DISC_INC_START_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_attc_start_included_service_discovery(
    uint8_t connection_id,
    struct open_cfw_cordio_attc_discovery_control_block *control
)
{
    if (open_cfw_cordio_attc_disc_valid(control)) {
        control->characteristic_index = 0U;
        control->end_handle_index = OPEN_CFW_ATTC_DISC_INDEX_NONE;
        open_cfw_cordio_attc_read_by_type_request(
            connection_id, control->service_start_handle,
            control->service_end_handle, 2U,
            open_cfw_cordio_attc_discovery_include_uuid, 1U
        );
    }
}
#endif

#if defined(OPEN_CFW_ATTC_DISC_BUILD_ALL) || defined(OPEN_CFW_ATTC_DISC_INC_COMPLETE_ONLY)
__attribute__((used, noinline)) uint8_t
open_cfw_cordio_attc_complete_included_service_discovery(
    struct open_cfw_cordio_attc_discovery_control_block *control,
    struct open_cfw_cordio_att_event *event
)
{
    uint8_t *input, pair_length, settings;
    uint16_t remaining;
    if (!open_cfw_cordio_attc_disc_valid(control) || event == NULL
        || event->header.event != OPEN_CFW_ATTC_DISC_EVENT_READ_TYPE) {
        return OPEN_CFW_ATTC_DISC_ERROR_UNDEFINED;
    }
    if (event->header.status == 0U) {
        if (event->value == NULL || event->value_length < 1U) {
            return OPEN_CFW_ATTC_DISC_ERROR_INVALID_RESPONSE;
        }
        input = event->value;
        pair_length = *input++;
        if (pair_length == OPEN_CFW_ATTC_DISC_INCLUDE_PAIR_UUID16) {
            settings = 0U;
        } else if (pair_length == OPEN_CFW_ATTC_DISC_INCLUDE_PAIR_UUID128) {
            settings = OPEN_CFW_ATTC_DISC_UUID128;
        } else {
            return OPEN_CFW_ATTC_DISC_ERROR_INVALID_RESPONSE;
        }
        remaining = (uint16_t)(event->value_length-1U);
        if (remaining == 0U || remaining % pair_length != 0U) {
            return OPEN_CFW_ATTC_DISC_ERROR_INVALID_RESPONSE;
        }
        while (remaining != 0U) {
            open_cfw_cordio_attc_discovery_process_included_service(
                control, settings, input
            );
            input += pair_length;
            remaining = (uint16_t)(remaining-pair_length);
        }
    }
    return (event->header.status != 0U || event->continuing == 0U)
        ? OPEN_CFW_ATTC_DISC_SUCCESS : OPEN_CFW_ATTC_DISC_CONTINUING;
}
#endif

#if defined(OPEN_CFW_ATTC_DISC_BUILD_ALL) || defined(OPEN_CFW_ATTC_DISC_CONFIG_START_ONLY)
__attribute__((used, noinline)) uint8_t
open_cfw_cordio_attc_start_configuration(
    uint8_t connection_id,
    struct open_cfw_cordio_attc_discovery_control_block *control
)
{
    if (control == NULL) {
        return OPEN_CFW_ATTC_DISC_ERROR_INVALID_RESPONSE;
    }
    control->characteristic_index = 0U;
    return open_cfw_cordio_attc_discovery_configuration_next(
        connection_id, control
    );
}
#endif

#if defined(OPEN_CFW_ATTC_DISC_BUILD_ALL) || defined(OPEN_CFW_ATTC_DISC_CONFIG_COMPLETE_ONLY)
__attribute__((used, noinline)) uint8_t
open_cfw_cordio_attc_complete_configuration(
    uint8_t connection_id,
    struct open_cfw_cordio_attc_discovery_control_block *control
)
{
    if (control == NULL
        || control->characteristic_index >= control->configuration_count) {
        return OPEN_CFW_ATTC_DISC_ERROR_INVALID_RESPONSE;
    }
    control->characteristic_index++;
    return open_cfw_cordio_attc_discovery_configuration_next(
        connection_id, control
    );
}
#endif

#if defined(OPEN_CFW_ATTC_DISC_BUILD_ALL) || defined(OPEN_CFW_ATTC_DISC_CONFIG_RESUME_ONLY)
__attribute__((used, noinline)) uint8_t
open_cfw_cordio_attc_resume_configuration(
    uint8_t connection_id,
    struct open_cfw_cordio_attc_discovery_control_block *control
)
{
    return open_cfw_cordio_attc_discovery_configuration_next(
        connection_id, control
    );
}
#endif
