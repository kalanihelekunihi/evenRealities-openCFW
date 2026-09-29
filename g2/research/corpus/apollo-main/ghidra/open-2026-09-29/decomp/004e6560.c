
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 even_ai_add_answer(int param_1,int param_2,byte param_3,char param_4,char param_5)

{
  undefined2 uVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int *piVar8;
  int iVar9;
  uint uVar10;
  
  iVar9 = param_2;
  if (param_1 == 0) {
    uVar2 = 0;
  }
  else {
    iVar3 = FUN_0044a43c(param_1);
    iVar5 = _DAT_004e69e0;
    if (((((*(char *)(_DAT_004e69e0 + 0x18) == '\0') || (param_4 != '\0')) ||
         (iVar7 = *(int *)(_DAT_004e69e0 + 0x14), iVar7 == 0)) ||
        ((*(int *)(iVar7 + 4) == 0 || (iVar4 = FUN_0043e2ea(*(undefined4 *)(iVar7 + 4)), iVar4 == 0)
         ))) || ((*(int *)(iVar7 + 8) == 0 ||
                 (iVar4 = FUN_0043e2ea(*(undefined4 *)(iVar7 + 8)), iVar4 == 0)))) {
      piVar8 = *(int **)(iVar5 + 0x14);
      if ((((*(char *)(iVar5 + 0x18) == '\0') || (piVar8 == (int *)0x0)) || (*piVar8 == 0)) ||
         (((iVar7 = FUN_0043e2ea(*piVar8), iVar7 == 0 || (piVar8[1] != 0)) ||
          (iVar7 = FUN_0043e2ea(piVar8[1]), iVar7 != 0)))) {
        if (4 < *(byte *)(iVar5 + 0x18)) {
          even_ai_dialogs_refresh();
          even_ai_layout_cache_invalidate();
        }
        piVar8 = (int *)even_ai_create_dialog_node();
        if (piVar8 == (int *)0x0) {
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            iVar9 = 0x68d;
            FUN_0043d574(1,PTR_s_even_ai_ui_004e6a7c,PTR_s_D__01_workspace_s200_ap510b_iar__004e6a78
                         ,_DAT_004e7164,0x68d,PTR_s_create_dialog_node_failed_004e6c24);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x4000000,PTR_s__even_ai_ui_create_dialog_node_f_004e6c2c,
                                PTR_s__even_ai_ui_create_dialog_node_f_004e6c2c);
          }
          uVar2 = 1;
          goto LAB_004e689e;
        }
        even_ai_dialog_index_set(piVar8);
        *(char *)(iVar5 + 0x18) = *(char *)(iVar5 + 0x18) + '\x01';
      }
      iVar7 = FUN_0043de82(*(undefined4 *)(iVar5 + 8));
      FUN_0043f506(iVar7,0x20b);
      FUN_0043f568(iVar7,0x3fffffff);
      FUN_0044131c(iVar7,0,0);
      even_ai_style_apply(iVar7,0,0);
      FUN_0044129e(iVar7,0,0);
      FUN_0043f09a(iVar7,0,0);
      if (param_2 == 0) {
        piVar8[3] = 0;
        piVar8[4] = 0;
      }
      else {
        uVar10 = (uint)param_3;
        iVar4 = FUN_00498668(iVar7);
        FUN_00498680(iVar4,param_2);
        FUN_0043f4c0(iVar4,0x20,0x20);
        even_ai_style_apply(iVar4,4,0);
        FUN_0043f09a(iVar4,0,0);
        piVar8[3] = iVar4;
        if ((char)uVar10 == -1) {
          piVar8[4] = 0;
        }
        else {
          iVar6 = FUN_0055751e(iVar7);
          FUN_0043f4c0(iVar6,200,4);
          iVar9 = 0;
          FUN_0043f6d6(iVar6,iVar4,0x14,8);
          func_0x00557630(iVar6,0,100);
          uVar2 = FUN_0044104c(_DAT_004e7168);
          FUN_0044127e(iVar6,uVar2,0);
          FUN_0044129e(iVar6,0xff,0);
          FUN_0044131c(iVar6,0,0);
          FUN_0044146a(iVar6,0,0);
          even_ai_style_apply(iVar6,0,0);
          uVar2 = FUN_0044104c(0xffffff);
          FUN_0044127e(iVar6,uVar2,0x20000);
          FUN_0044129e(iVar6,0xff,0x20000);
          FUN_0044146a(iVar6,0,0x20000);
          FUN_00557536(iVar6,uVar10 & 0xff,0);
          FUN_00440656(iVar6);
          piVar8[4] = iVar6;
        }
      }
      iVar4 = FUN_00499416(iVar7);
      FUN_0044131c(iVar4,0,0);
      even_ai_style_apply(iVar4,0,0);
      uVar2 = FUN_0044104c(0xffffff);
      FUN_0044140e(iVar4,uVar2,0);
      FUN_0044143e(iVar4,*_DAT_004e6c34,0);
      FUN_0044145a(iVar4,1,0);
      if (iVar3 != 0) {
        FUN_0049942e(iVar4,param_1);
        uVar1 = FUN_0044a43c(param_1);
        even_ai_node_stream_state_init(piVar8,0,uVar1);
        if (0x400 < *(ushort *)(iVar5 + 0x1a)) {
          even_ai_manage_char_window();
        }
      }
      if ((param_2 == 0) || (param_5 != '\x01')) {
        FUN_0043f506(iVar4,0x20b);
        if (param_2 == 0) {
          FUN_0043f09a(iVar4,0,0);
        }
        else {
          FUN_0043f09a(iVar4,0,0x28);
        }
      }
      else {
        FUN_0043f506(iVar4,0x1e7);
        FUN_0043f09a(iVar4,0x24,0);
      }
      piVar8[2] = iVar4;
      piVar8[1] = iVar7;
      uVar2 = 1;
    }
    else {
      if (iVar3 != 0) {
        FUN_0049942e(*(undefined4 *)(iVar7 + 8),param_1);
        uVar1 = FUN_0044a43c(param_1);
        even_ai_node_stream_state_init(iVar7,0,uVar1);
        if (0x400 < *(ushort *)(iVar5 + 0x1a)) {
          even_ai_manage_char_window();
        }
      }
      uVar2 = 0;
    }
  }
LAB_004e689e:
  return CONCAT44(iVar9,uVar2);
}

