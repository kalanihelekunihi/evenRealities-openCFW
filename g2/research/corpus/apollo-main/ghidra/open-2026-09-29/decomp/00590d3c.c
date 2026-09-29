
undefined4 FUN_00590d3c(int param_1,int param_2)

{
  bool bVar1;
  
  if (param_1 == 0x9c4) {
    return 0;
  }
  if (param_1 != 5000) {
    bVar1 = param_2 == 0;
    if (bVar1) {
      param_2 = 0x1d4c;
    }
    if (!bVar1 || param_1 != param_2) {
      if (param_1 != 10000) {
        return 4;
      }
      return 3;
    }
    return 2;
  }
  return 1;
}

