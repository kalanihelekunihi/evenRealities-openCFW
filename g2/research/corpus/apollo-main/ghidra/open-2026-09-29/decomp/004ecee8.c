
undefined8 FUN_004ecee8(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  double in_d0;
  
  iVar1 = FUN_004ece5c(param_1,param_2);
  if (iVar1 == 0) {
    uVar2 = 0xffffffff;
  }
  else if (in_d0 == DAT_004ed120) {
    uVar2 = FUN_004ecec4(param_1,param_2);
  }
  else {
    uVar2 = FUN_0044b728(param_1,param_2,DAT_004ed708);
  }
  return CONCAT44(param_4,uVar2);
}

