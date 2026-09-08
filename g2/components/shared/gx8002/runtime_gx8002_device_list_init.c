/* SPDX-License-Identifier: MIT */
/* Recovered empty circular lists for SPI and SPI-flash master registries. */
#include <stddef.h>
struct open_cfw_device_list {
    struct open_cfw_device_list *next;
    struct open_cfw_device_list *previous;
};
_Static_assert(sizeof(struct open_cfw_device_list) == 8, "C-SKY list ABI");
extern volatile struct open_cfw_device_list open_cfw_gx8002_device_heads[2];
void open_cfw_gx8002_device_list_init(void)
{
    struct open_cfw_device_list *spi = (struct open_cfw_device_list *)&open_cfw_gx8002_device_heads[0];
    struct open_cfw_device_list *flash = (struct open_cfw_device_list *)&open_cfw_gx8002_device_heads[1];
    open_cfw_gx8002_device_heads[0].next = spi;
    open_cfw_gx8002_device_heads[0].previous = spi;
    open_cfw_gx8002_device_heads[1].next = flash;
    open_cfw_gx8002_device_heads[1].previous = flash;
}
