
undefined8 FUN_005b41be(ushort *param_1,undefined4 param_2,undefined *param_3,undefined4 param_4)

{
  char *pcVar1;
  int iVar2;
  int *piVar3;
  int iVar4;
  uint uVar5;
  ushort *puVar6;
  int iVar7;
  
  pcVar1 = DAT_005b4888;
  iVar4 = DAT_005b4884;
  if (param_1 == (ushort *)0x0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      param_2 = 0xa0;
      param_3 = PTR_s_transcribe_data_is_NULL_005b4878;
      FUN_0043d574(1,DAT_005b485c,DAT_005b4858,PTR_s_conversate_transcribe_data_updat_005b487c,0xa0,
                   PTR_s_transcribe_data_is_NULL_005b4878,param_4);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__conversate_data_transcribe_data_005b4880,
                          PTR_s__conversate_data_transcribe_data_005b4880);
    }
  }
  else {
    puVar6 = (ushort *)(DAT_005b4884 + (uint)*(byte *)(DAT_005b4884 + 0x1008) * 0x402);
    if (*DAT_005b4888 == '\x01') {
      *DAT_005b4888 = '\0';
      if (*puVar6 < 0x401) {
        *(undefined1 *)((int)puVar6 + *puVar6 + 2) = 10;
        *puVar6 = *puVar6 + 1;
      }
      uVar5 = *(byte *)(iVar4 + 0x1008) + 1;
      *(char *)(iVar4 + 0x1008) = (char)uVar5 + (char)(uVar5 / 4) * -4;
      puVar6 = (ushort *)(iVar4 + (uint)*(byte *)(iVar4 + 0x1008) * 0x402);
    }
    FUN_0043c0e4(puVar6,0x402,0);
    FUN_00439be4(puVar6 + 1,param_1 + 1,*param_1);
    *puVar6 = *param_1;
    if (*(int *)(param_1 + 0x202) == 1) {
      *pcVar1 = '\x01';
    }
    iVar2 = DAT_005b488c;
    FUN_0043c0e4(DAT_005b488c,0x1008,0);
    piVar3 = DAT_005b4890;
    *DAT_005b4890 = 0;
    for (iVar7 = 0; iVar7 < 4; iVar7 = iVar7 + 1) {
      puVar6 = (ushort *)(iVar4 + ((int)(iVar7 + (uint)*(byte *)(iVar4 + 0x1008) + 1) % 4) * 0x402);
      if (*puVar6 != 0) {
        FUN_00439be4(iVar2 + *piVar3,puVar6 + 1,*puVar6);
        *piVar3 = *piVar3 + (uint)*puVar6;
      }
    }
  }
  return CONCAT44(param_3,param_2);
}

