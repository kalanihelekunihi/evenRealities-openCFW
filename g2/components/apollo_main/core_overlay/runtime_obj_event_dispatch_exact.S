/*
 * SPDX-License-Identifier: MIT
 *
 * Source-shaped AM-004 route for LVGL 9.3 lv_obj_event dispatcher at
 * 0x0043E7D2..0x0043EBEC.  Generated from authenticated stock
 * disassembly with retained/source provider calls named explicitly.
 */

    .syntax unified
    .thumb
    .section .text.open_cfw_runtime_obj_event_dispatch_exact,"ax",%progbits
    .global open_cfw_runtime_obj_event_dispatch_exact
    .type open_cfw_runtime_obj_event_dispatch_exact,%function
    .thumb_func
open_cfw_runtime_obj_event_dispatch_exact:
    push.w {r4, r5, r6, r7, r8, lr}
    sub sp, #0x20
    movs r6, r1
    movs r0, r6
    bl open_cfw_retained_lv_event_get_code_obj
    movs r4, r0
    movs r0, r6
    ldr r0, [r0]
    mov r8, r8
    movs r5, r0
    cmp r4, #1
    bne L_dispatch_0043e7f8
    movs r1, #0x20
    movs r0, r5
    bl open_cfw_retained_obj_add_state
    b L_dispatch_0043ebe6
