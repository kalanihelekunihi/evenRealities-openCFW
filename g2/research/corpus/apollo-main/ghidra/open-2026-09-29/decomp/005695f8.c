
int FUN_005695f8(undefined4 *param_1)

{
  int iVar1;
  int iVar2;
  
  iVar2 = 0;
  if (param_1 == (undefined4 *)0x0) {
    iVar2 = 6;
  }
  else if (*(char *)((int)param_1 + 0x15) == '\0') {
    if (((param_1[2] == param_1[7]) && (param_1[3] == param_1[8])) ||
       (iVar2 = FUN_00568d86(param_1,param_1 + 7), iVar2 == 0)) {
      param_1[1] = param_1[6];
      iVar1 = FT_Angle_Diff(*param_1,param_1[1]);
      if (iVar1 != 0) {
        iVar2 = FUN_005689e6(param_1,iVar1 < 0,param_1[9]);
        if (iVar2 != 0) {
          return iVar2;
        }
        iVar1 = FUN_00568abe(param_1,iVar1 >= 0,param_1[9]);
        iVar2 = 0;
        if (iVar1 != 0) {
          return iVar1;
        }
      }
      FUN_0056834a(param_1 + 0xd,0);
      FUN_0056834a(param_1 + 0x15,1);
    }
  }
  else {
    iVar2 = FUN_005688b8(param_1,*param_1,0);
    if ((iVar2 == 0) && (iVar2 = FUN_00569532(param_1,1), iVar2 == 0)) {
      param_1[2] = param_1[7];
      param_1[3] = param_1[8];
      iVar2 = FUN_005688b8(param_1,param_1[6] + 0xb40000,0);
      if (iVar2 == 0) {
        FUN_0056834a(param_1 + 0xd,0);
      }
    }
  }
  return iVar2;
}

