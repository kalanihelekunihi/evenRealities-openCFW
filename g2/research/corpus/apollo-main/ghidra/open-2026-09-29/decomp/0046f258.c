
bool APP_IsLeftSlaveRole(void)

{
  undefined1 uVar1;
  int iVar2;
  
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    uVar1 = FUN_0045a568();
    FUN_0043d574(4,DAT_0046f404,DAT_0046f400,DAT_0046f480,0x31b,DAT_0046f47c,
                 *(undefined1 *)(*DAT_0046f41c + 0x1f),uVar1);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    uVar1 = FUN_0045a568();
    compress_log_output(0x10800000,DAT_0046f484,DAT_0046f484,*(undefined1 *)(*DAT_0046f41c + 0x1f),
                        uVar1);
  }
  iVar2 = FUN_0045a568();
  return iVar2 == 2;
}

