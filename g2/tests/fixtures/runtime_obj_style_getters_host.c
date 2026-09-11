/*
 * SPDX-License-Identifier: MIT
 *
 * Host substitution for the source-owned LVGL style-property getters:
 * captures the (obj, part, property) triple forwarded to the shared
 * style-lookup core instead of calling the fixed stock address.
 */

static unsigned int open_cfw_test_runtime_style_getter_core(
    unsigned int obj,
    unsigned int part,
    unsigned int property
);

#define OPEN_CFW_RUNTIME_STYLE_GETTER_CORE(obj, part, property) \
    open_cfw_test_runtime_style_getter_core((obj), (part), (property))

#include "../../components/apollo_main/core_overlay/runtime_obj_style_getters.c"

unsigned int open_cfw_test_runtime_style_getter_calls;
unsigned int open_cfw_test_runtime_style_getter_obj;
unsigned int open_cfw_test_runtime_style_getter_part;
unsigned int open_cfw_test_runtime_style_getter_property;
unsigned int open_cfw_test_runtime_style_getter_result;

static unsigned int open_cfw_test_runtime_style_getter_core(
    unsigned int obj,
    unsigned int part,
    unsigned int property
)
{
    open_cfw_test_runtime_style_getter_calls += 1U;
    open_cfw_test_runtime_style_getter_obj = obj;
    open_cfw_test_runtime_style_getter_part = part;
    open_cfw_test_runtime_style_getter_property = property;
    return open_cfw_test_runtime_style_getter_result;
}

void open_cfw_test_runtime_style_getter_reset(unsigned int result)
{
    open_cfw_test_runtime_style_getter_calls = 0U;
    open_cfw_test_runtime_style_getter_obj = 0U;
    open_cfw_test_runtime_style_getter_part = 0U;
    open_cfw_test_runtime_style_getter_property = 0U;
    open_cfw_test_runtime_style_getter_result = result;
}
