
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_08000e1c(byte *param_1,uint param_2,int param_3)

{
  byte bVar1;
  byte bVar2;
  char cVar3;
  uint uVar4;
  byte *pbVar5;
  undefined4 *puVar6;
  undefined1 uVar7;
  char *pcVar8;
  int iVar9;
  int *piVar10;
  undefined4 uVar11;
  int local_40;
  undefined4 local_3c;
  undefined4 local_38;
  undefined1 local_34;
  byte local_33;
  undefined1 local_32;
  undefined1 local_31;
  undefined1 local_30;
  undefined1 local_2f;
  undefined1 local_2e;
  undefined1 uStack_2d;
  undefined4 local_2c;
  undefined1 local_28 [8];
  byte *pbStack_20;
  uint uStack_1c;
  int local_18;
  
  iVar9 = _DAT_0800118c;
  puVar6 = DAT_08001184;
  pbVar5 = DAT_08001180;
  piVar10 = &local_40;
  local_28[0] = 0;
  bVar1 = DAT_08001180[1];
  uVar11 = *DAT_08001184;
  pbStack_20 = param_1;
  uStack_1c = param_2;
  local_18 = param_3;
  if (param_1[2] != 2) {
    if (((*param_1 == 0x3d) && (bVar1 != 0)) &&
       (osEventFlagsSet(uVar11,0x80), *DAT_08001188 == '\0')) {
      g2_log_printf(s__AGING_NOT___exit_aging_status_0_080012b8);
      g2_log_printf(&DAT_080011b0);
    }
    if (local_18 == 0) {
      if (param_2 < 5) {
        return;
      }
      if (param_1[1] != 0) {
        return;
      }
      if (1 < param_1[2]) {
        return;
      }
      if (param_1[3] + 5 != param_2) {
        return;
      }
      uVar11 = 0x20;
    }
    else {
      if (param_2 < 5) {
        return;
      }
      if (param_1[1] != 0) {
        return;
      }
      if (1 < param_1[2]) {
        return;
      }
      if ((uint)param_1[3] + (uint)param_1[4] * 0x100 + 6 != param_2) {
        return;
      }
      uVar11 = 0x400;
    }
    osEventFlagsSet(*puVar6,uVar11);
    FUN_080001b4(DAT_080012e0,param_1,param_2);
    return;
  }
  bVar2 = *param_1;
  cVar3 = *DAT_08001188;
  if (bVar2 == 0x51) {
    local_40 = DAT_080011c8;
    local_3c = DAT_080011cc;
    local_38 = DAT_080011d0;
    FUN_08002f60(&local_3c,DAT_080011cc,DAT_080011d0,&local_34);
    uVar11 = 0xc;
    goto LAB_08000f1c;
  }
  if (bVar2 < 0x52) {
    if (bVar2 == 0x3f) {
      if (param_2 < 5) {
        return;
      }
      *(bool *)(_DAT_0800118c + 0x15) = param_1[4] != 0;
      if (cVar3 == '\0') {
        if (param_1[4] == 0) {
          pcVar8 = s_disable_08001204;
        }
        else {
          pcVar8 = s_enable_080011fc;
        }
        g2_log_printf(s__s_output__reason__cmd_0800120c,pcVar8);
        g2_log_printf(&DAT_080011b0);
      }
      if (*(char *)(iVar9 + 0x15) != '\0') {
        aging_indicator_apply();
        *(undefined1 *)(iVar9 + 0x10) = 0;
        *(undefined1 *)(iVar9 + 0x11) = 0;
      }
      uVar11 = 0x3f;
      goto LAB_08001102;
    }
    if (bVar2 < 0x40) {
      if (bVar2 == 6) {
        case_command_build_fixed(6);
        local_28[0] = 0xee;
LAB_08000eb0:
        FUN_08000928(local_28,1);
        return;
      }
      if (bVar2 == 0x14) {
        local_3c = 0;
        sensor_default_value_read(&local_3c);
        local_3c = FUN_0800018c(local_3c,10);
        local_40 = 0;
        calibrated_sensor_value_convert(&local_40);
        local_2c = 0;
        scaled_sensor_value_read(&local_2c);
        local_38 = DAT_080011b4;
        uVar4 = (uint)local_40 >> 0x1f;
        if (local_40 < 0) {
          local_40 = -local_40;
        }
        _local_34 = CONCAT13((char)((uint)local_40 >> 8),
                             CONCAT12((char)local_40,
                                      CONCAT11((byte)uVar4,*(undefined1 *)(iVar9 + 1))));
        iVar9 = local_3c;
        if (local_3c < 0) {
          iVar9 = ~-local_3c + 1;
        }
        uStack_2d = (undefined1)((uint)DAT_080011bc >> 0x18);
        _local_30 = CONCAT12((char)((uint)local_2c >> 8),CONCAT11((char)local_2c,(char)iVar9));
        uVar11 = 0xb;
        piVar10 = &local_38;
        goto LAB_08000f1c;
      }
      if (bVar2 == 0x3e) {
        if (param_2 < 5) {
          return;
        }
        bVar2 = param_1[4];
        if (*DAT_08001180 != bVar2) {
          *DAT_08001180 = bVar2 != 0;
          pbVar5[8] = 0;
          pbVar5[9] = 0;
          pbVar5[10] = 0;
          pbVar5[0xb] = 0;
          if (((bVar2 == 0) && (bVar1 != 0)) &&
             (osEventFlagsSet(uVar11,0x80), *DAT_08001188 == '\0')) {
            g2_log_printf(s__AGING_NOT___exit_aging_status_0_080011d4);
            g2_log_printf(&DAT_080011b0);
          }
        }
        uVar11 = 0x3e;
        goto LAB_08001102;
      }
    }
    else {
      if (bVar2 == 0x41) {
        case_command_build_fixed(0x41);
        local_28[0] = 0xff;
        goto LAB_08000eb0;
      }
      if (bVar2 == 0x50) {
        local_40 = DAT_080011c0;
        local_3c = CONCAT13((char)((uint)DAT_080011c4 >> 0x18),0x390201);
        uVar11 = 7;
        piVar10 = &local_40;
        goto LAB_08000f1c;
      }
    }
  }
  else {
    if (bVar2 == 0x5e) {
      if (0x13 < param_2) {
        iVar9 = FUN_0800373c(param_1 + 4);
        if (iVar9 == 0) {
          local_3c = DAT_08001288;
          local_40 = DAT_08001284;
          FUN_0800680c(&local_40,5);
          if (*DAT_08001188 != '\0') goto LAB_080010be;
          pcVar8 = s_Set_SN_Even_fail__0800128c;
        }
        else {
          case_command_build_fixed(0x5e);
          if (*DAT_08001188 != '\0') goto LAB_080010be;
          pcVar8 = s_Set_SN_Even_done__08001270;
        }
        g2_log_printf(pcVar8);
LAB_080010be:
        log_hex_buffer(param_1 + 4,0x10);
        return;
      }
      if (cVar3 != '\0') {
        return;
      }
      pcVar8 = s_SN_Even_length_wrong__080012a0;
      goto LAB_08000e96;
    }
    if (bVar2 < 0x5f) {
      if (bVar2 == 0x56) {
        if (param_2 < 6) {
          return;
        }
        if (param_1[4] == 0) {
          if (param_1[5] == 0) {
            if (cVar3 == '\0') {
              g2_log_printf(s_Enter_GLS_OTA_Status__L_08001224);
              g2_log_printf(&DAT_080011b0);
            }
            uVar7 = 1;
          }
          else {
            if (cVar3 == '\0') {
              g2_log_printf(s_Enter_GLS_OTA_Status__R_0800123c);
              g2_log_printf(&DAT_080011b0);
            }
            uVar7 = 2;
          }
          *(undefined1 *)(iVar9 + 0x19) = uVar7;
          *(undefined1 *)(iVar9 + 0x1a) = 0;
          return;
        }
        if (cVar3 == '\0') {
          g2_log_printf(s_Exit_GLS_OTA_Status_08001254);
          g2_log_printf(&DAT_080011b0);
        }
        *(undefined1 *)(iVar9 + 0x19) = 0;
        aging_led_status_clear();
        uVar11 = 0x56;
LAB_08001102:
        case_command_build_fixed(uVar11);
        return;
      }
      if (bVar2 == 0x5c) {
        local_40 = DAT_08001268;
        local_3c = CONCAT31((int3)((uint)DAT_0800126c >> 8),*(char *)(_DAT_0800118c + 4) == '\0');
        uVar11 = 5;
        piVar10 = &local_40;
        goto LAB_08000f1c;
      }
      if (bVar2 == 0x5d) {
        if (param_2 < 6) {
          return;
        }
        if (param_1[4] == 0) {
          case_gpio_pa7_write(param_1[5] == 0);
        }
        else {
          case_gpio_pa6_write(param_1[5] == 0);
        }
        uVar11 = 0x5d;
        goto LAB_08001102;
      }
    }
    else {
      if (bVar2 == 0x5f) {
        local_40 = 0x1003015f;
        FUN_08002f88(&local_3c);
        uVar11 = 0x14;
        piVar10 = &local_40;
LAB_08000f1c:
        FUN_0800680c(piVar10,uVar11);
        return;
      }
      if (bVar2 == 0x68) {
        if (param_2 < 5) {
          return;
        }
        *DAT_08001188 = param_1[4] != 0;
        uVar11 = 0x68;
        goto LAB_08001102;
      }
    }
  }
  if (cVar3 != '\0') {
    return;
  }
  g2_log_printf(s_dst_box__cannot_parse_cmd___02x_0800118f + 1,bVar2);
  pcVar8 = &DAT_080011b0;
LAB_08000e96:
  g2_log_printf(pcVar8);
  return;
}

