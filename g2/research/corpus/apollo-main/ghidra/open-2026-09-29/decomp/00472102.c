
undefined4 sync_info_fn_00472102(int param_1,undefined4 param_2,undefined4 param_3)

{
  char *pcVar1;
  char cVar2;
  int iVar3;
  undefined1 auStack_34 [12];
  int local_28;
  undefined1 auStack_24 [16];
  
  pcVar1 = DAT_00472228;
  if (param_1 == 0) {
    FUN_0043c0e4(DAT_00472228,0xc,0);
    FUN_0048f49c(auStack_24,param_2,param_3);
    FUN_00439c04(auStack_34,auStack_24,0x10);
    cVar2 = FUN_00490120(auStack_34,DAT_004721fc,pcVar1);
    if (cVar2 == '\0') {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        iVar3 = DAT_0047222c;
        if (local_28 != 0) {
          iVar3 = local_28;
        }
        FUN_0043d574(1,DAT_0047220c,DAT_00472208,DAT_00472234,0x8c,DAT_00472230,iVar3);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        iVar3 = DAT_0047222c;
        if (local_28 != 0) {
          iVar3 = local_28;
        }
        compress_log_output(0x4400000,DAT_00472238,DAT_00472238,iVar3);
      }
    }
    else {
      cVar2 = *pcVar1;
      if (cVar2 == '\0') {
        sync_info_fn_00471ee8(pcVar1[1]);
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(2,DAT_0047220c,DAT_00472208,DAT_00472234,0x9a,DAT_0047223c,cVar2);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x8400000,DAT_00472240,DAT_00472240,cVar2);
        }
      }
    }
  }
  return 0;
}

