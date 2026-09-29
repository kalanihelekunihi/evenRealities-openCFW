
uint FUN_005d8c00(uint *param_1,uint param_2)

{
  uint uVar1;
  
  if (param_2 < *param_1) {
    uVar1 = (uint)*(byte *)(param_1[2] + ((int)param_2 >> 3)) & 0x80 >> (param_2 & 7);
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

