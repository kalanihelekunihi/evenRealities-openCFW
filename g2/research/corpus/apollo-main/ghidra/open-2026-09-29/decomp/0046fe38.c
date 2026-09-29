
int FUN_0046fe38(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 local_c;
  
  local_c = param_4;
  iVar1 = FUN_0046fb0c(1,0,DAT_0047086c,param_4,param_1,param_2,param_3);
  if (iVar1 == 0) {
    FUN_004910f4(10);
    FUN_0046ff5c();
    FUN_00470f68();
    FUN_0046f9f6();
    FUN_00470f68();
    iVar1 = FUN_00470028(&local_c);
    if (iVar1 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,DAT_004700a8,DAT_004700a4,DAT_00470874,0x292,DAT_00470884,local_c);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_00470894,DAT_00470894,local_c);
      }
      FUN_004704ac();
      FUN_00470aac(1);
      FUN_0046f546();
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004700a8,DAT_004700a4,DAT_00470874,0x28e,DAT_0047087c,iVar1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_00470880,DAT_00470880,iVar1);
      }
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004700a8,DAT_004700a4,DAT_00470874,0x284,DAT_00470870,iVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00470878,DAT_00470878,iVar1);
    }
  }
  FUN_0046f50c();
  return iVar1;
}

