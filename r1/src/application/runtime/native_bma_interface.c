#include <stdint.h>
#include <stddef.h>
#include "bma4.h"
_Static_assert(sizeof(struct bma4_dev)==52,"pinned ARM BMA layout");
_Static_assert(offsetof(struct bma4_dev,intf_ptr)==4 && offsetof(struct bma4_dev,intf)==8 && offsetof(struct bma4_dev,intf_rslt)==9 && offsetof(struct bma4_dev,variant)==13 && offsetof(struct bma4_dev,read_write_len)==20 && offsetof(struct bma4_dev,bus_read)==36 && offsetof(struct bma4_dev,bus_write)==40 && offsetof(struct bma4_dev,delay_us)==44 && offsetof(struct bma4_dev,perf_mode_status)==50,"native field offsets");
/* Layout matches the pinned API; full native allocation extent remains gated. */
struct bma4_dev r1_bma_context __attribute__((section(".bss.r1.bma.context"),aligned(4)));
uint32_t r1_bma_bus_address __attribute__((section(".r1.bma.bus_address"),aligned(4)))=0x18;
__attribute__((naked)) uint32_t r1_bma_default_read(void)
{ __asm__ volatile("push {r4,lr}\nmov r4,r0\nldrb r0,[r3]\nuxth r3,r2\nmov r2,r1\nmov r1,r4\nbl r1_motion_bus_read_request\ncbz r0,1f\nmovs r0,#0\npop {r4,pc}\n1: mvn r0,#1\npop {r4,pc}\n"); }
__attribute__((naked)) uint32_t r1_bma_default_write(void)
{ __asm__ volatile("push {r4,lr}\nmov r4,r0\nldrb r0,[r3]\nuxth r3,r2\nmov r2,r1\nmov r1,r4\nbl r1_motion_bus_write_request\ncbz r0,1f\nmovs r0,#0\npop {r4,pc}\n1: mvn r0,#1\npop {r4,pc}\n"); }
__attribute__((naked)) uint32_t r1_bma_delay_us(void)
{ __asm__ volatile("cmp r0,#0\nbeq 1f\nldr r1,=r1_rtt_delay_cycles\nlsls r0,r0,#6\nbx r1\n1: bx lr\n"); }
__attribute__((naked)) uint32_t r1_bma_interface_initialize(void)
{
 __asm__ volatile("movs r1,#0\ncbz r0,1f\nmovs r2,#1\nstrb r2,[r0,#8]\nldr r2,=r1_bma_default_read\nstr r2,[r0,#36]\nldr r2,=r1_bma_default_write\nstr r2,[r0,#40]\nldr r2,=r1_bma_bus_address\nstr r2,[r0,#4]\nldr r2,=r1_bma_delay_us\nstr r2,[r0,#44]\nmovs r2,#64\nstrh r2,[r0,#20]\nmovs r2,#3\nstrb r2,[r0,#13]\nmovs r2,#0\nstrb r2,[r0,#50]\nb 2f\n1: mov.w r1,#0xffffffff\n2: mov r0,r1\nbx lr\n");
}
