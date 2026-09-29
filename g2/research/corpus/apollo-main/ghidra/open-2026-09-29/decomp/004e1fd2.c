
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_004e1fd2(uint param_1,undefined *param_2,uint param_3,undefined4 param_4)

{
  char cVar1;
  int iVar2;
  uint uVar3;
  undefined *puVar4;
  uint uVar5;
  
  uVar3 = param_1;
  puVar4 = param_2;
  uVar5 = param_3;
  cVar1 = FUN_0045a568();
  if (cVar1 == '\x01') {
    if ((param_1 & 0xff) == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        uVar3 = 0x67;
        puVar4 = PTR_s_try_to_start_evenai_004e2a44;
        FUN_0043d574(3,PTR_s_even_ai_page_004e2a50,PTR_s_D__01_workspace_s200_ap510b_iar__004e2a4c,
                     PTR_s_even_ai_display_ctrl_004e2a48);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__even_ai_page_try_to_start_evena_004e2a54,
                            PTR_s__even_ai_page_try_to_start_evena_004e2a54);
      }
      if (*(int *)(_DAT_004e2c24 + 4) == 0) {
        FUN_00464b2e(7,param_2,param_3 & 0xffff,0);
      }
      else {
        FUN_0045a8ee(7,0,0,*(undefined4 *)(_DAT_004e2c24 + 4));
      }
    }
    else if ((param_1 & 0xff) == 1) {
      iVar2 = FUN_00443484();
      if ((iVar2 == 1) && (iVar2 = FUN_004434d0(7), iVar2 == 1)) {
        FUN_00464bb2(7,param_2,param_3 & 0xffff,0,uVar3,puVar4,uVar5);
      }
    }
    else if ((param_1 & 0xff) == 2) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        uVar3 = 0x7a;
        puVar4 = PTR_s_try_to_stop_evenai__enable____d_004e2a58;
        FUN_0043d574(4,PTR_s_even_ai_page_004e2a50,PTR_s_D__01_workspace_s200_ap510b_iar__004e2a4c,
                     PTR_s_even_ai_display_ctrl_004e2a48,0x7a,
                     PTR_s_try_to_stop_evenai__enable____d_004e2a58,*_DAT_004e2c24,param_4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10400000,PTR_s__even_ai_page_try_to_stop_evenai_004e2c28,
                            PTR_s__even_ai_page_try_to_stop_evenai_004e2c28,*_DAT_004e2c24);
      }
      if (*_DAT_004e2c24 == '\x01') {
        FUN_00464c36(7,param_2,param_3 & 0xffff,0);
      }
    }
  }
  return CONCAT44(puVar4,uVar3);
}

