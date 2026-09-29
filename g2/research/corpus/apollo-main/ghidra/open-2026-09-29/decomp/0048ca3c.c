
void FUN_0048ca3c(int param_1)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  undefined1 auStack_40 [8];
  int local_38;
  int local_34;
  undefined1 auStack_30 [32];
  
  FUN_0048cad8(param_1,auStack_30);
  FUN_0048c80e(auStack_40,0x10);
  iVar1 = FUN_0048c920(param_1,0);
  iVar2 = FUN_0048c94e(param_1,0);
  local_38 = FUN_0044e486(param_1);
  local_38 = (*(int *)(param_1 + 0x14) + iVar1) - local_38;
  local_34 = FUN_0044e498(param_1);
  local_34 = (*(int *)(param_1 + 0x18) + iVar2) - local_34;
  for (uVar3 = 0; uVar3 < *(ushort *)(*(int *)(param_1 + 8) + 0x30); uVar3 = uVar3 + 1) {
    FUN_0048cfe0(*(undefined4 *)(**(int **)(param_1 + 8) + uVar3 * 4),auStack_30,auStack_40);
  }
  FUN_0048cbda(auStack_30);
  iVar1 = FUN_0048c81a(param_1,0);
  iVar2 = FUN_0048c824(param_1,0);
  if ((iVar1 == 0x3fffffff) || (iVar2 == 0x3fffffff)) {
    FUN_0043f1a4(param_1);
  }
  FUN_00451670(param_1,0x33,0);
  return;
}

