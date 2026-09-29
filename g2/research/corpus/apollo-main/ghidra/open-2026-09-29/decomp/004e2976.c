
undefined8 FUN_004e2976(int param_1,undefined4 param_2,uint param_3)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  
  uVar3 = param_3;
  FUN_004e1f7c();
  if (param_1 == 0) {
    iVar1 = APP_PbRxEvenAIFrameDataProcess(param_2,param_3 & 0xffff);
    if (iVar1 != 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar3 = 0x291;
        FUN_0043d574(1,PTR_s_even_ai_page_004e2a50,PTR_s_D__01_workspace_s200_ap510b_iar__004e2a4c,
                     PTR_s_EvenAI_common_data_handler_004e2dd0,0x291,
                     PTR_s_APP_PbRxEvenAIFrameDataProcess_f_004e2dcc);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__even_ai_page_APP_PbRxEvenAIFram_004e2dd4,
                            PTR_s__even_ai_page_APP_PbRxEvenAIFram_004e2dd4);
      }
      uVar2 = 0xffffffff;
      goto LAB_004e2a3e;
    }
  }
  else {
    if (param_1 != 5) {
      uVar2 = 0xffffffff;
      goto LAB_004e2a3e;
    }
    iVar1 = service_even_ai_fn_00498092(param_2,param_3);
    if (iVar1 != 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar3 = 0x298;
        FUN_0043d574(1,PTR_s_even_ai_page_004e2a50,PTR_s_D__01_workspace_s200_ap510b_iar__004e2a4c,
                     PTR_s_EvenAI_common_data_handler_004e2dd0,0x298,
                     PTR_s_SVC_DecodeLocalEvenAIInfo_failed_004e2dd8);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__even_ai_page_SVC_DecodeLocalEve_004e2ddc,
                            PTR_s__even_ai_page_SVC_DecodeLocalEve_004e2ddc);
      }
      uVar2 = 0xffffffff;
      goto LAB_004e2a3e;
    }
  }
  FUN_004e20f2(0);
  uVar2 = 0;
LAB_004e2a3e:
  return CONCAT44(uVar3,uVar2);
}

