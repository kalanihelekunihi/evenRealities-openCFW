
undefined8 FUN_00500ade(undefined4 param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  int iVar2;
  undefined4 uVar3;
  
  uVar3 = param_1;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    uVar3 = 0xf4;
    param_2 = PTR_s_STEP2__handle_APP_REQUEST_UPGRAD_005011b8;
    param_3 = param_1;
    FUN_0043d574(3,DAT_00501188,DAT_00501184,PTR_s_handle_request_upgrade_pb_file_005011bc,0xf4,
                 PTR_s_STEP2__handle_APP_REQUEST_UPGRAD_005011b8,param_1,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc400000,PTR_s__dashboard_ext_STEP2__handle_APP_005011c0,
                        PTR_s__dashboard_ext_STEP2__handle_APP_005011c0,param_1,uVar3,param_2,
                        param_3);
  }
  *DAT_005017a4 = param_1;
  puVar1 = DAT_00501170;
  FUN_0043c0e4(DAT_00501170,0x1024,0);
  *puVar1 = 3;
  *(undefined4 *)(puVar1 + 4) = param_1;
  *(undefined2 *)(puVar1 + 8) = 6;
  *(undefined4 *)(puVar1 + 0xc) = 0;
  FUN_00500a02();
  iVar2 = FUN_0045a568();
  if (iVar2 == 1) {
    FUN_00464cba(0);
  }
  FUN_0045bca0(10000);
  FUN_00454b4c(800);
  FUN_00500824();
  FUN_00500b7c(param_1);
  return CONCAT44(param_2,uVar3);
}

