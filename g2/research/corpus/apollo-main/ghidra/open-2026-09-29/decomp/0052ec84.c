
int FUN_0052ec84(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  byte bVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  int local_2c;
  int local_28;
  uint local_24;
  undefined4 uStack_20;
  
  local_24 = 0;
  local_2c = 0;
  uStack_20 = param_4;
  FUN_0052e788(&local_24,&local_2c);
  FUN_004733ee(DAT_0052f244);
  bVar2 = 0;
  while( true ) {
    if (local_24 <= bVar2) {
      return 0;
    }
    local_28 = 0;
    iVar3 = *(int *)(*(int *)(local_2c + (uint)bVar2 * 4) + 8);
    iVar4 = *(int *)(*(int *)(local_2c + (uint)bVar2 * 4) + 4);
    uVar5 = **(undefined4 **)(local_2c + (uint)bVar2 * 4);
    iVar1 = FUN_0052e6ac(param_1,iVar3,iVar4 + iVar3,&local_28);
    if (iVar1 != 0) break;
    iVar1 = FUN_004d34f8(uVar5,iVar4,0);
    if (local_28 != iVar1) {
      FUN_004733ee(DAT_0052f24c,iVar3,iVar4 + iVar3,local_28,iVar1);
      return 0xe;
    }
    bVar2 = bVar2 + 1;
  }
  FUN_004733ee(DAT_0052f248);
  return iVar1;
}

