
undefined4 FUN_00480f8a(uint param_1,byte param_2,uint *param_3)

{
  uint *puVar1;
  
  if (param_2 == 0) {
    puVar1 = (uint *)(DAT_0048174c + ((param_1 & 0xff) >> 5) * 4);
  }
  else if (param_2 == 2) {
    puVar1 = (uint *)(DAT_00481754 + ((param_1 & 0xff) >> 5) * 4);
  }
  else {
    if (1 < param_2) {
      return 6;
    }
    puVar1 = (uint *)(DAT_00481750 + ((param_1 & 0xff) >> 5) * 4);
  }
  *param_3 = *puVar1 >> (param_1 & 0x1f) & 1;
  return 0;
}

