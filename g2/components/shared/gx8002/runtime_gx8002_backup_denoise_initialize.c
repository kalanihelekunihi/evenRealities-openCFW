/* SPDX-License-Identifier: MIT */
/* Recovered control flow. Callee names with package offsets remain provisional. */
#include <stdint.h>
extern unsigned char backup_denoise_state[] __attribute__((aligned(4)));
extern uint32_t denoise_status_3c8f8(void);
extern void denoise_prepare_428e8(void *, void *, uint32_t, uint32_t);
extern void denoise_prepare_42850(void);
extern uint32_t denoise_rate_428c0(void);
extern void *denoise_allocate_4286c(uint32_t);
extern void *denoise_drc_470c4(uint32_t, uint32_t, void *);
extern int denoise_beamforming_44140(void);
extern int denoise_imcra_4425c(void);
extern int denoise_audio_42d58(void (*)(void));
extern void denoise_callback_44694(void);
extern int printf(const char *, ...);
extern const char denoise_msg_start[], denoise_msg_none[], denoise_msg_rate[];
extern const char denoise_msg_drc_ok[], denoise_msg_double[], denoise_msg_double_fail[];
extern const char denoise_msg_single[], denoise_msg_single_fail[], denoise_msg_drc_fail[];
extern const char denoise_msg_audio_fail[], denoise_msg_audio_ok[], denoise_msg_ok[];
int open_cfw_gx8002_backup_denoise_init(uint32_t previous_mode)
{
    (void)previous_mode;
    if (denoise_status_3c8f8() < 2u) {
        printf(denoise_msg_start);
        denoise_prepare_428e8(backup_denoise_state + 28, backup_denoise_state + 52, 40, 4);
        denoise_prepare_42850();
        uint32_t mode = *(volatile uint32_t *)(backup_denoise_state + 16);
        if (mode == 0) {
            printf(denoise_msg_double);
            if (denoise_beamforming_44140()) {
                printf(denoise_msg_double_fail);
                return -1;
            }
        } else if (mode == 1) {
            printf(denoise_msg_single);
            if (denoise_imcra_4425c()) {
                printf(denoise_msg_single_fail);
                return -1;
            }
        } else {
            printf(denoise_msg_none);
        }
        printf(denoise_msg_rate, denoise_rate_428c0(), 256);
        uint32_t rate = denoise_rate_428c0();
        void *buffer = denoise_allocate_4286c(512);
        void *drc = denoise_drc_470c4(rate, 256, buffer);
        *(void *volatile *)(backup_denoise_state + 24) = drc;
        if (!drc) {
            printf(denoise_msg_drc_fail);
            return -1;
        }
        printf(denoise_msg_drc_ok);
    }
    if (denoise_audio_42d58(denoise_callback_44694)) {
        printf(denoise_msg_audio_fail);
        return -1;
    }
    printf(denoise_msg_audio_ok);
    printf(denoise_msg_ok);
    return 0;
}
