/* Recovered Apollo Nema XY translation command, native 0x5228b0..0x522915.
 * The two float arguments arrive in s0/s1 under the vendor VFP ABI.
 */
#include <stdint.h>

extern void *audio_uart_nema_cl_get_space_514aec(uint32_t words);
extern void audio_uart_nema_child_514846(uint32_t address, uint32_t value);

void display_driver_nema_float_translate_5228b0(float x, float y)
    __attribute__((pcs("aapcs-vfp")));

void display_driver_nema_float_translate_5228b0(float x, float y)
{
    float const neg_x = -x;
    float const neg_y = -y;
    uint32_t *const command = audio_uart_nema_cl_get_space_514aec(2u);
    if (command == 0) return;

    command[0] = 0x174u;
    __builtin_memcpy(&command[1], &neg_y, sizeof(neg_y));
    command[2] = 0x168u;
    __builtin_memcpy(&command[3], &neg_x, sizeof(neg_x));

    if (neg_x < -2048.0f || neg_y < -2048.0f)
        audio_uart_nema_child_514846(0x118u, 0x80000000u);
}
