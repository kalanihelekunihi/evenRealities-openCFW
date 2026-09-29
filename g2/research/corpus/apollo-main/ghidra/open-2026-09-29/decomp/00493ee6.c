
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int FUN_00493ee6(int param_1,code *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  if ((param_1 == 0) || (param_2 == (code *)0x0)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004940c0,DAT_004940bc,PTR_s_evenhub_container_list_traverse_00494604,0x13c,
                   PTR_s_evenhub_container_list_traverse__00494600,param_3,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__evenhub_ui_evenhub_container_li_00494608,
                          PTR_s__evenhub_ui_evenhub_container_li_00494608);
    }
    iVar1 = -1;
  }
  else {
    iVar1 = 0;
    for (iVar3 = *(int *)(param_1 + 4); iVar3 != 0; iVar3 = *(int *)(iVar3 + 4)) {
      iVar2 = (*param_2)(iVar3,param_3);
      if (iVar2 != 0) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004940c0,DAT_004940bc,PTR_s_evenhub_container_list_traverse_00494604,
                       0x146,PTR_s_evenhub_container_list_traverse__0049460c,iVar2);
        }
        iVar3 = FUN_0043d0ce();
        if ((-1 < iVar3 << 0x1f) && (iVar3 = FUN_0043d0ce(), -1 < iVar3 << 0x1d)) {
          return iVar1;
        }
        compress_log_output(0x10400000,_DAT_004949b0,_DAT_004949b0,iVar2);
        return iVar1;
      }
      iVar1 = iVar1 + 1;
    }
  }
  return iVar1;
}

