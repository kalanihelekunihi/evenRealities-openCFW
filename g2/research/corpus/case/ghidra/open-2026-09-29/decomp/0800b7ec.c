
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void g2_timer_callback_4(void)

{
  char cVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  char *pcVar5;
  undefined4 in_r3;
  
  iVar3 = _DAT_0800b944;
  if (((*(char *)(_DAT_0800b944 + 7) == '\x04') && (*(char *)(_DAT_0800b944 + 4) != '\0')) &&
     (*(byte *)(_DAT_0800b944 + 5) < 3)) {
    *(byte *)(_DAT_0800b944 + 5) = *(byte *)(_DAT_0800b944 + 5) + 1;
    if (*(char *)(iVar3 + 2) == '\0') {
      aging_status_set_left(1);
    }
    if (*(char *)(iVar3 + 3) == '\0') {
      aging_status_set_right(1);
    }
    if (*(char *)(iVar3 + -0x35) == '\0') {
      g2_log_printf(s__AGING_RUNNING___Try_to_enter_ag_0800b947 + 1,*(undefined1 *)(iVar3 + 2),
                    *(undefined1 *)(iVar3 + 3),*(undefined1 *)(iVar3 + 5),in_r3);
      g2_log_printf(&DAT_0800b988);
    }
    if ((*(char *)(iVar3 + 2) == '\0') || (*(char *)(iVar3 + 3) == '\0')) {
      if (*(char *)(iVar3 + 5) != '\x03') goto LAB_0800b85e;
      *(undefined1 *)(iVar3 + 7) = 1;
      *(undefined1 *)(iVar3 + -0x3a) = 0;
      cVar1 = *(char *)(iVar3 + -0x35);
      uVar2 = DAT_0800b990;
    }
    else {
      *(undefined1 *)(iVar3 + 7) = 1;
      *(undefined1 *)(iVar3 + -0x3a) = 0;
      cVar1 = *(char *)(iVar3 + -0x35);
      uVar2 = DAT_0800b98c;
    }
    if (cVar1 == '\0') {
      g2_log_printf(uVar2);
      g2_log_printf(&DAT_0800b988);
    }
  }
  else {
LAB_0800b85e:
    cVar1 = *(char *)(iVar3 + 6);
    if ((cVar1 == '\x02') || (cVar1 == '\x03')) {
      if ((*(char *)(iVar3 + 2) == '\0') && (*(char *)(iVar3 + 3) == '\0')) {
        if (cVar1 == '\x03') {
          if (*(char *)(iVar3 + -0x35) == '\0') {
            g2_log_printf(s__AGING_NOT__Aging_done__and_GLS_a_0800ba04);
            g2_log_printf(&DAT_0800b988);
          }
          NVIC_SystemReset();
        }
      }
      else {
        if (*(char *)(iVar3 + -0x35) == '\0') {
          if (cVar1 == '\x02') {
            pcVar5 = s_AGING_ERROR_0800b9a8;
          }
          else {
            pcVar5 = s_AGING_DONE_0800b994;
          }
          g2_log_printf(&DAT_0800b9a0,pcVar5);
          if (*(char *)(iVar3 + -0x35) == '\0') {
            g2_log_printf(s_Stop_gls_aging__glsAgingL__d__gl_0800b9b4,*(undefined1 *)(iVar3 + 2),
                          *(undefined1 *)(iVar3 + 3));
            g2_log_printf(&DAT_0800b988);
          }
        }
        iVar4 = _DAT_0800b9e0;
        if (*(char *)(_DAT_0800b9e0 + 0x15) == '\0') {
          *(undefined1 *)(_DAT_0800b9e0 + 0x15) = 1;
          aging_indicator_apply();
          *(undefined1 *)(iVar4 + 0x10) = 0;
          *(undefined1 *)(iVar4 + 0x11) = 0;
          if (*(char *)(iVar3 + -0x35) != '\0') {
            return;
          }
          if (*(char *)(iVar3 + 6) == '\x02') {
            pcVar5 = s_AGING_ERROR_0800b9a8;
          }
          else {
            pcVar5 = s_AGING_DONE_0800b994;
          }
          g2_log_printf(&DAT_0800b9a0,pcVar5);
          if (*(char *)(iVar3 + -0x35) == '\0') {
            g2_log_printf(s_Enable_GLS_charging_by_default__0800b9e3 + 1);
            g2_log_printf(&DAT_0800b988);
          }
        }
      }
      iVar4 = _DAT_0800b9e0;
      if ((*(char *)(_DAT_0800b9e0 + 0x10) != '\0') && (*(char *)(iVar3 + 2) != '\0')) {
        aging_status_set_left(0);
      }
      if ((*(char *)(iVar4 + 0x11) != '\0') && (*(char *)(iVar3 + 3) != '\0')) {
        aging_status_set_right(0);
        return;
      }
    }
  }
  return;
}

