
int FUN_005dab8e(int param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  undefined1 *puVar4;
  uint uVar5;
  int local_18;
  undefined4 uStack_14;
  
  puVar4 = *(undefined1 **)(param_1 + 0x10);
  uVar5 = (uint)(*(ushort *)(param_1 + 8) >> 1);
  local_18 = param_3;
  uStack_14 = param_4;
  iVar1 = ft_mem_realloc(param_2,1,0,uVar5 + 1,0,&local_18);
  if (local_18 == 0) {
    for (uVar3 = 0; uVar3 < uVar5; uVar3 = uVar3 + 1) {
      uVar2 = (uint)CONCAT11(*puVar4,puVar4[1]);
      if (uVar2 == 0) break;
      if (0x5f < uVar2 - 0x20) {
        uVar2 = 0x3f;
      }
      *(char *)(iVar1 + uVar3) = (char)uVar2;
      puVar4 = puVar4 + 2;
    }
    *(undefined1 *)(iVar1 + uVar3) = 0;
  }
  else {
    iVar1 = 0;
  }
  return iVar1;
}

