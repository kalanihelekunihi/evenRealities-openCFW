
undefined4
ProductionTest_common_data_handler
          (undefined4 param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = param_3;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_1 = 0x21;
    param_2 = PTR_s_ProductionTest_recv_data_len_____005cf8c8;
    uVar2 = param_3;
    FUN_0043d574(3,PTR_s_production_test_005cf8d4,PTR_s_D__01_workspace_s200_ap510b_iar__005cf8d0,
                 PTR_s_ProductionTest_common_data_handl_005cf8cc,0x21,
                 PTR_s_ProductionTest_recv_data_len_____005cf8c8,param_3,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc400000,PTR_s__production_test_ProductionTest_r_005cf8d8,
                        PTR_s__production_test_ProductionTest_r_005cf8d8,param_3,param_1,param_2,
                        uVar2);
  }
  return 0;
}

