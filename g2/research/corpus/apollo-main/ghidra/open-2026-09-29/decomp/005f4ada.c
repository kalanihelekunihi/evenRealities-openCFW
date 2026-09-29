
uint Round_Down_To_Grid(undefined4 param_1,int param_2,int param_3)

{
  uint uVar1;
  
  if (param_2 < 0) {
    uVar1 = -(param_3 - param_2 & 0xffffffc0U);
    if (0 < (int)uVar1) {
      uVar1 = 0;
    }
  }
  else {
    uVar1 = param_3 + param_2 & 0xffffffc0;
    if ((int)uVar1 < 0) {
      uVar1 = 0;
    }
  }
  return uVar1;
}

