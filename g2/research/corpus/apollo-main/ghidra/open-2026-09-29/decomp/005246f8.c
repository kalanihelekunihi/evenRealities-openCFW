
uint FT_MulFix(uint param_1,uint param_2)

{
  uint uVar1;
  int iVar2;
  
  iVar2 = 1;
  if ((int)param_1 < 0) {
    param_1 = -param_1;
    iVar2 = -1;
  }
  if ((int)param_2 < 0) {
    param_2 = -param_2;
    iVar2 = -iVar2;
  }
  if (param_1 + (param_2 >> 8) < 0x1fff) {
    uVar1 = param_2 * param_1 + 0x8000 >> 0x10;
  }
  else {
    uVar1 = param_2 * (param_1 >> 0x10) + (param_2 >> 0x10) * (param_1 & 0xffff) +
            ((param_2 & 0xffff) * (param_1 & 0xffff) + 0x8000 >> 0x10);
  }
  if (iVar2 < 0) {
    uVar1 = -uVar1;
  }
  return uVar1;
}

