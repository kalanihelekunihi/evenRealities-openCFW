
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 case_ota_execute(void)

{
  char *pcVar1;
  int iVar2;
  char *pcVar3;
  uint uVar4;
  undefined4 uVar5;
  uint uVar6;
  uint uVar7;
  char cVar8;
  char cVar9;
  uint uVar10;
  undefined4 local_44;
  undefined4 local_40;
  undefined1 local_3c;
  undefined3 uStack_3b;
  int local_28;
  uint local_24;
  undefined4 local_20;
  undefined4 local_1c;
  
  pcVar3 = DAT_08001770;
  uVar7 = 0;
  while (pcVar1 = _DAT_08001774, *pcVar3 != '\0') {
    osDelay(100);
  }
  *pcVar3 = '\x01';
  if (*pcVar1 == '\0') {
    g2_log_printf(s__OTA_BOX___Check_gls_ready_08001777 + 1);
    g2_log_printf(&DAT_08001794);
  }
  local_1c = DAT_0800179c;
  local_20 = DAT_08001798;
  case_finalize_length_checksum(&local_20,5);
  gls_uart_transfer_uncontrolled(1,&local_20,5);
  *pcVar3 = '\0';
  iVar2 = gls_frame_validate_dispatch(1);
  if (iVar2 == 0x59) {
    osDelay(100);
    if (*pcVar1 == '\0') {
      g2_log_printf(s__OTA_BOX___Get_running_bank_080017bc);
      g2_log_printf(&DAT_08001794);
    }
    iVar2 = case_classify_status();
    *(char *)(_DAT_080017d8 + 0x18) = (char)iVar2;
    if (iVar2 == 0) {
      if (*pcVar1 != '\0') {
        return 0;
      }
      pcVar3 = s__OTA_BOX___Get_running_bank_fail_080017db + 1;
    }
    else {
      if (*pcVar1 == '\0') {
        g2_log_printf(s__OTA_BOX___Running_bank___d_08001800);
        g2_log_printf(&DAT_08001794);
      }
      iVar2 = FUN_08002d48();
      if (iVar2 == 0) {
        if (*pcVar1 != '\0') {
          return 0;
        }
        pcVar3 = s__OTA_BOX___Erase_bank_fail__0800181c;
      }
      else {
        if (*pcVar1 == '\0') {
          g2_log_printf(s__OTA_BOX___Copy_SN__08001838);
          g2_log_printf(&DAT_08001794);
        }
        iVar2 = FUN_08002b4c();
        if (iVar2 != 0) {
          if (*_DAT_08001774 == '\0') {
            g2_log_printf(s__OTA_BOX___Copy_SN_done__0800184c);
            g2_log_printf(&DAT_08001794);
            if (*_DAT_08001774 == '\0') {
              g2_log_printf(s__OTA_BOX___get_bin_file_08001884);
              g2_log_printf(&DAT_08001794);
            }
          }
          *pcVar3 = '\x01';
          uVar10 = 0xf0;
          local_28 = _DAT_080017d8 + 0x20;
          local_24 = 0;
          cVar9 = '\0';
          do {
            uVar6 = *(uint *)(_DAT_080017d8 + 0x20);
            if (uVar6 <= uVar7) {
              if (*_DAT_08001774 == '\0') {
                g2_log_printf(s__OTA_BOX___get_bin_file_done__to_080018b0,local_24);
                g2_log_printf(&DAT_08001794);
              }
              *pcVar3 = '\0';
              uVar5 = ota_image_be32_sum_verify();
              return uVar5;
            }
            if (uVar6 < uVar7 + uVar10) {
              uVar10 = uVar6 - uVar7 & 0xff;
            }
            *(undefined4 *)(_DAT_080017d8 + 0x28) = 0;
            *(undefined1 *)(local_28 + 0xc) = 0;
            local_44 = DAT_0800189c;
            local_40 = DAT_080018a0;
            _local_3c = CONCAT31((int3)((uint)DAT_080018a4 >> 8),(char)uVar10);
            uVar6 = 0;
            do {
              uVar4 = uVar6 + 1 & 0xff;
              *(char *)((int)&local_40 + uVar6) = (char)(uVar7 >> ((uVar6 & 0x1f) << 3));
              uVar6 = uVar4;
            } while (uVar4 < 4);
            case_finalize_length_checksum(&local_44,10);
            gls_uart_transfer_uncontrolled(1,&local_44,10);
            gls_frame_validate_dispatch(1);
            if ((*(int *)(_DAT_080017d8 + 0x28) == 0) || (*(char *)(local_28 + 0xc) == '\0')) {
              if (*_DAT_08001774 == '\0') {
                g2_log_printf(&DAT_080018ac);
              }
              local_24 = local_24 + 1 & 0xffff;
LAB_08001718:
              cVar8 = cVar9 + '\x01';
              if (cVar9 == '\n') {
                *pcVar3 = '\0';
                return 0;
              }
            }
            else {
              iVar2 = FUN_08002e04(uVar7);
              if (iVar2 == 0) {
                if (*_DAT_08001774 == '\0') {
                  g2_log_printf(&DAT_080018a8);
                }
                goto LAB_08001718;
              }
              uVar7 = *(byte *)(local_28 + 0xc) + uVar7;
              cVar8 = '\0';
            }
            osDelay(0x14);
            cVar9 = cVar8;
          } while( true );
        }
        if (*pcVar1 != '\0') {
          return 0;
        }
        pcVar3 = s__OTA_BOX___Copy_SN_fail__08001868;
      }
    }
  }
  else {
    if (*pcVar1 != '\0') {
      return 0;
    }
    pcVar3 = s__OTA_BOX___GLS_not_ready__080017a0;
  }
  g2_log_printf(pcVar3);
  g2_log_printf(&DAT_08001794);
  return 0;
}

