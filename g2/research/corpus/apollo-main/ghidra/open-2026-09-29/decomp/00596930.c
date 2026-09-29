
undefined8 FUN_00596930(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;
  
  iVar2 = FUN_005967bc();
  puVar1 = DAT_00596998;
  if (iVar2 == 0) {
    uVar3 = 0;
  }
  else {
    if (DAT_00596998[1] == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_3 = 0x1a6;
        FUN_0043d574(3,DAT_00596a8c,DAT_00596a88,PTR_s_conversate_tag_get_data_by_auto__00596ae8,
                     0x1a6,PTR_s_Auto_disp_node_is_NULL__set_to_h_00596ae4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__conversate_tag_Auto_disp_node_i_00596aec,
                            PTR_s__conversate_tag_Auto_disp_node_i_00596aec);
      }
      puVar1[1] = *puVar1;
    }
    else {
      DAT_00596998[1] = *(undefined4 *)(DAT_00596998[1] + 0x18);
    }
    uVar3 = puVar1[1];
  }
  return CONCAT44(param_3,uVar3);
}

