
undefined4 hw_error_classify_42c076(int param_1,uint param_2)

{
  undefined4 uVar1;
  
  param_2 = param_2 | *(uint *)(DAT_0042c6e8 + param_1 * 0x1000 + 0x204);
  if ((param_2 & 0x6c) == 0) {
    uVar1 = DAT_0042c6ec;
    if (((-1 < (int)(param_2 << 0x16)) && (uVar1 = DAT_0042c6f0, -1 < (int)(param_2 << 0x1b))) &&
       (uVar1 = 0, (param_2 & 0x4800) != 0)) {
      uVar1 = 1;
    }
  }
  else {
    uVar1 = 0x8000000;
  }
  return uVar1;
}

