
uint FUN_00416ba4(int param_1,uint param_2)

{
  if ((param_2 & param_2 - 1) != 0) {
    FUN_00415734(DAT_0041728c,DAT_00417200,0x1e5);
  }
  return (param_2 + param_1) - 1 & ~(param_2 - 1);
}

