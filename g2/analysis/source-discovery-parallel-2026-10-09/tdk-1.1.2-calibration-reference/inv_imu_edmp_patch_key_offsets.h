/*
 * ________________________________________________________________________________________________________
 * Copyright (c) 2021 InvenSense Inc. All rights reserved.
 *
 * This software, related documentation and any modifications thereto (collectively "Software") is subject
 * to InvenSense and its licensors' intellectual property rights under U.S. and international copyright
 * and other intellectual property rights laws.
 *
 * InvenSense and its licensors retain all intellectual property and proprietary rights in and to the Software
 * and any use, reproduction, disclosure or distribution of the Software without an express license agreement
 * from InvenSense is strictly prohibited.
 *
 * EXCEPT AS OTHERWISE PROVIDED IN A LICENSE AGREEMENT BETWEEN THE PARTIES, THE SOFTWARE IS
 * PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
 * TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT.
 * EXCEPT AS OTHERWISE PROVIDED IN A LICENSE AGREEMENT BETWEEN THE PARTIES, IN NO EVENT SHALL
 * INVENSENSE BE LIABLE FOR ANY DIRECT, SPECIAL, INDIRECT, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, OR ANY
 * DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
 * NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
 * OF THE SOFTWARE.
 *
 * ________________________________________________________________________________________________________
 */

#ifndef __INV_IMU_EDMP_PATCH_KEY_OFFSETS_H__
#define __INV_IMU_EDMP_PATCH_KEY_OFFSETS_H__

#ifdef __cplusplus
extern "C" {
#endif

#define RAM_MRM_IMG_PATCH_KEY_OFFSET	0x48
#define RAM_B2S_IMG_PATCH_KEY_OFFSET	0xF4
#define RAM_B2S_OVER_GAF_IMG_PATCH_KEY_OFFSET	0xF4
#define RAM_DISPATCH_IMG_PATCH_KEY_OFFSET	0x0
#define RAM_DISPATCH_OVER_GAF_IMG_PATCH_KEY_OFFSET	0x0
#define RAM_AID_IMG_PATCH_KEY_OFFSET	0x4C
#define RAM_AID_OVER_GAF_IMG_PATCH_KEY_OFFSET	0x4C
#define RAM_CALMAG_IMG_CHUNK6_PATCH_KEY_OFFSET	0x0
#define RAM_CALMAG_IMG_CHUNK7_PATCH_KEY_OFFSET	0x4
#define RAM_CALMAG_IMG_PART4_ACCEPTANCE_PATCH_KEY_OFFSET	0x8
#define RAM_CALMAG_IMG_POWERSAVE_PATCH_KEY_OFFSET	0xC


#ifdef __cplusplus
}
#endif

#endif // __INV_IMU_EDMP_PATCH_KEY_OFFSETS_H__
