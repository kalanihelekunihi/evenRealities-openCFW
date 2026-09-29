
void FUN_0044035e(int param_1,int param_2,int param_3,char param_4)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  
  uVar1 = FUN_0044ddea(param_1);
  for (uVar3 = 0; uVar3 < uVar1; uVar3 = uVar3 + 1) {
    iVar4 = *(int *)(**(int **)(param_1 + 8) + uVar3 * 4);
    if ((param_4 == '\0') || (iVar2 = FUN_0043e0e0(iVar4,0x40000), iVar2 == 0)) {
      *(int *)(iVar4 + 0x14) = param_2 + *(int *)(iVar4 + 0x14);
      *(int *)(iVar4 + 0x18) = param_3 + *(int *)(iVar4 + 0x18);
      *(int *)(iVar4 + 0x1c) = param_2 + *(int *)(iVar4 + 0x1c);
      *(int *)(iVar4 + 0x20) = param_3 + *(int *)(iVar4 + 0x20);
      FUN_0044035e(iVar4,param_2,param_3,0);
    }
  }
  return;
}

