/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_RUNTIME_TOUCH_PLATFORM_COMPLETION_H
#define OPEN_CFW_RUNTIME_TOUCH_PLATFORM_COMPLETION_H

#include <stddef.h>
#include <stdint.h>

typedef struct open_cfw_touch_runtime_state {
    uintptr_t stack_top;
    uintptr_t stack_limit;
    uint32_t fault_reason;
    uint32_t application_result;
    uint8_t exited;
} open_cfw_touch_runtime_state;

typedef struct open_cfw_touch_runtime_provider {
    void (*preinitialize)(void *context);
    void (*initialize)(void *context);
    uint32_t (*application_main)(void *context);
    void (*exit_application)(void *context, uint32_t result);
    void (*fault)(void *context, uint32_t reason);
    void (*disable_interrupts)(void *context);
    uint32_t (*handoff)(void *context);
    void *context;
} open_cfw_touch_runtime_provider;

typedef struct open_cfw_touch_mapping_config {
    uint8_t word_index[14];
    uint8_t mode;
    uint8_t primary_index;
    uint8_t secondary_index;
} open_cfw_touch_mapping_config;

typedef struct open_cfw_touch_mapping_image {
    uint8_t word_index[14];
    uint8_t selected_index;
    uint8_t valid_count;
    uint32_t words[14];
} open_cfw_touch_mapping_image;

typedef struct open_cfw_touch_profile_tables {
    uint8_t base[3][28];
    uint8_t override_mode_a[28];
    uint8_t override_mode_b[28];
    uint8_t override_mode_c[28];
} open_cfw_touch_profile_tables;

typedef struct open_cfw_touch_profile_selectors {
    uint8_t mode_a;
    uint8_t mode_b;
    uint8_t mode_c;
    uint8_t option_bits;
} open_cfw_touch_profile_selectors;

typedef struct open_cfw_touch_register_parameters {
    uint8_t channel;
    uint8_t polarity;
    uint8_t averaging;
    uint8_t threshold_a;
    uint8_t threshold_b;
    uint8_t threshold_c;
    uint8_t debounce;
    uint16_t resolution_a;
    uint16_t resolution_b;
    uint16_t timing_a;
    uint16_t timing_b;
    open_cfw_touch_profile_selectors selectors;
    open_cfw_touch_mapping_config mapping;
} open_cfw_touch_register_parameters;

typedef struct open_cfw_touch_register_image {
    uint32_t words[28];
    uint8_t profiles[4][28];
    open_cfw_touch_mapping_image mapping;
} open_cfw_touch_register_image;

extern const open_cfw_touch_profile_tables open_cfw_touch_safe_profile_tables;
extern const uint32_t open_cfw_touch_safe_mapping_words[14];

uintptr_t open_cfw_touch_runtime_0158_stack_limit(
    open_cfw_touch_runtime_state *state, uintptr_t stack_top);
uint32_t open_cfw_touch_runtime_0164_reset(
    open_cfw_touch_runtime_state *state,
    uint8_t *bss_start, uint8_t *bss_end,
    const open_cfw_touch_runtime_provider *provider);
void open_cfw_touch_runtime_0164_reset_entry(
    open_cfw_touch_runtime_state *state,
    uint8_t *bss_start, uint8_t *bss_end,
    const open_cfw_touch_runtime_provider *provider);
void open_cfw_touch_runtime_12a6_fault(
    open_cfw_touch_runtime_state *state, uint32_t reason,
    const open_cfw_touch_runtime_provider *provider);
uint32_t open_cfw_touch_runtime_141c_handoff(
    volatile uint32_t *handoff_register, uint32_t handler_token,
    const open_cfw_touch_runtime_provider *provider);
void open_cfw_touch_runtime_7038_halt(void);

uint32_t open_cfw_touch_config_1de4_load_mapping(
    const open_cfw_touch_mapping_config *config,
    const uint32_t table_words[14],
    open_cfw_touch_mapping_image *image);
void open_cfw_touch_config_1fbc_load_profiles(
    const open_cfw_touch_profile_tables *tables,
    const open_cfw_touch_profile_selectors *selectors,
    uint8_t output[4][28]);
uint32_t open_cfw_touch_config_2078_build(
    const open_cfw_touch_register_parameters *parameters,
    const open_cfw_touch_profile_tables *tables,
    const uint32_t mapping_words[14],
    open_cfw_touch_register_image *image);

#endif
