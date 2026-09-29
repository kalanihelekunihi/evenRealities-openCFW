
undefined8 APP_BleSlaveAsCmdRole(uint param_1,undefined4 param_2)

{
  int *piVar1;
  undefined1 uVar2;
  byte bVar3;
  int iVar4;
  
  piVar1 = DAT_0046f41c;
  *(char *)(*DAT_0046f41c + 0x1f) = (char)param_1;
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    uVar2 = FUN_0045a568();
    param_1 = 0x30f;
    param_2 = DAT_0046f46c;
    FUN_0043d574(4,DAT_0046f404,DAT_0046f400,DAT_0046f470,0x30f,DAT_0046f46c,
                 *(undefined1 *)(*piVar1 + 0x1f),uVar2);
  }
  iVar4 = FUN_0043d0ce();
  if (-1 < iVar4 << 0x1f) {
    iVar4 = FUN_0043d0ce();
    if (-1 < iVar4 << 0x1d) goto LAB_0046f1c0;
  }
  bVar3 = FUN_0045a568();
  param_1 = (uint)bVar3;
  compress_log_output(0x10800000,DAT_0046f474,DAT_0046f474,*(undefined1 *)(*piVar1 + 0x1f));
LAB_0046f1c0:
  return CONCAT44(param_2,param_1);
}

