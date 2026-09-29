
int Round_To_Half_Grid(undefined4 param_1,int param_2,int param_3)

{
  int iVar1;
  
  if (param_2 < 0) {
    iVar1 = -((param_3 - param_2 & 0xffffffc0U) + 0x20);
    if (0 < iVar1) {
      iVar1 = -0x20;
    }
  }
  else {
    iVar1 = (param_3 + param_2 & 0xffffffc0U) + 0x20;
    if (iVar1 < 0) {
      iVar1 = 0x20;
    }
  }
  return iVar1;
}

