
undefined8 FUN_00416b4e(int param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  if ((param_2 & param_2 - 1) != 0) {
    FUN_00415734(DAT_0041728c,DAT_00417200,0x1d7);
  }
  return CONCAT44(param_4,(param_2 + param_1) - 1 & ~(param_2 - 1));
}

