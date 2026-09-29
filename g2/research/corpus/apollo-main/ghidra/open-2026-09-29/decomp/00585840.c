
uint FUN_00585840(uint param_1,byte *param_2,int param_3)

{
  param_1 = param_1 ^ 0xffffffff;
  while (param_3 != 0) {
    param_1 = *(uint *)(DAT_00585984 + ((*param_2 ^ param_1) & 0xff) * 4) ^ param_1 >> 8;
    param_2 = param_2 + 1;
    param_3 = param_3 + -1;
  }
  return param_1 ^ 0xffffffff;
}

