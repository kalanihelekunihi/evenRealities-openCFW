
undefined8 FUN_0051381a(int param_1,undefined4 *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = FUN_005137c4(param_1);
  if (iVar1 == 0) {
    if (param_2 == (undefined4 *)0x0) {
      iVar1 = 6;
    }
    else {
      iVar1 = FUN_005137de();
      if (iVar1 == 0) {
        *param_2 = *(undefined4 *)(param_1 + 0x400c2000);
      }
      else {
        *param_2 = 0;
      }
    }
  }
  return CONCAT44(param_4,iVar1);
}

