
undefined4 FUN_004df7f2(uint param_1,undefined *param_2,uint param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  
  if (param_1 < 0x10) {
    uVar1 = *(undefined4 *)(PTR_DAT_004e028c + param_1 * 4);
  }
  else {
    uVar3 = param_1;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uVar3 = 0x176;
      param_2 = PTR_s_get_color_from_index__invalid_co_004e0290;
      param_3 = param_1;
      FUN_0043d574(2,PTR_s_common_text_container_004dfa0c,DAT_004dfa08,
                   PTR_s_get_color_from_index_004e0294,0x176,
                   PTR_s_get_color_from_index__invalid_co_004e0290,param_1,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8400000,PTR_s__common_text_container_get_color_004e0298,
                          PTR_s__common_text_container_get_color_004e0298,param_1,uVar3,param_2,
                          param_3);
    }
    uVar1 = 0xffffff;
  }
  return uVar1;
}

