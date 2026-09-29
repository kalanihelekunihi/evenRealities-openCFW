
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
even_ai_create_dialog_node
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  
  bVar1 = 0;
  do {
    if (4 < bVar1) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_2 = 0x741;
        FUN_0043d574(1,PTR_s_even_ai_ui_004e6a7c,PTR_s_D__01_workspace_s200_ap510b_iar__004e6a78,
                     _DAT_004e74c8,0x741,_DAT_004e74c4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,_DAT_004e7500);
      }
      iVar2 = 0;
LAB_004e69dc:
      return CONCAT44(param_2,iVar2);
    }
    if (*(char *)((uint)bVar1 * 0x24 + _DAT_004e716c + 0x1c) == '\0') {
      iVar2 = _DAT_004e716c + (uint)bVar1 * 0x24;
      FUN_0043c0e4(iVar2,0x24,0,_DAT_004e716c,param_2,param_3,param_4);
      *(undefined1 *)(iVar2 + 0x1c) = 1;
      *(undefined4 *)(iVar2 + 0x20) = 0;
      goto LAB_004e69dc;
    }
    bVar1 = bVar1 + 1;
  } while( true );
}

