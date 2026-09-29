
undefined8 FUN_004d4696(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  FUN_004d47cc(param_1);
  iVar1 = FUN_00441710(*(undefined4 *)(param_1 + 4));
  if (iVar1 != 1) {
    param_3 = DAT_004d47bc;
    FUN_0044d25c(3,DAT_004d47b0,0xa8,DAT_004d47c0,DAT_004d47bc,param_4);
  }
  return CONCAT44(param_3,(uint)(iVar1 == 1));
}

