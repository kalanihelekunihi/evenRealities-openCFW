
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void g2_timer_callback_3(void)

{
  char cVar1;
  int iVar2;
  int iVar3;
  char *pcVar4;
  undefined4 uVar5;
  
  iVar3 = _DAT_08009838;
  iVar2 = DAT_08009834;
  if (*(char *)(DAT_08009834 + 6) != '\x01') {
    return;
  }
  *(int *)(DAT_08009834 + 0xc) = *(int *)(DAT_08009834 + 0xc) + 5;
  cVar1 = *(char *)(iVar2 + 7);
  if (cVar1 == '\x01') {
    FUN_08009bc0();
    if ((((DAT_080098b4 < *(ushort *)(iVar3 + 0x36)) && (0x28 < *(byte *)(iVar3 + 0x32))) &&
        (DAT_080098b4 < *(ushort *)(iVar3 + 0x52))) &&
       ((0x28 < *(byte *)(iVar3 + 0x4e) && (*(char *)(iVar2 + -0x32) == '\0')))) {
      *(undefined1 *)(iVar2 + -0x3a) = 0;
    }
    else {
      if (*(byte *)(iVar2 + -0x3a) < 2) {
        *(byte *)(iVar2 + -0x3a) = *(byte *)(iVar2 + -0x3a) + 1;
        if (*(char *)(iVar2 + -0x35) != '\0') goto LAB_080097c8;
        g2_log_printf(s__AGING_RUNNING___GLS_bat_low__de_080098b8);
      }
      else {
        *(undefined1 *)(iVar2 + -0x3a) = 0;
        *(undefined1 *)(iVar2 + 7) = 2;
        *(undefined1 *)(iVar3 + 0x15) = 1;
        aging_indicator_apply();
        *(undefined1 *)(iVar3 + 0x10) = 0;
        *(undefined1 *)(iVar3 + 0x11) = 0;
        if (*(char *)(iVar2 + -0x35) != '\0') goto LAB_080097c8;
        g2_log_printf(s__AGING_RUNNING___GLS_bat_low__go_080098f8);
      }
      g2_log_printf(&DAT_0800992c);
    }
    if (*(char *)(iVar2 + -0x35) != '\0') goto LAB_080097c8;
    pcVar4 = s__AGING_RUNNING___AGING_ONLY__tim_08009930;
    uVar5 = *(undefined4 *)(iVar2 + 0xc);
LAB_080097be:
    g2_log_printf(pcVar4,uVar5);
  }
  else {
    if (cVar1 == '\x02') {
      FUN_08009bc0();
      if (((*(char *)(iVar3 + 0x31) != '\0') && (*(char *)(iVar3 + 0x4d) != '\0')) ||
         (*(char *)(iVar2 + -0x33) != '\0')) {
        *(undefined1 *)(iVar2 + 7) = 1;
        *(undefined1 *)(iVar2 + -0x3a) = 0;
        *(undefined1 *)(iVar3 + 0x15) = 0;
        aging_indicator_apply();
        *(undefined1 *)(iVar3 + 0x10) = 0;
        *(undefined1 *)(iVar3 + 0x11) = 0;
        if (*(char *)(iVar2 + -0x35) != '\0') goto LAB_080097c8;
        g2_log_printf(s__AGING_RUNNING___GLS_charge_done_08009958);
        g2_log_printf(&DAT_0800992c);
      }
      if (*(char *)(iVar2 + -0x35) != '\0') goto LAB_080097c8;
      pcVar4 = s__AGING_RUNNING___CHARGING_AGING__0800998c;
      uVar5 = *(undefined4 *)(iVar2 + 0xc);
      goto LAB_080097be;
    }
    if (cVar1 != '\x04') goto LAB_080097c8;
    FUN_08009cc8();
    if ((*(char *)(iVar3 + 0x10) == '\0') || (*(char *)(iVar3 + 0x11) == '\0')) {
      if (*(char *)(iVar2 + -0x35) != '\0') goto LAB_080097c8;
      g2_log_printf(s__AGING_RUNNING___GLS_not_inbox___0800987c,*(char *)(iVar3 + 0x10),
                    *(undefined1 *)(iVar3 + 0x11));
    }
    else {
      if (*(char *)(iVar2 + 4) != '\0') goto LAB_080097c8;
      *(undefined1 *)(iVar3 + 0x15) = 0;
      aging_indicator_apply();
      *(undefined1 *)(iVar3 + 0x10) = 0;
      *(undefined1 *)(iVar3 + 0x11) = 0;
      *(undefined1 *)(iVar2 + 4) = 1;
      *(undefined1 *)(iVar2 + 5) = 0;
      if (*(char *)(iVar2 + -0x35) != '\0') goto LAB_080097c8;
      g2_log_printf(s__AGING_RUNNING___GLS_ready__disa_0800983b + 1);
    }
  }
  g2_log_printf(&DAT_0800992c);
LAB_080097c8:
  if ((*(uint *)(iVar2 + 0xc) + *(uint *)(iVar2 + 8) < 0x3840) && (*(char *)(iVar2 + -0x31) == '\0')
     ) {
    if ((0x1c1f < *(uint *)(iVar2 + 8)) && (0x3b < *(uint *)(iVar2 + 0xc))) {
      *(undefined1 *)(iVar2 + 6) = 2;
      *(undefined1 *)(iVar3 + 2) = 4;
      osEventFlagsSet(*(undefined4 *)(iVar2 + -4),4);
      if (*(char *)(iVar2 + -0x35) == '\0') {
        g2_log_printf(DAT_080099e4);
        g2_log_printf(&DAT_0800992c);
        return;
      }
    }
  }
  else {
    if (*(char *)(iVar2 + -0x35) == '\0') {
      g2_log_printf(s__AGING_RUNNING___Timeout__go_to_A_080099b8);
      g2_log_printf(&DAT_0800992c);
    }
    *(undefined1 *)(iVar2 + 6) = 3;
    *(undefined1 *)(iVar3 + 2) = 4;
    case_gpio_pa6_write(0);
    case_gpio_pa7_write(1);
  }
  return;
}

