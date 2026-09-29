
int bq27427_soft_reset(void)

{
  int iVar1;
  int iVar2;
  undefined4 in_r3;
  
  iVar1 = bq27427_cfgupdate_priv(0);
  if (iVar1 != 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0053bce0,DAT_0053bcdc,DAT_0053c210,0x1f5,DAT_0053c20c,iVar1,in_r3);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_0053c214,DAT_0053c214,iVar1);
    }
  }
  return iVar1;
}

