
int FUN_00472d76(uint param_1,uint param_2)

{
  uint uVar1;
  int iVar2;
  
  if ((param_2 == 0) && (param_1 == 0)) {
    iVar2 = 1;
  }
  else {
    iVar2 = 0;
  }
  for (; (param_2 != 0 || (param_1 != 0)); param_1 = param_1 >> 4 | uVar1) {
    uVar1 = param_2 << 0x1c;
    param_2 = param_2 >> 4;
    iVar2 = iVar2 + 1;
  }
  return iVar2;
}

