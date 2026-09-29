
void FUN_0054ccd4(void)

{
  char *pcVar1;
  undefined4 *puVar2;
  uint *puVar3;
  undefined1 *puVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  int iVar7;
  undefined4 in_r3;
  uint local_20;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 uStack_14;
  
  uStack_14 = in_r3;
  uVar5 = FUN_0044e4aa(*DAT_0054d930);
  puVar3 = DAT_0054d934;
  uVar6 = FUN_0054cc00(*DAT_0054d934);
  iVar7 = FUN_0043d0ce();
  if (iVar7 << 0x1e < 0) {
    local_20 = *puVar3;
    local_1c = uVar5;
    local_18 = uVar6;
    FUN_0043d574(4,PTR_s_navigation_ui_0054cf58,DAT_0054cf54,DAT_0054cfc8,0xc7f,DAT_0054cfc4);
  }
  iVar7 = FUN_0043d0ce();
  if (-1 < iVar7 << 0x1f) {
    iVar7 = FUN_0043d0ce();
    if (-1 < iVar7 << 0x1d) goto LAB_0054cd38;
  }
  compress_log_output(0x10c00000,DAT_0054cfcc,DAT_0054cfcc,*puVar3,uVar5,uVar6);
LAB_0054cd38:
  FUN_0054d9a4();
  puVar4 = DAT_0054d938;
  *DAT_0054d938 = 0;
  puVar2 = DAT_0054ceb4;
  pcVar1 = DAT_0054ceb0;
  if (*DAT_0054ceb0 == '\x02') {
    iVar7 = ui_common_api_fn_00509dfa(*DAT_0054ceb4);
    if (iVar7 == 0) {
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_navigation_ui_0054cf58,DAT_0054cf54,DAT_0054cfc8,0xc84,DAT_0054ceb8);
      }
      iVar7 = FUN_0043d0ce();
      if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054cf30);
      }
      ui_common_api_fn_00509e14(*puVar2,&local_20,1);
      if ((local_20 & 0xff) == 10) {
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054cf58,DAT_0054cf54,DAT_0054cfc8,0xc89,
                       PTR_s_navigation_ui_reflash_page_handl_0054cf34);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054cf38,
                              PTR_s__navigation_ui_navigation_ui_ref_0054cf38);
        }
        FUN_0054cfd0(2);
        if (*DAT_0054d3b8 != 0) {
          FUN_0044d878(*DAT_0054d3b8);
        }
        *pcVar1 = '\t';
        *DAT_0054d93c = 0;
        *puVar4 = 0;
        ui_common_api_fn_00509f52(*puVar2);
        FUN_00548b98();
      }
      else if ((local_20 & 0xff) == 0x44) {
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054cf58,DAT_0054cf54,DAT_0054cfc8,0xc96,
                       PTR_s_navigation_ui_reflash_page_handl_0054cf3c);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054cf40,
                              PTR_s__navigation_ui_navigation_ui_ref_0054cf40);
        }
        FUN_0054cfd0(1);
      }
      else if ((local_20 & 0xff) == 0x45) {
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054cf58,DAT_0054cf54,DAT_0054cfc8,0xc99,
                       PTR_s_navigation_ui_reflash_page_handl_0054cf44);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054cf48,
                              PTR_s__navigation_ui_navigation_ui_ref_0054cf48);
        }
        FUN_0054cfd0(0);
      }
    }
  }
  return;
}

