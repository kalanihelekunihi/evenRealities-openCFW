
int FT_Init_FreeType(undefined4 *param_1)

{
  int iVar1;
  int iVar2;
  
  iVar1 = FUN_005676a0();
  if (iVar1 == 0) {
    iVar2 = 7;
  }
  else {
    iVar2 = FT_New_Library(iVar1,param_1);
    if (iVar2 == 0) {
      FT_Add_Default_Modules(*param_1);
    }
    else {
      FUN_005676c6(iVar1);
    }
  }
  return iVar2;
}

