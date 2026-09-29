
undefined8 FUN_0053d82c(int param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = FUN_00450286(param_1);
  if (iVar1 == 0x24) {
    FUN_0053d8fc();
  }
  else if (iVar1 == 0x28) {
    FUN_0053da54();
  }
  else if (iVar1 == 0x29) {
    FUN_0053db3c(**(undefined4 **)(param_1 + 0x10));
  }
  else {
    param_2 = DAT_0053dbd8;
    FUN_0044d25c(2,DAT_0053dbe0,0xba,DAT_0053dbdc,DAT_0053dbd8,iVar1,param_4);
    param_3 = iVar1;
  }
  return CONCAT44(param_3,param_2);
}

