
int FUN_004234d8(undefined4 param_1,int param_2)

{
  int iVar1;
  
  if (*(undefined4 **)(param_2 + 8) != (undefined4 *)0x0) {
    **(undefined4 **)(param_2 + 8) = 0;
  }
  iVar1 = FUN_00422ee2(param_1);
  if (iVar1 == 0) {
    FUN_00423524(param_1);
    iVar1 = 0;
  }
  return iVar1;
}

