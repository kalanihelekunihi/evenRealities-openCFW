
int TouchSendAppFile(int param_1,int param_2)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  ushort uVar4;
  ushort uVar5;
  uint uVar6;
  uint uVar7;
  short sVar8;
  uint uVar9;
  undefined1 auStack_ac [132];
  int local_28;
  
  iVar3 = 0xf;
  uVar4 = 0;
  uVar5 = 0;
  uVar6 = (param_2 + 0x7f) / 0x80;
  uVar7 = uVar6 << 7;
  uVar6 = (uVar6 & 0x1ffffff) * 4 - 1;
  local_28 = param_1;
  FUN_0043c0e4(auStack_ac,0x80,0xff);
  sVar8 = (short)uVar6;
  while( true ) {
    if (sVar8 < 0) {
      return iVar3;
    }
    uVar9 = uVar7;
    if (0x1f < uVar7) {
      uVar9 = 0x20;
    }
    FUN_00439be4(auStack_ac + (uint)uVar5 * 0x20,local_28 + ((uVar6 & 0xffff) - (int)sVar8) * 0x20,
                 uVar9 & 0xffff);
    iVar3 = TouchSendOnePacket(auStack_ac + (uint)uVar5 * 0x20,0x20);
    if (iVar3 != 0) break;
    uVar7 = uVar7 - (uVar9 & 0xffff);
    uVar5 = uVar5 + 1;
    if (3 < uVar5) {
      uVar1 = semantic_TouchCrc32(auStack_ac,(uint)uVar5 << 5);
      iVar3 = TouchProgramData((uint)uVar5 * (uint)uVar4 * 0x20,uVar1);
      if (iVar3 != 0) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(1,DAT_005608c8,DAT_005608c4,DAT_00561084,0x28a,DAT_00561080,iVar3);
        }
        iVar2 = FUN_0043d0ce();
        if ((-1 < iVar2 << 0x1f) && (iVar2 = FUN_0043d0ce(), -1 < iVar2 << 0x1d)) {
          return iVar3;
        }
        compress_log_output(0x4400000,DAT_00561088,DAT_00561088,iVar3);
        return iVar3;
      }
      uVar5 = 0;
      uVar4 = uVar4 + 1;
      FUN_0043c0e4(auStack_ac,0x80,0xff);
    }
    iVar3 = 0;
    sVar8 = sVar8 + -1;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(1,DAT_005608c8,DAT_005608c4,DAT_00561084,0x27e,DAT_00561080,iVar3);
  }
  iVar2 = FUN_0043d0ce();
  if ((-1 < iVar2 << 0x1f) && (iVar2 = FUN_0043d0ce(), -1 < iVar2 << 0x1d)) {
    return iVar3;
  }
  compress_log_output(0x4400000,DAT_00561088,DAT_00561088,iVar3);
  return iVar3;
}

