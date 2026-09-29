
void FUN_005d8c1e(uint *param_1,uint param_2)

{
  byte *pbVar1;
  
  if (param_2 < *param_1) {
    pbVar1 = (byte *)(param_1[2] + (param_2 >> 3));
    *pbVar1 = *pbVar1 & ~(0x80U >> (param_2 & 7));
  }
  return;
}

