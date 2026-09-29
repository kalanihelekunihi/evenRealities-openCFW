
undefined4 setting_parse_data_package(int param_1,undefined4 param_2,byte *param_3)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  uint local_28;
  undefined4 local_24;
  uint local_20;
  uint local_1c;
  undefined1 auStack_18 [12];
  uint local_c;
  
  if ((param_1 == 0) || (param_3 == (byte *)0x0)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_24 = DAT_0049bbc4;
      local_28 = 0x65;
      FUN_0043d574(1,DAT_0049bbc0,DAT_0049bbbc,DAT_0049bbc8);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0049bbcc,DAT_0049bbcc);
    }
    uVar3 = 0;
  }
  else {
    FUN_0048f49c(&local_28,param_1,param_2);
    FUN_00439c04(auStack_18,&local_28,0x10);
    cVar1 = FUN_00490120(auStack_18,DAT_0049bbd0,param_3);
    if (cVar1 == '\0') {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_20 = DAT_0049bbd4;
        if (local_c != 0) {
          local_20 = local_c;
        }
        local_24 = DAT_0049bbd8;
        local_28 = 0x6d;
        FUN_0043d574(1,DAT_0049bbc0,DAT_0049bbbc,DAT_0049bbc8);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        uVar4 = DAT_0049bbd4;
        if (local_c != 0) {
          uVar4 = local_c;
        }
        compress_log_output(0x4400000,DAT_0049bbdc,DAT_0049bbdc,uVar4);
      }
      uVar3 = 0;
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_1c = (uint)*(ushort *)(param_3 + 8);
        local_20 = (uint)*param_3;
        local_24 = DAT_0049bbe0;
        local_28 = 0x72;
        FUN_0043d574(4,DAT_0049bbc0,DAT_0049bbbc,DAT_0049bbc8);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        local_28 = (uint)*(ushort *)(param_3 + 8);
        compress_log_output(0x10800000,DAT_0049bbe4,DAT_0049bbe4,*param_3);
      }
      iVar2 = setting_is_duplicate_message(*(undefined4 *)(param_3 + 4));
      if (iVar2 == 0) {
        *DAT_0049bbf0 = (uint)*param_3;
        *DAT_0049bbf4 = *(undefined4 *)(param_3 + 4);
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          local_24 = DAT_0049bbf8;
          local_28 = 0x7e;
          FUN_0043d574(4,DAT_0049bbc0,DAT_0049bbbc,DAT_0049bbc8);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_0049bf98,DAT_0049bf98);
        }
        uVar3 = 1;
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          local_20 = *(uint *)(param_3 + 4);
          local_24 = DAT_0049bbe8;
          local_28 = 0x76;
          FUN_0043d574(2,DAT_0049bbc0,DAT_0049bbbc,DAT_0049bbc8);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x8400000,DAT_0049bbec,DAT_0049bbec,*(undefined4 *)(param_3 + 4));
        }
        uVar3 = 0;
      }
    }
  }
  return uVar3;
}

