#ifndef R1_NATIVE_MOTION_OPERATIONS_H
#define R1_NATIVE_MOTION_OPERATIONS_H
#include <stdint.h>
#include <stddef.h>
typedef struct {
 uint32_t (*configure)(void);
 uint32_t (*probe)(void);
 int32_t (*fifo)(uint8_t *, uint32_t);
 /* All IRQ providers are notifications; no caller consumes a status. */
 struct { void (*notify)(void); } interrupt;
 /* LIS tap policies have no arguments and return their completion word. */
 uint32_t (*aux16)(void);
 uint32_t (*aux20)(void);
} r1_motion_table;
_Static_assert(sizeof(r1_motion_table)==24 && _Alignof(r1_motion_table)==4 &&
               offsetof(r1_motion_table,configure)==0 &&
               offsetof(r1_motion_table,probe)==4 &&
               offsetof(r1_motion_table,fifo)==8 &&
               offsetof(r1_motion_table,interrupt)==12 &&
               offsetof(r1_motion_table,aux16)==16 &&
               offsetof(r1_motion_table,aux20)==20,
               "native six-word motion operation table");
uint32_t r1_lis2dw12_aux16_boundary(void),r1_lis2dw12_aux20_boundary(void);
#endif
