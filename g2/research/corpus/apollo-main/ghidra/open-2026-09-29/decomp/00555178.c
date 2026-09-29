
undefined8 FUN_00555178(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uStack_18;
  undefined4 uStack_14;
  
  uStack_18 = param_3;
  uStack_14 = param_4;
  iVar1 = FUN_0045a568();
  if (iVar1 == 1) {
    FUN_0043c0e4(&uStack_18,8,0);
    FUN_00589cb4();
    if (*(char *)(DAT_00555754 + 0x20) == '\x02') {
      FUN_00554fae(param_1,param_2);
    }
    else if (*(char *)(DAT_00555754 + 0x20) == '\x01') {
      FUN_00554f4c(param_1,param_2);
    }
    else if (param_1 == 0x48) {
      FUN_00589b68(9,0);
    }
  }
  return CONCAT44(uStack_14,uStack_18);
}

