/* SPDX-License-Identifier: MIT
 * Independently reconstructed fixed-address SPOT power-event interface.
 */
#ifndef STARTUP_EVENTS_A_H
#define STARTUP_EVENTS_A_H
#include <stdbool.h>
#include <stdint.h>

/* Values and public parameter types match Apollo510 HAL 5.1 am_hal_spotmgr.h. */
typedef enum {
    AM_HAL_SPOTMGR_STIM_CPU_STATE = 0,
    AM_HAL_SPOTMGR_STIM_GPU_STATE = 1,
    AM_HAL_SPOTMGR_STIM_TEMP = 2,
    AM_HAL_SPOTMGR_STIM_DEVPWR = 3,
    AM_HAL_SPOTMGR_STIM_AUDSSPWR = 4,
    AM_HAL_SPOTMGR_STIM_MEMPWR = 5,
    AM_HAL_SPOTMGR_STIM_SSRAMPWR = 6,
    AM_HAL_SPOTMGR_STIM_BACK_TO_DEFAULT_STATE = 7,
    AM_HAL_SPOTMGR_STIM_INIT_STATE = 8
} am_hal_spotmgr_stimulus_e;

uint32_t opencfw_boot_spotmgr_power_state_update_a(
    uint32_t stimulus, uint32_t on, void *args);

/* ABI-visible local structure passed to the recovered state/deep-sleep
 * children. Its offsets follow locked stack accesses, not public HAL structs.
 */
typedef struct {
    uint32_t device_power;        /* +0x00 */
    uint32_t audio_power;         /* +0x04 */
    uint32_t memory_power;        /* +0x08 */
    uint32_t ssram_power;         /* +0x0c */
    uint8_t temperature_class;    /* +0x10 */
    int8_t cpu_state;             /* +0x11 */
    int8_t gpu_state;             /* +0x12 */
} startup_events_a_snapshot;

#endif
