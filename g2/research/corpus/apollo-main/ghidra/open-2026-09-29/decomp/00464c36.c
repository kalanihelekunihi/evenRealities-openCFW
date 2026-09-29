
void FUN_00464c36(undefined2 param_1,undefined4 param_2,undefined2 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = param_4;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004651b8,DAT_004651b4,DAT_00465730,0x7f,DAT_0046572c,param_1,param_3,uVar2);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10800000,DAT_00465734,DAT_00465734,param_1,param_3);
  }
  FUN_00464772(param_1,param_2,param_3,param_4,5,2,0);
  return;
}

