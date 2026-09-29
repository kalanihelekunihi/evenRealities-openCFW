
void FUN_005322f6(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  char *pcVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  
  pcVar2 = *(char **)(param_2 + 4);
  bVar1 = pcVar2[3];
  uVar4 = (uint)bVar1;
  iVar5 = (uint)(byte)pcVar2[5] * 0x100 + (uint)(byte)pcVar2[4];
  if (*pcVar2 == '\a') {
    iVar6 = (uint)(byte)pcVar2[7] * 0x100 + (uint)(byte)pcVar2[6];
    iVar3 = FUN_0043d0ce(pcVar2 + 8);
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00532e8c,DAT_00532630,DAT_00532e88,0x210,DAT_00532e84,iVar6,iVar5,param_4);
    }
    iVar3 = FUN_0043d0ce();
    if (-1 < iVar3 << 0x1f) {
      iVar3 = FUN_0043d0ce();
      pcVar2 = (char *)(iVar3 << 0x1d);
      if (-1 < (int)pcVar2) goto LAB_005323ea;
    }
    pcVar2 = (char *)compress_log_output(0x10800000,DAT_00532e90,DAT_00532e90,iVar6,iVar5);
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00532e8c,DAT_00532630,DAT_00532e88,0x214,DAT_00532e94,iVar5);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_00532e98,DAT_00532e98,iVar5);
    }
    FUN_0043dacc(DAT_00532e9c,0x10,pcVar2 + 6,0x10);
    pcVar2 = pcVar2 + 0x16;
  }
LAB_005323ea:
  iVar5 = FUN_0043d0ce(pcVar2);
  if (iVar5 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00532e8c,DAT_00532630,DAT_00532e88,0x223,DAT_00532ea0,bVar1);
  }
  iVar5 = FUN_0043d0ce();
  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_00532ea4,DAT_00532ea4,bVar1);
  }
  if ((int)(uVar4 << 0x1f) < 0) {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00532e8c,DAT_00532630,DAT_00532e88,0x224,DAT_00532ea8);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00532eac,DAT_00532eac);
    }
  }
  if ((int)(uVar4 << 0x1e) < 0) {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00532e8c,DAT_00532630,DAT_00532e88,0x225,DAT_00532eb0);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00532ff0,DAT_00532ff0);
    }
  }
  if ((int)(uVar4 << 0x1d) < 0) {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00532e8c,DAT_00532630,DAT_00532e88,0x226,DAT_00532ff4);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00532ff8,DAT_00532ff8);
    }
  }
  if ((int)(uVar4 << 0x1c) < 0) {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00532e8c,DAT_00532630,DAT_00532e88,0x227,DAT_00533000);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00533008,DAT_00533008);
    }
  }
  if ((int)(uVar4 << 0x1b) < 0) {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00532e8c,DAT_00532630,DAT_00532e88,0x228,DAT_0053300c);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00533010,DAT_00533010);
    }
  }
  if ((int)(uVar4 << 0x1a) < 0) {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00532e8c,DAT_00532630,DAT_00532e88,0x229,DAT_00533014);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00533018,DAT_00533018);
    }
  }
  if ((int)(uVar4 << 0x19) < 0) {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00532e8c,DAT_00532630,DAT_00532e88,0x22a,DAT_0053301c);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00533280,DAT_00533280);
    }
  }
  return;
}

