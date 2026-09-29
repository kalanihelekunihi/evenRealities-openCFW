
undefined4 FUN_0044fe0e(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_10;
  
  if (param_1 == 0) {
    param_1 = FUN_0044fa1a();
  }
  if (param_1 == 0) {
    local_10 = DAT_0044ff90;
    FUN_0044d25c(2,DAT_0044ff7c,0x371,DAT_0044ff94);
  }
  else {
    *(undefined4 *)(param_1 + 0x300) = param_2;
    local_10 = param_4;
    if ((((*(int *)(param_1 + 0x2d4) == 4) &&
         (iVar1 = FUN_0044ddea(**(undefined4 **)(param_1 + 0x2b8)), iVar1 == 0)) &&
        (iVar1 = FUN_0044ddea(*(undefined4 *)(*(int *)(param_1 + 0x2b8) + 4)), iVar1 == 0)) &&
       (iVar1 = FUN_0044ddea(*(undefined4 *)(*(int *)(param_1 + 0x2b8) + 8)), iVar1 == 0)) {
      FUN_00482f8a(**(undefined4 **)(param_1 + 0x2b8));
    }
  }
  return local_10;
}

