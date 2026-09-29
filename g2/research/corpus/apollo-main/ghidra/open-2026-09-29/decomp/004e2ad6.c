
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong FUN_004e2ad6(char *param_1,uint param_2,undefined4 param_3,uint param_4)

{
  char cVar1;
  char *pcVar2;
  int iVar3;
  int iVar4;
  
  if ((param_1 == (char *)0x0) || (param_2 == 0)) {
    even_ai_ui_reflash(*_DAT_004e2de0);
  }
  else {
    iVar3 = service_even_ai_fn_00498092(param_1,param_2);
    if (iVar3 == 0) {
      FUN_004e20f2(1);
      even_ai_ui_reflash(*_DAT_004e2de0);
    }
    else {
      cVar1 = *param_1;
      if (cVar1 == '\x03') {
        even_ai_ui_reflash(*_DAT_004e2de0);
      }
      else if (cVar1 == '\x04') {
        if (*_DAT_004e2de4 == '\0') {
          EvenAI_InputEventWarp(param_1,param_2);
        }
        else if (((param_1[1] == 'D') || (param_1[1] == 'E')) && (*_DAT_004e2de4 == '\x01')) {
          EvenAI_InputEventWarp(param_1,param_2);
        }
        else {
          ui_common_api_fn_00509ca2(*_DAT_004e2de8,param_1,param_2 & 0xffff);
        }
      }
      else if (cVar1 == '\x05') {
        even_ai_stream_phase_update(param_1[1],*(undefined2 *)(param_1 + 2));
      }
      else if (cVar1 == '\x06') {
        if (5 < param_2) {
          FUN_00553d64(param_1[1],*(undefined4 *)(param_1 + 2));
        }
      }
      else if (cVar1 == '\b') {
        even_ai_stream_phase_update(param_1[1],*(undefined2 *)(param_1 + 2));
        FUN_004e1fa6();
        service_even_ai_fn_004982d4(param_1[2]);
        iVar4 = UX_GetSystemBLEStatus();
        iVar3 = _DAT_004e2c24;
        if (iVar4 == 1) {
          AUDM_appAcquire(3);
          even_ai_timer_start_all(5000);
        }
        else {
          *(undefined1 *)(_DAT_004e2c24 + 1) = 7;
          *(undefined1 *)(iVar3 + 2) = 2;
          even_ai_timer_start_all(3000);
        }
        pcVar2 = _DAT_004e2c38;
        if ((*_DAT_004e2c38 == '\x03') || (*_DAT_004e2c38 == '\x04')) {
          even_ai_stop_current_streaming(0);
        }
        else {
          even_ai_stop_current_streaming(1);
        }
        iVar3 = _DAT_004e2c24;
        *pcVar2 = *(char *)(_DAT_004e2c24 + 1);
        pcVar2[1] = *(char *)(iVar3 + 2);
        FUN_004e1fbe();
        even_ai_ui_reflash(*_DAT_004e2de0);
      }
    }
  }
  return (ulonglong)param_4 << 0x20;
}

