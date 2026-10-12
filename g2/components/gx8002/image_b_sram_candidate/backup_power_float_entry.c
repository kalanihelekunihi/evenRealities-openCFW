/* SPDX-License-Identifier: MIT
 * Native image-B 0x100100a4..0x100100ab is a call-through to 0x100100bc.
 * The latter is the genuine floating power core and remains separately
 * source/data qualified; this wrapper preserves the live hard-float ABI.
 * binh_b_stage2.bin SHA256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 */
extern float gx8002_image_b_power_float_core_100100bc(
    float base, float exponent);

float gx8002_image_b_power_float_100100a4(float base, float exponent)
{
    return gx8002_image_b_power_float_core_100100bc(base, exponent);
}
