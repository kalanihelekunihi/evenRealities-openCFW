#ifndef OPENCFW_STARTUP_ROOT_CARRY_H
#define OPENCFW_STARTUP_ROOT_CARRY_H
#include <stdint.h>
#include <stddef.h>
typedef struct {
 uint32_t ambient_r5,ambient_r7;
 uint32_t stack_r1,stack_r2,stack_r3;
} startup_root_register_carry_t;
_Static_assert(sizeof(startup_root_register_carry_t)==20,"root carry size");
_Static_assert(offsetof(startup_root_register_carry_t,stack_r1)==8,"R1 slot");
_Static_assert(offsetof(startup_root_register_carry_t,stack_r2)==12,"R2 slot");
_Static_assert(offsetof(startup_root_register_carry_t,stack_r3)==16,"R3 slot");
uint32_t reconstructed_initialize_clock_coupled_abi_core(startup_root_register_carry_t *root);
/* Assembly entry captures original ambient R5/R7 and reproduces mutated
 * saved R1/R2/R3 slots. Child contracts remain explicit analysis cuts. */
#endif
