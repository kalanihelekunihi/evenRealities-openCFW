
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
system_close_ReflashEventHandler(char *param_1,int param_2,undefined *param_3,undefined4 param_4)

{
  char cVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  int iVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  
  if ((param_1 == (char *)0x0) || (param_2 == 0)) {
    cVar1 = *_DAT_0046b09c;
    if (cVar1 == '\x01') {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        param_2 = 0x263;
        param_3 = PTR_s_system_close_ReflashEventHandler_0046b0a0;
        FUN_0043d574(4,DAT_0046b058,DAT_0046b054,PTR_s_system_close_ReflashEventHandler_0046b0a4,
                     0x263,PTR_s_system_close_ReflashEventHandler_0046b0a0,param_4);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__system_close_system_close_Refla_0046b0a8);
      }
      puVar3 = _DAT_0046b0ac;
      FUN_0044d878(*_DAT_0046b0ac);
      puVar2 = _DAT_0046ae70;
      uVar5 = FUN_00499416(*puVar3);
      *puVar2 = uVar5;
      uVar5 = _DAT_0046b0b0;
      uVar6 = FUN_00460084(_DAT_0046b0b0);
      uVar5 = FUN_0045fffe(uVar5,uVar6);
      FUN_0049942e(*puVar2,uVar5);
      FUN_0043f506(*puVar2,0x3fffffff);
      FUN_0043f568(*puVar2,0x3fffffff);
      FUN_0043ded4(*puVar2,0x10000);
      FUN_0043dfa4(*puVar2,0x10);
      FUN_0044143e(*puVar2,*_DAT_0046b08c,0);
      uVar5 = FUN_0044104c(0xffffff);
      FUN_0044140e(*puVar2,uVar5,0);
      system_close_create_options(1);
      system_close_option_position_0046a2ca();
      *_DAT_0046b0b4 = 1;
    }
    else {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        param_2 = 0x28a;
        param_3 = PTR_s_system_close_ReflashEventHandler_0046b0b8;
        FUN_0043d574(2,DAT_0046b058,DAT_0046b054,PTR_s_system_close_ReflashEventHandler_0046b0a4,
                     0x28a,PTR_s_system_close_ReflashEventHandler_0046b0b8,cVar1);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x8400000,PTR_s__system_close_system_close_Refla_0046b0bc,
                            PTR_s__system_close_system_close_Refla_0046b0bc,cVar1);
      }
    }
  }
  else {
    cVar1 = param_1[1];
    if (*param_1 == '\0') {
      if (*DAT_0046b004 == '\0') {
        if (cVar1 == '\n') {
          system_close_handle_click();
        }
        else if (cVar1 == 'D') {
          system_close_handle_scroll_up();
        }
        else if (cVar1 == 'E') {
          system_close_handle_scroll_down();
        }
        else if ((cVar1 == 'H') && (iVar4 = FUN_0045a568(), iVar4 == 1)) {
          FUN_00464c36(0x22,0,0,0);
        }
      }
      else {
        system_close_fifo_push_00469c26(param_1 + 1,5);
      }
    }
  }
  return CONCAT44(param_3,param_2);
}

