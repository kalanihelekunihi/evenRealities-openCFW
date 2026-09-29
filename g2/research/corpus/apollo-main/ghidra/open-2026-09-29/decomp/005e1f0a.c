
undefined8 FUN_005e1f0a(int param_1)

{
  int iVar1;
  undefined4 local_10;
  
  iVar1 = FUN_0056777c(param_1);
  if (iVar1 == 0) {
    local_10 = FT_Outline_Decompose(param_1 + 0xbc,DAT_005e2638,param_1);
    if (*(int *)(param_1 + 0xa0) == 0) {
      FUN_005e1594(param_1);
    }
  }
  else {
    local_10 = 0x40;
  }
  return CONCAT44(local_10,local_10);
}

