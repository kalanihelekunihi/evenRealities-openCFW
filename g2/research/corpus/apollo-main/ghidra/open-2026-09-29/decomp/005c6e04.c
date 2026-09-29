
void FUN_005c6e04(int param_1,uint param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  int local_40;
  int local_3c;
  int local_38;
  int local_34;
  int local_30 [2];
  int local_28;
  
  if (param_2 < *(uint *)(param_1 + 0x70)) {
    iVar1 = FUN_0043fe16(param_1);
    iVar2 = FUN_0044e586(param_1);
    if ((*(byte *)(param_1 + 0x74) & 0x1f) >> 3 == 0) {
      FUN_00440656(param_1);
    }
    else if ((*(byte *)(param_1 + 0x74) & 7) == 1) {
      iVar3 = FUN_005c579c(param_1,0);
      iVar4 = FUN_005c5772(param_1,0);
      iVar2 = (iVar3 + iVar4 + *(int *)(param_1 + 0x14)) - iVar2;
      iVar3 = FUN_005c57b2(param_1,0x50000);
      iVar4 = FUN_005c574a(param_1,0x20000);
      FUN_005c5738(&local_40,param_1 + 0x14);
      local_3c = (local_3c - iVar3) - iVar4;
      local_34 = iVar4 + iVar3 + local_34;
      if (param_2 < *(int *)(param_1 + 0x70) - 1U) {
        local_40 = ((iVar2 + (param_2 * iVar1) / (*(int *)(param_1 + 0x70) - 1U)) - iVar3) - iVar4;
        local_38 = iVar4 + iVar3 + iVar2 + ((param_2 + 1) * iVar1) / (*(int *)(param_1 + 0x70) - 1U)
        ;
        FUN_004405d4(param_1,&local_40);
      }
      if (param_2 != 0) {
        local_40 = ((iVar2 + ((param_2 - 1) * iVar1) / (*(int *)(param_1 + 0x70) - 1U)) - iVar3) -
                   iVar4;
        local_38 = iVar4 + iVar3 + iVar2 + (param_2 * iVar1) / (*(int *)(param_1 + 0x70) - 1U);
        FUN_004405d4(param_1,&local_40);
      }
    }
    else if ((*(byte *)(param_1 + 0x74) & 7) == 2) {
      iVar3 = FUN_005c5786(param_1,0);
      uVar6 = (uint)(iVar3 + iVar1) / *(uint *)(param_1 + 0x70);
      iVar1 = FUN_005c579c(param_1,0);
      iVar4 = FUN_005c5772(param_1,0);
      iVar5 = *(int *)(param_1 + 0x14);
      FUN_0043fc2a(param_1,local_30);
      iVar2 = (iVar4 + iVar1 + iVar5 + param_2 * uVar6) - iVar2;
      local_28 = uVar6 + iVar2;
      local_30[0] = iVar2 - iVar3;
      FUN_004405d4(param_1,local_30);
    }
    else {
      FUN_00440656(param_1);
    }
  }
  return;
}

