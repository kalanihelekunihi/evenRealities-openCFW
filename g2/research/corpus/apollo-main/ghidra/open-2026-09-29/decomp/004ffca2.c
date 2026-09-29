
undefined4 Health_common_data_handler(uint param_1,byte *param_2,uint param_3,undefined4 param_4)

{
  byte bVar1;
  char cVar2;
  int iVar3;
  uint uStack_20;
  byte *pbStack_1c;
  uint uStack_18;
  undefined4 uStack_14;
  
  uStack_20 = param_1;
  pbStack_1c = param_2;
  uStack_18 = param_3;
  uStack_14 = param_4;
  health_data_mutex_init();
  if (param_1 == 0) {
    iVar3 = func_0x0055a350(param_2,param_3 & 0xffff);
    if ((((iVar3 == 0) && (cVar2 = FUN_0045a568(), cVar2 == '\x01')) &&
        (iVar3 = FUN_00443484(), iVar3 == 1)) && (iVar3 = FUN_004434d0(1), iVar3 == 1)) {
      uStack_20 = *(uint *)PTR_DAT_004ffdf4;
      pbStack_1c = *(byte **)(PTR_DAT_004ffdf4 + 4);
      FUN_00464bb2(1,&uStack_20,6,0);
    }
  }
  else if (param_1 == 5) {
    if ((param_2 == (byte *)0x0) || (param_3 == 0)) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        pbStack_1c = PTR_s_Invalid_raw_data_or_len_004ffdf8;
        uStack_20 = 0x6a;
        FUN_0043d574(2,DAT_004ffde0,DAT_004ffddc,PTR_s_Health_common_data_handler_004ffdfc);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x8000000,PTR_s__health_page_Invalid_raw_data_or_004ffe00,
                            PTR_s__health_page_Invalid_raw_data_or_004ffe00);
      }
    }
    else {
      bVar1 = *param_2;
      if (bVar1 != 1) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          uStack_18 = (uint)bVar1;
          pbStack_1c = PTR_s_Unknown_command___d_004ffe04;
          uStack_20 = 0xa1;
          FUN_0043d574(2,DAT_004ffde0,DAT_004ffddc,PTR_s_Health_common_data_handler_004ffdfc);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x8400000,PTR_s__health_page_Unknown_command___d_004ffe08,
                              PTR_s__health_page_Unknown_command___d_004ffe08,bVar1);
        }
      }
    }
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      pbStack_1c = PTR_s_Unknown_event_type___d_004ffe0c;
      uStack_20 = 0xaa;
      uStack_18 = param_1;
      FUN_0043d574(2,DAT_004ffde0,DAT_004ffddc,PTR_s_Health_common_data_handler_004ffdfc);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8400000,PTR_s__health_page_Unknown_event_type__004ffe10,
                          PTR_s__health_page_Unknown_event_type__004ffe10,param_1);
    }
  }
  return 0;
}

