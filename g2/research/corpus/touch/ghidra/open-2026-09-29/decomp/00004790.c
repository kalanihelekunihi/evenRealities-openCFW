
undefined4 touch_leaf_1490_bounded_sum(undefined4 param_1,int param_2,int param_3)

{
  undefined4 uVar1;
  
  if (param_2 == 0) {
    uVar1 = 0;
  }
  else if ((uint)(param_2 + param_3) < 0x10001) {
    uVar1 = 1;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

