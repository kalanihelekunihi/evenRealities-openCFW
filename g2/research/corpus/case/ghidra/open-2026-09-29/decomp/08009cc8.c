
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_08009cc8(void)

{
  int iVar1;
  byte *pbVar2;
  
  pbVar2 = _DAT_08009d2c;
  iVar1 = DAT_08009d28;
  if ((*(char *)(DAT_08009d28 + 0x10) == '\0') || (*(char *)(DAT_08009d28 + 0x11) == '\0')) {
    *_DAT_08009d2c = *_DAT_08009d2c + 1;
    if (pbVar2[7] == 0) {
      g2_log_printf(s_Gls_not_inbox__err_cnt___d_08009d2f + 1);
      g2_log_printf(&DAT_08009d4c);
    }
    if (9 < *pbVar2) {
      _DAT_08009d2c[0x42] = 2;
      *(undefined1 *)(iVar1 + 2) = 4;
      osEventFlagsSet(*(undefined4 *)(pbVar2 + 0x38),4);
      if (pbVar2[7] == 0) {
        g2_log_printf(s__AGING_ERROR__Not_Inbox_Error_08009d50);
        g2_log_printf(&DAT_08009d4c);
        return;
      }
    }
  }
  else {
    *_DAT_08009d2c = 0;
  }
  return;
}

