
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void glasses_status_poll_dispatch(void)

{
  char cVar1;
  char cVar2;
  short sVar3;
  bool bVar4;
  bool bVar5;
  int iVar6;
  char *pcVar7;
  undefined1 uVar8;
  char *pcVar9;
  int iVar10;
  int extraout_r1;
  int extraout_r1_00;
  int extraout_r1_01;
  int extraout_r1_02;
  int extraout_r1_03;
  undefined1 local_20 [4];
  byte local_1c;
  undefined1 uStack_1b;
  undefined2 uStack_1a;
  
  pcVar7 = _DAT_08001ad8;
  iVar6 = DAT_08001ad0;
  cVar1 = *(char *)(DAT_08001ad0 + 0x10);
  cVar2 = *(char *)(DAT_08001ad0 + 0x11);
  if ((cVar1 == '\0') && (cVar2 == '\0')) {
    return;
  }
  bVar4 = true;
  bVar5 = true;
  if (*DAT_08001ad4 == '\0') {
LAB_0800193e:
    if (*(char *)(iVar6 + 0x10) != '\0') goto LAB_08001944;
  }
  else {
    if ((cVar1 == '\0') || (cVar2 == '\0')) {
      bVar4 = false;
      bVar5 = false;
      if (((*(uint *)(DAT_08001ad0 + 0xc) < 5) ||
          (__aeabi_uidiv(*(uint *)(DAT_08001ad0 + 0xc),0x14), extraout_r1 == 0)) &&
         (*pcVar7 == '\0')) {
        g2_log_printf(s_only_one_side__dont_send_0x13__L_08001adb + 1,cVar1,cVar2);
        g2_log_printf(&DAT_08001b08);
      }
      goto LAB_0800193e;
    }
LAB_08001944:
    iVar10 = DAT_08001ad0;
    if ((*(char *)(DAT_08001ad0 + 0x31) != '\0') && (sVar3 = *(short *)(iVar6 + 0x38), sVar3 != 0))
    {
      bVar4 = false;
      __aeabi_uidiv(sVar3,0x1e);
      if (extraout_r1_00 == 0) {
        if (*(char *)(iVar10 + 0x33) == '\0') {
          if (*pcVar7 == '\0') {
            pcVar9 = s_L_charging_done__dont_send_0x13__08001b38;
            goto LAB_08001980;
          }
        }
        else if (*pcVar7 == '\0') {
          pcVar9 = s_L_water_detected__disable_5V__ti_08001b0c;
LAB_08001980:
          g2_log_printf(pcVar9,sVar3);
          g2_log_printf(&DAT_08001b08);
        }
      }
    }
  }
  iVar6 = DAT_08001ad0;
  if (((*(char *)(DAT_08001ad0 + 0x11) != '\0') && (*(char *)(DAT_08001ad0 + 0x4d) != '\0')) &&
     (sVar3 = *(short *)(DAT_08001ad0 + 0x54), sVar3 != 0)) {
    bVar5 = false;
    __aeabi_uidiv(sVar3,0x1e);
    if (extraout_r1_01 == 0) {
      if (*(char *)(iVar6 + 0x4f) == '\0') {
        if (*pcVar7 != '\0') goto LAB_080019d4;
        pcVar9 = s_R_charging_done__dont_send_0x13__08001b98;
      }
      else {
        if (*pcVar7 != '\0') goto LAB_080019d4;
        pcVar9 = s_R_water_detected__disable_5V__ti_08001b6c;
      }
      g2_log_printf(pcVar9,sVar3);
      g2_log_printf(&DAT_08001b08);
    }
  }
LAB_080019d4:
  iVar6 = DAT_08001ad0;
  local_20 = (undefined1  [4])DAT_08001bcc;
  if (*(char *)(DAT_08001ad0 + 4) == '\0') {
    uVar8 = 2;
  }
  else {
    uVar8 = 1;
  }
  uStack_1a = (undefined2)((uint)DAT_08001bd0 >> 0x10);
  _local_1c = CONCAT11(uVar8,*(char *)(DAT_08001ad0 + 3) << 7 | *(byte *)(DAT_08001ad0 + 1));
  if (((*(char *)(DAT_08001ad0 + 0x10) != '\0') && (bVar4)) &&
     (__aeabi_uidiv(*(undefined4 *)(DAT_08001ad0 + 0x44),0xf), extraout_r1_02 == 0)) {
    local_20[2] = 0;
    case_finalize_length_checksum(local_20,7);
    gls_uart_transfer_controlled(1,local_20,7);
    *(int *)(iVar6 + 0x48) = *(int *)(iVar6 + 0x48) + 1;
    iVar10 = gls_frame_validate_dispatch(1);
    if (iVar10 == 0x13) {
      *(undefined4 *)(iVar6 + 0x40) = 0;
      *(undefined4 *)(iVar6 + 0x44) = 0;
      *(int *)(iVar6 + 0x3c) = *(int *)(iVar6 + 0x3c) + 1;
    }
    else {
      *(undefined4 *)(iVar6 + 0x3c) = 0;
      *(int *)(iVar6 + 0x40) = *(int *)(iVar6 + 0x40) + 1;
      if (*pcVar7 == '\0') {
        g2_log_printf(s_Fail_to_get_GLS_L_status__cnt__d_08001bd4);
        g2_log_printf(&DAT_08001b08);
      }
    }
  }
  if (((*(char *)(iVar6 + 0x11) != '\0') && (bVar5)) &&
     (__aeabi_uidiv(*(undefined4 *)(iVar6 + 0x60),0xf), extraout_r1_03 == 0)) {
    local_20[2] = 1;
    case_finalize_length_checksum(local_20,7);
    gls_uart_transfer_controlled(0,local_20,7,1);
    *(int *)(iVar6 + 100) = *(int *)(iVar6 + 100) + 1;
    iVar10 = gls_frame_validate_dispatch(0);
    if (iVar10 == 0x13) {
      *(undefined4 *)(iVar6 + 0x5c) = 0;
      *(undefined4 *)(iVar6 + 0x60) = 0;
      *(int *)(iVar6 + 0x58) = *(int *)(iVar6 + 0x58) + 1;
    }
    else {
      *(int *)(iVar6 + 0x5c) = *(int *)(iVar6 + 0x5c) + 1;
      *(undefined4 *)(iVar6 + 0x58) = 0;
      if (*pcVar7 == '\0') {
        g2_log_printf(s_Fail_to_get_GLS_R_status__cnt__d_08001bf8);
        g2_log_printf(&DAT_08001b08);
      }
    }
  }
  return;
}

