/* SPDX-License-Identifier: MIT */
/* Clean-room event-object initialization, callback dispatch, and enqueueing. */
typedef __UINT32_TYPE__ open_cfw_event_rt_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_queue_create_416816(void);
extern void open_cfw_bootloader_log_4176ce(void);
extern void open_cfw_bootloader_named_object_create_4163b2(void);
extern void open_cfw_bootloader_event_object_create_416610(void);
extern void open_cfw_bootloader_runtime_object_delete_416200(void);
extern void open_cfw_bootloader_runtime_task_create_4160fe(void);
extern void open_cfw_bootloader_queue_receive_416920(void);
extern void open_cfw_bootloader_queue_send_4168a2(void);

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_event_runtime_init_42e53c(void)
{__asm volatile(
 "push {r2, r3, r4, lr}\nldr.w r4, [pc, #0x2f8]\nldr r0, [r4]\ncmp r0, #0\nbne 1f\n"
 "ldr.w r2, [pc, #0x2f0]\nmovs r1, #8\nmovs r0, #0xf\n"
 "bl open_cfw_bootloader_queue_create_416816\nstr r0, [r4]\nldr r0, [r4]\ncmp r0, #0\nbne 1f\n"
 "ldr.w r0, [pc, #0x2e0]\nstr r0, [sp, #4]\nmovs r0, #0x58\nstr r0, [sp]\n"
 "ldr.w r3, [pc, #0x2dc]\nldr.w r2, [pc, #0x2dc]\nldr.w r1, [pc, #0x2dc]\nmovs r0, #1\n"
 "bl open_cfw_bootloader_log_4176ce\nb 1f\n"
 "1:\nldr.w r4, [pc, #0x2d4]\nldr r0, [r4]\ncmp r0, #0\nbne 2f\n"
 "ldr.w r3, [pc, #0x2cc]\nmovs r2, #0\nmovs r1, #0\naddw r0, pc, #0x165\n"
 "bl open_cfw_bootloader_named_object_create_4163b2\nstr r0, [r4]\nldr r0, [r4]\ncmp r0, #0\nbne 2f\n"
 "ldr.w r0, [pc, #0x2b8]\nstr r0, [sp, #4]\nmovs r0, #0x61\nstr r0, [sp]\n"
 "ldr.w r3, [pc, #0x29c]\nldr.w r2, [pc, #0x29c]\nldr.w r1, [pc, #0x29c]\nmovs r0, #1\n"
 "bl open_cfw_bootloader_log_4176ce\nb 2f\n"
 "2:\nldr.w r4, [pc, #0x2a0]\nldr r0, [r4]\ncmp r0, #0\nbne 3f\n"
 "ldr.w r0, [pc, #0x298]\nbl open_cfw_bootloader_event_object_create_416610\nstr r0, [r4]\n"
 "ldr r0, [r4]\ncmp r0, #0\nbne 3f\nldr.w r0, [pc, #0x28c]\nstr r0, [sp, #4]\n"
 "movs r0, #0x6a\nstr r0, [sp]\nldr.w r3, [pc, #0x264]\nldr.w r2, [pc, #0x264]\n"
 "ldr.w r1, [pc, #0x264]\nmovs r0, #1\nbl open_cfw_bootloader_log_4176ce\nb 3f\n"
 "3:\nldr.w r4, [pc, #0x274]\nldr r0, [r4]\ncmp r0, #0\nbeq 4f\n"
 "ldr r0, [r4]\nbl open_cfw_bootloader_runtime_object_delete_416200\nmovs r0, #0\nstr r0, [r4]\n"
 "4:\nldr r0, [r4]\ncmp r0, #0\nbne 5f\nldr.w r2, [pc, #0x25c]\nmovs r1, #0\n"
 "addw r0, pc, #0x31\nbl open_cfw_bootloader_runtime_task_create_4160fe\nstr r0, [r4]\nldr r0, [r4]\n"
 "cmp r0, #0\nbne 5f\nldr.w r0, [pc, #0x24c]\nstr r0, [sp, #4]\nmovs r0, #0x79\n"
 "str r0, [sp]\nldr.w r3, [pc, #0x214]\nldr.w r2, [pc, #0x214]\nldr.w r1, [pc, #0x214]\n"
 "movs r0, #1\nbl open_cfw_bootloader_log_4176ce\nb 5f\n5:\npop {r0, r1, r4, pc}\n");}

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_event_callback_loop_42e644(void)
{__asm volatile(
 "push {lr}\nsub sp, #0x14\nb 2f\n1:\nldr r0, [sp, #0xc]\nldr r1, [sp, #0x10]\nblx r1\n"
 "2:\nmovs.w r3, #-1\nmovs r2, #0\nadd r1, sp, #0xc\nldr.w r0, [pc, #0x1dc]\nldr r0, [r0]\n"
 "bl open_cfw_bootloader_queue_receive_416920\ncmp r0, #0\nbeq 1b\nstr r0, [sp, #8]\n"
 "ldr.w r0, [pc, #0x208]\nstr r0, [sp, #4]\nmovs r0, #0x8c\nstr r0, [sp]\n"
 "ldr.w r3, [pc, #0x204]\nldr.w r2, [pc, #0x1d0]\nldr.w r1, [pc, #0x1d0]\n"
 "movs r0, #1\nbl open_cfw_bootloader_log_4176ce\nb 2b\n");}

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_event_callback_enqueue_42e686(void)
{__asm volatile(
 "push {r3, r4, lr}\nsub sp, #0x14\nmovs r3, r2\nldr.w r2, [pc, #0x1d8]\nldr r2, [r2]\n"
 "cmp r2, #0\nbne 1f\nldr.w r0, [pc, #0x1e4]\nstr r0, [sp, #4]\nmovs r0, #0x96\n"
 "str r0, [sp]\nldr.w r3, [pc, #0x1dc]\nldr.w r2, [pc, #0x1a0]\nldr.w r1, [pc, #0x1a0]\n"
 "movs r0, #1\nbl open_cfw_bootloader_log_4176ce\nb 3f\n"
 "1:\nstr r0, [sp, #0x10]\nstr r1, [sp, #0xc]\nldr.w r4, [pc, #0x17c]\nldr r0, [r4]\n"
 "cmp r0, #0\nbeq 3f\nmovs r2, #0\nadd r1, sp, #0xc\nldr r0, [r4]\n"
 "bl open_cfw_bootloader_queue_send_4168a2\ncmp r0, #0\nbeq 3f\nstr r0, [sp, #8]\n"
 "ldr.w r0, [pc, #0x1b0]\nstr r0, [sp, #4]\nmovs r0, #0xa0\nstr r0, [sp]\n"
 "ldr.w r3, [pc, #0x1a0]\nldr.w r2, [pc, #0x164]\nldr.w r1, [pc, #0x164]\n"
 "movs r0, #1\nbl open_cfw_bootloader_log_4176ce\n"
 "3:\nadd sp, #0x18\npop {r4, pc}\n");}