L_dispatch_0043e7f8:
    cmp r4, #0xb
    bne L_dispatch_0043e852
    movs r1, #0x20
    movs r0, r5
    bl open_cfw_retained_obj_remove_state
    movs r0, r6
    ldr r0, [r0, #0x10]
    mov r8, r8
    bl open_cfw_retained_indev_scroll_obj_is_null
    cmp r0, #0
    bne.w L_dispatch_0043ebe6
    movs r1, #8
    movs r0, r5
    bl open_cfw_retained_obj_has_flag_core
    cmp r0, #0
    beq.w L_dispatch_0043ebe6
    movs r0, r5
    bl open_cfw_retained_obj_get_state_core
    lsls r0, r0, #0x1f
    bmi L_dispatch_0043e836
    movs r1, #1
    movs r0, r5
    bl open_cfw_retained_obj_add_state
    b L_dispatch_0043e83e
L_dispatch_0043e836:
    movs r1, #1
    movs r0, r5
    bl open_cfw_retained_obj_remove_state
L_dispatch_0043e83e:
    movs r2, #0
    movs r1, #0x23
    movs r0, r5
    bl open_cfw_retained_obj_send_value_changed
    uxtb r0, r0
    cmp r0, #1
    beq.w L_dispatch_0043ebe6
    b L_dispatch_0043ebe6
L_dispatch_0043e852:
    cmp r4, #3
    bne L_dispatch_0043e860
    movs r1, #0x20
    movs r0, r5
    bl open_cfw_retained_obj_remove_state
    b L_dispatch_0043ebe6
L_dispatch_0043e860:
    cmp r4, #0x32
    bne L_dispatch_0043e884
    movs r0, r5
    bl open_cfw_retained_obj_get_child_count
    movs r4, r0
    movs r6, #0
L_dispatch_0043e86e:
    cmp r6, r4
    bhs.w L_dispatch_0043ebe6
    ldr r0, [r5, #8]
    ldr r0, [r0]
    ldr.w r0, [r0, r6, lsl #2]
    bl open_cfw_retained_obj_invalidate
    adds r6, r6, #1
    b L_dispatch_0043e86e
L_dispatch_0043e884:
    cmp r4, #0x11
    bne.w L_dispatch_0043ea24
    movs r1, #8
    movs r0, r5
    bl open_cfw_retained_obj_has_flag_core
    cmp r0, #0
    beq L_dispatch_0043e8da
    movs r0, r6
    bl open_cfw_retained_event_get_key
    movs r4, r0
    cmp r4, #0x13
    beq L_dispatch_0043e8a6
    cmp r4, #0x11
    bne L_dispatch_0043e8b0
L_dispatch_0043e8a6:
    movs r1, #1
    movs r0, r5
    bl open_cfw_retained_obj_add_state
    b L_dispatch_0043e8c0
L_dispatch_0043e8b0:
    cmp r4, #0x14
    beq L_dispatch_0043e8b8
    cmp r4, #0x12
    bne L_dispatch_0043e8c0
L_dispatch_0043e8b8:
    movs r1, #1
    movs r0, r5
    bl open_cfw_retained_obj_remove_state
L_dispatch_0043e8c0:
    cmp r4, #0xa
    beq.w L_dispatch_0043ebe6
    movs r2, #0
    movs r1, #0x23
    movs r0, r5
    bl open_cfw_retained_obj_send_value_changed
    uxtb r0, r0
    cmp r0, #1
    beq.w L_dispatch_0043ebe6
    b L_dispatch_0043ebe6
L_dispatch_0043e8da:
    mov.w r1, #0x810
    movs r0, r5
    bl open_cfw_retained_obj_has_flag_core
    cmp r0, #0
    beq.w L_dispatch_0043ebe6
    movs r0, r5
    bl open_cfw_retained_obj_is_editable_disabled
    cmp r0, #0
    bne.w L_dispatch_0043ebe6
    movs r4, #0
    movs r0, r5
    bl open_cfw_retained_obj_get_scroll_left
    movs r7, r0
    movs r0, r5
    bl open_cfw_retained_obj_get_scroll_right
    mov r8, r0
    movs r0, r6
    bl open_cfw_retained_event_get_key
    cmp r0, #0x12
    bne L_dispatch_0043e936
    movs r0, r5
    bl open_cfw_retained_obj_get_scroll_x
    movs r6, r0
    movs r0, r5
    bl open_cfw_retained_obj_get_width
    movs r2, r4
    uxtb r2, r2
    movs r1, #4
    sdiv r0, r0, r1
    adds r6, r0, r6
    movs r1, r6
    movs r0, r5
    bl open_cfw_retained_obj_scroll_to_x
    b L_dispatch_0043ebe6
L_dispatch_0043e936:
    cmp r0, #0x11
    bne L_dispatch_0043e95e
    movs r0, r5
    bl open_cfw_retained_obj_get_scroll_x
    movs r6, r0
    movs r0, r5
    bl open_cfw_retained_obj_get_width
    movs r2, r4
    uxtb r2, r2
    movs r1, #4
    sdiv r0, r0, r1
    subs r6, r6, r0
    movs r1, r6
    movs r0, r5
    bl open_cfw_retained_obj_scroll_to_x
    b L_dispatch_0043ebe6
L_dispatch_0043e95e:
    cmp r0, #0x13
    bne L_dispatch_0043e9c0
    movs r0, r5
    bl open_cfw_retained_obj_get_scroll_dir
    tst.w r0, #3
    beq L_dispatch_0043e978
    cmp r7, #1
    bge L_dispatch_0043e99c
    cmp.w r8, #1
    bge L_dispatch_0043e99c
L_dispatch_0043e978:
    movs r0, r5
    bl open_cfw_retained_obj_get_scroll_x
    movs r6, r0
    movs r0, r5
    bl open_cfw_retained_obj_get_width
    movs r2, r4
    uxtb r2, r2
    movs r1, #4
    sdiv r0, r0, r1
    adds r6, r0, r6
    movs r1, r6
    movs r0, r5
    bl open_cfw_retained_obj_scroll_to_x
    b L_dispatch_0043ebe6
L_dispatch_0043e99c:
    movs r0, r5
    bl open_cfw_retained_obj_get_scroll_y
    movs r6, r0
    movs r0, r5
    bl open_cfw_retained_obj_get_height
    movs r2, r4
    uxtb r2, r2
    movs r1, #4
    sdiv r0, r0, r1
    adds r6, r0, r6
    movs r1, r6
    movs r0, r5
    bl open_cfw_retained_obj_scroll_to_y
    b L_dispatch_0043ebe6
L_dispatch_0043e9c0:
    cmp r0, #0x14
    bne.w L_dispatch_0043ebe6
    movs r0, r5
    bl open_cfw_retained_obj_get_scroll_dir
    tst.w r0, #3
    beq L_dispatch_0043e9dc
    cmp r7, #1
    bge L_dispatch_0043ea00
    cmp.w r8, #1
    bge L_dispatch_0043ea00
L_dispatch_0043e9dc:
    movs r0, r5
    bl open_cfw_retained_obj_get_scroll_x
    movs r6, r0
    movs r0, r5
    bl open_cfw_retained_obj_get_width
    movs r2, r4
    uxtb r2, r2
    movs r1, #4
    sdiv r0, r0, r1
    subs r6, r6, r0
    movs r1, r6
    movs r0, r5
    bl open_cfw_retained_obj_scroll_to_x
    b L_dispatch_0043ebe6
L_dispatch_0043ea00:
    movs r0, r5
    bl open_cfw_retained_obj_get_scroll_y
    movs r6, r0
    movs r0, r5
    bl open_cfw_retained_obj_get_height
    movs r2, r4
    uxtb r2, r2
    movs r1, #4
    sdiv r0, r0, r1
    subs r6, r6, r0
    movs r1, r6
    movs r0, r5
    bl open_cfw_retained_obj_scroll_to_y
    b L_dispatch_0043ebe6
L_dispatch_0043ea24:
    cmp r4, #0x13
    bne L_dispatch_0043ea9c
    mov.w r1, #0x400
    movs r0, r5
    bl open_cfw_retained_obj_has_flag_core
    cmp r0, #0
    beq L_dispatch_0043ea3e
    movs r1, #1
    movs r0, r5
    bl open_cfw_retained_obj_scroll_to_view
L_dispatch_0043ea3e:
    movs r0, #0
    movs r0, r5
    bl open_cfw_retained_obj_clear_focus_scroll_state
    bl open_cfw_retained_group_get_editing
    movs r4, r0
    movs r7, #2
    bl open_cfw_retained_indev_get_scroll_obj
    cmp r0, #0
    bne L_dispatch_0043ea5c
    movs r0, r6
    bl open_cfw_retained_event_stop_bubbling
L_dispatch_0043ea5c:
    bl open_cfw_retained_indev_get_type
    movs r1, r0
    uxtb r1, r1
    cmp r1, #2
    beq L_dispatch_0043ea6e
    uxtb r0, r0
    cmp r0, #4
    bne L_dispatch_0043ea72
L_dispatch_0043ea6e:
    orrs r7, r7, #4
L_dispatch_0043ea72:
    uxtb r4, r4
    cmp r4, #0
    beq L_dispatch_0043ea88
    orrs r7, r7, #8
    movs r1, r7
    uxth r1, r1
    movs r0, r5
    bl open_cfw_retained_obj_add_state
    b L_dispatch_0043ebe6
L_dispatch_0043ea88:
    movs r1, r7
    uxth r1, r1
    movs r0, r5
    bl open_cfw_retained_obj_add_state
    movs r1, #8
    movs r0, r5
    bl open_cfw_retained_obj_remove_state
    b L_dispatch_0043ebe6
L_dispatch_0043ea9c:
    cmp r4, #0xc
    bne L_dispatch_0043eaaa
    movs r1, #0x40
    movs r0, r5
    bl open_cfw_retained_obj_add_state
    b L_dispatch_0043ebe6
L_dispatch_0043eaaa:
    cmp r4, #0xe
    bne L_dispatch_0043eade
    movs r1, #0x40
    movs r0, r5
    bl open_cfw_retained_obj_remove_state
    movs r0, r5
    bl open_cfw_retained_obj_get_scrollbar_mode
    cmp r0, #2
    bne.w L_dispatch_0043ebe6
    mov r2, sp
    add r1, sp, #0x10
    movs r0, r5
    bl open_cfw_retained_obj_get_scrollbar_area_pair
    add r1, sp, #0x10
    movs r0, r5
    bl open_cfw_retained_obj_invalidate_area
    mov r1, sp
    movs r0, r5
    bl open_cfw_retained_obj_invalidate_area
    b L_dispatch_0043ebe6
L_dispatch_0043eade:
    cmp r4, #0x14
    bne L_dispatch_0043eaec
    movs r1, #0xe
    movs r0, r5
    bl open_cfw_retained_obj_remove_state
    b L_dispatch_0043ebe6
L_dispatch_0043eaec:
    cmp r4, #0x31
    bne L_dispatch_0043eb30
    movs r1, #0
    movs r0, r5
    bl open_cfw_retained_obj_get_style_width
    movs r4, r0
    movs r1, #0
    movs r0, r5
    bl open_cfw_retained_obj_get_style_height
    uxth r0, r0
    cmp r0, #0
    bne L_dispatch_0043eb0c
    cmp r4, #0
    beq L_dispatch_0043eb12
L_dispatch_0043eb0c:
    movs r0, r5
    bl open_cfw_retained_obj_invalidate
L_dispatch_0043eb12:
    movs r0, r5
    bl open_cfw_retained_obj_get_child_count
    movs r6, r0
    movs r4, #0
L_dispatch_0043eb1c:
    cmp r4, r6
    bhs L_dispatch_0043ebe6
    ldr r0, [r5, #8]
    ldr r0, [r0]
    ldr.w r0, [r0, r4, lsl #2]
    bl open_cfw_retained_obj_invalidate
    adds r4, r4, #1
    b L_dispatch_0043eb1c
L_dispatch_0043eb30:
    cmp r4, #0x2a
    bne L_dispatch_0043eb78
    movs r1, #0
    movs r0, r5
    bl open_cfw_retained_obj_get_style_min_width
    movs r6, r0
    movs r1, #0
    movs r0, r5
    bl open_cfw_retained_obj_get_style_max_width
    movs r7, r0
    movs r1, #0
    movs r0, r5
    bl open_cfw_retained_obj_get_style_width
    movs r4, r0
    movs r1, #0
    movs r0, r5
    bl open_cfw_retained_obj_get_style_height
    uxth r0, r0
    cmp r0, #0
    bne L_dispatch_0043eb70
    cmp r4, #0
    bne L_dispatch_0043eb70
    mvns r0, #0xc0000000
    cmp r6, r0
    beq L_dispatch_0043eb70
    cmp r7, r0
    bne L_dispatch_0043ebe6
L_dispatch_0043eb70:
    movs r0, r5
    bl open_cfw_retained_obj_invalidate
    b L_dispatch_0043ebe6
L_dispatch_0043eb78:
    cmp r4, #0x2c
    bne L_dispatch_0043eb8c
    ldrh r0, [r5, #0x2a]
    orrs r0, r0, #2
    strh r0, [r5, #0x2a]
    movs r0, r5
    bl open_cfw_retained_obj_invalidate
    b L_dispatch_0043ebe6
L_dispatch_0043eb8c:
    cmp r4, #0x1b
    bne L_dispatch_0043eba2
    movs r1, #0
    movs r0, r5
    bl open_cfw_retained_obj_get_group
    movs r1, r0
    movs r0, r6
    bl open_cfw_retained_event_set_result
    b L_dispatch_0043ebe6
L_dispatch_0043eba2:
    cmp r4, #0x1d
    beq L_dispatch_0043ebae
    cmp r4, #0x20
    beq L_dispatch_0043ebae
    cmp r4, #0x1a
    bne L_dispatch_0043ebb6
L_dispatch_0043ebae:
    movs r0, r6
    bl open_cfw_runtime_obj_draw_event_core
    b L_dispatch_0043ebe6
L_dispatch_0043ebb6:
    cmp r4, #0x17
    bne L_dispatch_0043ebcc
    movs r1, #0x20
    movs r0, r5
    bl open_cfw_retained_obj_remove_state
    movs r1, #0x40
    movs r0, r5
    bl open_cfw_retained_obj_remove_state
    b L_dispatch_0043ebe6
L_dispatch_0043ebcc:
    cmp r4, #0x18
    bne L_dispatch_0043ebda
    movs r1, #0x10
    movs r0, r5
    bl open_cfw_retained_obj_add_state
    b L_dispatch_0043ebe6
L_dispatch_0043ebda:
    cmp r4, #0x19
    bne L_dispatch_0043ebe6
    movs r1, #0x10
    movs r0, r5
    bl open_cfw_retained_obj_remove_state
L_dispatch_0043ebe6:
    add sp, #0x20
    pop.w {r4, r5, r6, r7, r8, pc}
    .size open_cfw_runtime_obj_event_dispatch_exact, .-open_cfw_runtime_obj_event_dispatch_exact
