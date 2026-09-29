
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_005e641c(undefined1 param_1,uint param_2)

{
  int *piVar1;
  int iVar2;
  
  piVar1 = _DAT_005e68d8;
  FUN_005e4c84(0);
  FUN_005ec9c0();
  FUN_005e65f8();
  if (*piVar1 != 0) {
    FUN_0043dfa4(*piVar1,1);
  }
  if ((param_2 & 0xff) != 0) {
    FUN_005eae2c(param_2 & 0xff);
  }
  FUN_005eb8da();
  if (piVar1[0x85] != 0) {
    iVar2 = FUN_005eb61e(2);
    *(bool *)(piVar1 + 0x9f) = iVar2 == 0;
    *(undefined1 *)((int)piVar1 + 0x279) = 0;
    FUN_005ebb96();
  }
  if ((((piVar1[0x73] != 0) && (piVar1[0x74] != 0)) && (piVar1[0x75] != 0)) && (piVar1[0x77] != 0))
  {
    FUN_0043dfa4(piVar1[0x73],1);
    FUN_005ea30c();
    FUN_005e47fe(piVar1[0x74],_DAT_005e6dc8);
    FUN_0049942e(piVar1[0x75],PTR_s_Select_an_option_005e6f50);
    FUN_0049942e(piVar1[0x77],PTR_s__Swipe___tap__005e6f54);
    FUN_005e4894();
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(3,PTR_s_terminal_ui_005e6b90,PTR_s_D__01_workspace_s200_ap510b_iar__005e6b8c,
                 PTR_s_terminal_ui_action_query_show_005e6f5c,0x5c1,
                 PTR_s_query_panel_shown__from_state__d_005e6f58,param_1,param_2);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc800000,PTR_s__terminal_ui_query_panel_shown__f_005e7200,
                        PTR_s__terminal_ui_query_panel_shown__f_005e7200,param_1,param_2);
  }
  return 0;
}

