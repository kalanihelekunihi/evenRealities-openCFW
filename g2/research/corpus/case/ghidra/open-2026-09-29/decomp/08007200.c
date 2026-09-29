
/* WARNING: Removing unreachable block (ram,0x0800726a) */
/* WARNING: Removing unreachable block (ram,0x08007272) */
/* WARNING: Removing unreachable block (ram,0x0800727e) */
/* WARNING: Removing unreachable block (ram,0x0800730a) */
/* WARNING: Removing unreachable block (ram,0x0800731e) */
/* WARNING: Removing unreachable block (ram,0x0800732a) */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void g2_thread_entry_3(void)

{
  char cVar1;
  byte bVar2;
  ushort uVar3;
  byte bVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  undefined4 uVar8;
  int extraout_r1;
  undefined4 extraout_r1_00;
  undefined4 extraout_r1_01;
  int extraout_r1_02;
  int extraout_r1_03;
  int extraout_r1_04;
  int extraout_r1_05;
  undefined1 extraout_r2;
  undefined1 extraout_r3;
  int iVar9;
  char *pcVar10;
  uint uStack_20;
  uint uStack_1c;
  uint uStack_18;
  uint uStack_14;
  undefined4 uStack_10;
  undefined1 uStack_c;
  undefined3 uStack_b;
  
  iVar5 = DAT_080075e8;
  iVar7 = DAT_080075e8 + 0x40;
  uStack_18 = 0;
  *(int *)(DAT_080075e8 + 0xc) = *(int *)(DAT_080075e8 + 0xc) + 1;
  iVar9 = *(int *)(iVar5 + 8);
  __aeabi_uidiv(iVar9,5);
  *(int *)(iVar5 + 8) = iVar9 + 1;
  if ((extraout_r1 == 0) && (*(char *)(_DAT_080075ec + 6) != '\0')) {
    case_periodic_policy_adapter();
  }
  iVar9 = _DAT_080075ec;
  if ((((*(char *)(iVar5 + 4) == '\0') && (*(char *)(iVar5 + 3) == '\0')) &&
      (*(char *)(iVar5 + 0x10) == '\0')) && (*(char *)(iVar5 + 0x11) == '\0')) {
LAB_080072bc:
    if (((((*(char *)(_DAT_080075ec + 0x3d) == '\0') && (*(char *)(iVar5 + 0x10) != '\0')) &&
         (*(char *)(iVar5 + 0x31) != '\0')) &&
        ((*(char *)(iVar5 + 0x33) == '\0' && (*(char *)(iVar5 + 0x11) != '\0')))) &&
       ((*(char *)(iVar5 + 0x4d) != '\0' && (*(char *)(iVar5 + 0x4f) == '\0')))) {
      *(short *)(iVar5 + 0x38) = *(short *)(iVar5 + 0x38) + 1;
      *(short *)(iVar5 + 0x54) = *(short *)(iVar5 + 0x54) + 1;
    }
LAB_08007376:
    cVar1 = *(char *)(iVar5 + 0x19);
    if (cVar1 != '\0') {
      *(undefined1 *)(iVar5 + 0x10) = 1;
      *(undefined1 *)(iVar5 + 0x11) = 1;
      if (*(char *)(iVar5 + 0x1a) == '\0') {
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
            *(undefined1 *)(iVar5 + 0x1a) = 1;
            iVar7 = case_ota_execute();
            if (iVar7 == 0) {
              if (*(char *)(_DAT_080075ec + 7) == '\0') {
                g2_log_printf(s__OTA_BOX___get_bin_file_fail__ex_08007b50);
                g2_log_printf(&DAT_08007b84);
              }
              ota_result_inform_glasses(0);
              *(undefined1 *)(iVar5 + 0x1c) = 0;
              *(undefined1 *)(iVar5 + 0x1d) = 0;
              *(undefined4 *)(iVar5 + 0x20) = 0;
              *(undefined4 *)(iVar5 + 0x24) = 0;
              *(undefined4 *)(iVar5 + 0x28) = 0;
              *(undefined1 *)(iVar5 + 0x2c) = 0;
              *(undefined1 *)(iVar5 + 0x19) = 0;
              *(undefined1 *)(iVar5 + 0x18) = 0;
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
        *(undefined1 *)(iVar5 + 0x1a) = 1;
        case_command_build_fixed(0x56);
      }
      goto LAB_08007eda;
    }
  }
  else {
    if (*(char *)(iVar5 + 4) == '\0') {
      if (*(char *)(iVar5 + 3) != '\0') goto LAB_0800736a;
      goto LAB_080072bc;
    }
    if ((*(char *)(iVar5 + 3) == '\0') && (*(char *)(iVar5 + 4) == '\0')) goto LAB_08007376;
LAB_0800736a:
    pcVar10 = (char *)(_DAT_080075ec + 0x3c);
    if (*(char *)(_DAT_080075ec + 0x3d) != '\0') goto LAB_08007376;
    if ((*(char *)(iVar5 + 0x10) == '\0') || (*(char *)(iVar5 + 0x31) == '\0')) {
      if ((*(char *)(iVar5 + 0x11) != '\0') && (*(char *)(iVar5 + 0x4d) != '\0')) {
        if (*(char *)(iVar5 + 0x10) == '\0') {
          if (*(char *)(iVar5 + 0x31) != '\0') goto LAB_080073d8;
        }
        else if (*(char *)(iVar5 + 0x31) != '\0') goto LAB_080073b2;
        goto LAB_0800742c;
      }
      *(undefined2 *)(iVar5 + 0x38) = 0;
LAB_08007462:
      *(undefined2 *)(iVar5 + 0x54) = 0;
    }
    else {
LAB_080073b2:
      if ((*(char *)(iVar5 + 0x11) != '\0') && (*(char *)(iVar5 + 0x4d) != '\0')) {
        if (*(ushort *)(iVar5 + 0x38) < *(ushort *)(iVar5 + 0x54)) {
          *(ushort *)(iVar5 + 0x54) = *(ushort *)(iVar5 + 0x38);
        }
        else {
          *(ushort *)(iVar5 + 0x38) = *(ushort *)(iVar5 + 0x54);
        }
      }
LAB_080073d8:
      uVar3 = *(ushort *)(iVar5 + 0x38);
      *(ushort *)(iVar5 + 0x38) = uVar3 + 1;
      iVar6 = _DAT_080075ec;
      if (300 < uVar3) {
        if (*(char *)(iVar5 + 0x33) == '\0') {
          if (*(char *)(_DAT_080075ec + 7) == '\0') {
            g2_log_printf(s_L_fake_standby_cnt_300s__now_che_08007664);
            g2_log_printf(&DAT_08007608);
          }
          glasses_charge_state_reset(1);
          if (*(char *)(iVar6 + 3) != '\0') {
            idle_mode_exit();
          }
        }
        else {
          if (*(char *)(_DAT_080075ec + 7) == '\0') {
            g2_log_printf(s_L_water_detected__only_clear_tim_0800763c);
            g2_log_printf(&DAT_08007608);
          }
          *(undefined2 *)(iVar5 + 0x38) = 0;
        }
      }
LAB_0800742c:
      if ((*(char *)(iVar5 + 0x4d) != '\0') &&
         (uVar3 = *(ushort *)(iVar5 + 0x54), *(ushort *)(iVar5 + 0x54) = uVar3 + 1, 300 < uVar3)) {
        if (*(char *)(iVar5 + 0x4f) != '\0') {
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
    if ((*(char *)(iVar5 + 3) != '\0') || (*(char *)(iVar5 + 4) == '\0')) {
LAB_08007508:
      *(undefined1 *)(iVar5 + 0x17) = 0;
      goto LAB_08007376;
    }
    if (*(char *)(iVar5 + 0x10) == '\0') {
      if (((*(char *)(iVar5 + 0x11) == '\0') && (*(char *)(iVar9 + 0x3d) == '\0')) &&
         (*pcVar10 == '\0')) {
        bVar2 = *(byte *)(iVar5 + 0x17);
        if (((bVar2 < 0x1f) && (*(byte *)(iVar5 + 0x17) = bVar2 + 1, bVar2 == 0x1d)) &&
           (*(char *)(_DAT_080075ec + 7) == '\0')) {
          pcVar10 = s_Box_idle_mode_ON___empty_box__080076ec;
          goto LAB_0800754c;
        }
        goto LAB_08007376;
      }
      goto LAB_08007508;
    }
    if (((*(char *)(iVar5 + 0x11) == '\0') || (*(char *)(iVar9 + 0x3d) != '\0')) ||
       (((*pcVar10 != '\0' ||
         (((*(char *)(iVar5 + 0x31) == '\0' || (*(char *)(iVar5 + 0x4d) == '\0')) ||
          (*(char *)(iVar5 + 0x33) != '\0')))) ||
        ((*(char *)(iVar5 + 0x4f) != '\0' || (*(char *)(iVar5 + 0x19) != '\0'))))))
    goto LAB_08007508;
    bVar2 = *(byte *)(iVar5 + 0x17);
    if (((bVar2 < 0x1f) && (*(byte *)(iVar5 + 0x17) = bVar2 + 1, bVar2 == 0x1d)) &&
       (*(char *)(_DAT_080075ec + 7) == '\0')) {
      pcVar10 = s_Box_idle_mode_ON___gls_bat_full__0800770c;
LAB_0800754c:
      g2_log_printf(pcVar10);
      g2_log_printf(&DAT_08007608);
      goto LAB_08007376;
    }
  }
  if (*(char *)(iVar5 + 0x1a) != '\0') {
    *(undefined1 *)(iVar5 + 0x10) = 0;
    *(undefined1 *)(iVar5 + 0x11) = 0;
    *(undefined1 *)(iVar5 + 0x1a) = 0;
    dual_side_indicator_update();
  }
  iVar9 = _DAT_08007b88;
  if (*(char *)(_DAT_080075ec + 0x3d) != '\0') {
    *(undefined1 *)(iVar5 + 0x10) = 1;
    *(undefined1 *)(iVar5 + 0x11) = 1;
    goto LAB_08007eda;
  }
  if (*(char *)(iVar5 + 0x15) == '\0') {
    *(undefined1 *)(iVar5 + 0x10) = 1;
    *(undefined1 *)(iVar5 + 0x11) = 1;
    aging_indicator_apply();
    goto LAB_08007eda;
  }
  uStack_1c = (uint)*(byte *)(iVar5 + 0x10);
  uStack_14 = (uint)*(byte *)(iVar5 + 0x11);
  while (iVar6 = _DAT_08007b88, *(char *)(iVar9 + 4) != '\0') {
    osDelay(0x32);
  }
  *(undefined1 *)(_DAT_08007b88 + 4) = 1;
  glasses_charge_control_policy();
  *(undefined1 *)(iVar6 + 4) = 0;
  if ((*(byte *)(iVar5 + 0x10) == 0) && (*(char *)(iVar5 + 0x1b) != '\0')) {
    *(undefined1 *)(iVar5 + 0x1b) = 0;
  }
  iVar9 = _DAT_08007b88;
  if ((*(byte *)(iVar5 + 0x10) == uStack_1c) && (*(byte *)(iVar5 + 0x11) == uStack_14)) {
LAB_08007850:
    iVar7 = _DAT_08007b88;
    *(undefined1 *)(_DAT_08007b88 + 4) = 1;
    if ((((*(uint *)(iVar5 + 0x3c) < 10) || (*(uint *)(iVar5 + 0x58) < 10)) &&
        (*(char *)(_DAT_08007b88 + 0x3d) == '\0')) ||
       (uStack_18 = uStack_18 + 1 & 0xff, 9 < uStack_18)) {
      glasses_status_poll_dispatch();
      uStack_18 = 0;
    }
    *(undefined1 *)(iVar7 + 4) = 0;
  }
  else {
    if (*(char *)(_DAT_08007b88 + 3) != '\0') {
      idle_mode_exit();
    }
    if (*(char *)(iVar5 + 0x10) == '\0') {
      left_glasses_state_reset();
      *(undefined1 *)(iVar5 + 0x32) = extraout_r3;
      *(undefined1 *)(iVar5 + 0x12) = 0;
      uVar8 = extraout_r1_01;
    }
    else {
      left_glasses_state_reset();
      uVar8 = extraout_r1_00;
    }
    if (*(char *)(iVar5 + 0x11) == '\0') {
      right_glasses_state_reset(iVar7,uVar8,*(undefined1 *)(iVar5 + 0x4e));
      *(undefined1 *)(iVar5 + 0x4e) = extraout_r2;
      *(undefined1 *)(iVar5 + 0x13) = 0;
    }
    else {
      right_glasses_state_reset();
    }
    if (*(char *)(iVar9 + 4) == '\0') goto LAB_08007850;
  }
  if ((*(byte *)(iVar5 + 0x10) == uStack_1c) && (*(byte *)(iVar5 + 0x11) == uStack_14)) {
    if (10 < *(uint *)(iVar5 + 0xc)) {
      if (*(char *)(iVar5 + 0x14) == '\x01') {
        if ((((*(char *)(iVar5 + 0x30) != '\0') && (*(char *)(iVar5 + 0x4c) != '\0')) &&
            (*(char *)(iVar5 + 0x33) == '\0')) && (*(char *)(iVar5 + 0x4f) == '\0')) {
          if (*(char *)(_DAT_08007b88 + 7) == '\0') {
            pcVar10 = s_Switch_charging_result__ERROR__>_08007c98;
            goto LAB_08007936;
          }
          goto LAB_080079b0;
        }
      }
      else if (*(char *)(iVar5 + 0x14) == '\x02') {
        if ((*(char *)(iVar5 + 0x34) == '\0') || (bVar2 = 0, *(char *)(iVar5 + 0x30) != '\0')) {
          bVar2 = 1;
        }
        if ((*(char *)(iVar5 + 0x50) == '\0') || (bVar4 = 0, *(char *)(iVar5 + 0x4c) != '\0')) {
          bVar4 = 1;
        }
        if (!(bool)(bVar2 & bVar4)) {
          if (*(char *)(_DAT_08007b88 + 7) == '\0') {
            pcVar10 = s_Switch_charging_result__GOOD__>_E_08007cc0;
            goto LAB_08007936;
          }
          goto LAB_080079b0;
        }
      }
    }
  }
  else {
    *(undefined4 *)(iVar5 + 0xc) = 0;
    if (*(byte *)(iVar5 + 2) < 3) {
      case_gpio_pa6_write(0);
      case_gpio_pa7_write(0);
      *(undefined1 *)(iVar5 + 2) = 2;
      if (*(char *)(_DAT_08007b88 + 7) == '\0') {
        g2_log_printf(s_clear_led_since_gls_status_updat_08007b8b + 1);
        g2_log_printf(&DAT_08007b84);
      }
    }
    iVar7 = _DAT_08007b88;
    if (*(char *)(iVar5 + 0x11) == '\0') {
      if (*(char *)(iVar5 + 0x10) == '\0') {
        if (*(char *)(_DAT_08007b88 + 7) == '\0') {
          pcVar10 = s_L___R_GLS_OUT__show_led_after_1s_08007c2c;
          goto LAB_08007936;
        }
      }
      else if (*(char *)(_DAT_08007b88 + 7) == '\0') {
        pcVar10 = s_L_IN__R_OUT__wait_1s_to_confirm__08007c74;
LAB_08007936:
        g2_log_printf(pcVar10);
        g2_log_printf(&DAT_08007b84);
      }
    }
    else if (*(char *)(iVar5 + 0x10) == '\0') {
      if (*(char *)(_DAT_08007b88 + 7) == '\0') {
        pcVar10 = s_L_OUT__R_IN__wait_1s_to_confirm__08007c50;
        goto LAB_08007936;
      }
    }
    else if ((*(char *)(iVar5 + 0x30) == '\0') || (*(char *)(iVar5 + 0x4c) == '\0')) {
      if (*(char *)(_DAT_08007b88 + 7) == '\0') {
        g2_log_printf(s_L___R_GLS_IN__Charging_status_un_08007bf0);
        g2_log_printf(&DAT_08007b84);
      }
      *(undefined1 *)(iVar7 + 1) = 8;
    }
    else if (*(char *)(_DAT_08007b88 + 7) == '\0') {
      pcVar10 = s_L___R_GLS_IN__Charging_status_co_08007bb0;
      goto LAB_08007936;
    }
LAB_080079b0:
    periodic_timer_restart();
  }
  if (7 < *(uint *)(iVar5 + 0x40)) {
    __aeabi_uidiv(*(undefined4 *)(iVar5 + 0x44),0xf);
    if ((extraout_r1_02 == 0) && (*(char *)(_DAT_08007b88 + 7) == '\0')) {
      g2_log_printf(s_No_reply_from_GLS_L__wait_for__d_08007ce8,0xf);
      g2_log_printf(&DAT_08007b84);
    }
    *(int *)(iVar5 + 0x44) = *(int *)(iVar5 + 0x44) + 1;
  }
  if (7 < *(uint *)(iVar5 + 0x5c)) {
    __aeabi_uidiv(*(undefined4 *)(iVar5 + 0x60),0xf);
    if ((extraout_r1_03 == 0) && (*(char *)(_DAT_08007b88 + 7) == '\0')) {
      g2_log_printf(s_No_reply_from_GLS_R__wait_for__d_08007d0c,0xf);
      g2_log_printf(&DAT_08007b84);
    }
    *(int *)(iVar5 + 0x60) = *(int *)(iVar5 + 0x60) + 1;
  }
  if (7 < *(uint *)(iVar5 + 0x40)) {
    uVar8 = *(undefined4 *)(iVar5 + 0x44);
    __aeabi_uidiv(uVar8,0xb4);
    if (extraout_r1_04 == 0) {
      if (*(char *)(_DAT_08007b88 + 8) == '\0') {
        glasses_sides_reset(1,0);
        if (*(char *)(_DAT_08007b88 + 7) == '\0') {
          pcVar10 = s_No_reply_from_GLS_L_for__ds__res_08007d5c;
          uVar8 = *(undefined4 *)(iVar5 + 0x44);
          goto LAB_08007a54;
        }
      }
      else if (*(char *)(_DAT_08007b88 + 7) == '\0') {
        pcVar10 = s_No_reply_from_GLS_L_for__ds__do_n_08007d30;
LAB_08007a54:
        g2_log_printf(pcVar10,uVar8);
        g2_log_printf(&DAT_08007b84);
      }
    }
  }
  if ((7 < *(uint *)(iVar5 + 0x5c)) &&
     (__aeabi_uidiv(*(undefined4 *)(iVar5 + 0x60),0xb4), iVar7 = _DAT_08007b88, extraout_r1_05 == 0)
     ) {
    if (*(char *)(_DAT_08007b88 + 8) == '\0') {
      glasses_sides_reset(0,1);
      if (*(char *)(iVar7 + 7) == '\0') {
        pcVar10 = s_No_reply_from_GLS_R_for__ds__res_08007db4;
        uVar8 = *(undefined4 *)(iVar5 + 0x60);
        goto LAB_08007a96;
      }
    }
    else if (*(char *)(_DAT_08007b88 + 7) == '\0') {
      pcVar10 = s_No_reply_from_GLS_R_for__ds__do_n_08007d88;
      uVar8 = *(undefined4 *)(iVar5 + 0x44);
LAB_08007a96:
      g2_log_printf(pcVar10,uVar8);
      g2_log_printf(&DAT_08007b84);
    }
  }
  if (((7 < *(uint *)(iVar5 + 0x40)) && (*(int *)(iVar5 + 0x44) == 0xd2)) ||
     ((7 < *(uint *)(iVar5 + 0x5c) && (*(int *)(iVar5 + 0x60) == 0xd2)))) {
    periodic_timer_restart();
  }
  iVar7 = _DAT_08007b88;
  if ((((((*(char *)(iVar5 + 0x10) != '\0') && (*(char *)(iVar5 + 0x11) != '\0')) &&
        (0x14 < *(uint *)(iVar5 + 0xc))) &&
       ((0x32 < *(byte *)(iVar5 + 0x32) && (0x14 < *(byte *)(iVar5 + 1))))) &&
      (*(char *)(iVar5 + 0x1b) == '\0')) && (*(char *)(_DAT_08007b88 + 4) == '\0')) {
    *(undefined1 *)(_DAT_08007b88 + 4) = 1;
    if (*(char *)(iVar7 + 7) == '\0') {
      g2_log_printf(s__OTA_BOX___check_box_ota_firmwar_08007de0);
      g2_log_printf(&DAT_08007b84);
    }
    osDelay(100);
    uStack_14 = DAT_08007e04;
    uStack_10 = DAT_08007e08;
    _uStack_c = CONCAT31((int3)((uint)DAT_08007e0c >> 8),0x1e);
    gls_uart_transfer_controlled(1,&uStack_14,9);
    *(undefined1 *)(iVar5 + 0x1b) = 1;
    *(undefined1 *)(iVar7 + 4) = 0;
    gls_frame_validate_dispatch(1);
  }
  iVar7 = _DAT_08007b88;
  if (*(char *)(_DAT_08007b88 + 3) != '\0') {
    uStack_20 = osEventFlagsGet(*(undefined4 *)(_DAT_08007b88 + 0x38));
    if ((int)(uStack_20 << 0x1e) < 0) {
      osEventFlagsClear(*(undefined4 *)(iVar7 + 0x38),2);
      osTimerStart(*(undefined4 *)(iVar7 + 0x10),DAT_08007ee4);
    }
    if ((int)(uStack_20 << 0x13) < 0) {
      osEventFlagsClear(*(undefined4 *)(iVar7 + 0x38),0x1000);
      idle_mode_exit();
    }
    if (((*(char *)(iVar5 + 1) == '\0') && (*(byte *)(iVar5 + 3) == 0)) &&
       (uStack_20 = (uint)*(byte *)(iVar5 + 3), scaled_sensor_value_read(&uStack_20),
       uStack_20 < DAT_08007ee8)) {
      if (*(char *)(iVar7 + 7) == '\0') {
        g2_log_printf(s_Standby_from_idle_mode__reason__l_08007eec);
        g2_log_printf(&DAT_08007f18);
      }
      peripheral_transaction_guard(0x10,&uStack_1c,1);
      peripheral_transaction_guard(0x11,&uStack_1c,1);
      glasses_channel_command_pack(0);
      peripheral_mode_write_retry(0);
      HAL_PWR_DisableWakeUpPin(0x2b);
      HAL_PWR_EnableWakeUpPin(DAT_08007f1c);
      *(undefined4 *)(DAT_08007f24 + 0x18) = DAT_08007f20;
      HAL_PWR_EnterSTANDBYMode();
    }
  }
  if (0x1d < *(byte *)(iVar5 + 0x17)) {
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

