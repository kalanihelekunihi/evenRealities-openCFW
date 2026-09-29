
undefined4 FUN_0043c400(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = param_3;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_1 = 0x33;
    param_2 = DAT_0043c758;
    uVar2 = param_3;
    FUN_0043d574(3,DAT_0043c764,DAT_0043c760,DAT_0043c75c,0x33,DAT_0043c758,param_3,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc400000,PTR_s__aging_test_AgingTest_recv_data_l_0043c768,
                        PTR_s__aging_test_AgingTest_recv_data_l_0043c768,param_3,param_1,param_2,
                        uVar2);
  }
  return 0;
}

