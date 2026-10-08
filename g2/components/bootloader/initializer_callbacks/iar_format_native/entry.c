/* Preserve the stock232-byte entry frame so decimal digit scratch retains the
 * actual prior stack bytes on generation-budget overflow paths. No opcode array. */
#include "engine.h"
__attribute__((naked)) int32_t opencfw_iar_format_engine(opencfw_format_put put,void *context,const char *format,uint32_t **cursor,unsigned mode){__asm__ volatile(
 "push.w {r0,r4,r5,r6,r7,r8,r9,r10,r11,lr}\n"
 "sub sp,#192\n"
 "mov r4,sp\n"
 "ldr r5,[sp,#232]\n"
 "sub sp,#8\n"
 "str r5,[sp]\n"
 "str r4,[sp,#4]\n"
 "bl opencfw_iar_format_core\n"
 "add sp,#8\n"
 "add sp,#196\n"
 "pop.w {r4,r5,r6,r7,r8,r9,r10,r11,pc}\n");}
