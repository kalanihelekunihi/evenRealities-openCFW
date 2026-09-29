
bool dfu_image_crc_check_42d890(int *param_1,uint *param_2)

{
  undefined4 uVar1;
  int *piVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  uint uVar7;
  bool bVar8;
  uint local_20;
  
  local_20 = 0;
  uVar6 = (*param_2 & 0xffffff) - 8;
  uVar3 = stream_mode_42d84c(1);
  uVar1 = DAT_0042e108;
  iVar4 = FUN_004153a4(DAT_0042e108,uVar3);
  *param_1 = iVar4;
  if (*param_1 == 0) {
    elog_output(1,DAT_0042e118,DAT_0042e114,DAT_0042e110,0xcf,DAT_0042e10c,uVar1);
    bVar8 = false;
  }
  else {
    FUN_004154d2(*param_1,8,0);
    for (uVar7 = 0; piVar2 = DAT_0042e124, uVar1 = DAT_0042e11c,
        uVar7 < uVar6 / *(uint *)(*DAT_0042e124 + 4); uVar7 = uVar7 + 1) {
      iVar4 = FUN_00415484(DAT_0042e11c,1,*(undefined4 *)(*DAT_0042e124 + 4),*param_1);
      if (iVar4 != *(int *)(*piVar2 + 4)) {
        elog_output(1,DAT_0042e118,DAT_0042e114,DAT_0042e110,0xd7,DAT_0042e120,iVar4);
      }
      local_20 = crc32_table_42e1ec(uVar1,*(undefined4 *)(*piVar2 + 4),&local_20);
    }
    iVar4 = uVar6 - *(uint *)(*DAT_0042e124 + 4) * (uVar6 / *(uint *)(*DAT_0042e124 + 4));
    if (iVar4 != 0) {
      iVar5 = FUN_00415484(DAT_0042e11c,1,iVar4,*param_1);
      if (iVar5 != iVar4) {
        elog_output(1,DAT_0042e118,DAT_0042e114,DAT_0042e110,0xdf,DAT_0042e128,iVar5,iVar4);
      }
      local_20 = crc32_table_42e1ec(uVar1,iVar4,&local_20);
    }
    if (*param_1 != 0) {
      FUN_00415446(*param_1);
      *param_1 = 0;
    }
    elog_output(4,DAT_0042e118,DAT_0042e114,DAT_0042e110,0xe4,DAT_0042e130,local_20,
                *(undefined4 *)(DAT_0042e12c + 4));
    bVar8 = local_20 == param_2[1];
  }
  return bVar8;
}

