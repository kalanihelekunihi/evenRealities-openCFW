
int FUN_0041ba80(byte param_1)

{
  int iVar1;
  
  if ((param_1 == 1) || (param_1 == 2)) {
    if ((param_1 == 2) && ((*DAT_0041c488 & 0x3f) >> 4 != 3)) {
      iVar1 = 7;
    }
    else if (param_1 == *DAT_0041c484) {
      iVar1 = 0;
    }
    else {
      iVar1 = FUN_0041b954(param_1);
      if (iVar1 == 0) {
        if ((*DAT_0041c480 & 0x1f) >> 3 == (uint)param_1) {
          iVar1 = 0;
        }
        else {
          iVar1 = 1;
        }
      }
    }
  }
  else {
    iVar1 = 6;
  }
  return iVar1;
}

