/* Stock 0x6249c and 0x624c8: legacy Goodix profile commands. */
#include <stdint.h>

extern void r1_goodix_switch_profile(uint32_t);
extern void r1_goodix_stop_stock_profiles(void);
extern uint32_t r1_legacy_bounded_reply_send(const void *, uint32_t);

static uint32_t profile_command(void *packet, uint32_t profile)
{
    uint8_t *bytes = (uint8_t *)packet;
    if (bytes[3] == 0u)
        r1_goodix_switch_profile(profile);
    else if (bytes[3] == 1u)
        r1_goodix_stop_stock_profiles();
    else
        return 0u;
    bytes[4] = 1u;
    return r1_legacy_bounded_reply_send(packet, 5u);
}

uint32_t r1_goodix_profile_2_command_adapter(uint32_t handle, void *packet)
{
    (void)handle;
    return profile_command(packet, 0u);
}

uint32_t r1_goodix_profile_40_command_adapter(uint32_t handle, void *packet)
{
    (void)handle;
    return profile_command(packet, 1u);
}
