
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_004716ba(int param_1,byte *param_2,undefined *param_3,undefined4 param_4)

{
  byte bVar1;
  byte bVar2;
  byte *pbVar3;
  char cVar4;
  int iVar5;
  undefined *puVar6;
  uint uStack_38;
  undefined4 uStack_34;
  undefined *puStack_30;
  uint uStack_2c;
  undefined1 auStack_28 [12];
  undefined *puStack_1c;
  undefined4 uStack_18;
  
  uStack_18 = param_4;
  iVar5 = FUN_0043d0ce();
  if (iVar5 << 0x1e < 0) {
    uStack_34 = PTR_s_module_configure_data_handler_re_00471b44;
    uStack_38 = 0xdc;
    puStack_30 = param_3;
    FUN_0043d574(4,DAT_00471ae0,DAT_00471adc,PTR_s_ModuleConfigureService_common_da_00471b48);
  }
  iVar5 = FUN_0043d0ce();
  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
    compress_log_output(0x10400000,PTR_s__general_configure_module_config_00471b4c,
                        PTR_s__general_configure_module_config_00471b4c,param_3);
  }
  pbVar3 = _DAT_00471b50;
  if (param_1 == 0) {
    FUN_0043c0e4(_DAT_00471b50,8,0);
    FUN_0048f49c(&uStack_38,param_2,param_3);
    FUN_00439c04(auStack_28,&uStack_38,0x10);
    cVar4 = FUN_00490120(auStack_28,DAT_00471b00,pbVar3);
    if (cVar4 == '\0') {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        puStack_30 = PTR_s__none__00471b54;
        if (puStack_1c != (undefined *)0x0) {
          puStack_30 = puStack_1c;
        }
        uStack_34 = PTR_s_module_configure_data_handler_pr_00471b58;
        uStack_38 = 0xe3;
        FUN_0043d574(1,DAT_00471ae0,DAT_00471adc,PTR_s_ModuleConfigureService_common_da_00471b48);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        puVar6 = PTR_s__none__00471b54;
        if (puStack_1c != (undefined *)0x0) {
          puVar6 = puStack_1c;
        }
        compress_log_output(0x4400000,PTR_s__general_configure_module_config_00471b5c,
                            PTR_s__general_configure_module_config_00471b5c,puVar6);
      }
    }
    else {
      bVar1 = *pbVar3;
      bVar2 = pbVar3[1];
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        uStack_2c = (uint)bVar2;
        puStack_30 = (undefined *)(uint)bVar1;
        uStack_34 = PTR_s_module_configure_data_handler_cm_00471b60;
        uStack_38 = 0xe9;
        FUN_0043d574(4,DAT_00471ae0,DAT_00471adc,PTR_s_ModuleConfigureService_common_da_00471b48);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        uStack_38 = (uint)bVar2;
        compress_log_output(0x10800000,PTR_s__general_configure_module_config_00471b64,
                            PTR_s__general_configure_module_config_00471b64,bVar1);
      }
      if (bVar1 == 0) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          uStack_34 = PTR_s_module_configure_data_handler_re_00471b68;
          uStack_38 = 0xec;
          FUN_0043d574(4,DAT_00471ae0,DAT_00471adc,PTR_s_ModuleConfigureService_common_da_00471b48);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__general_configure_module_config_00471b6c,
                              PTR_s__general_configure_module_config_00471b6c);
        }
        if (*(short *)(pbVar3 + 2) == 3) {
          FUN_004711b2(*(undefined4 *)(pbVar3 + 4));
          *DAT_00471b14 = 1;
          osEventFlagsSet(*_DAT_00471b70,4);
          FUN_00471224(bVar2);
        }
      }
      else if (bVar1 == 2) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          uStack_34 = PTR_s_module_configure_data_handler_re_00471b7c;
          uStack_38 = 0xfb;
          FUN_0043d574(4,DAT_00471ae0,DAT_00471adc,PTR_s_ModuleConfigureService_common_da_00471b48);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__general_configure_module_config_00471b80,
                              PTR_s__general_configure_module_config_00471b80);
        }
        if (*(short *)(pbVar3 + 2) == 4) {
          *DAT_00471ae8 = *(undefined4 *)(pbVar3 + 4);
          *DAT_00471b2c = 1;
          osEventFlagsSet(*_DAT_00471b70,4);
          FUN_0047142a(bVar2);
        }
      }
      else if (bVar1 < 2) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          uStack_34 = PTR_s_module_configure_data_handler_re_00471b74;
          uStack_38 = 0xf6;
          FUN_0043d574(4,DAT_00471ae0,DAT_00471adc,PTR_s_ModuleConfigureService_common_da_00471b48);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__general_configure_module_config_00471b78,
                              PTR_s__general_configure_module_config_00471b78);
        }
        FUN_0047132c(bVar2);
      }
      else {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          puStack_30 = (undefined *)(uint)bVar1;
          uStack_34 = PTR_s_module_configure_data_handler__u_00471b84;
          uStack_38 = 0x105;
          FUN_0043d574(2,DAT_00471ae0,DAT_00471adc,PTR_s_ModuleConfigureService_common_da_00471b48);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x8400000,PTR_s__general_configure_module_config_00471b88,
                              PTR_s__general_configure_module_config_00471b88,bVar1);
        }
      }
    }
  }
  else if (param_1 == 5) {
    bVar1 = *param_2;
    if (bVar1 == 1) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        uStack_34 = PTR_s_module_configure_data_handler_re_00471b8c;
        uStack_38 = 0x10d;
        FUN_0043d574(3,DAT_00471ae0,DAT_00471adc,PTR_s_ModuleConfigureService_common_da_00471b48);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__general_configure_module_config_00471b90,
                            PTR_s__general_configure_module_config_00471b90);
      }
      if ((uint)param_2[1] != *DAT_00471ac4) {
        FUN_004711b2(param_2[1]);
        *DAT_00471b14 = 1;
        osEventFlagsSet(*_DAT_00471b70,4);
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          puStack_30 = (undefined *)(uint)param_2[1];
          uStack_34 = PTR_s_module_configure_data_handler_se_00471b94;
          uStack_38 = 0x112;
          FUN_0043d574(3,DAT_00471ae0,DAT_00471adc,PTR_s_ModuleConfigureService_common_da_00471b48);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0xc400000,PTR_s__general_configure_module_config_00471b98,
                              PTR_s__general_configure_module_config_00471b98,param_2[1]);
        }
      }
    }
    else if (bVar1 == 2) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        uStack_34 = PTR_s_module_configure_data_handler_re_00471b8c;
        uStack_38 = 0x117;
        FUN_0043d574(4,DAT_00471ae0,DAT_00471adc,PTR_s_ModuleConfigureService_common_da_00471b48);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__general_configure_module_config_00471b90,
                            PTR_s__general_configure_module_config_00471b90);
      }
      FUN_0043c0e4(&uStack_34,10,0);
      uStack_34._0_2_ = CONCAT11((char)*DAT_00471ac4,1);
      uStack_38 = 5;
      FUN_00465480(0x20,&uStack_34,2,0);
    }
    else {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        puStack_30 = (undefined *)(uint)bVar1;
        uStack_34 = PTR_s_module_configure_data_handler__u_00471b84;
        uStack_38 = 0x120;
        FUN_0043d574(2,DAT_00471ae0,DAT_00471adc,PTR_s_ModuleConfigureService_common_da_00471b48);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x8400000,PTR_s__general_configure_module_config_00471b88,
                            PTR_s__general_configure_module_config_00471b88,bVar1);
      }
    }
  }
  return 0;
}

