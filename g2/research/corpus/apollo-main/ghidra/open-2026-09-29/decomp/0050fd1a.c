
undefined4 FUN_0050fd1a(uint param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  
  iVar2 = DAT_0050fe9c;
  if ((*DAT_0050fe7c == '\0') || (3 < (param_1 & 0xff))) {
    uVar1 = 0xffffffff;
  }
  else if (*(int *)(DAT_0050fe9c + (param_1 & 0xff) * 4) == 0) {
    uVar5 = param_1;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_3 = param_1 & 0xff;
      uVar5 = 0x13b;
      param_2 = DAT_0050fee4;
      FUN_0043d574(1,DAT_0050febc,DAT_0050feb8,DAT_0050fee8,0x13b,DAT_0050fee4,param_3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_0050feec,DAT_0050feec,param_1 & 0xff,uVar5,param_2,param_3);
    }
    uVar1 = 0xffffffff;
  }
  else {
    FUN_0050fe0e();
    iVar3 = FUN_00463e9a(*(undefined4 *)(iVar2 + (param_1 & 0xff) * 4));
    if ((iVar3 != 0) && (iVar4 = FUN_0043e2ea(iVar3), iVar4 != 0)) {
      FUN_0043dfa4(iVar3,1);
    }
    FUN_00463ea6(*(undefined4 *)(iVar2 + (param_1 & 0xff) * 4));
    *DAT_0050feac = (char)param_1;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0050febc,DAT_0050feb8,DAT_0050fee8,0x154,DAT_0050fef0,param_1 & 0xff);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_0050fef4,DAT_0050fef4,param_1 & 0xff);
    }
    uVar1 = 0;
  }
  return uVar1;
}

