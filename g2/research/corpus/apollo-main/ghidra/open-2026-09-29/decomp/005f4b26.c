
uint Round_To_Double_Grid(undefined4 param_1,int param_2,int param_3)

{
  uint uVar1;
  
  if (param_2 < 0) {
    uVar1 = -((param_3 - param_2) + 0x10U & 0xffffffe0);
    if (0 < (int)uVar1) {
      uVar1 = 0;
    }
  }
  else {
    uVar1 = param_3 + param_2 + 0x10U & 0xffffffe0;
    if ((int)uVar1 < 0) {
      uVar1 = 0;
    }
  }
  return uVar1;
}

