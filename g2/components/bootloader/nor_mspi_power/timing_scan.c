/* SPDX-License-Identifier: MIT
 * Source reconstruction of the locked 36 x 32 MSPI/NOR timing scan.
 * The profile table is runtime data at 0x20000244. HAL control, JEDEC read,
 * and logging remain explicit providers.
 */
#include "timing_scan.h"

#include <stdint.h>

#define ACTIVE_HANDLE_SLOT UINT32_C(0x200270dc)
#define PROFILE_TABLE      UINT32_C(0x20000244)
#define EXPECTED_JEDEC_ID  UINT32_C(0x002539c2)

extern uint32_t opencfw_hal_mspi_control(uint32_t handle, uint32_t request,
                                         void *value);
extern uint32_t opencfw_bl_nor_read_jedec_id(uint32_t *id,
    uint32_t reserved1, uint32_t reserved2, uint32_t initial_word);
extern void opencfw_bl_log(uint32_t level, const char *module,
    const char *file, const char *function, uint32_t line,
    const char *format, ...);

static const char log_module[] = "drv.norflash";
static const char log_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\flash\\drv_mx25u25643g.c";
static const char log_function[] = "mspi_timing_check";
static const char window_format[] =
    "Timing Scan found a window %d fine steps wide in setting %d.";
static const char profile_format[] =
    "TxNeg %d, RxNeg %d, RxCap %d, TxDQSDelay %d, Turnaround %d == 0x%08X";
static const char center_format[] = "RxDQSDelay is set to %d.";

static uint32_t leading_ones(uint32_t bits)
{
    uint32_t count = 0u;
    while (bits != 0u) {
        bits &= bits << 1;
        ++count;
    }
    return count;
}

static uint32_t window_center(uint32_t bits)
{
    uint32_t run_length = 0u;
    uint32_t longest = 0u;
    uint32_t center = 0u;
    uint32_t odd = 0u;
    uint32_t in_run = 0u;

    for (uint32_t step = 0u; step < 32u; ++step) {
        const uint32_t is_set = (bits >> step) & 1u;
        uint32_t close = 0u;
        if (is_set != 0u) {
            in_run = 1u;
            ++run_length;
        } else if (in_run != 0u) {
            in_run = 0u;
            close = 1u;
        }
        if (step == 31u && in_run != 0u)
            close = 1u;
        if (close != 0u) {
            if (longest < run_length) {
                center = (step - 1u) - (run_length >> 1);
                odd = run_length & 1u;
                longest = run_length;
            }
            run_length = 0u;
        }
    }

    if (center < 16u && ((bits >> 31) & 1u) != 0u)
        center -= odd;
    else if (center > 15u && (bits & 1u) != 0u)
        ++center;
    return center;
}

uint32_t opencfw_provider_420002(uint8_t output[6])
{
    volatile const uint8_t *const profiles =
        (volatile const uint8_t *)(uintptr_t)PROFILE_TABLE;
    volatile uint32_t masks[36];
    uint32_t best_score = 0u;
    uint32_t best_profile = 0u;
    uint8_t control_record[6];
    volatile const uint32_t *const handle_slot =
        (volatile const uint32_t *)(uintptr_t)ACTIVE_HANDLE_SLOT;

    for (uint32_t profile = 0u; profile < 36u; ++profile)
        masks[profile] = 0u;

    for (uint32_t profile = 0u; profile < 36u; ++profile) {
        control_record[0] = profiles[profile * 6u + 0u];
        control_record[1] = profiles[profile * 6u + 1u];
        control_record[2] = profiles[profile * 6u + 2u];
        control_record[3] = profiles[profile * 6u + 3u];
        control_record[5] = 8u;
        for (uint32_t step = 0u; step < 32u; ++step) {
            uint32_t id = 0u;
            control_record[4] = (uint8_t)step;
            (void)opencfw_hal_mspi_control(*handle_slot, 0x10u,
                                           control_record);
            const uint32_t status = opencfw_bl_nor_read_jedec_id(
                &id, 0u, 0u, 0u);
            if (status == 0u && id == EXPECTED_JEDEC_ID)
                masks[profile] |= UINT32_C(1) << step;
        }
    }

    for (uint32_t profile = 0u; profile < 36u; ++profile) {
        const uint32_t score = leading_ones(masks[profile]);
        if (best_score < score) {
            best_score = score;
            best_profile = profile;
        }
    }

    opencfw_bl_log(2u, log_module, log_file, log_function, 0x1c6u,
        window_format, best_score, best_profile);
    opencfw_bl_log(2u, log_module, log_file, log_function, 0x1cdu,
        profile_format, profiles[best_profile * 6u + 0u],
        profiles[best_profile * 6u + 1u],
        profiles[best_profile * 6u + 2u],
        profiles[best_profile * 6u + 3u],
        profiles[best_profile * 6u + 5u], masks[best_profile]);

    const uint32_t center = window_center(masks[best_profile]);
    opencfw_bl_log(2u, log_module, log_file, log_function, 0x1d3u,
                   center_format, center);
    output[4] = (uint8_t)center;
    output[0] = profiles[best_profile * 6u + 0u];
    output[1] = profiles[best_profile * 6u + 1u];
    output[2] = profiles[best_profile * 6u + 2u];
    output[3] = profiles[best_profile * 6u + 3u];
    output[5] = profiles[best_profile * 6u + 5u];
    return 0u;
}
