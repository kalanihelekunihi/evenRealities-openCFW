/* Native image-B 0x100034d4: two selected children in exact order. */
#include <stdint.h>

extern uint32_t gx8002_image_b_platform_status_10003fb8(void);
extern void gx8002_image_b_analog_config_update_100051d8(void);

void gx8002_image_b_system_board_child_100034d4(void)
{
    (void)gx8002_image_b_platform_status_10003fb8();
    gx8002_image_b_analog_config_update_100051d8();
}
