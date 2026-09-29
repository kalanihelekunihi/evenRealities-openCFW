
undefined4 FUN_0800b024(int param_1,uint param_2,uint param_3,uint param_4)

{
  undefined4 uVar1;
  
  uVar1 = 0;
  *(uint *)(param_1 + 4) = param_2;
  *(int *)(param_1 + 0x10) = param_1;
  if (param_3 < param_2) {
    if ((param_3 < param_4) && (param_4 <= param_2)) {
      uVar1 = 1;
    }
    else {
      FUN_0800bfb0(*(undefined4 *)(DAT_0800b060 + 0xc),param_1 + 4);
    }
  }
  else if (param_3 - param_4 < *(uint *)(param_1 + 0x18)) {
    FUN_0800bfb0(*(undefined4 *)(DAT_0800b060 + 0x10),param_1 + 4);
  }
  else {
    uVar1 = 1;
  }
  return uVar1;
}

