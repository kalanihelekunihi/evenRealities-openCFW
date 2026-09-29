
undefined8 FUN_004d4666(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  FUN_004d47cc(param_1);
  iVar1 = FUN_00441750(*(undefined4 *)(param_1 + 4),0xffffffff);
  if (iVar1 != 1) {
    param_3 = DAT_004d47b4;
    FUN_0044d25c(3,DAT_004d47b0,0x84,DAT_004d47b8,DAT_004d47b4,param_4);
  }
  return CONCAT44(param_3,(uint)(iVar1 == 1));
}

