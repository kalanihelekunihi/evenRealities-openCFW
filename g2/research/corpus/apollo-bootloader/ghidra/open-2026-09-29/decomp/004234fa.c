
undefined8 FUN_004234fa(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  if (*(undefined4 **)(param_2 + 8) != (undefined4 *)0x0) {
    **(undefined4 **)(param_2 + 8) = 0;
  }
  iVar1 = FUN_00422f4c(param_1);
  if (iVar1 == 0) {
    FUN_00423608(param_1);
  }
  return CONCAT44(param_4,iVar1);
}

