
undefined8 FUN_0052ebca(undefined4 param_1,int param_2)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  byte bVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  int local_30;
  uint local_2c;
  undefined4 local_28;
  
  iVar3 = 0;
  iVar1 = 0;
  local_2c = 0;
  local_30 = 0;
  local_28 = param_1;
  FUN_0052e788(&local_2c,&local_30);
  FUN_004733ee(DAT_0052f23c);
  bVar4 = 0;
  do {
    if (local_2c <= bVar4) {
LAB_0052ec7a:
      return CONCAT44(local_30,iVar1);
    }
    iVar5 = *(int *)(*(int *)(local_30 + (uint)bVar4 * 4) + 8);
    iVar6 = **(int **)(local_30 + (uint)bVar4 * 4);
    uVar2 = *(uint *)(*(int *)(local_30 + (uint)bVar4 * 4) + 4);
    while (uVar2 != 0) {
      uVar7 = uVar2;
      if (0xf8 < uVar2) {
        uVar7 = 0xf8;
      }
      iVar1 = FUN_0052eaf8(local_28,iVar5,iVar6,uVar7 & 0xff);
      if (iVar1 != 0) {
        FUN_004733ee(DAT_0052f240);
        goto LAB_0052ec7a;
      }
      iVar5 = uVar7 + iVar5;
      iVar6 = iVar6 + uVar7;
      uVar2 = uVar2 - uVar7;
      iVar3 = uVar7 + iVar3;
      if (param_2 != 0) {
        FUN_0052eba8(iVar3,param_2);
      }
    }
    bVar4 = bVar4 + 1;
  } while( true );
}

