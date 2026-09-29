
/* WARNING: Function: case_switch8_offset replaced with injection: switch8_r3 */
/* WARNING (jumptable): Removing unreachable block (ram,0x08000940) */
/* WARNING: Removing unreachable block (ram,0x08000940) */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_08000928(byte *param_1,uint param_2)

{
  char cVar1;
  byte bVar2;
  byte *pbVar3;
  char *pcVar4;
  char *pcVar5;
  uint uVar6;
  undefined1 auStack_30 [32];
  
  pcVar5 = DAT_08000c68;
  uVar6 = (uint)*param_1;
  cVar1 = *DAT_08000c68;
  if (uVar6 == 0xaf) {
    if (param_2 < 2) {
      return;
    }
    pcVar5 = (char *)(uint)param_1[1];
    *DAT_08000c68 = pcVar5 != (char *)0x0;
    if (pcVar5 == (char *)0x0) {
      return;
    }
    pcVar4 = &DAT_08000c88;
  }
  else {
    if (uVar6 < 0xb0) {
                    /* WARNING: Could not recover jumptable at 0x08000940. Too many branches */
                    /* WARNING: Treating indirect jump as call */
      if (uVar6 - 0xa0 < (uint)DAT_08000944) {
        pbVar3 = (byte *)(uVar6 + 0x80008a5);
      }
      else {
        pbVar3 = (byte *)(DAT_08000944 + 0x8000945);
      }
      (*(code *)((uint)*pbVar3 * 2 + 0x8000945))();
      return;
    }
    if (uVar6 == 0xd4) {
      if (cVar1 == '\0') {
        g2_log_printf(s_Set_PMIC_chip_id_to_0x08_08000df0);
        g2_log_printf(&DAT_08000cac);
      }
      right_channel_transaction_guard(0x14,8);
      return;
    }
    if (uVar6 < 0xd5) {
      if (uVar6 == 0xd1) {
        if (param_2 < 4) {
          return;
        }
        *(bool *)DAT_08000d74 = param_1[1] != 0;
        *(bool *)DAT_08000d78 = param_1[2] != 0;
        *(bool *)_DAT_08000d7c = param_1[3] != 0;
        if (cVar1 != '\0') {
          return;
        }
        g2_log_printf(s_simu_full_bat__d__simu_empty_bat_08000d7f + 1);
        goto LAB_080009f4;
      }
      if (uVar6 < 0xd2) {
        if (uVar6 == 0xb0) {
          osEventFlagsSet(*DAT_08000d00,0x100);
          return;
        }
        if (uVar6 != 0xd0) {
          return;
        }
        if (param_2 < 2) {
          return;
        }
        glasses_channel_command_pack(param_1[1] != 0);
        if (*pcVar5 != '\0') {
          return;
        }
        if (param_1[1] == 0) {
          pcVar5 = s_Disable_08000c93;
        }
        else {
          pcVar5 = s_Enable_08000c6f;
        }
        pcVar5 = pcVar5 + 1;
        pcVar4 = s__s_watchdog_4005_08000d60;
      }
      else if (uVar6 == 0xd2) {
        if (param_2 < 2) {
          return;
        }
        bVar2 = param_1[1];
        *_DAT_08000c78 = bVar2 != 0;
        if (cVar1 != '\0') {
          return;
        }
        if (bVar2 != 0) {
          pcVar5 = s_Disable_08000c93;
        }
        else {
          pcVar5 = s_Enable_08000c6f;
        }
        pcVar5 = pcVar5 + 1;
        pcVar4 = s__s_one_side_charging_08000db8;
      }
      else {
        if (uVar6 != 0xd3) {
          return;
        }
        if (cVar1 != '\0') {
          return;
        }
        if (*_DAT_08000c78 == '\0') {
          pcVar5 = s_enabled_08000dd0;
        }
        else {
          pcVar5 = s_disabled_08000c7b + 1;
        }
        pcVar4 = s_One_side_charging___s_08000dd8;
      }
    }
    else {
      if (uVar6 == 0xdd) {
        *(bool *)_DAT_08000d04 = param_1[1] != 0;
        return;
      }
      if (uVar6 != 0xdf) {
        if (uVar6 != 0xee) {
          if (uVar6 != 0xff) {
            return;
          }
          if (cVar1 == '\0') {
            g2_log_printf(s__Reset__reason__cmd__08000d4b + 1);
            g2_log_printf(&DAT_08000cac);
          }
          NVIC_SystemReset();
          return;
        }
        if (*(char *)(_DAT_08000c6c + 3) == '\0') {
          if (cVar1 == '\0') {
            g2_log_printf(s_Standby__reason__cmd__08000d28);
            g2_log_printf(&DAT_08000cac);
          }
          peripheral_transaction_guard(0x10,auStack_30,1);
          peripheral_transaction_guard(0x11,auStack_30,1);
          glasses_channel_command_pack(0);
          peripheral_mode_write_retry(0);
          HAL_PWR_DisableWakeUpPin(0x2b);
          HAL_PWR_EnableWakeUpPin(DAT_08000d40);
          *(undefined4 *)(_DAT_08000d48 + 0x18) = DAT_08000d44;
          HAL_PWR_EnterSTANDBYMode();
          return;
        }
        if (cVar1 != '\0') {
          return;
        }
        g2_log_printf(s_usb_in__cannot_enter_shipmode__08000d07 + 1);
        goto LAB_080009f4;
      }
      if (param_2 < 2) {
        return;
      }
      bVar2 = param_1[1];
      *(bool *)_DAT_08000e0c = bVar2 != 0;
      if (cVar1 != '\0') {
        return;
      }
      if (bVar2 != 0) {
        pcVar5 = s_Enable_08000c6f;
      }
      else {
        pcVar5 = s_Disable_08000c93;
      }
      pcVar5 = pcVar5 + 1;
      pcVar4 = s__s_dog_feed_08000e0f + 1;
    }
  }
  g2_log_printf(pcVar4,pcVar5);
LAB_080009f4:
  g2_log_printf(&DAT_08000cac);
  return;
}

