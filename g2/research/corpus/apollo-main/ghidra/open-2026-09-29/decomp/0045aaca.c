
undefined4 FUN_0045aaca(undefined4 param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  
  uVar3 = param_2;
  iVar2 = param_3;
  uVar4 = param_4;
  puVar1 = (undefined1 *)file_heap_allocate(param_3 + 4);
  if (puVar1 == (undefined1 *)0x0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,DAT_0045b100,DAT_0045b0fc,DAT_0045b6d8,0xfb,DAT_0045b124,param_3);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_0045b12c,DAT_0045b12c,param_3);
    }
    uVar3 = 0xffffffff;
  }
  else {
    *puVar1 = (char)param_4;
    puVar1[1] = (char)((uint)param_4 >> 8);
    puVar1[2] = (char)((uint)param_4 >> 0x10);
    puVar1[3] = (char)((uint)param_4 >> 0x18);
    FUN_00439be4(puVar1 + 4,param_2,param_3);
    iVar2 = FUN_00491184(DAT_0045b6dc,param_1,puVar1,param_3 + 4,0,uVar3,iVar2,uVar4);
    if (iVar2 == 0) {
      uVar3 = 0;
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0045b100,DAT_0045b0fc,DAT_0045b6d8,0x105,DAT_0045b134);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_0045b138,DAT_0045b138);
      }
      file_heap_free(puVar1);
      uVar3 = 0xffffffff;
    }
  }
  return uVar3;
}

