
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_08002fc8(void)

{
  bool bVar1;
  char *pcVar2;
  char *pcVar3;
  byte *pbVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  int iVar8;
  char *pcVar9;
  byte bVar10;
  uint uVar11;
  char cVar12;
  byte local_2c [4];
  undefined1 auStack_28 [4];
  char local_24 [4];
  undefined1 auStack_20 [12];
  
  pcVar3 = DAT_08003344;
  if (*DAT_08003344 == '\0') {
    uVar5 = case_device_info_word6();
    uVar6 = case_device_info_word5();
    uVar7 = case_device_info_word4();
    g2_log_printf(s________B200__s__08x_08x_08x______08003350,s_1_2_57_08003348,uVar7,uVar6,uVar5);
    g2_log_printf(&DAT_08003374);
  }
  pcVar9 = DAT_08003378;
  pcVar2 = DAT_08003378;
  pcVar2[8] = '\0';
  pcVar2[9] = '\0';
  pcVar2[10] = '\0';
  pcVar2[0xb] = '\0';
  pcVar2[0xc] = '\0';
  pcVar2[0xd] = '\0';
  pcVar2[0xe] = '\0';
  pcVar2[0xf] = '\0';
  pcVar9[1] = '\0';
  pcVar9[2] = '\0';
  iVar8 = case_register_any_bits(_DAT_0800337c,0x20);
  pcVar9[3] = iVar8 == 0;
  iVar8 = case_register_any_bits(0x50000000,4);
  pcVar9[4] = iVar8 == 1;
  pcVar9[0x12] = *pcVar9 == '\x03';
  pcVar2 = DAT_08003378;
  DAT_08003378[0x13] = *pcVar9 == '\x03';
  pcVar2[0x10] = '\0';
  pcVar2[0x11] = '\0';
  pcVar2[0x14] = '\0';
  pcVar2[0x15] = '\x01';
  pcVar2[0x17] = '\0';
  pcVar2[0x1c] = '\0';
  pcVar2[0x1d] = '\0';
  pcVar2[0x18] = '\0';
  pcVar2[0x19] = '\0';
  pcVar2[0x1a] = '\0';
  pcVar2[0x1b] = '\0';
  pcVar2[0x24] = '\0';
  pcVar2[0x25] = '\0';
  pcVar2[0x26] = '\0';
  pcVar2[0x27] = '\0';
  pcVar2[0x20] = '\0';
  pcVar2[0x21] = '\0';
  pcVar2[0x22] = '\0';
  pcVar2[0x23] = '\0';
  pcVar2[0x28] = '\0';
  pcVar2[0x29] = '\0';
  pcVar2[0x2a] = '\0';
  pcVar2[0x2b] = '\0';
  pcVar2[0x2c] = '\0';
  pcVar2[0x16] = '\x01';
  case_run_pair();
  bVar1 = true;
  cVar12 = '\0';
  local_2c[0] = 0;
  do {
    case_run_guarded(0,local_2c,1);
    if (local_2c[0] == 0xa0) {
      if (cVar12 != '\x03') {
        if (*pcVar3 != '\0') goto LAB_080030c6;
        g2_log_printf(s_2217_self_check_done__080033b4);
        goto LAB_080030c0;
      }
      break;
    }
    case_wait_elapsed(100);
    cVar12 = cVar12 + '\x01';
  } while (cVar12 != '\x03');
  bVar1 = false;
  if (*pcVar3 == '\0') {
    g2_log_printf(s_Pself_check_fail__reason__2217_w_0800337f + 1,local_2c[0]);
LAB_080030c0:
    g2_log_printf(&DAT_08003374);
  }
LAB_080030c6:
  peripheral_init_retry();
  cVar12 = '\0';
  local_2c[0] = 0;
LAB_080030d0:
  while (peripheral_transaction_guard(0x14,local_2c,1), local_2c[0] != 0x14) {
    if (*pcVar3 == '\0') {
      g2_log_printf(s_using__0x70__chipid__0x_x_080033cc);
      g2_log_printf(&DAT_08003374);
    }
    if (local_2c[0] != 0) {
      if (*pcVar3 == '\0') {
        g2_log_printf(s_reset_pmic_register____080033e8);
        g2_log_printf(&DAT_08003374);
      }
      right_channel_transaction_guard(0x14);
    }
    case_wait_elapsed(100);
    cVar12 = cVar12 + '\x01';
    iVar8 = case_register_any_bits(_DAT_0800337c,0x20);
    if (iVar8 != 0) goto code_r0x0800312c;
    cVar12 = '\0';
    case_wait_elapsed(200);
  }
  if (cVar12 != '\x03') {
    if (*pcVar3 == '\0') {
      g2_log_printf(s__pmic_self_check_done__08003437 + 1);
      g2_log_printf(&DAT_08003374);
    }
    uVar11 = 0;
    do {
      peripheral_transaction_guard(uVar11 + 0x10 & 0xff,auStack_20 + uVar11,1);
      uVar11 = uVar11 + 1 & 0xff;
    } while (uVar11 < 8);
    if (*pcVar3 == '\0') {
      g2_log_printf(s_PMIC_reg_0x10_0x17__08003450);
    }
    log_hex_buffer(auStack_20,8);
    goto LAB_080031b2;
  }
  goto LAB_08003148;
code_r0x0800312c:
  if (cVar12 == '\x03') goto LAB_08003148;
  goto LAB_080030d0;
LAB_08003148:
  if (*pcVar3 == '\0') {
    g2_log_printf(s_self_check_fail__reason__pmic_in_08003400);
    g2_log_printf(&DAT_08003374);
  }
  glasses_channel_command_pack(0);
  HAL_PWR_DisableWakeUpPin(0x2b);
  HAL_PWR_EnableWakeUpPin(DAT_0800342c);
  *(undefined4 *)(_DAT_08003434 + 0x18) = DAT_08003430;
  HAL_PWR_EnterSTANDBYMode();
LAB_080031b2:
  iVar8 = case_register_any_bits(_DAT_0800337c,0x20);
  pcVar2 = DAT_08003378;
  DAT_08003378[3] = iVar8 == 0;
  peripheral_mode_write_retry(iVar8 != 0);
  if (*pcVar3 == '\0') {
    g2_log_printf(s_PMIC_enable_boost___d_08003464,pcVar2[3] == '\0');
    g2_log_printf(&DAT_08003374);
  }
  case_wait_elapsed(10);
  local_2c[0] = 0;
  FUN_08009040(0,1,local_2c);
  if (local_2c[0] == 0x81) {
    FUN_080090ac(0xa4,1,_DAT_0800347c);
    pbVar4 = _DAT_0800347c;
    bVar10 = *_DAT_0800347c;
    if ((int)((uint)bVar10 << 0x1c) < 0) {
      bVar10 = (bVar10 & 7) * '\x02' + 0x50;
    }
    else {
      bVar10 = (bVar10 & 7) * '\x02' + 0x60;
    }
    *_DAT_0800347c = bVar10;
    if (*pcVar3 == '\0') {
      bVar10 = *pbVar4;
      pcVar9 = s_2510_self_check_done__adjVal__d_0800347f + 1;
      goto LAB_0800324c;
    }
  }
  else {
    bVar1 = false;
    if (*pcVar3 == '\0') {
      pcVar9 = s_self_check_fail__reason__2510_wr_080034a0;
      bVar10 = local_2c[0];
LAB_0800324c:
      g2_log_printf(pcVar9,bVar10);
      g2_log_printf(&DAT_08003374);
    }
  }
  local_2c[0] = 0;
  gls_frame_pack_l(0,1,local_2c);
  if (local_2c[0] >> 4 == 9) {
    glasses_channel_command_pack(1);
    if (*pcVar3 == '\0') {
      g2_log_printf(s_4005_self_check_done__080034d4);
      g2_log_printf(&DAT_08003374);
    }
    if (bVar1) goto LAB_080032cc;
  }
  else if (*pcVar3 == '\0') {
    g2_log_printf(s_self_check_fail__reason__4005_wr_080034ec);
    g2_log_printf(&DAT_08003374);
  }
  uVar11 = 0;
  do {
    if (*pcVar3 == '\0') {
      g2_log_printf(s_wait_for__ds_to_reset______08003520,5 - uVar11);
      g2_log_printf(&DAT_08003374);
    }
    case_wait_elapsed(1000);
    uVar11 = uVar11 + 1 & 0xff;
  } while (uVar11 < 5);
  NVIC_SystemReset();
LAB_080032cc:
  iVar8 = case_query_command_a2_is_one();
  if (iVar8 != 0) {
    if (*pcVar3 == '\0') {
      g2_log_printf(s_Show_led_for_usb_reset__0800353c);
      g2_log_printf(&DAT_08003374);
    }
    case_toggle_lines_three();
    case_command_a2_clear();
  }
  case_configure_register_sequence();
  peripheral_transaction_guard(0x10,auStack_28,1);
  peripheral_transaction_guard(0x11,auStack_28,1);
  left_channel_transaction_guard(10,0x40);
  left_channel_transaction_guard(0xb,0xff);
  bounded_percentage_convert(local_24);
  pcVar2[1] = local_24[0];
  FUN_0800d178();
  iVar8 = DAT_08003554;
  uVar11 = 0;
  do {
    FUN_08009040(uVar11,1,iVar8 + uVar11);
    uVar11 = uVar11 + 1 & 0xff;
  } while (uVar11 < 8);
  FUN_0800d218();
  return;
}

