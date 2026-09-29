
undefined4 DRV_IMUAccelConfig(int param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  
  if (param_1 - 100U < 0x1325) {
    *DAT_004a5ecc = param_1;
    iVar3 = param_1;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      iVar3 = 0x489;
      param_2 = DAT_004a5ed0;
      param_3 = param_1;
      FUN_0043d574(2,DAT_004a5378,DAT_004a5374,DAT_004a5ed4,0x489,DAT_004a5ed0,param_1,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_004a5ef0,DAT_004a5ef0,param_1,iVar3,param_2,param_3);
    }
    uVar1 = 0;
  }
  else {
    uVar1 = 0xffffffff;
  }
  return uVar1;
}

