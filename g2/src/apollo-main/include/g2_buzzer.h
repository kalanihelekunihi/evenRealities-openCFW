/* Buzzer driver (stock driver/buzzer/drv_buzzer.c, native 0x5026bc..0x502d55).
 *
 * Apollo510 TIMER7 PWM on GPIO 145. Scripted playback is paced by a one-shot
 * OS timer whose callback posts input-thread message 2; the input thread then
 * calls buzzer_play_next. DRV_BuzzerPlay (0x502bf0, posts message 1) is
 * defined as audio_wear_child_502bf0 in drivers/peripherals/wear-child. */
#ifndef G2_BUZZER_H
#define G2_BUZZER_H

#include <stdint.h>

#define G2_BUZZER_GPIO        145u
#define G2_BUZZER_TIMER       7u
#define G2_BUZZER_VOICE_COUNT 9u  /* DRV_BuzzerPlayAfterQueue accepts 0..8 */

uint32_t buzzer_pwm_config(uint32_t timer, uint16_t clock, uint32_t frequency, uint8_t duty);
void buzzer_pwm_start(void);
void buzzer_pwm_stop(void);
void buzzer_pwm_update(uint32_t frequency, uint8_t duty);
void buzzer_beep_start(uint32_t frequency, uint8_t duty);
void buzzer_beep_stop(uint8_t release);
void _buzzerPlayVoice(void);
void buzzer_timer_callback(void *argument);
void _buzzerPlayStart(const uint8_t *voice);
void _buzzerPlayStop(void);
void DRV_BuzzerInit(void);
void buzzer_play_next(void);
void DRV_BuzzerPlayAfterQueue(int32_t type);
void DRV_BuzzerPlayNote(uint8_t note, uint8_t tone, uint8_t beat);
void DRV_BuzzerStart(uint32_t frequency, uint8_t duty);
void DRV_BuzzerStop(void);

#endif
