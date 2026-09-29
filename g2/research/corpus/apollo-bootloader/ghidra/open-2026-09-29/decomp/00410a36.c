
undefined8 FUN_00410a36(int param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  if (*(uint *)(param_1 + 0x6c) <= param_2) {
    FUN_00415734(DAT_00411668,DAT_0041129c,0x114);
  }
  iVar1 = (**(code **)(*(int *)(param_1 + 0x68) + 0xc))(*(undefined4 *)(param_1 + 0x68),param_2);
  if (0 < iVar1) {
    FUN_00415734(DAT_004112a4,DAT_0041129c,0x116);
  }
  return CONCAT44(param_4,iVar1);
}

