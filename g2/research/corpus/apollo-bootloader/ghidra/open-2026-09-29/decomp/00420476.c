
int FUN_00420476(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_c;
  
  local_c = param_4;
  iVar1 = FUN_00420254(1,0,DAT_00420c40,param_4,param_1,param_2,param_3);
  if (iVar1 == 0) {
    FUN_0041f9d8(10);
    FUN_0042052a();
    FUN_00420f10();
    FUN_004201ba();
    FUN_00420f10();
    iVar1 = FUN_0042059e(&local_c);
    if (iVar1 == 0) {
      elog_output(3,DAT_00420adc,DAT_00420978,DAT_00420c48,0x292,DAT_00420c50,local_c);
      FUN_00420890();
      FUN_00420c5c(1);
      FUN_0041fe62();
    }
    else {
      elog_output(1,DAT_00420adc,DAT_00420978,DAT_00420c48,0x28e,DAT_00420c4c,iVar1);
    }
  }
  else {
    elog_output(1,DAT_00420adc,DAT_00420978,DAT_00420c48,0x284,DAT_00420c44,iVar1);
  }
  FUN_0041fe28();
  return iVar1;
}

