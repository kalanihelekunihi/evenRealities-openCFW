
undefined8 FUN_004d0444(undefined4 param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_004d01bc(param_2,param_3);
  uVar2 = param_2;
  if (iVar1 != 0) {
    uVar2 = FUN_004d01d4(param_2,param_3 - *DAT_004d0964);
    FUN_004cfde8(uVar2);
    FUN_004cfe88(param_2);
    FUN_004d019a(param_1,param_2);
  }
  return CONCAT44(param_4,uVar2);
}

