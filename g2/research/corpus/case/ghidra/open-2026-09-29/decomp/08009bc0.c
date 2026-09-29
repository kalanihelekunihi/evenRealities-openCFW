
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_08009bc0(void)

{
  int iVar1;
  int iVar2;
  byte *pbVar3;
  
  iVar2 = FUN_08001408();
  iVar1 = _DAT_08009c44;
  pbVar3 = (byte *)(_DAT_08009c44 + -0x3c);
  if (iVar2 == 0) {
    *pbVar3 = *pbVar3 + 1;
    if (*(char *)(iVar1 + -0x35) == '\0') {
      g2_log_printf(s_Cannot_get_aging_status__err_cnt_08009c74);
      g2_log_printf(&DAT_08009c70);
    }
  }
  else {
    *pbVar3 = 0;
    if (*(char *)(iVar1 + -0x35) == '\0') {
      g2_log_printf(s_Get_aging_status_success__L__d__R_08009c47 + 1,*(undefined1 *)(iVar1 + 2),
                    *(undefined1 *)(iVar1 + 3));
      g2_log_printf(&DAT_08009c70);
    }
    if ((*(char *)(iVar1 + 2) == '\0') || (*(char *)(iVar1 + 3) == '\0')) {
      *pbVar3 = 10;
      goto LAB_08009c1c;
    }
  }
  if (*pbVar3 < 10) {
    return;
  }
LAB_08009c1c:
  *(undefined1 *)(iVar1 + 6) = 2;
  *(undefined1 *)(_DAT_08009c9c + 2) = 4;
  osEventFlagsSet(*(undefined4 *)(iVar1 + -4),4);
  if (*(char *)(iVar1 + -0x35) == '\0') {
    g2_log_printf(s__AGING_ERROR__Get_Aging_Status_E_08009c9f + 1);
    g2_log_printf(&DAT_08009c70);
  }
  return;
}

