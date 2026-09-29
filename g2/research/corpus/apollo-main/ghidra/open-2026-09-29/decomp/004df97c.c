
int FUN_004df97c(int param_1,int param_2)

{
  int iVar1;
  
  if (param_1 == 0) {
    param_1 = 1;
  }
  if (100 < param_2) {
    param_1 = param_1 << 1;
  }
  if (param_1 < 0x1c) {
    iVar1 = 0x1c;
  }
  else {
    iVar1 = ((param_1 + 0x1b) / 0x1c) * 0x1c;
  }
  return iVar1;
}

