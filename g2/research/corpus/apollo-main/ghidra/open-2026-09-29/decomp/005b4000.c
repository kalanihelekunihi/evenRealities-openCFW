
/* WARNING: Removing unreachable block (ram,0x005b4086) */

void FUN_005b4000(int param_1,ushort param_2)

{
  short sVar1;
  int iVar2;
  ushort uVar3;
  ushort uVar4;
  
  iVar2 = DAT_005b484c;
  uVar3 = 0;
  uVar4 = 0;
  FUN_0043c0e4(DAT_005b484c + 10,0x6d62,0);
  *(undefined2 *)(iVar2 + 6) = 0;
  if ((param_1 == 0) || (param_2 == 0)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,DAT_005b485c,DAT_005b4858,DAT_005b4854,0x70,DAT_005b4850);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_005b4860,DAT_005b4860);
    }
  }
  else {
    while (((uVar3 < param_2 && (uVar4 < 14000)) &&
           (sVar1 = FUN_005b3f94((uint)uVar3 + param_1,param_2 - uVar3,0x220), sVar1 != 0))) {
      *(ushort *)(iVar2 + (uint)uVar4 * 2 + 10) = uVar3;
      uVar4 = uVar4 + 1;
      uVar3 = sVar1 + uVar3;
    }
    *(ushort *)(iVar2 + (uint)uVar4 * 2 + 10) = uVar3;
    *(ushort *)(iVar2 + 6) = uVar4;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,DAT_005b485c,DAT_005b4858,DAT_005b4854,0x8d,DAT_005b4864,param_2,uVar3,uVar4,
                   0x220,uVar3 < param_2);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xd400000,DAT_005b4868,DAT_005b4868,param_2,uVar3,uVar4,0x220,
                          uVar3 < param_2);
    }
  }
  return;
}

