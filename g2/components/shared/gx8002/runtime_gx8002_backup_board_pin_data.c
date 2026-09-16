/* SPDX-License-Identifier: MIT */
#include <stdint.h>
struct pin_configuration { uint8_t pin_id, function; };
#define PIN(n) {n, (n)==2 ? 0 : 1}
const struct pin_configuration open_cfw_gx8002_backup_board_pins[13]={
 PIN(0),PIN(1),PIN(2),PIN(3),PIN(4),PIN(5),PIN(6),PIN(7),PIN(8),PIN(9),PIN(10),PIN(11),PIN(12)
};
_Static_assert(sizeof(open_cfw_gx8002_backup_board_pins)==26,"pin table ABI");
const char open_cfw_gx8002_backup_board_conflict[]="pin %d function conflict !\n";
const char open_cfw_gx8002_backup_board_fatal[]="!!!pin set error!\n Please check Board Options!!!";
const char open_cfw_gx8002_backup_board_error[]="pin %d set error!\n";
volatile uint32_t open_cfw_gx8002_backup_board_initialized;
