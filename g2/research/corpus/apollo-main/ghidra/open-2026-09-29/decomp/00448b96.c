
undefined8 FUN_00448b96(undefined4 param_1,int param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  int local_20;
  int local_1c;
  undefined4 uStack_18;
  
  uVar5 = 0;
  local_20 = param_2;
  local_1c = param_3;
  uStack_18 = param_4;
  do {
    while( true ) {
      do {
        uVar4 = uVar5;
        iVar3 = DAT_00448fb8;
        local_20 = FUN_00448938(DAT_00448fb8);
        local_1c = FUN_00448938(iVar3 + 4);
        iVar1 = FUN_00448938(local_20);
        uVar5 = uVar4 + 1;
        if (10000 < (int)uVar5) {
          *(int *)(DAT_00448fbc + 0x2c) = *(int *)(DAT_00448fbc + 0x2c) + 1;
          iVar3 = 0;
          goto LAB_00448c72;
        }
        iVar2 = FUN_00448938(iVar3);
      } while (local_20 != iVar2);
      if (local_20 != local_1c) break;
      if (iVar1 == 0) {
        iVar3 = 0;
        goto LAB_00448c72;
      }
      FUN_00448940(iVar3 + 4,&local_1c,iVar1);
    }
  } while ((iVar1 == 0) ||
          (iVar2 = FUN_00448940(iVar3,&local_20,iVar1), iVar3 = DAT_00448fbc, iVar2 == 0));
  *(uint *)(DAT_00448fbc + 0x24) = uVar4 + *(int *)(DAT_00448fbc + 0x24);
  if (*(uint *)(iVar3 + 0x28) < uVar5) {
    *(uint *)(iVar3 + 0x28) = uVar5;
  }
  if (local_20 == DAT_00448fb4) {
    FUN_00439be4(local_20 + 0xd,iVar1 + 0xd,*(ushort *)(iVar1 + 8) + 1);
    *(undefined2 *)(local_20 + 8) = *(undefined2 *)(iVar1 + 8);
    *(undefined2 *)(local_20 + 10) = *(undefined2 *)(iVar1 + 10);
    iVar3 = local_20;
  }
  else {
    FUN_00439be4(local_20 + 0xd,iVar1 + 0xd,*(ushort *)(iVar1 + 8) + 1);
    *(undefined2 *)(local_20 + 8) = *(undefined2 *)(iVar1 + 8);
    *(undefined2 *)(local_20 + 10) = *(undefined2 *)(iVar1 + 10);
    iVar3 = local_20;
  }
LAB_00448c72:
  return CONCAT44(local_20,iVar3);
}

