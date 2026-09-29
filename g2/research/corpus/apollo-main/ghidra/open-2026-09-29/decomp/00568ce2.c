
undefined8
FUN_00568ce2(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar2 = 0;
  iVar1 = FT_Angle_Diff(*param_1,param_1[1]);
  if (iVar1 != 0) {
    iVar2 = FUN_005689e6(param_1,iVar1 < 0,param_2);
    if (iVar2 == 0) {
      iVar2 = FUN_00568abe(param_1,iVar1 >= 0,param_2);
    }
  }
  return CONCAT44(param_4,iVar2);
}

