
void FUN_005d7106(int *param_1)

{
  int iVar1;
  int iVar2;
  
  iVar1 = param_1[2];
  for (iVar2 = *param_1; iVar2 != 0; iVar2 = iVar2 + -1) {
    *(uint *)(iVar1 + 0x10) = *(uint *)(iVar1 + 0x10) & 0xfffffffb;
    *(undefined4 *)(iVar1 + 0x18) = 0xffffffff;
    iVar1 = iVar1 + 0x1c;
  }
  return;
}

