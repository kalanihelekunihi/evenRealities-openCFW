
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_005560d0(undefined4 param_1,uint param_2)

{
  int iVar1;
  
  if (((*(int *)(_DAT_00556260 + 0x18) != 0) && (*(char *)(_DAT_00556260 + 0x21) == '\0')) &&
     (*(int *)(_DAT_00556260 + 0x3c) == 0)) {
    if (((*(uint *)(_DAT_00556260 + 0x2c) <= param_2) &&
        (param_2 < *(int *)(_DAT_00556260 + 0x2c) + 4U)) &&
       ((param_2 < *(uint *)(_DAT_00556cac + 0xc) &&
        (iVar1 = FUN_0044dce2(*(undefined4 *)(_DAT_00556260 + 0x18),
                              param_2 - *(int *)(_DAT_00556260 + 0x2c)), iVar1 != 0)))) {
      FUN_00555514(iVar1,param_2);
    }
    FUN_00555200(1);
  }
  return 0;
}

