
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 even_ai_add_question(int param_1,char param_2,undefined4 param_3)

{
  undefined2 uVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int *piVar6;
  
  if (param_1 == 0) {
    uVar2 = 0;
  }
  else {
    iVar3 = FUN_0044a43c(param_1);
    iVar5 = DAT_004e64a8;
    piVar6 = *(int **)(DAT_004e64a8 + 0x14);
    if (((((param_2 == '\0') && (piVar6 != (int *)0x0)) && (*piVar6 != 0)) &&
        (iVar4 = FUN_0043e2ea(*piVar6), iVar4 != 0)) &&
       ((piVar6[1] == 0 || (iVar4 = FUN_0043e2ea(piVar6[1]), iVar4 == 0)))) {
      if (iVar3 != 0) {
        FUN_0049942e(*piVar6,param_1);
        uVar1 = FUN_0044a43c(param_1);
        even_ai_node_stream_state_init(piVar6,1,uVar1);
        if (0x400 < *(ushort *)(iVar5 + 0x1a)) {
          even_ai_manage_char_window();
        }
      }
      if ((char)piVar6[5] == '\x01') {
        *(undefined1 *)(piVar6 + 5) = 0;
        uVar2 = 1;
      }
      else {
        uVar2 = 0;
      }
    }
    else {
      if (((piVar6 == (int *)0x0) || ((*piVar6 != 0 || (iVar4 = FUN_0043e2ea(*piVar6), iVar4 != 0)))
          ) || ((piVar6[1] == 0 || (iVar4 = FUN_0043e2ea(piVar6[1]), iVar4 == 0)))) {
        if (4 < *(byte *)(iVar5 + 0x18)) {
          even_ai_dialogs_refresh();
          even_ai_layout_cache_invalidate();
        }
        piVar6 = (int *)even_ai_create_dialog_node();
        if (piVar6 == (int *)0x0) {
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            param_3 = 0x5a4;
            FUN_0043d574(1,PTR_s_even_ai_ui_004e6a7c,PTR_s_D__01_workspace_s200_ap510b_iar__004e6a78
                         ,PTR_s_even_ai_add_question_004e6c28,0x5a4,
                         PTR_s_create_dialog_node_failed_004e6c24);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x4000000,PTR_s__even_ai_ui_create_dialog_node_f_004e6c2c,
                                PTR_s__even_ai_ui_create_dialog_node_f_004e6c2c);
          }
          uVar2 = 1;
          goto LAB_004e64a2;
        }
        even_ai_dialog_index_set(piVar6);
        *(char *)(iVar5 + 0x18) = *(char *)(iVar5 + 0x18) + '\x01';
      }
      else if (piVar6[1] != 0) {
        FUN_0044d7b8(piVar6[1]);
        piVar6[1] = 0;
        piVar6[2] = 0;
        piVar6[3] = 0;
        piVar6[4] = 0;
      }
      iVar4 = FUN_00499416(*(undefined4 *)(iVar5 + 8));
      FUN_0044131c(iVar4,0,0);
      even_ai_style_apply(iVar4,0,0);
      uVar2 = FUN_0044104c(_DAT_004e6c30);
      FUN_0044140e(iVar4,uVar2,0);
      FUN_0044143e(iVar4,*_DAT_004e6c34,0);
      FUN_0044145a(iVar4,1,0);
      FUN_0043f506(iVar4,0x20b);
      if (iVar3 != 0) {
        FUN_0049942e(iVar4,param_1);
        uVar1 = FUN_0044a43c(param_1);
        even_ai_node_stream_state_init(piVar6,1,uVar1);
        if (0x400 < *(ushort *)(iVar5 + 0x1a)) {
          even_ai_manage_char_window();
        }
      }
      FUN_0043f09a(iVar4,0,0);
      *piVar6 = iVar4;
      *(undefined1 *)(piVar6 + 5) = 0;
      uVar2 = 1;
    }
  }
LAB_004e64a2:
  return CONCAT44(param_3,uVar2);
}

