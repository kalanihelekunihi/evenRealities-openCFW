
undefined8 FUN_0044fe8e(int param_1,char param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_10;
  
  if (param_1 == 0) {
    param_1 = FUN_0044fa1a();
  }
  if (param_1 == 0) {
    local_10 = DAT_0044ff90;
    FUN_0044d25c(2,DAT_0044ff7c,0x3a4,DAT_0044ff98);
  }
  else {
    if (param_2 == '\0') {
      iVar1 = -1;
    }
    else {
      iVar1 = 1;
    }
    *(int *)(param_1 + 0x264) = iVar1 + *(int *)(param_1 + 0x264);
    local_10 = param_3;
  }
  return CONCAT44(param_4,local_10);
}

