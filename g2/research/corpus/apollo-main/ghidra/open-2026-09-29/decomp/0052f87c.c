
undefined4 FUN_0052f87c(int param_1,uint param_2)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 *puVar3;
  int iVar4;
  uint uVar5;
  
  if (param_2 < 5) {
    for (uVar5 = 0; iVar1 = DAT_0052ffc0, uVar5 < param_2; uVar5 = uVar5 + 1) {
      puVar3 = (undefined4 *)(uVar5 * 0xc + param_1);
      *(undefined4 *)(DAT_0052ffc0 + uVar5 * 0x10) = *puVar3;
      *(undefined4 *)(uVar5 * 0x10 + iVar1 + 4) = puVar3[1];
      *(undefined4 *)(uVar5 * 0x10 + iVar1 + 8) = puVar3[2];
      *(undefined4 *)(uVar5 * 0x10 + iVar1 + 0xc) = 0;
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0052ff50,DAT_0052ff4c,DAT_0052ffb8,0x108,DAT_0052ffc4,uVar5,
                     *(undefined4 *)(iVar1 + uVar5 * 0x10),*(undefined4 *)(uVar5 * 0x10 + iVar1 + 4)
                     ,*(undefined4 *)(uVar5 * 0x10 + iVar1 + 8));
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x11000000,DAT_0052ffc8,DAT_0052ffc8,uVar5,
                            *(undefined4 *)(iVar1 + uVar5 * 0x10),
                            *(undefined4 *)(uVar5 * 0x10 + iVar1 + 4),
                            *(undefined4 *)(uVar5 * 0x10 + iVar1 + 8));
      }
    }
    for (; param_2 < 4; param_2 = param_2 + 1) {
      FUN_0048949c(DAT_0052ffc0 + param_2 * 0x10,0x10);
    }
    uVar2 = 1;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0052ff50,DAT_0052ff4c,DAT_0052ffb8,0xf9,DAT_0052ffb4,param_2,4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4800000,DAT_0052ffbc,DAT_0052ffbc,param_2,4);
    }
    uVar2 = 0;
  }
  return uVar2;
}

