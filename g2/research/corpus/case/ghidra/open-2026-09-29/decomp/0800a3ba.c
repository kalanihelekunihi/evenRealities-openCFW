
int case_sign_extend_u16(uint param_1)

{
  int iVar1;
  
  if ((int)(param_1 << 0x10) < 0) {
    iVar1 = -1;
    param_1 = -param_1 & 0xffff;
  }
  else {
    iVar1 = 1;
  }
  return iVar1 * param_1;
}

