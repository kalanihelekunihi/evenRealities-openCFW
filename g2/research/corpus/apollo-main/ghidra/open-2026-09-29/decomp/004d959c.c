
void SVC_KvdbReadAll(void)

{
  int *piVar1;
  int iVar2;
  undefined4 in_r3;
  short sVar3;
  int local_1c;
  uint local_18;
  undefined4 uStack_14;
  
  uStack_14 = in_r3;
  SVC_KvdbDefaultDescriptor(&local_1c);
  piVar1 = DAT_004d9aa8;
  *DAT_004d9aa8 = local_1c;
  for (sVar3 = 0; (uint)(int)sVar3 < local_18; sVar3 = sVar3 + 1) {
    if (*(int *)(*piVar1 + sVar3 * 0xc + 8) != 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004d9ab8,DAT_004d9ab4,DAT_004d9ab0,0x8d,DAT_004d9aac,(int)sVar3,
                     *(undefined4 *)(*piVar1 + sVar3 * 0xc),
                     *(undefined4 *)(*piVar1 + sVar3 * 0xc + 8));
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10c00000,DAT_004d9abc,DAT_004d9abc,(int)sVar3,
                            *(undefined4 *)(*piVar1 + sVar3 * 0xc),
                            *(undefined4 *)(*piVar1 + sVar3 * 0xc + 8));
      }
      iVar2 = SVC_FlashDBBlobRead(0,*(undefined4 *)(*piVar1 + sVar3 * 0xc),
                                  *(undefined4 *)(*piVar1 + sVar3 * 0xc + 4),
                                  *(uint *)(*piVar1 + sVar3 * 0xc + 8) & 0xffff);
      if (iVar2 == 0) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(1,DAT_004d9ab8,DAT_004d9ab4,DAT_004d9ab0,0x90,DAT_004d9ac0,(int)sVar3,
                       *(undefined4 *)(*piVar1 + sVar3 * 0xc));
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x4800000,DAT_004d9ac4,DAT_004d9ac4,(int)sVar3,
                              *(undefined4 *)(*piVar1 + sVar3 * 0xc));
        }
      }
    }
  }
  return;
}

