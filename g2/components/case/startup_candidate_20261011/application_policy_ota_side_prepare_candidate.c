/* SPDX-License-Identifier: MIT
 * Native CASE 0xbe90/0xbede OTA side power command sequences.
 */
#include <stdint.h>
extern void case_policy_sensor_command(uint32_t channel,uint32_t value); /* 0x99e8 */
extern void case_policy_sensor_delay(uint32_t amount); /* 0xa7b0 */
void case_policy_ota_left_prepare(void)
{
    case_policy_sensor_command(5u,3u);
    case_policy_sensor_command(6u,0xc1u);
    case_policy_sensor_command(3u,0xa6u);
    case_policy_sensor_delay(30u);
    case_policy_sensor_command(7u,3u);
}
void case_policy_ota_left_finish(void) /* 0xbeba */
{
    case_policy_sensor_command(7u,0x20u);
    case_policy_sensor_command(6u,0x81u);
    case_policy_sensor_command(5u,3u);
    case_policy_sensor_command(3u,0xffu);
}
void case_policy_ota_right_prepare(void)
{
    case_policy_sensor_command(5u,3u);
    case_policy_sensor_command(6u,0xc1u);
    case_policy_sensor_command(4u,0xa6u);
    case_policy_sensor_delay(30u);
    case_policy_sensor_command(7u,5u);
}
void case_policy_ota_right_finish(void) /* 0xbf08 */
{
    case_policy_sensor_command(7u,0x20u);
    case_policy_sensor_command(6u,0x81u);
    case_policy_sensor_command(5u,3u);
    case_policy_sensor_command(4u,0xffu);
}
