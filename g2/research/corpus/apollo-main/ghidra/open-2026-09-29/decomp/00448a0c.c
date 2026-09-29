
undefined8 FUN_00448a0c(void)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  int in_r3;
  uint uVar5;
  uint uVar6;
  int local_10;
  
  uVar6 = 0;
  local_10 = in_r3;
  while( true ) {
    uVar5 = uVar6;
    uVar1 = DAT_00448fb0;
    local_10 = FUN_00448938(DAT_00448fb0);
    if (local_10 == 0) {
      *(int *)(DAT_00448fbc + 4) = *(int *)(DAT_00448fbc + 4) + 1;
      iVar4 = 0;
      goto LAB_00448a8c;
    }
    uVar2 = FUN_00448938(local_10);
    iVar4 = DAT_00448fbc;
    uVar6 = uVar5 + 1;
    if (1000 < (int)uVar6) break;
    iVar3 = FUN_00448940(uVar1,&local_10,uVar2);
    iVar4 = DAT_00448fbc;
    if (iVar3 != 0) {
      *(uint *)(DAT_00448fbc + 0xc) = uVar5 + *(int *)(DAT_00448fbc + 0xc);
      if (*(uint *)(iVar4 + 0x10) < uVar6) {
        *(uint *)(iVar4 + 0x10) = uVar6;
      }
      FUN_004488ec(local_10 + 4,1);
      FUN_00448930(local_10,0);
      iVar4 = local_10;
LAB_00448a8c:
      return CONCAT44(local_10,iVar4);
    }
  }
  *(int *)(DAT_00448fbc + 0x2c) = *(int *)(DAT_00448fbc + 0x2c) + 1;
  *(int *)(iVar4 + 4) = *(int *)(iVar4 + 4) + 1;
  iVar4 = 0;
  goto LAB_00448a8c;
}

