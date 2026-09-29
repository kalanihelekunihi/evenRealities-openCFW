
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
even_ai_common_timer_mgr_process_timeout
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  int iVar2;
  undefined4 uStack_18;
  undefined1 uStack_14;
  undefined1 uStack_13;
  undefined1 uStack_12;
  undefined1 uStack_11;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  uStack_14 = (undefined1)param_2;
  uStack_13 = (undefined1)((uint)param_2 >> 8);
  uStack_12 = (undefined1)((uint)param_2 >> 0x10);
  uStack_11 = (undefined1)((uint)param_2 >> 0x18);
  uStack_18 = param_1;
  if (*(char *)(DAT_004e3130 + 8) == '\x02') {
    uStack_10 = param_3;
    uStack_c = param_4;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uStack_14 = SUB41(PTR_s_even_ai_common_timer__processing_004e3154,0);
      uStack_13 = (undefined1)((uint)PTR_s_even_ai_common_timer__processing_004e3154 >> 8);
      uStack_12 = (undefined1)((uint)PTR_s_even_ai_common_timer__processing_004e3154 >> 0x10);
      uStack_11 = (undefined1)((uint)PTR_s_even_ai_common_timer__processing_004e3154 >> 0x18);
      uStack_18 = 0x55;
      FUN_0043d574(3,DAT_004e3138,DAT_004e3134,PTR_s_even_ai_common_timer_mgr_process_004e3158);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__even_ai_timer_even_ai_common_ti_004e315c,
                          PTR_s__even_ai_timer_even_ai_common_ti_004e315c);
    }
    even_ai_common_timer_mgr_stop();
    cVar1 = *_DAT_004e3160;
    if (cVar1 == '\x01') {
      if (_DAT_004e3160[1] == '\x01') {
        iVar2 = FUN_0045a568();
        if (iVar2 == 1) {
          even_ai_common_timer_mgr_start(3000);
          uStack_10 = *_DAT_004e3164;
          uStack_18 = 5;
          FUN_00464f76(7,&uStack_10,3,0);
        }
      }
      else if (_DAT_004e3160[1] == '\x02') {
        FUN_0043c0e4(&uStack_14,3,0);
        if (*(char *)(_DAT_004e3168 + 8) == '\0') {
          service_even_ai_fn_00498528(3);
        }
        uStack_12 = 4;
        uStack_13 = 7;
        uStack_14 = 7;
        iVar2 = FUN_0045a568();
        if (iVar2 == 1) {
          even_ai_common_timer_mgr_start(3000);
          uStack_18 = 5;
          FUN_00464f76(7,&uStack_14,3,0);
        }
      }
    }
    else if ((cVar1 == '\x05') || (cVar1 == '\x06')) {
      service_even_ai_fn_0049832e(3,0);
    }
    else if (cVar1 == '\a') {
      service_even_ai_fn_0049832e(3,0);
    }
  }
  return CONCAT17(uStack_11,CONCAT16(uStack_12,CONCAT15(uStack_13,CONCAT14(uStack_14,uStack_18))));
}

