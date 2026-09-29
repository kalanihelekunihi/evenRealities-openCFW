
int FUN_005dabee(int param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  ushort uVar1;
  byte bVar2;
  int iVar3;
  uint uVar4;
  byte *pbVar5;
  int local_18;
  undefined4 uStack_14;
  
  pbVar5 = *(byte **)(param_1 + 0x10);
  uVar1 = *(ushort *)(param_1 + 8);
  local_18 = param_3;
  uStack_14 = param_4;
  iVar3 = ft_mem_realloc(param_2,1,0,uVar1 + 1,0,&local_18);
  if (local_18 == 0) {
    for (uVar4 = 0; uVar4 < uVar1; uVar4 = uVar4 + 1) {
      bVar2 = *pbVar5;
      pbVar5 = pbVar5 + 1;
      if (bVar2 == 0) break;
      if (0x5f < bVar2 - 0x20) {
        bVar2 = 0x3f;
      }
      *(byte *)(iVar3 + uVar4) = bVar2;
    }
    *(undefined1 *)(iVar3 + uVar4) = 0;
  }
  else {
    iVar3 = 0;
  }
  return iVar3;
}

