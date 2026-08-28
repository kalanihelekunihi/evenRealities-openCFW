/* SPDX-License-Identifier: BSD-3-Clause */
/*
 * Reviewable Thumb-2 realization of AmbiqSuite 5.1.0
 * am_hal_mspi_interrupt_service (am_hal_mspi.c:4169). The control-flow
 * blocks, ABI, callback ordering, and named provider edges are independently
 * corroborated by the same-size Apollo-main body at 0x004C240E.
 *
 * Executable instructions are expressed only as Thumb-2 mnemonics. Adjacent
 * literal/alignment pools remain retained data outside this section.
 */
.syntax unified
.thumb
.cpu cortex-m55

.extern open_cfw_bootloader_clock_release_422364
.extern open_cfw_bootloader_mspi_cq_enable_423f8e
.extern open_cfw_bootloader_mspi_cq_disable_423fac
.extern open_cfw_bootloader_mspi_program_dma_42403e
.extern open_cfw_bootloader_cmdq_get_status_427a56
.extern open_cfw_bootloader_cmdq_error_resume_427b38

.section .text.open_cfw_bootloader_mspi_interrupt_service_426536,"ax",%progbits
.global open_cfw_bootloader_mspi_interrupt_service_426536
.type open_cfw_bootloader_mspi_interrupt_service_426536,%function
.thumb_func
open_cfw_bootloader_mspi_interrupt_service_426536:

    /* ABI r0=pHandle, r1=ui32IntStatus; validate the MSPI state handle. */
    push.w   {r0, r1, r2, r3, r4, r5, r6, r7, r8, lr} /* 00426536 */
    movs     r7, r1                                 /* 0042653a */
    movs     r4, r0                                 /* 0042653c */
    cmp      r0, #0x0                               /* 0042653e */
    beq      .L_00426550                            /* 00426540 */
    ldr      r0, [r0]                               /* 00426542 */
    bic      r0, r0, #0xfe000000                    /* 00426544 */
    ldr.w    r1, [pc, #0x6b8]                       /* 00426548 */
    cmp      r0, r1                                 /* 0042654c */
    beq      .L_00426554                            /* 0042654e */
.L_00426550:
    movs     r0, #0x2                               /* 00426550 */
    b        .L_004267f8                            /* 00426552 */

    /* Select the high-priority transaction path and accumulate interrupt status. */
.L_00426554:
    ldr      r5, [r4, #0x4]                         /* 00426554 */
    ldrb.w   r0, [r4, #0x83c]                       /* 00426556 */
    cmp      r0, #0x0                               /* 0042655a */
    beq.w    .L_00426676                            /* 0042655c */
    ldr      r0, [r4, #0x24]                        /* 00426560 */
    orrs     r7, r0                                 /* 00426562 */
    str      r7, [r4, #0x24]                        /* 00426564 */
    ldr      r0, [r4, #0x24]                        /* 00426566 */
    tst.w    r0, #0x18c0                            /* 00426568 */
    beq      .L_00426624                            /* 0042656c */

    /* Wait for DMA completion, snapshot/clear status, and reset the transfer block on error. */
.L_0042656e:
    ldr      r6, [pc, #0x294]                       /* 0042656e */
    ldr      r0, [r4, #0x4]                         /* 00426570 */
    adds.w   r0, r6, r0, lsl #12                    /* 00426572 */
    ldr.w    r0, [r0, #0x104]                       /* 00426576 */
    lsls     r0, r0, #0x1f                          /* 0042657a */
    bmi      .L_0042656e                            /* 0042657c */
    ldr      r1, [r4, #0x24]                        /* 0042657e */
    adds.w   r0, r6, r5, lsl #12                    /* 00426580 */
    ldr.w    r0, [r0, #0x204]                       /* 00426584 */
    orrs     r1, r0                                 /* 00426588 */
    str      r1, [r4, #0x24]                        /* 0042658a */
    movs.w   r0, #0xffffffff                        /* 0042658c */
    adds.w   r1, r6, r5, lsl #12                    /* 00426590 */
    str.w    r0, [r1, #0x208]                       /* 00426594 */
    ldr      r0, [r4, #0x24]                        /* 00426598 */
    tst.w    r0, #0x1880                            /* 0042659a */
    beq      .L_004265d0                            /* 0042659e */
    movs     r1, #0x1                               /* 004265a0 */
    adds.w   r0, r6, r5, lsl #12                    /* 004265a2 */
    adds.w   r0, r0, #0x100                         /* 004265a6 */
    ldr      r2, [r0]                               /* 004265aa */
    lsrs     r2, r2, #0x2                           /* 004265ac */
    lsls     r2, r2, #0x2                           /* 004265ae */
    str      r2, [r0]                               /* 004265b0 */
    adds.w   r0, r6, r5, lsl #12                    /* 004265b2 */
    adds     r0, #0x30                              /* 004265b6 */
    ldr      r2, [r0]                               /* 004265b8 */
    bics     r2, r2, #0x40000000                    /* 004265ba */
    str      r2, [r0]                               /* 004265be */
    adds.w   r0, r6, r5, lsl #12                    /* 004265c0 */
    adds     r0, #0x30                              /* 004265c4 */
    ldr      r2, [r0]                               /* 004265c6 */
    orrs     r2, r2, #0x40000000                    /* 004265c8 */
    str      r2, [r0]                               /* 004265cc */
    b        .L_004265d2                            /* 004265ce */
.L_004265d0:
    movs     r1, #0x0                               /* 004265d0 */

    /* Advance the high-priority ring and deliver its completion callback. */
.L_004265d2:
    ldr.w    r0, [r4, #0x850]                       /* 004265d2 */
    adds     r0, r0, #0x1                           /* 004265d6 */
    str.w    r0, [r4, #0x850]                       /* 004265d8 */
    ldr.w    r0, [r4, #0x840]                       /* 004265dc */
    subs     r0, r0, #0x1                           /* 004265e0 */
    str.w    r0, [r4, #0x840]                       /* 004265e2 */
    ldr.w    r2, [r4, #0x850]                       /* 004265e6 */
    ldr.w    r0, [r4, #0x848]                       /* 004265ea */
    udiv     r3, r2, r0                             /* 004265ee */
    mls      r2, r0, r3, r2                         /* 004265f2 */
    ldr.w    r3, [r4, #0x854]                       /* 004265f6 */
    movs     r0, #0x18                              /* 004265fa */
    muls     r2, r0, r2                             /* 004265fc */
    add.w    r7, r3, r2                             /* 004265fe */
    ldr      r0, [r7, #0x10]                        /* 00426602 */
    cmp      r0, #0x0                               /* 00426604 */
    beq      .L_00426612                            /* 00426606 */
    ldr      r0, [r7, #0x14]                        /* 00426608 */
    ldr      r2, [r7, #0x10]                        /* 0042660a */
    blx      r2                                     /* 0042660c */
    movs     r0, #0x0                               /* 0042660e */
    str      r0, [r7, #0x10]                        /* 00426610 */
.L_00426612:
    ldr.w    r0, [r4, #0x840]                       /* 00426612 */
    cmp      r0, #0x0                               /* 00426616 */
    beq      .L_00426628                            /* 00426618 */
    movs     r0, #0x0                               /* 0042661a */
    str      r0, [r4, #0x24]                        /* 0042661c */
    movs     r0, r4                                 /* 0042661e */
    bl       open_cfw_bootloader_mspi_program_dma_42403e /* 00426620 */
.L_00426624:
    movs     r0, #0x0                               /* 00426624 */
    b        .L_004267f8                            /* 00426626 */
.L_00426628:
    movs     r0, #0x0                               /* 00426628 */
    strb.w   r0, [r4, #0x83c]                       /* 0042662a */
    movs     r0, #0x0                               /* 0042662e */
    adds.w   r1, r6, r5, lsl #12                    /* 00426630 */
    str.w    r0, [r1, #0x100]                       /* 00426634 */
    adds.w   r0, r6, r5, lsl #12                    /* 00426638 */
    ldr.w    r0, [r0, #0x200]                       /* 0042663c */
    bics     r0, r0, #0x40                          /* 00426640 */
    adds.w   r1, r6, r5, lsl #12                    /* 00426644 */
    str.w    r0, [r1, #0x200]                       /* 00426648 */
    movs     r0, #0x80                              /* 0042664c */
    adds.w   r6, r6, r5, lsl #12                    /* 0042664e */
    str.w    r0, [r6, #0x2b4]                       /* 00426652 */
    ldr      r0, [r4, #0x20]                        /* 00426656 */
    cmp      r0, #0x0                               /* 00426658 */
    bne      .L_00426624                            /* 0042665a */
    ldrb.w   r0, [r4, #0x8c9]                       /* 0042665c */
    cmp      r0, #0x4                               /* 00426660 */
    beq      .L_00426624                            /* 00426662 */
    ldr      r1, [r4, #0x4]                         /* 00426664 */
    adds     r1, #0x10                              /* 00426666 */
    uxtb     r1, r1                                 /* 00426668 */
    movs     r0, #0x4                               /* 0042666a */
    bl       open_cfw_bootloader_clock_release_422364 /* 0042666c */
    cmp      r0, #0x0                               /* 00426670 */
    beq      .L_00426624                            /* 00426672 */
    b        .L_004267f8                            /* 00426674 */

    /* Command-queue path: accumulate status and query the retained CMDQ provider. */
.L_00426676:
    ldr      r0, [r4, #0x20]                        /* 00426676 */
    cmp      r0, #0x0                               /* 00426678 */
    beq.w    .L_004267f6                            /* 0042667a */
    ldr.w    r0, [pc, #0x588]                       /* 0042667e */
    mov.w    r1, #0x8d0                             /* 00426682 */
    mul      r1, r1, r5                             /* 00426686 */
    add      r0, r1                                 /* 0042668a */
    addw     r6, r0, #0x828                         /* 0042668c */
    ldr      r0, [r4, #0x24]                        /* 00426690 */
    orrs     r0, r7                                 /* 00426692 */
    str      r0, [r4, #0x24]                        /* 00426694 */
    ldr      r0, [r6]                               /* 00426696 */
    cmp      r0, #0x0                               /* 00426698 */
    beq.w    .L_004267c6                            /* 0042669a */
    mov      r1, sp                                 /* 0042669e */
    ldr      r0, [r6]                               /* 004266a0 */
    bl       open_cfw_bootloader_cmdq_get_status_427a56 /* 004266a2 */
    cmp      r0, #0x0                               /* 004266a6 */
    bne.w    .L_004267c6                            /* 004266a8 */
    movs     r0, #0x0                               /* 004266ac */
    strb.w   r0, [r4, #0x834]                       /* 004266ae */
    b        .L_004266fc                            /* 004266b2 */

    /* Drain successful CQ callbacks through the last processed index. */
.L_004266b4:
    ldr      r0, [r4, #0x1c]                        /* 004266b4 */
    ldr      r1, [sp]                               /* 004266b6 */
    cmp      r0, r1                                 /* 004266b8 */
    beq      .L_00426704                            /* 004266ba */
    ldr      r0, [r4, #0x1c]                        /* 004266bc */
    adds     r0, r0, #0x1                           /* 004266be */
    str      r0, [r4, #0x1c]                        /* 004266c0 */
    ldr      r0, [r4, #0x20]                        /* 004266c2 */
    subs     r0, r0, #0x1                           /* 004266c4 */
    str      r0, [r4, #0x20]                        /* 004266c6 */
    ldrb.w   r8, [r4, #0x1c]                        /* 004266c8 */
    and      r8, r8, #0xff                          /* 004266cc */
    add.w    r0, r4, r8, lsl #2                     /* 004266d0 */
    ldr      r0, [r0, #0x28]                        /* 004266d4 */
    cmp      r0, #0x0                               /* 004266d6 */
    beq      .L_004266fc                            /* 004266d8 */
    movs     r1, #0x0                               /* 004266da */
    add.w    r0, r4, r8, lsl #2                     /* 004266dc */
    ldr.w    r0, [r0, #0x428]                       /* 004266e0 */
    add.w    r2, r4, r8, lsl #2                     /* 004266e4 */
    ldr      r2, [r2, #0x28]                        /* 004266e8 */
    blx      r2                                     /* 004266ea */
    ldrb.w   r0, [r4, #0x82c]                       /* 004266ec */
    cmp      r0, #0x2                               /* 004266f0 */
    beq      .L_004266fc                            /* 004266f2 */
    movs     r0, #0x0                               /* 004266f4 */
    add.w    r1, r4, r8, lsl #2                     /* 004266f6 */
    str      r0, [r1, #0x28]                        /* 004266fa */
.L_004266fc:
    ldrb.w   r0, [r4, #0x834]                       /* 004266fc */
    cmp      r0, #0x0                               /* 00426700 */
    beq      .L_004266b4                            /* 00426702 */

    /* Deliver the one additional failure callback required by an error status. */
.L_00426704:
    ldrb.w   r0, [r4, #0x834]                       /* 00426704 */
    cmp      r0, #0x0                               /* 00426708 */
    bne      .L_004267c6                            /* 0042670a */
    tst.w    r7, #0x1880                            /* 0042670c */
    bne      .L_0042671a                            /* 00426710 */
    ldrb.w   r0, [sp, #0xe]                         /* 00426712 */
    cmp      r0, #0x0                               /* 00426716 */
    beq      .L_004267b6                            /* 00426718 */
.L_0042671a:
    ldr      r0, [r4, #0x1c]                        /* 0042671a */
    adds     r0, r0, #0x1                           /* 0042671c */
    str      r0, [r4, #0x1c]                        /* 0042671e */
    ldr      r0, [r4, #0x20]                        /* 00426720 */
    subs     r0, r0, #0x1                           /* 00426722 */
    str      r0, [r4, #0x20]                        /* 00426724 */
    ldrb     r7, [r4, #0x1c]                        /* 00426726 */
    and      r7, r7, #0xff                          /* 00426728 */
    add.w    r0, r4, r7, lsl #2                     /* 0042672c */
    ldr      r0, [r0, #0x28]                        /* 00426730 */
    cmp      r0, #0x0                               /* 00426732 */
    beq      .L_00426758                            /* 00426734 */
    movs     r1, #0x1                               /* 00426736 */
    add.w    r0, r4, r7, lsl #2                     /* 00426738 */
    ldr.w    r0, [r0, #0x428]                       /* 0042673c */
    add.w    r2, r4, r7, lsl #2                     /* 00426740 */
    ldr      r2, [r2, #0x28]                        /* 00426744 */
    blx      r2                                     /* 00426746 */
    ldrb.w   r0, [r4, #0x82c]                       /* 00426748 */
    cmp      r0, #0x2                               /* 0042674c */
    beq      .L_00426758                            /* 0042674e */
    movs     r0, #0x0                               /* 00426750 */
    add.w    r1, r4, r7, lsl #2                     /* 00426752 */
    str      r0, [r1, #0x28]                        /* 00426756 */
.L_00426758:
    movs     r0, r4                                 /* 00426758 */

    /* Disable/reset/resume the CQ after error, then re-enable it when work remains. */
    bl       open_cfw_bootloader_mspi_cq_disable_423fac /* 0042675a */
    cmp      r0, #0x0                               /* 0042675e */
    bne      .L_004267f8                            /* 00426760 */
    ldr      r0, [pc, #0xa0]                        /* 00426762 */
    adds.w   r1, r0, r5, lsl #12                    /* 00426764 */
    adds.w   r1, r1, #0x100                         /* 00426768 */
    ldr      r2, [r1]                               /* 0042676c */
    lsrs     r2, r2, #0x2                           /* 0042676e */
    lsls     r2, r2, #0x2                           /* 00426770 */
    str      r2, [r1]                               /* 00426772 */
    adds.w   r1, r0, r5, lsl #12                    /* 00426774 */
    adds     r1, #0x30                              /* 00426778 */
    ldr      r2, [r1]                               /* 0042677a */
    bics     r2, r2, #0x40000000                    /* 0042677c */
    str      r2, [r1]                               /* 00426780 */
    adds.w   r1, r0, r5, lsl #12                    /* 00426782 */
    adds     r1, #0x30                              /* 00426786 */
    ldr      r2, [r1]                               /* 00426788 */
    orrs     r2, r2, #0x40000000                    /* 0042678a */
    str      r2, [r1]                               /* 0042678e */
    adds.w   r1, r0, r5, lsl #12                    /* 00426790 */
    ldr.w    r1, [r1, #0x2ac]                       /* 00426794 */
    adds.w   r0, r0, r5, lsl #12                    /* 00426798 */
    str.w    r1, [r0, #0x2ac]                       /* 0042679c */
    ldr      r0, [r6]                               /* 004267a0 */
    bl       open_cfw_bootloader_cmdq_error_resume_427b38 /* 004267a2 */
    ldr      r0, [r4, #0x20]                        /* 004267a6 */
    cmp      r0, #0x0                               /* 004267a8 */
    beq      .L_004267b6                            /* 004267aa */
    movs     r0, r4                                 /* 004267ac */
    bl       open_cfw_bootloader_mspi_cq_enable_423f8e /* 004267ae */
    cmp      r0, #0x0                               /* 004267b2 */
    bne      .L_004267f8                            /* 004267b4 */
.L_004267b6:
    ldr      r0, [r4, #0x20]                        /* 004267b6 */
    cmp      r0, #0x0                               /* 004267b8 */
    bne      .L_004267c6                            /* 004267ba */
    movs     r0, r4                                 /* 004267bc */
    bl       open_cfw_bootloader_mspi_cq_disable_423fac /* 004267be */
    cmp      r0, #0x0                               /* 004267c2 */
    bne      .L_004267f8                            /* 004267c4 */

    /* Quiesce DMA and release the non-HFRC clock after the queue drains. */
.L_004267c6:
    ldr      r0, [r4, #0x20]                        /* 004267c6 */
    cmp      r0, #0x0                               /* 004267c8 */
    bne      .L_004267f6                            /* 004267ca */
    ldr      r0, [pc, #0x34]                        /* 004267cc */
    adds.w   r0, r0, r5, lsl #12                    /* 004267ce */
    adds.w   r0, r0, #0x100                         /* 004267d2 */
    ldr      r1, [r0]                               /* 004267d6 */
    lsrs     r1, r1, #0x2                           /* 004267d8 */
    lsls     r1, r1, #0x2                           /* 004267da */
    str      r1, [r0]                               /* 004267dc */
    ldrb.w   r0, [r4, #0x8c9]                       /* 004267de */
    cmp      r0, #0x4                               /* 004267e2 */
    beq      .L_004267f6                            /* 004267e4 */
    ldr      r1, [r4, #0x4]                         /* 004267e6 */
    adds     r1, #0x10                              /* 004267e8 */
    uxtb     r1, r1                                 /* 004267ea */
    movs     r0, #0x4                               /* 004267ec */
    bl       open_cfw_bootloader_clock_release_422364 /* 004267ee */
    cmp      r0, #0x0                               /* 004267f2 */
    bne      .L_004267f8                            /* 004267f4 */
.L_004267f6:
    movs     r0, #0x0                               /* 004267f6 */

    /* Return the Ambiq HAL status in r0. */
.L_004267f8:
    add      sp, #0x10                              /* 004267f8 */
    pop.w    {r4, r5, r6, r7, r8, pc}               /* 004267fa */
.size open_cfw_bootloader_mspi_interrupt_service_426536, .-open_cfw_bootloader_mspi_interrupt_service_426536

/* SPDX-License-Identifier: BSD-3-Clause */
/*
 * Reviewable Thumb-2 realization of AmbiqSuite 5.1.0
 * am_hal_mspi_power_control (am_hal_mspi.c:4440). Register save/restore
 * ordering, short-enum ABI, and named provider edges are independently
 * corroborated by the same-size Apollo-main body at 0x004C26E0.
 *
 * Executable instructions are expressed only as Thumb-2 mnemonics. Adjacent
 * literal/alignment pools remain retained data outside this section.
 */
.syntax unified
.thumb
.cpu cortex-m55

.extern open_cfw_bootloader_pwrctrl_periph_enable_41bf84
.extern open_cfw_bootloader_pwrctrl_periph_disable_41c17a
.extern open_cfw_bootloader_delay_us_41d1c0
.extern open_cfw_bootloader_clock_request_4222f0
.extern open_cfw_bootloader_clock_release_all_4223d8
.extern open_cfw_bootloader_mspi_cq_enable_423f8e
.extern open_cfw_bootloader_mspi_cq_disable_423fac
.extern open_cfw_bootloader_mspi_clkgen_ctrl_4249a0
.extern open_cfw_bootloader_mspi_interrupt_disable_426484

.section .text.open_cfw_bootloader_mspi_power_control_426808,"ax",%progbits
.global open_cfw_bootloader_mspi_power_control_426808
.type open_cfw_bootloader_mspi_power_control_426808,%function
.thumb_func
open_cfw_bootloader_mspi_power_control_426808:

    /* ABI r0=pHandle, r1=ePowerState (short enum), r2=bRetainState; validate the handle. */
    push     {r4, r5, r6, lr}                       /* 00426808 */
    movs     r4, r0                                 /* 0042680a */
    movs     r6, r2                                 /* 0042680c */
    movs     r5, r4                                 /* 0042680e */
    cmp      r4, #0x0                               /* 00426810 */
    beq      .L_00426822                            /* 00426812 */
    ldr      r0, [r4]                               /* 00426814 */
    bic      r0, r0, #0xfe000000                    /* 00426816 */
    ldr.w    r2, [pc, #0x3e8]                       /* 0042681a */
    cmp      r0, r2                                 /* 0042681e */
    beq      .L_00426826                            /* 00426820 */
.L_00426822:
    movs     r0, #0x2                               /* 00426822 */
    b        .L_00426a24                            /* 00426824 */

    /* Dispatch WAKE versus NORMALSLEEP/DEEPSLEEP and reject other states. */
.L_00426826:
    uxtb     r1, r1                                 /* 00426826 */
    cmp      r1, #0x0                               /* 00426828 */
    beq      .L_00426838                            /* 0042682a */
    cmp      r1, #0x2                               /* 0042682c */
    beq.w    .L_00426a26                            /* 0042682e */
    blo.w    .L_00426a26                            /* 00426832 */
    b        .L_00426bfa                            /* 00426836 */

    /* WAKE: validate retained state and enable the selected MSPI peripheral. */
.L_00426838:
    movs     r0, r6                                 /* 00426838 */
    uxtb     r0, r0                                 /* 0042683a */
    cmp      r0, #0x0                               /* 0042683c */
    beq      .L_0042684c                            /* 0042683e */
    ldrb.w   r0, [r5, #0x860]                       /* 00426840 */
    cmp      r0, #0x0                               /* 00426844 */
    bne      .L_0042684c                            /* 00426846 */
    movs     r0, #0x7                               /* 00426848 */
    b        .L_00426a24                            /* 0042684a */
.L_0042684c:
    ldr      r0, [r5, #0x4]                         /* 0042684c */
    adds     r0, #0x10                              /* 0042684e */
    uxtb     r0, r0                                 /* 00426850 */
    bl       open_cfw_bootloader_pwrctrl_periph_enable_41bf84 /* 00426852 */
    uxtb     r6, r6                                 /* 00426856 */
    cmp      r6, #0x0                               /* 00426858 */
    beq.w    .L_00426a00                            /* 0042685a */
    ldrb.w   r0, [r5, #0x8c9]                       /* 0042685e */
    cmp      r0, #0x7                               /* 00426862 */
    bne      .L_0042686a                            /* 00426864 */
    movs     r0, #0x7                               /* 00426866 */
    b        .L_00426a24                            /* 00426868 */

    /* Retained wake: request its clock and restore the saved register image. */
.L_0042686a:
    ldr      r1, [r5, #0x4]                         /* 0042686a */
    adds     r1, #0x10                              /* 0042686c */
    uxtb     r1, r1                                 /* 0042686e */
    ldrb.w   r0, [r5, #0x8c9]                       /* 00426870 */
    bl       open_cfw_bootloader_clock_request_4222f0 /* 00426874 */
    cmp      r0, #0x0                               /* 00426878 */
    bne.w    .L_00426a24                            /* 0042687a */
    movs     r3, #0x0                               /* 0042687e */
    movs     r2, #0x0                               /* 00426880 */
    movs     r1, #0x1                               /* 00426882 */
    ldr      r0, [r5, #0x4]                         /* 00426884 */
    bl       open_cfw_bootloader_mspi_clkgen_ctrl_4249a0 /* 00426886 */
    ldr.w    r0, [pc, #0x380]                       /* 0042688a */
    ldr      r1, [r5, #0x4]                         /* 0042688e */

    /* Restore DEV, pad, CQ, DMA, threshold, and interrupt registers in upstream order. */
    adds.w   r1, r0, r1, lsl #12                    /* 00426890 */
    ldr.w    r2, [r5, #0x864]                       /* 00426894 */
    str.w    r2, [r1, #0x80]                        /* 00426898 */
    ldr      r1, [r5, #0x4]                         /* 0042689c */
    adds.w   r1, r0, r1, lsl #12                    /* 0042689e */
    ldr.w    r2, [r5, #0x868]                       /* 004268a2 */
    str.w    r2, [r1, #0x84]                        /* 004268a6 */
    ldr      r1, [r5, #0x4]                         /* 004268aa */
    adds.w   r1, r0, r1, lsl #12                    /* 004268ac */
    ldr.w    r2, [r5, #0x86c]                       /* 004268b0 */
    str.w    r2, [r1, #0x88]                        /* 004268b4 */
    ldr      r1, [r5, #0x4]                         /* 004268b8 */
    adds.w   r1, r0, r1, lsl #12                    /* 004268ba */
    ldr.w    r2, [r5, #0x870]                       /* 004268be */
    str.w    r2, [r1, #0x8c]                        /* 004268c2 */
    ldr      r1, [r5, #0x4]                         /* 004268c6 */
    adds.w   r1, r0, r1, lsl #12                    /* 004268c8 */
    ldr.w    r2, [r5, #0x874]                       /* 004268cc */
    str.w    r2, [r1, #0x90]                        /* 004268d0 */
    ldr      r1, [r5, #0x4]                         /* 004268d4 */
    adds.w   r1, r0, r1, lsl #12                    /* 004268d6 */
    ldr.w    r2, [r5, #0x878]                       /* 004268da */
    str.w    r2, [r1, #0x94]                        /* 004268de */
    ldr      r1, [r5, #0x4]                         /* 004268e2 */
    adds.w   r1, r0, r1, lsl #12                    /* 004268e4 */
    ldr.w    r2, [r5, #0x87c]                       /* 004268e8 */
    str.w    r2, [r1, #0x98]                        /* 004268ec */
    ldr      r1, [r5, #0x4]                         /* 004268f0 */
    adds.w   r1, r0, r1, lsl #12                    /* 004268f2 */
    ldr.w    r2, [r5, #0x880]                       /* 004268f6 */
    str.w    r2, [r1, #0x9c]                        /* 004268fa */
    ldr      r1, [r5, #0x4]                         /* 004268fe */
    adds.w   r1, r0, r1, lsl #12                    /* 00426900 */
    ldr.w    r2, [r5, #0x884]                       /* 00426904 */
    str.w    r2, [r1, #0xa0]                        /* 00426908 */
    ldr      r1, [r5, #0x4]                         /* 0042690c */
    adds.w   r1, r0, r1, lsl #12                    /* 0042690e */
    ldr.w    r2, [r5, #0x888]                       /* 00426912 */
    str.w    r2, [r1, #0xa4]                        /* 00426916 */
    ldr      r1, [r5, #0x4]                         /* 0042691a */
    adds.w   r1, r0, r1, lsl #12                    /* 0042691c */
    ldr.w    r2, [r5, #0x88c]                       /* 00426920 */
    str.w    r2, [r1, #0xa8]                        /* 00426924 */
    ldr      r1, [r5, #0x4]                         /* 00426928 */
    adds.w   r1, r0, r1, lsl #12                    /* 0042692a */
    ldr.w    r2, [r5, #0x890]                       /* 0042692e */
    str      r2, [r1, #0x30]                        /* 00426932 */
    ldr      r1, [r5, #0x4]                         /* 00426934 */
    adds.w   r1, r0, r1, lsl #12                    /* 00426936 */
    ldr.w    r2, [r5, #0x894]                       /* 0042693a */
    str      r2, [r1, #0x44]                        /* 0042693e */
    ldr      r1, [r5, #0x4]                         /* 00426940 */
    adds.w   r1, r0, r1, lsl #12                    /* 00426942 */
    ldr.w    r2, [r5, #0x898]                       /* 00426946 */
    str      r2, [r1, #0x48]                        /* 0042694a */
    ldr      r1, [r5, #0x4]                         /* 0042694c */
    adds.w   r1, r0, r1, lsl #12                    /* 0042694e */
    ldr.w    r2, [r5, #0x89c]                       /* 00426952 */
    str      r2, [r1, #0x4c]                        /* 00426956 */
    ldr      r1, [r5, #0x4]                         /* 00426958 */
    adds.w   r1, r0, r1, lsl #12                    /* 0042695a */
    ldr.w    r2, [r5, #0x8a4]                       /* 0042695e */
    str.w    r2, [r1, #0x2a8]                       /* 00426962 */
    ldr      r1, [r5, #0x4]                         /* 00426966 */
    adds.w   r1, r0, r1, lsl #12                    /* 00426968 */
    ldr.w    r2, [r5, #0x8a8]                       /* 0042696c */
    str.w    r2, [r1, #0x2b8]                       /* 00426970 */
    ldr      r1, [r5, #0x4]                         /* 00426974 */
    adds.w   r1, r0, r1, lsl #12                    /* 00426976 */
    ldr.w    r2, [r5, #0x8ac]                       /* 0042697a */
    str.w    r2, [r1, #0x2c0]                       /* 0042697e */
    ldr      r1, [r5, #0x4]                         /* 00426982 */
    adds.w   r1, r0, r1, lsl #12                    /* 00426984 */
    ldr.w    r2, [r5, #0x8b0]                       /* 00426988 */
    str.w    r2, [r1, #0x2c4]                       /* 0042698c */
    ldr      r1, [r5, #0x4]                         /* 00426990 */
    adds.w   r1, r0, r1, lsl #12                    /* 00426992 */
    ldr.w    r2, [r5, #0x8b4]                       /* 00426996 */
    str.w    r2, [r1, #0x200]                       /* 0042699a */
    ldr      r1, [r5, #0x4]                         /* 0042699e */
    adds.w   r1, r0, r1, lsl #12                    /* 004269a0 */
    ldrb.w   r2, [r5, #0x8b8]                       /* 004269a4 */
    and      r2, r2, #0xff                          /* 004269a8 */
    str.w    r2, [r1, #0x2b4]                       /* 004269ac */
    ldr      r1, [r5, #0x4]                         /* 004269b0 */
    adds.w   r1, r0, r1, lsl #12                    /* 004269b2 */
    ldr.w    r2, [r5, #0x8bc]                       /* 004269b6 */
    str.w    r2, [r1, #0x114]                       /* 004269ba */
    ldr      r1, [r5, #0x4]                         /* 004269be */
    adds.w   r1, r0, r1, lsl #12                    /* 004269c0 */
    ldr.w    r2, [r5, #0x8c0]                       /* 004269c4 */
    str.w    r2, [r1, #0x118]                       /* 004269c8 */
    ldr      r1, [r5, #0x4]                         /* 004269cc */
    adds.w   r1, r0, r1, lsl #12                    /* 004269ce */
    ldr.w    r2, [r5, #0x8c4]                       /* 004269d2 */
    str      r2, [r1, #0x20]                        /* 004269d6 */
    ldr      r1, [r5, #0x4]                         /* 004269d8 */
    adds.w   r0, r0, r1, lsl #12                    /* 004269da */
    ldr.w    r1, [r5, #0x8a0]                       /* 004269de */
    lsrs     r1, r1, #0x1                           /* 004269e2 */
    lsls     r1, r1, #0x1                           /* 004269e4 */
    str.w    r1, [r0, #0x2a0]                       /* 004269e6 */
    ldrb.w   r0, [r5, #0x8a0]                       /* 004269ea */
    lsls     r0, r0, #0x1f                          /* 004269ee */
    bpl      .L_004269f8                            /* 004269f0 */
    movs     r0, r5                                 /* 004269f2 */
    bl       open_cfw_bootloader_mspi_cq_enable_423f8e /* 004269f4 */
.L_004269f8:
    movs     r0, #0x0                               /* 004269f8 */
    strb.w   r0, [r5, #0x860]                       /* 004269fa */
    b        .L_00426a22                            /* 004269fe */

    /* Fresh wake: select/request HFRC and enable the MSPI clock generator. */
.L_00426a00:
    movs     r0, #0x4                               /* 00426a00 */
    strb.w   r0, [r5, #0x8c9]                       /* 00426a02 */
    ldr      r1, [r5, #0x4]                         /* 00426a06 */
    adds     r1, #0x10                              /* 00426a08 */
    uxtb     r1, r1                                 /* 00426a0a */
    movs     r0, #0x4                               /* 00426a0c */
    bl       open_cfw_bootloader_clock_request_4222f0 /* 00426a0e */
    cmp      r0, #0x0                               /* 00426a12 */
    bne      .L_00426a24                            /* 00426a14 */
    movs     r3, #0x8                               /* 00426a16 */
    movs     r2, #0x1                               /* 00426a18 */
    movs     r1, #0x1                               /* 00426a1a */
    ldr      r0, [r5, #0x4]                         /* 00426a1c */
    bl       open_cfw_bootloader_mspi_clkgen_ctrl_4249a0 /* 00426a1e */
.L_00426a22:
    movs     r0, #0x0                               /* 00426a22 */
.L_00426a24:
    pop      {r4, r5, r6, pc}                       /* 00426a24 */

    /* Sleep/deep-sleep: reject pending HP/CQ work before changing power state. */
.L_00426a26:
    ldr.w    r0, [r5, #0x840]                       /* 00426a26 */
    cmp      r0, #0x0                               /* 00426a2a */
    bne      .L_00426a34                            /* 00426a2c */
    ldr      r0, [r5, #0x20]                        /* 00426a2e */
    cmp      r0, #0x0                               /* 00426a30 */
    beq      .L_00426a38                            /* 00426a32 */
.L_00426a34:
    movs     r0, #0x3                               /* 00426a34 */
    b        .L_00426a24                            /* 00426a36 */

    /* When requested, save the complete MSPI register image and CQ enable state. */
.L_00426a38:
    uxtb     r6, r6                                 /* 00426a38 */
    cmp      r6, #0x0                               /* 00426a3a */
    beq.w    .L_00426bb0                            /* 00426a3c */
    ldr      r0, [pc, #0x1c8]                       /* 00426a40 */
    ldr      r1, [r5, #0x4]                         /* 00426a42 */
    adds.w   r1, r0, r1, lsl #12                    /* 00426a44 */
    ldr.w    r1, [r1, #0x80]                        /* 00426a48 */
    str.w    r1, [r5, #0x864]                       /* 00426a4c */
    ldr      r1, [r5, #0x4]                         /* 00426a50 */
    adds.w   r1, r0, r1, lsl #12                    /* 00426a52 */
    ldr.w    r1, [r1, #0x84]                        /* 00426a56 */
    str.w    r1, [r5, #0x868]                       /* 00426a5a */
    ldr      r1, [r5, #0x4]                         /* 00426a5e */
    adds.w   r1, r0, r1, lsl #12                    /* 00426a60 */
    ldr.w    r1, [r1, #0x88]                        /* 00426a64 */
    str.w    r1, [r5, #0x86c]                       /* 00426a68 */
    ldr      r1, [r5, #0x4]                         /* 00426a6c */
    adds.w   r1, r0, r1, lsl #12                    /* 00426a6e */
    ldr.w    r1, [r1, #0x8c]                        /* 00426a72 */
    str.w    r1, [r5, #0x870]                       /* 00426a76 */
    ldr      r1, [r5, #0x4]                         /* 00426a7a */
    adds.w   r1, r0, r1, lsl #12                    /* 00426a7c */
    ldr.w    r1, [r1, #0x90]                        /* 00426a80 */
    str.w    r1, [r5, #0x874]                       /* 00426a84 */
    ldr      r1, [r5, #0x4]                         /* 00426a88 */
    adds.w   r1, r0, r1, lsl #12                    /* 00426a8a */
    ldr.w    r1, [r1, #0x94]                        /* 00426a8e */
    str.w    r1, [r5, #0x878]                       /* 00426a92 */
    ldr      r1, [r5, #0x4]                         /* 00426a96 */
    adds.w   r1, r0, r1, lsl #12                    /* 00426a98 */
    ldr.w    r1, [r1, #0x98]                        /* 00426a9c */
    str.w    r1, [r5, #0x87c]                       /* 00426aa0 */
    ldr      r1, [r5, #0x4]                         /* 00426aa4 */
    adds.w   r1, r0, r1, lsl #12                    /* 00426aa6 */
    ldr.w    r1, [r1, #0x9c]                        /* 00426aaa */
    str.w    r1, [r5, #0x880]                       /* 00426aae */
    ldr      r1, [r5, #0x4]                         /* 00426ab2 */
    adds.w   r1, r0, r1, lsl #12                    /* 00426ab4 */
    ldr.w    r1, [r1, #0xa0]                        /* 00426ab8 */
    str.w    r1, [r5, #0x884]                       /* 00426abc */
    ldr      r1, [r5, #0x4]                         /* 00426ac0 */
    adds.w   r1, r0, r1, lsl #12                    /* 00426ac2 */
    ldr.w    r1, [r1, #0xa4]                        /* 00426ac6 */
    str.w    r1, [r5, #0x888]                       /* 00426aca */
    ldr      r1, [r5, #0x4]                         /* 00426ace */
    adds.w   r1, r0, r1, lsl #12                    /* 00426ad0 */
    ldr.w    r1, [r1, #0xa8]                        /* 00426ad4 */
    str.w    r1, [r5, #0x88c]                       /* 00426ad8 */
    ldr      r1, [r5, #0x4]                         /* 00426adc */
    adds.w   r1, r0, r1, lsl #12                    /* 00426ade */
    ldr      r1, [r1, #0x30]                        /* 00426ae2 */
    str.w    r1, [r5, #0x890]                       /* 00426ae4 */
    ldr      r1, [r5, #0x4]                         /* 00426ae8 */
    adds.w   r1, r0, r1, lsl #12                    /* 00426aea */
    ldr      r1, [r1, #0x44]                        /* 00426aee */
    str.w    r1, [r5, #0x894]                       /* 00426af0 */
    ldr      r1, [r5, #0x4]                         /* 00426af4 */
    adds.w   r1, r0, r1, lsl #12                    /* 00426af6 */
    ldr      r1, [r1, #0x48]                        /* 00426afa */
    str.w    r1, [r5, #0x898]                       /* 00426afc */
    ldr      r1, [r5, #0x4]                         /* 00426b00 */
    adds.w   r1, r0, r1, lsl #12                    /* 00426b02 */
    ldr      r1, [r1, #0x4c]                        /* 00426b06 */
    str.w    r1, [r5, #0x89c]                       /* 00426b08 */
    ldr      r1, [r5, #0x4]                         /* 00426b0c */
    adds.w   r1, r0, r1, lsl #12                    /* 00426b0e */
    ldr.w    r1, [r1, #0x2a8]                       /* 00426b12 */
    str.w    r1, [r5, #0x8a4]                       /* 00426b16 */
    ldr      r1, [r5, #0x4]                         /* 00426b1a */
    adds.w   r1, r0, r1, lsl #12                    /* 00426b1c */
    ldr.w    r1, [r1, #0x2b8]                       /* 00426b20 */
    str.w    r1, [r5, #0x8a8]                       /* 00426b24 */
    ldr      r1, [r5, #0x4]                         /* 00426b28 */
    adds.w   r1, r0, r1, lsl #12                    /* 00426b2a */
    ldr.w    r1, [r1, #0x2c0]                       /* 00426b2e */
    str.w    r1, [r5, #0x8ac]                       /* 00426b32 */
    ldr      r1, [r5, #0x4]                         /* 00426b36 */
    adds.w   r1, r0, r1, lsl #12                    /* 00426b38 */
    ldr.w    r1, [r1, #0x2c4]                       /* 00426b3c */
    str.w    r1, [r5, #0x8b0]                       /* 00426b40 */
    ldr      r1, [r5, #0x4]                         /* 00426b44 */
    adds.w   r1, r0, r1, lsl #12                    /* 00426b46 */
    ldr.w    r1, [r1, #0x200]                       /* 00426b4a */
    str.w    r1, [r5, #0x8b4]                       /* 00426b4e */
    ldr      r1, [r5, #0x4]                         /* 00426b52 */
    adds.w   r1, r0, r1, lsl #12                    /* 00426b54 */
    ldr.w    r1, [r1, #0x2b0]                       /* 00426b58 */
    str.w    r1, [r5, #0x8b8]                       /* 00426b5c */
    ldr      r1, [r5, #0x4]                         /* 00426b60 */
    adds.w   r1, r0, r1, lsl #12                    /* 00426b62 */
    ldr.w    r1, [r1, #0x114]                       /* 00426b66 */
    str.w    r1, [r5, #0x8bc]                       /* 00426b6a */
    ldr      r1, [r5, #0x4]                         /* 00426b6e */
    adds.w   r1, r0, r1, lsl #12                    /* 00426b70 */
    ldr.w    r1, [r1, #0x118]                       /* 00426b74 */
    str.w    r1, [r5, #0x8c0]                       /* 00426b78 */
    ldr      r1, [r5, #0x4]                         /* 00426b7c */
    adds.w   r1, r0, r1, lsl #12                    /* 00426b7e */
    ldr      r1, [r1, #0x20]                        /* 00426b82 */
    str.w    r1, [r5, #0x8c4]                       /* 00426b84 */
    ldr      r1, [r5, #0x4]                         /* 00426b88 */
    adds.w   r1, r0, r1, lsl #12                    /* 00426b8a */
    ldr.w    r1, [r1, #0x2a0]                       /* 00426b8e */
    str.w    r1, [r5, #0x8a0]                       /* 00426b92 */
    ldr      r1, [r5, #0x4]                         /* 00426b96 */
    adds.w   r0, r0, r1, lsl #12                    /* 00426b98 */
    ldr.w    r0, [r0, #0x2a0]                       /* 00426b9c */
    lsls     r0, r0, #0x1f                          /* 00426ba0 */
    bpl      .L_00426baa                            /* 00426ba2 */
    movs     r0, r5                                 /* 00426ba4 */
    bl       open_cfw_bootloader_mspi_cq_disable_423fac /* 00426ba6 */
.L_00426baa:
    movs     r0, #0x1                               /* 00426baa */
    strb.w   r0, [r5, #0x860]                       /* 00426bac */

    /* Disable interrupts, flush XIP delay, power down, gate clocks, and release clock users. */
.L_00426bb0:
    movw     r1, #0x1fff                            /* 00426bb0 */
    movs     r0, r4                                 /* 00426bb4 */
    bl       open_cfw_bootloader_mspi_interrupt_disable_426484 /* 00426bb6 */
    ldr      r0, [r5, #0x4]                         /* 00426bba */
    ldr      r1, [pc, #0x4c]                        /* 00426bbc */
    adds.w   r1, r1, r0, lsl #12                    /* 00426bbe */
    ldr.w    r0, [r1, #0x90]                        /* 00426bc2 */
    lsls     r0, r0, #0x1f                          /* 00426bc6 */
    bpl      .L_00426bd2                            /* 00426bc8 */
    ldr.w    r0, [r5, #0x8cc]                       /* 00426bca */
    bl       open_cfw_bootloader_delay_us_41d1c0    /* 00426bce */
.L_00426bd2:
    ldr      r0, [r5, #0x4]                         /* 00426bd2 */
    adds     r0, #0x10                              /* 00426bd4 */
    uxtb     r0, r0                                 /* 00426bd6 */
    bl       open_cfw_bootloader_pwrctrl_periph_disable_41c17a /* 00426bd8 */
    movs     r3, #0x0                               /* 00426bdc */
    movs     r2, #0x0                               /* 00426bde */
    movs     r1, #0x0                               /* 00426be0 */
    ldr      r0, [r5, #0x4]                         /* 00426be2 */
    bl       open_cfw_bootloader_mspi_clkgen_ctrl_4249a0 /* 00426be4 */
    ldr      r0, [r5, #0x4]                         /* 00426be8 */
    adds     r0, #0x10                              /* 00426bea */
    uxtb     r0, r0                                 /* 00426bec */
    bl       open_cfw_bootloader_clock_release_all_4223d8 /* 00426bee */
    cmp      r0, #0x0                               /* 00426bf2 */
    bne.w    .L_00426a24                            /* 00426bf4 */
    b        .L_00426a22                            /* 00426bf8 */

    /* Return AM_HAL_STATUS_INVALID_ARG for an unsupported power state. */
.L_00426bfa:
    movs     r0, #0x6                               /* 00426bfa */

    /* Return the Ambiq HAL status in r0. */
    b        .L_00426a24                            /* 00426bfc */
.size open_cfw_bootloader_mspi_power_control_426808, .-open_cfw_bootloader_mspi_power_control_426808
