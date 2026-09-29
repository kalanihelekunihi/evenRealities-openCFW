
undefined8 FUN_004e78aa(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = param_2;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    uVar2 = 0x197;
    param_3 = DAT_004e82e4;
    param_4 = param_2;
    FUN_0043d574(4,DAT_004e7fe8,DAT_004e7fe4,DAT_004e82e8,0x197,DAT_004e82e4,param_2);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_004e8434,DAT_004e8434,param_2,uVar2,param_3,param_4);
  }
  FUN_0043f142(param_1,param_2);
  return CONCAT44(param_3,uVar2);
}

