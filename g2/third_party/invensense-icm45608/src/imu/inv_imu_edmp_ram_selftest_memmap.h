/*
 *
 * Copyright (c) [2024] by InvenSense, Inc.
 * 
 * Permission to use, copy, modify, and/or distribute this software for any
 * purpose with or without fee is hereby granted.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
 * WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
 * SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 * WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION
 * OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
 * CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 *
 */

#ifndef __INV_IMU_EDMP_STC_MEMMAP_H__
#define __INV_IMU_EDMP_STC_MEMMAP_H__

#ifdef __cplusplus
extern "C" {
#endif

/* stc_configparams
 *
 * Self-test input parameters
 * bit0: If set, enable self-test init, must be set when any of accel or gyro self-test enable bit is set (bits 2:1)
 * bit1: If set, enable accel self-test 
 * bit2: If set, enable gyro self-test
 * bit3~6: Unused
 * bit7~9: Averaging time used to perform self-test (0/1/2/3/4/5: 10/20/40/80/160/320 ms)
 * bit10~12: Tolerance between factory trim and accel self-test response (0/1/2/3/4/5/6/7: 5/10/15/20/25/30/40/50%)
 * bit13~15: Tolerance between factory trim and gyro self-test response (0/1/2/3/4/5/6/7: 5/10/15/20/25/30/40/50%)
 * Warning: it is required to load a dedicated SRAM image to be used
 */
#define EDMP_STC_CONFIGPARAMS                                   0x34
#define EDMP_STC_CONFIGPARAMS_SIZE                              4

/* stc_result
 *
 * Results/status from self-test run
 * bit0: AX Self-test result (0:pass 1:fail)
 * bit1: AY Self-test result (0:pass 1:fail)
 * bit2: AZ Self-test result (0:pass 1:fail)
 * bit3: GX Self-test result (0:pass 1:fail)
 * bit4: GY Self-test result (0:pass 1:fail)
 * bit5: GZ Self-test result (0:pass 1:fail)
 * bit6~7: Self-test status (0:Done 1:InProgress 2:Error)
 * Warning: it is required to load a dedicated SRAM image to be used
 */
#define EDMP_STC_RESULT                                         0x38
#define EDMP_STC_RESULT_SIZE                                    4

#ifdef __cplusplus
}
#endif

#endif // __INV_IMU_EDMP_STC_MEMMAP_H__