#else
typedef open_cfw_event_rt_u32 (*open_cfw_event_rt_create_fn)(void);
typedef void (*open_cfw_event_rt_callback_fn)(open_cfw_event_rt_u32);

__attribute__((used,noinline,visibility("default")))
open_cfw_event_rt_u32 open_cfw_bootloader_event_runtime_init_42e53c_portable(
    open_cfw_event_rt_u32 handles[4],const open_cfw_event_rt_u32 created[4])
{open_cfw_event_rt_u32 failures=0U,i;for(i=0;i<3U;i++)if(handles[i]==0U){handles[i]=created[i];if(handles[i]==0U)failures|=1U<<i;}handles[3]=created[3];if(handles[3]==0U)failures|=8U;return failures;}

__attribute__((used,noinline,visibility("default")))
open_cfw_event_rt_u32 open_cfw_bootloader_event_callback_loop_step_42e644_portable(
    open_cfw_event_rt_u32 receive_status,open_cfw_event_rt_u32 argument,
    open_cfw_event_rt_callback_fn callback)
{if(receive_status==0U){callback(argument);return 1U;}return 0U;}

__attribute__((used,noinline,visibility("default")))
open_cfw_event_rt_u32 open_cfw_bootloader_event_callback_enqueue_42e686_portable(
    open_cfw_event_rt_u32 runtime_ready,open_cfw_event_rt_u32 queue_ready,
    open_cfw_event_rt_u32 send_status)
{if(runtime_ready==0U)return 1U;if(queue_ready==0U)return 0U;return send_status!=0U?2U:0U;}
#endif
