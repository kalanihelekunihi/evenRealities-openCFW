
uint FUN_0058fcf0(uint param_1,int param_2,byte *param_3)

{
  for (; param_2 != 0; param_2 = param_2 + -1) {
    param_1 = *(uint *)(DAT_0058fd18 + ((uint)*param_3 ^ param_1 & 0xff) * 4) ^ param_1 >> 8;
    param_3 = param_3 + 1;
  }
  return param_1 ^ 0xffffffff;
}

