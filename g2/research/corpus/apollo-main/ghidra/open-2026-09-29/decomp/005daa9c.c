
undefined4 FUN_005daa9c(int param_1,int param_2,int param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int local_14;
  int local_10;
  undefined4 uStack_c;
  
  if (*(int *)(param_1 + 0x2ac) == 0) {
    local_14 = param_2;
    local_10 = param_3;
    uStack_c = param_4;
    if ((*(int *)(param_1 + 700) == 0) ||
       (((*(uint *)(param_1 + 4) & DAT_005db3e4) == 0 && (-1 < *(int *)(param_1 + 8) << 0x10)))) {
      iVar2 = FUN_005da5d6(param_1,6,&local_14,&local_10,param_1);
      if (iVar2 == 0) {
        uVar1 = 0;
      }
      else {
        if (local_14 == -1) {
          uVar1 = FUN_005da518(*(undefined4 *)(param_1 + 100),*(undefined4 *)(param_1 + 0x170),
                               local_10 * 0x14 + *(int *)(param_1 + 0x164),
                               PTR_LAB_005da1a8_1_005db568,1);
        }
        else {
          uVar1 = FUN_005da446(*(undefined4 *)(param_1 + 100),*(undefined4 *)(param_1 + 0x170),
                               local_14 * 0x14 + *(int *)(param_1 + 0x164),
                               PTR_LAB_005da1a8_1_005db568,1);
        }
        *(undefined4 *)(param_1 + 0x2ac) = uVar1;
      }
    }
    else {
      uVar1 = FUN_005da73a(param_1);
      *(undefined4 *)(param_1 + 0x2ac) = uVar1;
      uVar1 = *(undefined4 *)(param_1 + 0x2ac);
    }
  }
  else {
    uVar1 = *(undefined4 *)(param_1 + 0x2ac);
  }
  return uVar1;
}

