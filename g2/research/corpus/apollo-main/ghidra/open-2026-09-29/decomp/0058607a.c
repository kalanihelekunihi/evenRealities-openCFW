
/* WARNING: Removing unreachable block (ram,0x00586356) */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int FUN_0058607a(int param_1,undefined4 param_2,undefined2 param_3,undefined4 param_4)

{
  longlong lVar1;
  undefined4 *puVar2;
  int *piVar3;
  uint *puVar4;
  char cVar5;
  int iVar6;
  undefined4 uVar7;
  uint uVar8;
  undefined *apuStack_74 [3];
  undefined1 uStack_68;
  undefined1 uStack_67;
  undefined1 uStack_66;
  undefined1 uStack_65;
  undefined1 uStack_64;
  undefined1 uStack_63;
  undefined1 uStack_5c;
  undefined1 uStack_5b;
  undefined4 uStack_50;
  undefined4 uStack_4c;
  undefined1 uStack_48;
  undefined1 uStack_47;
  undefined1 auStack_3c [24];
  uint uStack_24;
  int iStack_20;
  undefined4 uStack_14;
  
  piVar3 = _DAT_00586408;
  uStack_14 = param_4;
  if (param_1 == 2) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      apuStack_74[0] = PTR_s_navigation_ui_event_handler_UI_E_005863f0;
      FUN_0043d574(4,PTR_s_navigation_main_005863ac,PTR_s_D__01_workspace_s200_ap510b_iar__005863a8,
                   PTR_s_navigation_ui_event_handler_005863f4,0xe5);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__navigation_main_navigation_ui_e_005863f8,
                          PTR_s__navigation_main_navigation_ui_e_005863f8);
    }
    iVar6 = osKernelGetTickCount();
    *_DAT_005863fc = iVar6;
    *_DAT_005863c0 = 0;
    *_DAT_005863cc = 0;
    ble_state_skip_manual_start(0);
    *_DAT_00586400 = param_4;
    FUN_00545d18(param_4,param_2,param_3);
    puVar2 = _DAT_005863b4;
    *(undefined4 *)(_DAT_00586404 + 4) = *_DAT_005863b4;
    FUN_0046410a(*puVar2);
    param_1 = 0;
  }
  else if (param_1 == 3) {
    FUN_00549c24(param_2,param_3);
    param_1 = 0;
  }
  else if (param_1 == 4) {
    *_DAT_00586408 = *_DAT_00586408 + 1;
    if (0x3c < *piVar3) {
      *piVar3 = 0;
      piVar3 = _DAT_0058640c;
      *_DAT_0058640c = *_DAT_0058640c + -1;
      if (*piVar3 < 1) {
        *piVar3 = 0x14;
        cVar5 = FUN_0045a570();
        if (cVar5 == '\x01') {
          uStack_48 = 0xf0;
          uStack_47 = 0;
          FUN_00464bb2(8,&uStack_48,2,0);
        }
      }
    }
    piVar3 = _DAT_00586414;
    if ((*_DAT_00586410 == 1) && (*_DAT_00586414 = *_DAT_00586414 + -1, *piVar3 < 1)) {
      *piVar3 = 0xf0;
      cVar5 = FUN_0045a570();
      if (cVar5 == '\x01') {
        FUN_0043c0e4(&uStack_5c,10,0);
        uStack_5c = 0xf3;
        uStack_5b = 0;
        FUN_00464bb2(8,&uStack_5c,6,0);
      }
    }
    piVar3 = _DAT_00586418;
    if ((*_DAT_00586418 != 0) || (*_DAT_0058641c != 0)) {
      uVar7 = service_time_current_epoch_get();
      service_time_epoch_to_calendar(uVar7,auStack_3c);
      puVar4 = _DAT_00586420;
      if ((*_DAT_00586420 != uStack_24) || (*_DAT_00586424 != iStack_20)) {
        FUN_0043c0e4(apuStack_74,10,0);
        *puVar4 = uStack_24;
        *_DAT_00586424 = iStack_20;
        iVar6 = FUN_0046650c();
        if (iVar6 == 1) {
          uVar8 = uStack_24 % 0xc;
          if (uVar8 == 0) {
            uVar8 = 0xc;
          }
          if (uStack_24 < 0xc) {
            uVar7 = 0x58638c;
          }
          else {
            uVar7 = 0x586390;
          }
          FUN_004b4728(apuStack_74,_DAT_00586428,uVar8,iStack_20,uVar7);
        }
        else {
          FUN_004b4728(apuStack_74,_DAT_0058642c,uStack_24,iStack_20);
        }
        iVar6 = FUN_0043e2ea(*piVar3);
        if (iVar6 != 0) {
          FUN_0049942e(*piVar3,apuStack_74);
        }
        piVar3 = _DAT_0058641c;
        iVar6 = FUN_0043e2ea(*_DAT_0058641c);
        if (iVar6 != 0) {
          FUN_0049942e(*piVar3,apuStack_74);
        }
      }
    }
    piVar3 = _DAT_00586434;
    if ((((*_DAT_00586430 == '\n') || (*_DAT_00586430 == '\x01')) && (*_DAT_00586434 != 0)) &&
       (iVar6 = FUN_0043e2ea(*(undefined4 *)*_DAT_00586434), iVar6 != 0)) {
      FUN_00463f34(*piVar3);
      iVar6 = FUN_0045a570();
      if (((iVar6 == 1) && (iVar6 = FUN_00463fa4(*piVar3), 0 < iVar6)) && ((iVar6 + 1U & 3) == 0)) {
        FUN_0043c0e4(&uStack_68,10,0);
        uStack_68 = 0xf6;
        uStack_67 = (undefined1)iVar6;
        uStack_66 = 0;
        uStack_65 = 0;
        uStack_64 = 0;
        uStack_63 = 0;
        FUN_00464bb2(8,&uStack_68,6,0);
      }
    }
    param_1 = 0;
  }
  else if (param_1 == 5) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      apuStack_74[0] = PTR_s_navigation_ui_event_handler_DISP_00586438;
      FUN_0043d574(3,PTR_s_navigation_main_005863ac,PTR_s_D__01_workspace_s200_ap510b_iar__005863a8,
                   PTR_s_navigation_ui_event_handler_005863f4,0x14a);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__navigation_main_navigation_ui_e_0058643c,
                          PTR_s__navigation_main_navigation_ui_e_0058643c);
    }
    piVar3 = _DAT_00586434;
    if (*_DAT_00586434 != 0) {
      FUN_00463e1c(*_DAT_00586434,1);
      *piVar3 = 0;
    }
    FUN_0054c268(param_2,param_3);
    ble_param_reset_delayed_event(10000);
    FUN_0054566c();
    *_DAT_005863c0 = 0;
    *_DAT_005863cc = 0;
    iVar6 = osKernelGetTickCount();
    lVar1 = (ulonglong)(uint)(iVar6 - *_DAT_005863fc) * 1000;
    uStack_4c = FUN_0047cc60((int)lVar1,(int)((ulonglong)lVar1 >> 0x20),1000,0);
    uStack_50 = *(undefined4 *)PTR_DAT_00586440;
    FUN_0048eb32(_DAT_00586444,2,&uStack_50);
    param_1 = 0;
  }
  return param_1;
}

