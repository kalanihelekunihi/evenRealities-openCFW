
undefined4 FUN_004e9eb8(int param_1,uint param_2,uint param_3,undefined4 param_4)

{
  ushort *puVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  uint uVar5;
  
  iVar4 = param_1;
  uVar5 = param_2;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_3 = param_2 & 0xffff;
    iVar4 = 0x92;
    uVar5 = DAT_004eac54;
    FUN_0043d574(4,DAT_004ea7f8,DAT_004ea7f4,DAT_004eac58,0x92,DAT_004eac54,param_3,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if (-1 < iVar2 << 0x1f) {
    iVar2 = FUN_0043d0ce();
    if (-1 < iVar2 << 0x1d) goto LAB_004e9f0a;
  }
  compress_log_output(0x10400000,DAT_004eac5c,DAT_004eac5c,param_2 & 0xffff,iVar4,uVar5,param_3);
LAB_004e9f0a:
  puVar1 = DAT_004ea7e8;
  if (param_1 == 0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004ea7f8,DAT_004ea7f4,DAT_004eac58,0x95,DAT_004eacb8);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004eacbc,DAT_004eacbc);
    }
    uVar3 = 0;
  }
  else if ((param_2 & 0xffff) < (uint)*DAT_004ea7e8) {
    FUN_00439be4(param_1,DAT_004ea7e4 + (param_2 & 0xffff) * 0x428,0x428);
    uVar3 = 1;
  }
  else {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004ea7f8,DAT_004ea7f4,DAT_004eac58,0x9a,DAT_004eacf0,param_2 & 0xffff,
                   *puVar1);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x8800000,DAT_004eacf4,DAT_004eacf4,param_2 & 0xffff,*puVar1);
    }
    uVar3 = 0;
  }
  return uVar3;
}

