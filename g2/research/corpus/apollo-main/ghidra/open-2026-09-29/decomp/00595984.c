
uint FUN_00595984(int param_1,undefined4 param_2,uint param_3)

{
  bool bVar1;
  
  bVar1 = 5 < param_1 - 0x61U;
  if (bVar1) {
    param_3 = param_1 - 0x41;
  }
  if (!bVar1 || param_3 < 6) {
    return 1;
  }
  return -(uint)(param_1 - 0x30U < 10) >> 0x1f;
}

