
undefined8 FUN_004108c4(int param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  
  FUN_00410522(param_1,param_3);
  iVar1 = FUN_00410802(param_1,param_2,param_3,param_4 & 0xff);
  if ((iVar1 == 0) &&
     (iVar1 = (**(code **)(*(int *)(param_1 + 0x68) + 0x10))(*(undefined4 *)(param_1 + 0x68)),
     0 < iVar1)) {
    FUN_00415734(DAT_004112a4,DAT_0041129c,0xdd);
  }
  return CONCAT44(param_4,iVar1);
}

