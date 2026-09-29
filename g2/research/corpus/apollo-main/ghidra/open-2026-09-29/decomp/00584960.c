
bool FUN_00584960(undefined4 param_1,undefined4 param_2)

{
  int *piVar1;
  
  piVar1 = DAT_005849a4;
  if (*DAT_005849a4 == 0) {
    *DAT_005849a4 = DAT_00584998;
  }
  FUN_0044b5a0(param_1,*(undefined4 *)(*(int *)*piVar1 + 4),param_2);
  *piVar1 = *(int *)(*piVar1 + 4);
  return *piVar1 != 0;
}

