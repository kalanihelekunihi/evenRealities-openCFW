
undefined8 FUN_004cfd18(uint param_1)

{
  int iVar1;
  
  iVar1 = 0x20;
  if (param_1 == 0) {
    iVar1 = 0x1f;
  }
  if ((param_1 & 0xffff0000) == 0) {
    param_1 = param_1 << 0x10;
    iVar1 = iVar1 + -0x10;
  }
  if ((param_1 & 0xff000000) == 0) {
    param_1 = param_1 << 8;
    iVar1 = iVar1 + -8;
  }
  if ((param_1 & 0xf0000000) == 0) {
    param_1 = param_1 << 4;
    iVar1 = iVar1 + -4;
  }
  if ((param_1 & 0xc0000000) == 0) {
    param_1 = param_1 << 2;
    iVar1 = iVar1 + -2;
  }
  if (-1 < (int)param_1) {
    param_1 = param_1 << 1;
    iVar1 = iVar1 + -1;
  }
  return CONCAT44(param_1,iVar1);
}

