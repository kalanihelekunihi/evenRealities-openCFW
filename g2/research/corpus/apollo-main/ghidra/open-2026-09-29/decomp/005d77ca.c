
void FUN_005d77ca(int *param_1,int param_2)

{
  int iVar1;
  undefined4 *puVar2;
  int iVar3;
  
  puVar2 = *(undefined4 **)(param_1[5] + 4);
  iVar3 = param_1[2];
  for (iVar1 = *param_1; iVar1 != 0; iVar1 = iVar1 + -1) {
    *(undefined4 *)(iVar3 + 0x10) = 0;
    *(undefined4 *)(iVar3 + 0x18) = 0;
    if (param_2 == 0) {
      *(undefined4 *)(iVar3 + 0x1c) = *puVar2;
      *(undefined4 *)(iVar3 + 0x20) = puVar2[1];
    }
    else {
      *(undefined4 *)(iVar3 + 0x1c) = puVar2[1];
      *(undefined4 *)(iVar3 + 0x20) = *puVar2;
    }
    iVar3 = iVar3 + 0x28;
    puVar2 = puVar2 + 2;
  }
  return;
}

