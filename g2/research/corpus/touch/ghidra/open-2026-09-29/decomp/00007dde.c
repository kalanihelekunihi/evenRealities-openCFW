
undefined4 touch_sub_4ade(uint param_1,int param_2)

{
  undefined4 uVar1;
  
  if (param_1 < 3) {
    if ((*(byte *)(*(int *)(param_2 + 0x10) + param_1 * 0x3c + 0x23) & 6) == 6) {
      uVar1 = 1;
    }
    else {
      uVar1 = 0;
    }
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

