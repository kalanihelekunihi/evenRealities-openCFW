/* SPDX-License-Identifier: MIT. Test linkage adapters for serialized stock
 * task entry pointers. Branches execute compiled source; these placements
 * are not the original instruction encoding or a byte-identical layout. */
.syntax unified
.thumb
.section .timer_task_adapter,"ax",%progbits
.thumb_func
.global opencfw_test_timer_entry
opencfw_test_timer_entry: b.w opencfw_boot_timer_task
.section .manager_task_adapter,"ax",%progbits
.thumb_func
.global opencfw_test_manager_entry
opencfw_test_manager_entry: b.w opencfw_boot_manager_task
.section .event_task_adapter,"ax",%progbits
.thumb_func
.global opencfw_test_event_entry
opencfw_test_event_entry: b.w opencfw_boot_event_thread

.section .dfu_init_adapter,"ax",%progbits
.thumb_func
.global opencfw_test_dfu_init_entry
opencfw_test_dfu_init_entry: b.w opencfw_boot_dfu_thread_init

.section .timer_callback_adapter,"ax",%progbits
.thumb_func
.global opencfw_test_timer_callback_entry
opencfw_test_timer_callback_entry: b.w opencfw_boot_timer_callback_dispatcher
