
undefined8 FUN_00448a8e(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  undefined4 local_18;
  undefined4 uStack_14;
  
  local_18 = param_3;
  uStack_14 = param_4;
  if (param_1 != 0) {
    FUN_004488ec(param_1 + 4,0);
    uVar5 = 0;
    do {
      uVar4 = uVar5;
      uVar1 = DAT_00448fb0;
      local_18 = FUN_00448938(DAT_00448fb0);
      FUN_00448930(param_1,local_18);
      uVar5 = uVar4 + 1;
      if (1000 < (int)uVar5) {
        *(int *)(DAT_00448fbc + 0x2c) = *(int *)(DAT_00448fbc + 0x2c) + 1;
        goto LAB_00448aee;
      }
      iVar3 = FUN_00448940(uVar1,&local_18,param_1);
      iVar2 = DAT_00448fbc;
    } while (iVar3 == 0);
    *(uint *)(DAT_00448fbc + 0x14) = uVar4 + *(int *)(DAT_00448fbc + 0x14);
    if (*(uint *)(iVar2 + 0x18) < uVar5) {
      *(uint *)(iVar2 + 0x18) = uVar5;
    }
  }
LAB_00448aee:
  return CONCAT44(uStack_14,local_18);
}

