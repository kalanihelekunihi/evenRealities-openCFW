
void FUN_005d75ee(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar2 = param_1[2];
  for (iVar1 = *param_1; iVar1 != 0; iVar1 = iVar1 + -1) {
    FUN_005d73d0(iVar2,param_2,param_3,param_4);
    iVar2 = iVar2 + 0x1c;
  }
  return;
}

