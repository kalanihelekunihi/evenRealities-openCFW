
undefined1 APP_IsLocalSlaveAsCmdRole(void)

{
  undefined1 uVar1;
  int iVar2;
  
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    uVar1 = FUN_0045a568();
    FUN_0043d574(4,DAT_0046f404,DAT_0046f400,DAT_0046f478,0x314,DAT_0046f46c,
                 *(undefined1 *)(*DAT_0046f41c + 0x1f),uVar1);
  }
  iVar2 = FUN_0043d0ce();
  if (-1 < iVar2 << 0x1f) {
    iVar2 = FUN_0043d0ce();
    if (-1 < iVar2 << 0x1d) goto LAB_0046f22a;
  }
  uVar1 = FUN_0045a568();
  compress_log_output(0x10800000,DAT_0046f474,DAT_0046f474,*(undefined1 *)(*DAT_0046f41c + 0x1f),
                      uVar1);
LAB_0046f22a:
  iVar2 = FUN_0045a568();
  if ((iVar2 == 1) || (*(char *)(*DAT_0046f41c + 0x1f) == '\0')) {
    uVar1 = 1;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

