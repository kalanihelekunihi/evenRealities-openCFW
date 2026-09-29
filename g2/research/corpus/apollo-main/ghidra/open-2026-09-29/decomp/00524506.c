
int FT_MSB(uint param_1)

{
  int iVar1;
  
  iVar1 = 0;
  if ((param_1 & 0xffff0000) != 0) {
    param_1 = param_1 >> 0x10;
    iVar1 = 0x10;
  }
  if ((param_1 & 0xff00) != 0) {
    param_1 = param_1 >> 8;
    iVar1 = iVar1 + 8;
  }
  if ((param_1 & 0xf0) != 0) {
    param_1 = param_1 >> 4;
    iVar1 = iVar1 + 4;
  }
  if ((param_1 & 0xc) != 0) {
    param_1 = param_1 >> 2;
    iVar1 = iVar1 + 2;
  }
  if ((int)(param_1 << 0x1e) < 0) {
    iVar1 = iVar1 + 1;
  }
  return iVar1;
}

