
undefined8 FUN_0045accc(undefined2 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  
  uVar4 = param_3;
  uVar3 = param_4;
  puVar1 = (undefined1 *)file_heap_allocate(0xe);
  if (puVar1 == (undefined1 *)0x0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uVar4 = 0x122;
      FUN_0043d574(2,DAT_0045b100,DAT_0045b0fc,DAT_0045b840,0x122,DAT_0045b83c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_0045b844,DAT_0045b844);
    }
    uVar3 = 0xffffffff;
  }
  else {
    *puVar1 = (char)param_4;
    puVar1[1] = (char)((uint)param_4 >> 8);
    puVar1[2] = (char)((uint)param_4 >> 0x10);
    puVar1[3] = (char)((uint)param_4 >> 0x18);
    puVar1[4] = (char)param_1;
    puVar1[5] = (char)((ushort)param_1 >> 8);
    puVar1[6] = (char)param_2;
    puVar1[7] = (char)((uint)param_2 >> 8);
    puVar1[8] = (char)((uint)param_2 >> 0x10);
    puVar1[9] = (char)((uint)param_2 >> 0x18);
    puVar1[10] = (char)param_3;
    puVar1[0xb] = (char)((uint)param_3 >> 8);
    puVar1[0xc] = (char)((uint)param_3 >> 0x10);
    puVar1[0xd] = (char)((uint)param_3 >> 0x18);
    uVar4 = 0;
    iVar2 = FUN_00491184(DAT_0045b848,0,puVar1,0xe,0,uVar3);
    if (iVar2 == 0) {
      uVar3 = 0;
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        uVar4 = 0x136;
        FUN_0043d574(2,DAT_0045b100,DAT_0045b0fc,DAT_0045b840,0x136,DAT_0045b134);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_0045b138,DAT_0045b138);
      }
      file_heap_free(puVar1);
      uVar3 = 0xffffffff;
    }
  }
  return CONCAT44(uVar4,uVar3);
}

