
int FUN_0059b6d0(int param_1,int param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = FUN_0059b6a0();
  iVar2 = param_1;
  if (iVar1 != 0) {
    iVar2 = param_1 + -1;
  }
  iVar1 = (param_2 << 3) / ((iVar2 + 1) * 10);
  if (param_1 < 6) {
    iVar3 = 0xff;
  }
  else {
    iVar3 = 0xb5;
  }
  if (0x73 < iVar1) {
    iVar1 = 0x73;
  }
  iVar2 = iVar1 + iVar2 * 5 + 0x6e;
  if (iVar3 < iVar2) {
    iVar2 = iVar3;
  }
  return iVar2;
}

