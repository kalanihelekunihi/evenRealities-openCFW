
undefined4
FT_Add_Default_Modules(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  
  for (piVar1 = DAT_00524318; *piVar1 != 0; piVar1 = piVar1 + 1) {
    FT_Add_Module(param_1,*piVar1);
  }
  return param_4;
}

