
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void glasses_charge_control_policy(void)

{
  bool bVar1;
  bool bVar2;
  bool bVar3;
  bool bVar4;
  int iVar5;
  byte *pbVar6;
  int iVar7;
  uint uVar8;
  
  iVar5 = DAT_0800d0ec;
  bVar1 = true;
  bVar3 = false;
  bVar2 = true;
  bVar4 = false;
  if ((*(char *)(DAT_0800d0ec + 0x10) == '\0') || (*(char *)(DAT_0800d0ec + 0x31) != '\0')) {
LAB_0800ceac:
    if (((*(char *)(iVar5 + 0x11) != '\0') && (*(char *)(iVar5 + 0x4d) == '\0')) &&
       ((*DAT_0800d0f0 == '\0' || (*(char *)(iVar5 + 0x10) != '\0')))) {
      case_update_cached_byte(5,3);
      case_update_cached_byte(4,0xaf);
      case_update_cached_byte(6,0x8d);
      osDelay(3);
      iVar7 = case_trimmed_average8();
      uVar8 = __aeabi_uidiv(iVar7 * 1000,*DAT_0800d0f4);
      if (uVar8 < 0x79) {
        if (uVar8 < 0x50) {
          bVar4 = true;
        }
      }
      else {
        *(undefined1 *)(iVar5 + 0x11) = 1;
        bVar2 = false;
        DAT_0800d0f8[1] = 0;
      }
    }
  }
  else if ((*DAT_0800d0f0 == '\0') || (*(char *)(DAT_0800d0ec + 0x11) != '\0')) {
    case_update_cached_byte(5,3);
    case_update_cached_byte(3,0xaf);
    case_update_cached_byte(6,0x8b);
    osDelay(3);
    iVar7 = case_trimmed_average8();
    uVar8 = __aeabi_uidiv(iVar7 * 1000,*DAT_0800d0f4);
    pbVar6 = DAT_0800d0f8;
    if (uVar8 < 0x79) {
      if (uVar8 < 0x50) {
        bVar3 = true;
      }
    }
    else {
      *(undefined1 *)(iVar5 + 0x10) = 1;
      bVar1 = false;
      *pbVar6 = 0;
    }
    goto LAB_0800ceac;
  }
  if (!bVar2 && !bVar1) {
    return;
  }
  case_copy_head8_to_tail8();
  if (bVar1) {
    if (*(char *)(iVar5 + 0x10) != '\0') {
      case_update_cached_byte(6,0xc1);
    }
    case_update_cached_byte(3,0xae);
    osDelay(3);
  }
  if (bVar2) {
    if (*(char *)(iVar5 + 0x11) != '\0') {
      case_update_cached_byte(6,0xc1);
    }
    case_update_cached_byte(4,0xae);
    osDelay(3);
  }
  if (bVar1) {
    case_update_cached_byte(6,0x85);
    osDelay(2);
    uVar8 = case_trimmed_average8();
    if (uVar8 < 0x26d) {
      case_update_cached_byte(5,0xb);
      osDelay(3);
      uVar8 = case_trimmed_average8();
      *(bool *)(iVar5 + 0x10) = uVar8 < 0x26c;
      if (uVar8 < 0x26c) goto LAB_0800cfa2;
LAB_0800cfd2:
      *DAT_0800d0f8 = 0;
    }
    else {
      *(undefined1 *)(iVar5 + 0x10) = 1;
LAB_0800cfa2:
      if (!bVar3) goto LAB_0800cfd2;
      if (*DAT_0800d0f8 < 6) {
        *DAT_0800d0f8 = *DAT_0800d0f8 + 1;
      }
      else {
        if (*_DAT_0800d0fc == '\0') {
          g2_log_printf(s_L_water_detected__disable_5V_out_0800d0ff + 1);
          g2_log_printf(&DAT_0800d128);
        }
        *(undefined1 *)(iVar5 + 0x31) = 1;
        *(undefined1 *)(iVar5 + 0x33) = 1;
      }
    }
    if ((((*(char *)(iVar5 + 0x10) != '\0') && (*(char *)(iVar5 + 0x11) != '\0')) &&
        (*(char *)(iVar5 + 0x31) != '\0')) && (*(char *)(iVar5 + 0x33) == '\0')) {
      case_update_cached_byte(5,3);
      case_update_cached_byte(6,0x81);
      case_update_cached_byte(7,0x20);
      case_update_cached_byte(3,0xaf);
      osDelay(5);
      case_update_cached_byte(3,0xae);
    }
  }
  if (!bVar2) goto LAB_0800d0e6;
  case_update_cached_byte(6,0x87);
  osDelay(2);
  uVar8 = case_trimmed_average8();
  if (uVar8 < 0x26d) {
    case_update_cached_byte(5,7);
    osDelay(3);
    uVar8 = case_trimmed_average8();
    *(bool *)(iVar5 + 0x11) = uVar8 < 0x26c;
    if (uVar8 < 0x26c) goto LAB_0800d06a;
LAB_0800d09a:
    DAT_0800d0f8[1] = 0;
  }
  else {
    *(undefined1 *)(iVar5 + 0x11) = 1;
LAB_0800d06a:
    if (!bVar4) goto LAB_0800d09a;
    if (DAT_0800d0f8[1] < 6) {
      DAT_0800d0f8[1] = DAT_0800d0f8[1] + 1;
    }
    else {
      if (*_DAT_0800d0fc == '\0') {
        g2_log_printf(s_R_water_detected__disable_5V_out_0800d12c);
        g2_log_printf(&DAT_0800d128);
      }
      *(undefined1 *)(iVar5 + 0x4d) = 1;
      *(undefined1 *)(iVar5 + 0x4f) = 1;
    }
  }
  if (((*(char *)(iVar5 + 0x10) != '\0') && (*(char *)(iVar5 + 0x11) != '\0')) &&
     ((*(char *)(iVar5 + 0x4d) != '\0' && (*(char *)(iVar5 + 0x4f) == '\0')))) {
    case_update_cached_byte(5,3);
    case_update_cached_byte(6,0x81);
    case_update_cached_byte(7,0x20);
    case_update_cached_byte(4,0xaf);
    osDelay(5);
    case_update_cached_byte(4,0xae);
  }
LAB_0800d0e6:
  dual_side_indicator_update();
  return;
}

