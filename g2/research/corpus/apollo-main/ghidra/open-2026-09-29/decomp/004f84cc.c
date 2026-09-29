
undefined8 FUN_004f84cc(ushort *param_1,undefined4 param_2)

{
  ushort *puVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  iVar3 = 0;
  iVar4 = 0;
  quicklist_lock_storage();
  for (iVar5 = 0; puVar1 = DAT_004f8628, iVar2 = iVar4, iVar5 < (int)(uint)*DAT_004f8628;
      iVar5 = iVar5 + 1) {
    if (*(char *)((int)DAT_004f8628 + iVar5 * 0x128 + 0x129) == '\0') {
      if (iVar4 != iVar5) {
        FUN_00439be4(DAT_004f8628 + iVar4 * 0x94 + 4,DAT_004f8628 + iVar5 * 0x94 + 4,0x128);
      }
      iVar4 = iVar4 + 1;
    }
    else {
      iVar3 = iVar3 + 1;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_1 = (ushort *)0xc3d;
        param_2 = DAT_004f8fec;
        FUN_0043d574(4,DAT_004f8918,DAT_004f8914,DAT_004f8ff0,0xc3d,DAT_004f8fec,
                     *(undefined4 *)(puVar1 + iVar5 * 0x94 + 0x8a),puVar1 + iVar5 * 0x94 + 4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        param_1 = puVar1 + iVar5 * 0x94 + 4;
        compress_log_output(0x10800000,DAT_004f8ff4,DAT_004f8ff4,
                            *(undefined4 *)(puVar1 + iVar5 * 0x94 + 0x8a));
      }
    }
  }
  for (; iVar2 < (int)(uint)*puVar1; iVar2 = iVar2 + 1) {
    FUN_0043c0e4(puVar1 + iVar2 * 0x94 + 4,0x128,0);
  }
  *puVar1 = (ushort)iVar4;
  if (0 < iVar3) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      param_1 = (ushort *)0xc4b;
      param_2 = DAT_004f8ff8;
      FUN_0043d574(4,DAT_004f8918,DAT_004f8914,DAT_004f8ff0,0xc4b,DAT_004f8ff8,iVar3,*puVar1);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      param_1 = (ushort *)(uint)*puVar1;
      compress_log_output(0x10800000,DAT_004f9344,DAT_004f9344,iVar3);
    }
  }
  quicklist_unlock_storage();
  return CONCAT44(param_2,param_1);
}

