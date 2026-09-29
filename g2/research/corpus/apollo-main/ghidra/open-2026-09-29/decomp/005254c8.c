
void ft_glyphslot_grid_fit_metrics(int param_1,char param_2)

{
  int iVar1;
  int iVar2;
  int *piVar3;
  
  piVar3 = (int *)(param_1 + 0x18);
  if (param_2 == '\0') {
    *(uint *)(param_1 + 0x2c) = *(uint *)(param_1 + 0x2c) & 0xffffffc0;
    *(uint *)(param_1 + 0x30) = *(uint *)(param_1 + 0x30) & 0xffffffc0;
    iVar1 = *(int *)(param_1 + 0x20);
    iVar2 = *(int *)(param_1 + 0x24);
    *(uint *)(param_1 + 0x20) = *(uint *)(param_1 + 0x20) & 0xffffffc0;
    *(uint *)(param_1 + 0x24) = *(int *)(param_1 + 0x24) + 0x3fU & 0xffffffc0;
    *piVar3 = (*piVar3 + iVar1 + 0x3fU & 0xffffffc0) - *(int *)(param_1 + 0x20);
    *(uint *)(param_1 + 0x1c) =
         *(int *)(param_1 + 0x24) - (iVar2 - *(int *)(param_1 + 0x1c) & 0xffffffc0U);
  }
  else {
    *(uint *)(param_1 + 0x20) = *(uint *)(param_1 + 0x20) & 0xffffffc0;
    *(uint *)(param_1 + 0x24) = *(int *)(param_1 + 0x24) + 0x3fU & 0xffffffc0;
    iVar1 = *(int *)(param_1 + 0x2c);
    iVar2 = *(int *)(param_1 + 0x30);
    *(uint *)(param_1 + 0x2c) = *(uint *)(param_1 + 0x2c) & 0xffffffc0;
    *(uint *)(param_1 + 0x30) = *(uint *)(param_1 + 0x30) & 0xffffffc0;
    *piVar3 = (*piVar3 + iVar1 + 0x3fU & 0xffffffc0) - *(int *)(param_1 + 0x2c);
    *(uint *)(param_1 + 0x1c) =
         (*(int *)(param_1 + 0x1c) + iVar2 + 0x3fU & 0xffffffc0) - *(int *)(param_1 + 0x30);
  }
  *(uint *)(param_1 + 0x28) = *(int *)(param_1 + 0x28) + 0x20U & 0xffffffc0;
  *(uint *)(param_1 + 0x34) = *(int *)(param_1 + 0x34) + 0x20U & 0xffffffc0;
  return;
}

