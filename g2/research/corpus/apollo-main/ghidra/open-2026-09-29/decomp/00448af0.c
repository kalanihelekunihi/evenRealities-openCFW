
undefined8 FUN_00448af0(int param_1,undefined4 param_2,int param_3,int param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  int local_18;
  int local_14;
  
  local_18 = param_3;
  if (param_1 == 0) {
    uVar1 = 0;
  }
  else {
    local_14 = param_4;
    FUN_004488ec(param_1 + 4,2);
    FUN_00448930(param_1,0);
    uVar5 = 0;
    do {
      while( true ) {
        do {
          uVar4 = uVar5;
          uVar1 = DAT_00448fc0;
          local_18 = FUN_00448938(DAT_00448fc0);
          local_14 = FUN_00448938(local_18);
          iVar2 = DAT_00448fbc;
          uVar5 = uVar4 + 1;
          if (10000 < (int)uVar5) {
            *(int *)(DAT_00448fbc + 0x2c) = *(int *)(DAT_00448fbc + 0x2c) + 1;
            *(int *)(iVar2 + 4) = *(int *)(iVar2 + 4) + 1;
            FUN_00448a8e(param_1);
            uVar1 = 0;
            goto LAB_00448b94;
          }
          iVar2 = FUN_00448938(uVar1);
        } while (local_18 != iVar2);
        if (local_14 == 0) break;
        FUN_00448940(uVar1,&local_18,local_14);
      }
      iVar3 = FUN_00448940(local_18,&local_14,param_1);
      iVar2 = DAT_00448fbc;
    } while (iVar3 == 0);
    *(uint *)(DAT_00448fbc + 0x1c) = uVar4 + *(int *)(DAT_00448fbc + 0x1c);
    if (*(uint *)(iVar2 + 0x20) < uVar5) {
      *(uint *)(iVar2 + 0x20) = uVar5;
    }
    FUN_00448940(uVar1,&local_18,param_1);
    uVar1 = 1;
  }
LAB_00448b94:
  return CONCAT44(local_18,uVar1);
}

