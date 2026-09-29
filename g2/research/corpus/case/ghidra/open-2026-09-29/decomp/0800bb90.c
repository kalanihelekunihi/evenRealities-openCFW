
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void g2_timer_callback_5(void)

{
  char cVar1;
  char cVar2;
  char cVar3;
  bool bVar4;
  char *pcVar5;
  int iVar6;
  char *pcVar7;
  byte bVar8;
  
  iVar6 = _DAT_0800bd0c;
  pcVar5 = DAT_0800bd08;
  cVar1 = *(char *)(_DAT_0800bd0c + 7);
  if (DAT_0800bd08[0x10] == '\0') {
    if (DAT_0800bd08[0x11] == '\0') {
      if (cVar1 == '\0') {
        g2_log_printf(s_L___R_GLS_OUT__confirmed__show_l_0800bdf8);
        g2_log_printf(&DAT_0800bd40);
      }
      pcVar5[0x14] = '\0';
      if (3 < (byte)pcVar5[2]) {
        return;
      }
      if (pcVar5[2] == 3) {
        osTimerStop(*(undefined4 *)(iVar6 + 0x18));
      }
      glasses_charge_side_select(1);
      pcVar5[2] = '\x02';
LAB_0800bcda:
      osTimerStart(*(undefined4 *)(iVar6 + 0x10),DAT_0800be20);
      return;
    }
    if (cVar1 != '\0') goto LAB_0800bcec;
    pcVar7 = s_L_OUT__R_IN__confirmed__show_err_0800be24;
  }
  else if (DAT_0800bd08[0x11] == '\0') {
    if (cVar1 != '\0') goto LAB_0800bcec;
    pcVar7 = s_L_IN__R_OUT__confirmed__show_err_0800be4c;
  }
  else {
    cVar2 = DAT_0800bd08[0x34];
    if ((cVar2 == '\0') || (bVar4 = false, DAT_0800bd08[0x30] != '\0')) {
      bVar4 = true;
    }
    cVar3 = DAT_0800bd08[0x50];
    if ((cVar3 == '\0') || (DAT_0800bd08[0x4c] != '\0')) {
      bVar8 = 1;
    }
    else {
      bVar8 = 0;
    }
    if ((bool)(bVar4 & bVar8)) {
      if ((cVar2 != '\0') || (*(uint *)(DAT_0800bd08 + 0x44) < 0xd2)) {
        if ((cVar3 != '\0') || (*(uint *)(DAT_0800bd08 + 0x60) < 0xd2)) {
          if (*DAT_0800bd08 == '\x03') {
            *DAT_0800bd08 = '\0';
            if (cVar1 == '\0') {
              g2_log_printf(s_L___R_GLS_IN__RTC_wake_up__keep_s_0800bd74);
              g2_log_printf(&DAT_0800bd40);
            }
            pcVar5[0x14] = '\x02';
            return;
          }
          if (cVar1 == '\0') {
            g2_log_printf(DAT_0800bd9c,cVar2,DAT_0800bd08[0x30],cVar3,DAT_0800bd08[0x4c]);
            g2_log_printf(&DAT_0800bd40);
          }
          *(undefined1 *)(iVar6 + 1) = 0;
          pcVar5[0x14] = '\x02';
          if (3 < (byte)pcVar5[2]) {
            return;
          }
          pcVar5[2] = '\x02';
          glasses_charge_side_select(1);
          goto LAB_0800bcda;
        }
        if (cVar2 != '\0') {
          if (cVar1 == '\0') {
            g2_log_printf(s_No_reply_from_GLS_R_for_210s__sh_0800bd44);
            g2_log_printf(&DAT_0800bd40);
          }
          pcVar5[0x4d] = '\x01';
          pcVar5[0x4f] = '\x01';
          goto LAB_0800bcec;
        }
      }
      if (cVar1 == '\0') {
        g2_log_printf(s_No_reply_from_GLS_L_for_210s__sh_0800bd0f + 1);
        g2_log_printf(&DAT_0800bd40);
      }
      pcVar5[0x31] = '\x01';
      pcVar5[0x33] = '\x01';
      goto LAB_0800bcec;
    }
    if (bVar4) {
      if (cVar1 != '\0') goto LAB_0800bcec;
      pcVar7 = s_R_charging_not_confirmed__show_e_0800bdcc;
    }
    else {
      if (cVar1 != '\0') goto LAB_0800bcec;
      pcVar7 = s_L_charging_not_confirmed__show_e_0800bda0;
    }
  }
  g2_log_printf(pcVar7);
  g2_log_printf(&DAT_0800bd40);
LAB_0800bcec:
  pcVar5[0x14] = '\x01';
  if (3 < (byte)pcVar5[2]) {
    return;
  }
  pcVar5[2] = '\x03';
  osEventFlagsSet(*(undefined4 *)(iVar6 + 0x38),4);
  return;
}

