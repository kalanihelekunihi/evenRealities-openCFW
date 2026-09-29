
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_00493bdc(int param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  
  if ((param_1 == 0) || (param_2 == 0)) {
    iVar1 = FUN_0043d0ce();
    uVar3 = param_2;
    if (iVar1 << 0x1e < 0) {
      uVar3 = 0xe7;
      FUN_0043d574(1,DAT_004940c0,DAT_004940bc,PTR_s_evenhub_container_list_create_fr_00494458,0xe7,
                   PTR_s_evenhub_container_list_create_fr_00494454,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__evenhub_ui_evenhub_container_li_0049445c);
    }
    uVar2 = 0xffffffff;
  }
  else {
    FUN_00493d02(param_1);
    uVar3 = (uint)*(ushort *)(param_2 + 0x1558);
    iVar1 = FUN_00493722(param_1,param_2 + 8,*(undefined2 *)(param_2 + 4),param_2 + 0x155c,uVar3,
                         param_2 + 0x36a0,*(undefined2 *)(param_2 + 0x369c));
    if (iVar1 == 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar3 = 0xf7;
        FUN_0043d574(3,DAT_004940c0,DAT_004940bc,PTR_s_evenhub_container_list_create_fr_00494458,
                     0xf7,PTR_s_evenhub_container_list_create_fr_00494468,
                     *(undefined4 *)(param_1 + 0xc));
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc400000,_DAT_004945e4,_DAT_004945e4,*(undefined4 *)(param_1 + 0xc));
      }
      uVar2 = 0;
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar3 = 0xf2;
        FUN_0043d574(1,DAT_004940c0,DAT_004940bc,PTR_s_evenhub_container_list_create_fr_00494458,
                     0xf2,PTR_s_evenhub_container_list_create_fr_00494460);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__evenhub_ui_evenhub_container_li_00494464,
                            PTR_s__evenhub_ui_evenhub_container_li_00494464);
      }
      FUN_00493d02(param_1);
      uVar2 = 0xffffffff;
    }
  }
  return CONCAT44(uVar3,uVar2);
}

