
undefined1 FUN_00544000(undefined4 *param_1,char *param_2)

{
  char cVar1;
  undefined4 uVar2;
  int iVar3;
  undefined1 uVar4;
  byte bVar5;
  uint uVar6;
  uint uVar7;
  int iVar8;
  undefined1 auStack_58 [8];
  undefined4 local_50;
  int local_4c;
  byte local_48 [4];
  undefined4 local_44;
  undefined1 auStack_40 [32];
  
  uVar4 = 0;
  FUN_00585a12(param_1,*(undefined4 *)(param_2 + 0x50),auStack_58,0x18);
  cVar1 = FUN_005858a8(auStack_58,6);
  *param_2 = cVar1;
  *(undefined4 *)(param_2 + 8) = local_50;
  if (((*(int *)(param_2 + 8) == -1) || ((uint)param_1[4] < *(uint *)(param_2 + 8))) ||
     (*(uint *)(param_2 + 8) < 0x18)) {
    param_2[8] = '\x18';
    param_2[9] = '\0';
    param_2[10] = '\0';
    param_2[0xb] = '\0';
    if (*param_2 != '\x05') {
      *param_2 = '\x05';
      FUN_004733ee(DAT_00544b6c);
      uVar2 = FUN_00585c94(param_1);
      FUN_004733ee(DAT_00544b70,*param_1,uVar2);
      FUN_004733ee(DAT_00544b74,*(undefined4 *)(param_2 + 0x50));
      FUN_005858d8(param_1,*(undefined4 *)(param_2 + 0x50),auStack_58,6,5,1);
    }
    param_2[1] = '\0';
    uVar4 = 2;
  }
  else {
    uVar2 = FUN_00585840(0,local_48,4);
    iVar3 = FUN_00585840(uVar2,&local_44,4);
    uVar6 = *(int *)(param_2 + 8) - 0x18;
    for (uVar7 = 0; uVar7 < uVar6; uVar7 = iVar8 + uVar7) {
      if (uVar7 + 0x20 < uVar6) {
        iVar8 = 0x20;
      }
      else {
        iVar8 = uVar6 - uVar7;
      }
      FUN_00585a12(param_1,uVar7 + *(int *)(param_2 + 0x50) + 0x18,auStack_40,iVar8);
      iVar3 = FUN_00585840(iVar3,auStack_40,iVar8);
    }
    if (iVar3 == local_4c) {
      param_2[1] = '\x01';
      iVar3 = *(int *)(param_2 + 0x50);
      FUN_00585a12(param_1,iVar3 + 0x18,param_2 + 0x10,local_48[0]);
      *(uint *)(param_2 + 0x54) = iVar3 + 0x18 + (uint)local_48[0];
      *(undefined4 *)(param_2 + 0xc) = local_44;
      param_2[2] = local_48[0];
      if (0x3f < local_48[0]) {
        local_48[0] = 0x3f;
      }
      param_2[local_48[0] + 0x10] = '\0';
    }
    else {
      bVar5 = local_48[0];
      if (0x40 < local_48[0]) {
        bVar5 = 0x40;
      }
      param_2[1] = '\0';
      uVar4 = 2;
      FUN_00585a12(param_1,*(int *)(param_2 + 0x50) + 0x18,param_2 + 0x10,bVar5);
      FUN_004733ee(DAT_00544b6c);
      uVar2 = FUN_00585c94(param_1);
      FUN_004733ee(DAT_00544b70,*param_1,uVar2);
      FUN_004733ee(DAT_00544cd4,bVar5,param_2 + 0x10,*(undefined4 *)(param_2 + 0x50));
    }
  }
  return uVar4;
}

