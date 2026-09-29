
void service_nvdb_defaults_validate(void)

{
  int *piVar1;
  undefined4 uVar2;
  int iVar3;
  short sVar4;
  int local_20;
  uint local_1c;
  
  service_nvdb_defaults_get(&local_20);
  piVar1 = DAT_00510998;
  *DAT_00510998 = local_20;
  for (sVar4 = 0; (uint)(int)sVar4 < local_1c; sVar4 = sVar4 + 1) {
    if (*(int *)(*piVar1 + sVar4 * 0xc + 8) != 0) {
      iVar3 = SVC_FlashDBBlobRead(1,*(undefined4 *)(*piVar1 + sVar4 * 0xc),
                                  *(undefined4 *)(*piVar1 + sVar4 * 0xc + 4),
                                  *(uint *)(*piVar1 + sVar4 * 0xc + 8) & 0xffff);
      if (iVar3 == 0) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(1,DAT_005109a8,DAT_005109a4,DAT_005109a0,0x92,DAT_005109b0,(int)sVar4,
                       *(undefined4 *)(*piVar1 + sVar4 * 0xc));
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x4800000,DAT_005109b4,DAT_005109b4,(int)sVar4,
                              *(undefined4 *)(*piVar1 + sVar4 * 0xc));
        }
      }
      iVar3 = FUN_0046cacc(*(undefined4 *)(*piVar1 + sVar4 * 0xc),DAT_005109b8);
      if (iVar3 == 0) {
        nvdbSysDtMarkLegacyPsn();
        uVar2 = DAT_005109bc;
        iVar3 = SVC_ReadPSNFromOTP(DAT_005109bc,0);
        if (iVar3 == 0) {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(3,DAT_005109a8,DAT_005109a4,DAT_005109a0,0x9a,DAT_005109c4,uVar2,
                         DAT_005109c0);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0xc800000,DAT_005109c8,DAT_005109c8,uVar2,DAT_005109c0);
          }
          iVar3 = DAT_005109cc;
          FUN_00439be4(DAT_005109cc + 1,uVar2,0xe);
          *(undefined1 *)(iVar3 + 0xf) = 0;
        }
        else {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(1,DAT_005109a8,DAT_005109a4,DAT_005109a0,0xa0,DAT_0051099c);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x4000000,DAT_005109ac,DAT_005109ac);
          }
        }
      }
    }
  }
  return;
}

