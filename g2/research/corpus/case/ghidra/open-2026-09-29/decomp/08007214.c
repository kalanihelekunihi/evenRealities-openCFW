
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void case_policy_iteration(void)

{
  char cVar1;
  byte bVar2;
  ushort uVar3;
  byte bVar4;
  int iVar5;
  undefined4 uVar6;
  int extraout_r1;
  undefined4 extraout_r1_00;
  undefined4 extraout_r1_01;
  int extraout_r1_02;
  int extraout_r1_03;
  int extraout_r1_04;
  int extraout_r1_05;
  undefined1 extraout_r2;
  undefined1 extraout_r3;
  int unaff_r4;
  int unaff_r5;
  int unaff_r6;
  int iVar7;
  char *pcVar8;
  int in_stack_00000000;
  int in_stack_00000004;
  uint in_stack_00000008;
  uint in_stack_0000000c;
  uint in_stack_00000010;
  uint in_stack_00000014;
  undefined4 in_stack_00000018;
  undefined4 in_stack_0000001c;
  
  *(int *)(unaff_r4 + 0xc) = *(int *)(unaff_r4 + 0xc) + 1;
  iVar7 = *(int *)(unaff_r4 + 8);
  __aeabi_uidiv(iVar7,5);
  *(int *)(unaff_r4 + 8) = iVar7 + 1;
  if ((extraout_r1 == 0) && (*(char *)(_DAT_080075ec + 6) != '\0')) {
    case_periodic_policy_adapter();
  }
  if ((((*(char *)(unaff_r4 + 4) == '\0') && (*(char *)(unaff_r4 + 3) == '\0')) &&
      (*(char *)(unaff_r4 + 0x10) == '\0')) && (*(char *)(unaff_r4 + 0x11) == '\0')) {
    if (unaff_r6 == 10) {
      if (*(char *)(_DAT_080075ec + 7) == '\0') {
        g2_log_printf(s_Standby__reason__idle__080075ef + 1);
        g2_log_printf(&DAT_08007608);
      }
      peripheral_transaction_guard(0x10,&stack0x00000008,1);
      peripheral_transaction_guard(0x11,&stack0x00000008,1);
      glasses_channel_command_pack(0);
      peripheral_mode_write_retry(0);
      HAL_PWR_DisableWakeUpPin(0x2b);
      HAL_PWR_EnableWakeUpPin(DAT_0800760c);
      *(undefined4 *)(DAT_08007614 + 0x18) = DAT_08007610;
      HAL_PWR_EnterSTANDBYMode();
      goto LAB_08007252;
    }
LAB_080072bc:
    if (((((*(char *)(_DAT_080075ec + 0x3d) == '\0') && (*(char *)(unaff_r4 + 0x10) != '\0')) &&
         (*(char *)(in_stack_00000004 + 0x11) != '\0')) &&
        ((*(char *)(in_stack_00000004 + 0x13) == '\0' && (*(char *)(unaff_r4 + 0x11) != '\0')))) &&
       ((*(char *)(in_stack_00000000 + 0xd) != '\0' && (*(char *)(in_stack_00000000 + 0xf) == '\0'))
       )) {
      *(short *)(unaff_r4 + 0x38) = *(short *)(unaff_r4 + 0x38) + 1;
      *(short *)(in_stack_00000000 + 0x14) = *(short *)(in_stack_00000000 + 0x14) + 1;
      if (unaff_r5 == 5) {
        stm32_hal_peripheral_init(_DAT_08007618,0x3840,4);
        if (*(char *)(_DAT_080075ec + 7) == '\0') {
          g2_log_printf(s_Standby__reason__gls_bat_full__0800761b + 1);
          g2_log_printf(&DAT_08007608);
        }
        peripheral_transaction_guard(0x10,&stack0x00000008,1);
        peripheral_transaction_guard(0x11,&stack0x00000008,1);
        glasses_channel_command_pack(0);
        peripheral_mode_write_retry(0);
        HAL_PWR_DisableWakeUpPin(0x2b);
        HAL_PWR_EnableWakeUpPin(DAT_0800760c);
        *(undefined4 *)(DAT_08007614 + 0x18) = DAT_08007610;
        HAL_PWR_EnterSTANDBYMode();
      }
    }
LAB_08007376:
    cVar1 = *(char *)(unaff_r4 + 0x19);
    if (cVar1 != '\0') {
      *(undefined1 *)(unaff_r4 + 0x10) = 1;
      *(undefined1 *)(unaff_r4 + 0x11) = 1;
      if (*(char *)(unaff_r4 + 0x1a) == '\0') {
        if (cVar1 == '\x01') {
          if (*(char *)(_DAT_080075ec + 7) == '\0') {
            g2_log_printf(s_ota_gls_ready_L_08007730);
            g2_log_printf(&DAT_08007608);
          }
          left_indicator_sequence();
        }
        else {
          if (cVar1 != '\x02') {
            if (*(char *)(_DAT_080075ec + 7) == '\0') {
              g2_log_printf(s_ota_box_ready_08007750);
              g2_log_printf(&DAT_08007608);
            }
            left_indicator_sequence();
            *(undefined1 *)(unaff_r4 + 0x1a) = 1;
            iVar7 = case_ota_execute();
            if (iVar7 == 0) {
              if (*(char *)(_DAT_080075ec + 7) == '\0') {
                g2_log_printf(s__OTA_BOX___get_bin_file_fail__ex_08007b50);
                g2_log_printf(&DAT_08007b84);
              }
              ota_result_inform_glasses(0);
              *(undefined1 *)(unaff_r4 + 0x1c) = 0;
              *(undefined1 *)(unaff_r4 + 0x1d) = 0;
              *(undefined4 *)(unaff_r4 + 0x20) = 0;
              *(undefined4 *)(unaff_r4 + 0x24) = 0;
              *(undefined4 *)(unaff_r4 + 0x28) = 0;
              *(undefined1 *)(in_stack_00000004 + 0xc) = 0;
              *(undefined1 *)(unaff_r4 + 0x19) = 0;
              *(undefined1 *)(unaff_r4 + 0x18) = 0;
              aging_led_status_clear();
            }
            else {
              if (*(char *)(_DAT_080075ec + 7) == '\0') {
                g2_log_printf(s__OTA_BOX___Get_bin_file_success_08007760);
                g2_log_printf(&DAT_08007608);
              }
              ota_result_inform_glasses(1);
              osDelay(100);
              option_byte_bank_swap();
            }
            goto LAB_08007eda;
          }
          if (*(char *)(_DAT_080075ec + 7) == '\0') {
            g2_log_printf(s_ota_gls_ready_R_08007740);
            g2_log_printf(&DAT_08007608);
          }
          right_indicator_sequence();
        }
        *(undefined1 *)(unaff_r4 + 0x1a) = 1;
        case_command_build_fixed(0x56);
      }
      goto LAB_08007eda;
    }
  }
  else {
LAB_08007252:
    iVar7 = _DAT_080075ec;
    if (*(char *)(unaff_r4 + 4) == '\0') {
      if (*(char *)(unaff_r4 + 3) != '\0') goto LAB_0800736a;
      goto LAB_080072bc;
    }
    if ((*(char *)(unaff_r4 + 3) == '\0') && (*(char *)(unaff_r4 + 4) == '\0')) goto LAB_08007376;
LAB_0800736a:
    pcVar8 = (char *)(_DAT_080075ec + 0x3c);
    if (*(char *)(_DAT_080075ec + 0x3d) != '\0') goto LAB_08007376;
    if ((*(char *)(unaff_r4 + 0x10) == '\0') || (*(char *)(in_stack_00000004 + 0x11) == '\0')) {
      if ((*(char *)(unaff_r4 + 0x11) != '\0') && (*(char *)(in_stack_00000000 + 0xd) != '\0')) {
        if (*(char *)(unaff_r4 + 0x10) == '\0') {
          if (*(char *)(in_stack_00000004 + 0x11) != '\0') goto LAB_080073d8;
        }
        else if (*(char *)(in_stack_00000004 + 0x11) != '\0') goto LAB_080073b2;
        goto LAB_0800742c;
      }
      *(undefined2 *)(unaff_r4 + 0x38) = 0;
LAB_08007462:
      *(undefined2 *)(in_stack_00000000 + 0x14) = 0;
    }
    else {
LAB_080073b2:
      if ((*(char *)(unaff_r4 + 0x11) != '\0') && (*(char *)(in_stack_00000000 + 0xd) != '\0')) {
        if (*(ushort *)(unaff_r4 + 0x38) < *(ushort *)(in_stack_00000000 + 0x14)) {
          *(ushort *)(in_stack_00000000 + 0x14) = *(ushort *)(unaff_r4 + 0x38);
        }
        else {
          *(ushort *)(unaff_r4 + 0x38) = *(ushort *)(in_stack_00000000 + 0x14);
        }
      }
LAB_080073d8:
      uVar3 = *(ushort *)(unaff_r4 + 0x38);
      *(ushort *)(unaff_r4 + 0x38) = uVar3 + 1;
      iVar5 = _DAT_080075ec;
      if (300 < uVar3) {
        if (*(char *)(in_stack_00000004 + 0x13) == '\0') {
          if (*(char *)(_DAT_080075ec + 7) == '\0') {
            g2_log_printf(s_L_fake_standby_cnt_300s__now_che_08007664);
            g2_log_printf(&DAT_08007608);
          }
          glasses_charge_state_reset(1);
          if (*(char *)(iVar5 + 3) != '\0') {
            idle_mode_exit();
          }
        }
        else {
          if (*(char *)(_DAT_080075ec + 7) == '\0') {
            g2_log_printf(s_L_water_detected__only_clear_tim_0800763c);
            g2_log_printf(&DAT_08007608);
          }
          *(undefined2 *)(unaff_r4 + 0x38) = 0;
        }
      }
LAB_0800742c:
      if ((*(char *)(in_stack_00000000 + 0xd) != '\0') &&
         (uVar3 = *(ushort *)(in_stack_00000000 + 0x14),
         *(ushort *)(in_stack_00000000 + 0x14) = uVar3 + 1, 300 < uVar3)) {
        if (*(char *)(in_stack_00000000 + 0xf) != '\0') {
          if (*(char *)(_DAT_080075ec + 7) == '\0') {
            g2_log_printf(s_R_water_detected__only_clear_tim_08007694);
            g2_log_printf(&DAT_08007608);
          }
          goto LAB_08007462;
        }
        if (*(char *)(_DAT_080075ec + 7) == '\0') {
          g2_log_printf(s_R_fake_standby_cnt_300s__now_che_080076bc);
          g2_log_printf(&DAT_08007608);
        }
        glasses_charge_state_reset(0);
      }
    }
    if ((*(char *)(unaff_r4 + 3) != '\0') || (*(char *)(unaff_r4 + 4) == '\0')) {
LAB_08007508:
      *(undefined1 *)(unaff_r4 + 0x17) = 0;
      goto LAB_08007376;
    }
    if (*(char *)(unaff_r4 + 0x10) == '\0') {
      if (((*(char *)(unaff_r4 + 0x11) == '\0') && (*(char *)(iVar7 + 0x3d) == '\0')) &&
         (*pcVar8 == '\0')) {
        bVar2 = *(byte *)(unaff_r4 + 0x17);
        if (((bVar2 < 0x1f) && (*(byte *)(unaff_r4 + 0x17) = bVar2 + 1, bVar2 == 0x1d)) &&
           (*(char *)(_DAT_080075ec + 7) == '\0')) {
          pcVar8 = s_Box_idle_mode_ON___empty_box__080076ec;
          goto LAB_0800754c;
        }
        goto LAB_08007376;
      }
      goto LAB_08007508;
    }
    if (((*(char *)(unaff_r4 + 0x11) == '\0') || (*(char *)(iVar7 + 0x3d) != '\0')) ||
       (((*pcVar8 != '\0' ||
         (((*(char *)(in_stack_00000004 + 0x11) == '\0' ||
           (*(char *)(in_stack_00000000 + 0xd) == '\0')) ||
          (*(char *)(in_stack_00000004 + 0x13) != '\0')))) ||
        ((*(char *)(in_stack_00000000 + 0xf) != '\0' || (*(char *)(unaff_r4 + 0x19) != '\0'))))))
    goto LAB_08007508;
    bVar2 = *(byte *)(unaff_r4 + 0x17);
    if (((bVar2 < 0x1f) && (*(byte *)(unaff_r4 + 0x17) = bVar2 + 1, bVar2 == 0x1d)) &&
       (*(char *)(_DAT_080075ec + 7) == '\0')) {
      pcVar8 = s_Box_idle_mode_ON___gls_bat_full__0800770c;
LAB_0800754c:
      g2_log_printf(pcVar8);
      g2_log_printf(&DAT_08007608);
      goto LAB_08007376;
    }
  }
  if (*(char *)(unaff_r4 + 0x1a) != '\0') {
    *(undefined1 *)(unaff_r4 + 0x10) = 0;
    *(undefined1 *)(unaff_r4 + 0x11) = 0;
    *(undefined1 *)(unaff_r4 + 0x1a) = 0;
    dual_side_indicator_update();
  }
  iVar7 = _DAT_08007b88;
  if (*(char *)(_DAT_080075ec + 0x3d) != '\0') {
    *(undefined1 *)(unaff_r4 + 0x10) = 1;
    *(undefined1 *)(unaff_r4 + 0x11) = 1;
    goto LAB_08007eda;
  }
  if (*(char *)(unaff_r4 + 0x15) == '\0') {
    *(undefined1 *)(unaff_r4 + 0x10) = 1;
    *(undefined1 *)(unaff_r4 + 0x11) = 1;
    aging_indicator_apply();
    goto LAB_08007eda;
  }
  in_stack_0000000c = (uint)*(byte *)(unaff_r4 + 0x10);
  in_stack_00000014 = (uint)*(byte *)(unaff_r4 + 0x11);
  while (iVar5 = _DAT_08007b88, *(char *)(iVar7 + 4) != '\0') {
    osDelay(0x32);
  }
  *(undefined1 *)(_DAT_08007b88 + 4) = 1;
  glasses_charge_control_policy();
  *(undefined1 *)(iVar5 + 4) = 0;
  if ((*(byte *)(unaff_r4 + 0x10) == 0) && (*(char *)(unaff_r4 + 0x1b) != '\0')) {
    *(undefined1 *)(unaff_r4 + 0x1b) = 0;
  }
  iVar7 = _DAT_08007b88;
  if ((*(byte *)(unaff_r4 + 0x10) == in_stack_0000000c) &&
     (*(byte *)(unaff_r4 + 0x11) == in_stack_00000014)) {
LAB_08007850:
    iVar7 = _DAT_08007b88;
    *(undefined1 *)(_DAT_08007b88 + 4) = 1;
    if ((((*(uint *)(unaff_r4 + 0x3c) < 10) || (*(uint *)(unaff_r4 + 0x58) < 10)) &&
        (*(char *)(_DAT_08007b88 + 0x3d) == '\0')) ||
       (in_stack_00000010 = in_stack_00000010 + 1 & 0xff, 9 < in_stack_00000010)) {
      glasses_status_poll_dispatch();
      in_stack_00000010 = 0;
    }
    *(undefined1 *)(iVar7 + 4) = 0;
  }
  else {
    if (*(char *)(_DAT_08007b88 + 3) != '\0') {
      idle_mode_exit();
    }
    if (*(char *)(unaff_r4 + 0x10) == '\0') {
      left_glasses_state_reset();
      *(undefined1 *)(in_stack_00000004 + 0x12) = extraout_r3;
      *(undefined1 *)(unaff_r4 + 0x12) = 0;
      uVar6 = extraout_r1_01;
    }
    else {
      left_glasses_state_reset();
      uVar6 = extraout_r1_00;
    }
    if (*(char *)(unaff_r4 + 0x11) == '\0') {
      right_glasses_state_reset(in_stack_00000000,uVar6,*(undefined1 *)(in_stack_00000000 + 0xe));
      *(undefined1 *)(in_stack_00000000 + 0xe) = extraout_r2;
      *(undefined1 *)(unaff_r4 + 0x13) = 0;
    }
    else {
      right_glasses_state_reset();
    }
    if (*(char *)(iVar7 + 4) == '\0') goto LAB_08007850;
  }
  if ((*(byte *)(unaff_r4 + 0x10) == in_stack_0000000c) &&
     (*(byte *)(unaff_r4 + 0x11) == in_stack_00000014)) {
    if (10 < *(uint *)(unaff_r4 + 0xc)) {
      if (*(char *)(unaff_r4 + 0x14) == '\x01') {
        if ((((*(char *)(in_stack_00000004 + 0x10) != '\0') &&
             (*(char *)(in_stack_00000000 + 0xc) != '\0')) &&
            (*(char *)(in_stack_00000004 + 0x13) == '\0')) &&
           (*(char *)(in_stack_00000000 + 0xf) == '\0')) {
          if (*(char *)(_DAT_08007b88 + 7) == '\0') {
            pcVar8 = s_Switch_charging_result__ERROR__>_08007c98;
            goto LAB_08007936;
          }
          goto LAB_080079b0;
        }
      }
      else if (*(char *)(unaff_r4 + 0x14) == '\x02') {
        if ((*(char *)(in_stack_00000004 + 0x14) == '\0') ||
           (bVar2 = 0, *(char *)(in_stack_00000004 + 0x10) != '\0')) {
          bVar2 = 1;
        }
        if ((*(char *)(in_stack_00000000 + 0x10) == '\0') ||
           (bVar4 = 0, *(char *)(in_stack_00000000 + 0xc) != '\0')) {
          bVar4 = 1;
        }
        if (!(bool)(bVar2 & bVar4)) {
          if (*(char *)(_DAT_08007b88 + 7) == '\0') {
            pcVar8 = s_Switch_charging_result__GOOD__>_E_08007cc0;
            goto LAB_08007936;
          }
          goto LAB_080079b0;
        }
      }
    }
  }
  else {
    *(undefined4 *)(unaff_r4 + 0xc) = 0;
    if (*(byte *)(unaff_r4 + 2) < 3) {
      case_gpio_pa6_write(0);
      case_gpio_pa7_write(0);
      *(undefined1 *)(unaff_r4 + 2) = 2;
      if (*(char *)(_DAT_08007b88 + 7) == '\0') {
        g2_log_printf(s_clear_led_since_gls_status_updat_08007b8b + 1);
        g2_log_printf(&DAT_08007b84);
      }
    }
    iVar7 = _DAT_08007b88;
    if (*(char *)(unaff_r4 + 0x11) == '\0') {
      if (*(char *)(unaff_r4 + 0x10) == '\0') {
        if (*(char *)(_DAT_08007b88 + 7) == '\0') {
          pcVar8 = s_L___R_GLS_OUT__show_led_after_1s_08007c2c;
          goto LAB_08007936;
        }
      }
      else if (*(char *)(_DAT_08007b88 + 7) == '\0') {
        pcVar8 = s_L_IN__R_OUT__wait_1s_to_confirm__08007c74;
LAB_08007936:
        g2_log_printf(pcVar8);
        g2_log_printf(&DAT_08007b84);
      }
    }
    else if (*(char *)(unaff_r4 + 0x10) == '\0') {
      if (*(char *)(_DAT_08007b88 + 7) == '\0') {
        pcVar8 = s_L_OUT__R_IN__wait_1s_to_confirm__08007c50;
        goto LAB_08007936;
      }
    }
    else if ((*(char *)(in_stack_00000004 + 0x10) == '\0') ||
            (*(char *)(in_stack_00000000 + 0xc) == '\0')) {
      if (*(char *)(_DAT_08007b88 + 7) == '\0') {
        g2_log_printf(s_L___R_GLS_IN__Charging_status_un_08007bf0);
        g2_log_printf(&DAT_08007b84);
      }
      *(undefined1 *)(iVar7 + 1) = 8;
    }
    else if (*(char *)(_DAT_08007b88 + 7) == '\0') {
      pcVar8 = s_L___R_GLS_IN__Charging_status_co_08007bb0;
      goto LAB_08007936;
    }
LAB_080079b0:
    periodic_timer_restart();
  }
  if (7 < *(uint *)(unaff_r4 + 0x40)) {
    __aeabi_uidiv(*(undefined4 *)(unaff_r4 + 0x44),0xf);
    if ((extraout_r1_02 == 0) && (*(char *)(_DAT_08007b88 + 7) == '\0')) {
      g2_log_printf(s_No_reply_from_GLS_L__wait_for__d_08007ce8,0xf);
      g2_log_printf(&DAT_08007b84);
    }
    *(int *)(unaff_r4 + 0x44) = *(int *)(unaff_r4 + 0x44) + 1;
  }
  if (7 < *(uint *)(unaff_r4 + 0x5c)) {
    __aeabi_uidiv(*(undefined4 *)(unaff_r4 + 0x60),0xf);
    if ((extraout_r1_03 == 0) && (*(char *)(_DAT_08007b88 + 7) == '\0')) {
      g2_log_printf(s_No_reply_from_GLS_R__wait_for__d_08007d0c,0xf);
      g2_log_printf(&DAT_08007b84);
    }
    *(int *)(unaff_r4 + 0x60) = *(int *)(unaff_r4 + 0x60) + 1;
  }
  if (7 < *(uint *)(unaff_r4 + 0x40)) {
    uVar6 = *(undefined4 *)(unaff_r4 + 0x44);
    __aeabi_uidiv(uVar6,0xb4);
    if (extraout_r1_04 == 0) {
      if (*(char *)(_DAT_08007b88 + 8) == '\0') {
        glasses_sides_reset(1,0);
        if (*(char *)(_DAT_08007b88 + 7) == '\0') {
          pcVar8 = s_No_reply_from_GLS_L_for__ds__res_08007d5c;
          uVar6 = *(undefined4 *)(unaff_r4 + 0x44);
          goto LAB_08007a54;
        }
      }
      else if (*(char *)(_DAT_08007b88 + 7) == '\0') {
        pcVar8 = s_No_reply_from_GLS_L_for__ds__do_n_08007d30;
LAB_08007a54:
        g2_log_printf(pcVar8,uVar6);
        g2_log_printf(&DAT_08007b84);
      }
    }
  }
  if ((7 < *(uint *)(unaff_r4 + 0x5c)) &&
     (__aeabi_uidiv(*(undefined4 *)(unaff_r4 + 0x60),0xb4), iVar7 = _DAT_08007b88,
     extraout_r1_05 == 0)) {
    if (*(char *)(_DAT_08007b88 + 8) == '\0') {
      glasses_sides_reset(0,1);
      if (*(char *)(iVar7 + 7) == '\0') {
        pcVar8 = s_No_reply_from_GLS_R_for__ds__res_08007db4;
        uVar6 = *(undefined4 *)(unaff_r4 + 0x60);
        goto LAB_08007a96;
      }
    }
    else if (*(char *)(_DAT_08007b88 + 7) == '\0') {
      pcVar8 = s_No_reply_from_GLS_R_for__ds__do_n_08007d88;
      uVar6 = *(undefined4 *)(unaff_r4 + 0x44);
LAB_08007a96:
      g2_log_printf(pcVar8,uVar6);
      g2_log_printf(&DAT_08007b84);
    }
  }
  if (((7 < *(uint *)(unaff_r4 + 0x40)) && (*(int *)(unaff_r4 + 0x44) == 0xd2)) ||
     ((7 < *(uint *)(unaff_r4 + 0x5c) && (*(int *)(unaff_r4 + 0x60) == 0xd2)))) {
    periodic_timer_restart();
  }
  iVar7 = _DAT_08007b88;
  if ((((((*(char *)(unaff_r4 + 0x10) != '\0') && (*(char *)(unaff_r4 + 0x11) != '\0')) &&
        (0x14 < *(uint *)(unaff_r4 + 0xc))) &&
       ((0x32 < *(byte *)(in_stack_00000004 + 0x12) && (0x14 < *(byte *)(unaff_r4 + 1))))) &&
      (*(char *)(unaff_r4 + 0x1b) == '\0')) && (*(char *)(_DAT_08007b88 + 4) == '\0')) {
    *(undefined1 *)(_DAT_08007b88 + 4) = 1;
    if (*(char *)(iVar7 + 7) == '\0') {
      g2_log_printf(s__OTA_BOX___check_box_ota_firmwar_08007de0);
      g2_log_printf(&DAT_08007b84);
    }
    osDelay(100);
    in_stack_00000014 = DAT_08007e04;
    in_stack_00000018 = DAT_08007e08;
    in_stack_0000001c = CONCAT31((int3)((uint)DAT_08007e0c >> 8),0x1e);
    gls_uart_transfer_controlled(1,&stack0x00000014,9);
    *(undefined1 *)(unaff_r4 + 0x1b) = 1;
    *(undefined1 *)(iVar7 + 4) = 0;
    gls_frame_validate_dispatch(1);
  }
  iVar7 = _DAT_08007b88;
  if (*(char *)(_DAT_08007b88 + 3) != '\0') {
    in_stack_00000008 = osEventFlagsGet(*(undefined4 *)(_DAT_08007b88 + 0x38));
    if ((int)(in_stack_00000008 << 0x1e) < 0) {
      osEventFlagsClear(*(undefined4 *)(iVar7 + 0x38),2);
      osTimerStart(*(undefined4 *)(iVar7 + 0x10),DAT_08007ee4);
    }
    if ((int)(in_stack_00000008 << 0x13) < 0) {
      osEventFlagsClear(*(undefined4 *)(iVar7 + 0x38),0x1000);
      idle_mode_exit();
    }
    if (((*(char *)(unaff_r4 + 1) == '\0') && (*(byte *)(unaff_r4 + 3) == 0)) &&
       (in_stack_00000008 = (uint)*(byte *)(unaff_r4 + 3),
       scaled_sensor_value_read(&stack0x00000008), in_stack_00000008 < DAT_08007ee8)) {
      if (*(char *)(iVar7 + 7) == '\0') {
        g2_log_printf(s_Standby_from_idle_mode__reason__l_08007eec);
        g2_log_printf(&DAT_08007f18);
      }
      peripheral_transaction_guard(0x10,&stack0x0000000c,1);
      peripheral_transaction_guard(0x11,&stack0x0000000c,1);
      glasses_channel_command_pack(0);
      peripheral_mode_write_retry(0);
      HAL_PWR_DisableWakeUpPin(0x2b);
      HAL_PWR_EnableWakeUpPin(DAT_08007f1c);
      *(undefined4 *)(DAT_08007f24 + 0x18) = DAT_08007f20;
      HAL_PWR_EnterSTANDBYMode();
    }
  }
  if (0x1d < *(byte *)(unaff_r4 + 0x17)) {
    if (*(char *)(iVar7 + 3) == '\0') {
      osThreadTerminate(*(undefined4 *)(iVar7 + 0x2c));
      osThreadTerminate(*(undefined4 *)(iVar7 + 0x30));
      osThreadTerminate(*(undefined4 *)(iVar7 + 0x28));
      *(undefined1 *)(iVar7 + 3) = 1;
    }
    stm32_hal_peripheral_init(DAT_08007f28,7,4);
    HAL_PWR_DisableWakeUpPin(0x2b);
    HAL_PWR_EnableWakeUpPin(DAT_08007f1c + 8);
    HAL_PWR_EnterSLEEPMode(0,1);
    board_peripheral_init();
    goto LAB_08007ed6;
  }
LAB_08007eda:
  do {
    osDelay(1000);
LAB_08007ed6:
    case_policy_iteration();
  } while( true );
}

