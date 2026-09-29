
int FUN_005eb438(int param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  if ((param_1 == 0) || (*(int *)(param_1 + 0x214) == 0)) {
    iVar3 = 0;
  }
  else {
    iVar1 = FUN_0043fdda(*(undefined4 *)(param_1 + 0x214));
    iVar2 = func_0x005eb2a8(*(undefined4 *)(param_1 + 0x214),0);
    iVar3 = func_0x005eb2b2(*(undefined4 *)(param_1 + 0x214),0);
    iVar3 = (iVar1 - iVar2) - iVar3;
    if (iVar3 < 1) {
      iVar3 = iVar1;
    }
  }
  return iVar3;
}

