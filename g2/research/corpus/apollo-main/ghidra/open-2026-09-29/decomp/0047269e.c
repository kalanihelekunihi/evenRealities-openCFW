
undefined4 FUN_0047269e(int param_1,ushort param_2)

{
  char cVar1;
  undefined4 uVar2;
  int iVar3;
  int *piVar4;
  
  if (param_1 == 0) {
    uVar2 = 0xffffffff;
  }
  else {
    if (7 < param_2) {
      piVar4 = (int *)(param_1 + 7);
      if (((*(char *)(param_1 + 4) != '\b') && (*DAT_00472bf8 != 0)) &&
         ((uint)(*piVar4 - *DAT_00472bf8) < 100)) {
        return 0;
      }
      *DAT_00472bf8 = *piVar4;
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00472bbc,DAT_00472bb8,DAT_00472c00,500,DAT_00472bfc,*piVar4,
                     *(undefined1 *)(param_1 + 4));
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10800000,DAT_00472c04,DAT_00472c04,*piVar4,
                            *(undefined1 *)(param_1 + 4));
      }
    }
    if (*(char *)(param_1 + 3) == '\0') {
      cVar1 = *(char *)(param_1 + 4);
      if (cVar1 == '\0') {
        FUN_004c5916(4,3,0,0);
      }
      else if (cVar1 == '\x01') {
        FUN_004c5916(4,0,0,0);
      }
      else if (cVar1 == '\x02') {
        FUN_004c5916(4,1,0,0);
      }
      else if (cVar1 == '\x04') {
        FUN_004c5916(4,5,*(undefined1 *)(param_1 + 5),*(undefined1 *)(param_1 + 6));
      }
      else if (cVar1 == '\x05') {
        FUN_004c5916(4,4,*(undefined1 *)(param_1 + 5),*(undefined1 *)(param_1 + 6));
      }
      else if (cVar1 == '\b') {
        FUN_004c5916(4,0xe,0,0);
      }
    }
    uVar2 = 0;
  }
  return uVar2;
}

