
int SVC_Settings_GetMaxLum(void)

{
  char cVar1;
  char *pcVar2;
  int iVar3;
  undefined *puVar4;
  byte bVar5;
  uint uVar6;
  uint in_fpscr;
  int iVar7;
  float fVar8;
  float afStack_44 [11];
  
  FUN_00439c04(afStack_44,DAT_0046c6e4,0x2c);
  pcVar2 = (char *)SVC_NvdbGetSysData(5);
  bVar5 = *pcVar2 - 5;
  if (10 < (byte)(*pcVar2 - 5U)) {
    bVar5 = 10;
  }
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(4,PTR_s_service_settings_0046c664,DAT_0046c660,DAT_0046c6ec,0x1ec,DAT_0046c6e8,
                 bVar5);
  }
  iVar3 = FUN_0043d0ce();
  if (-1 < iVar3 << 0x1f) {
    iVar3 = FUN_0043d0ce();
    if (-1 < iVar3 << 0x1d) goto LAB_0046c2b6;
  }
  compress_log_output(0x10400000,DAT_0046c6f0,DAT_0046c6f0,bVar5);
LAB_0046c2b6:
  cVar1 = FUN_0045a568();
  if (cVar1 == '\x01') {
    uVar6 = (uint)*(byte *)(DAT_0046c6a8 + 0x17);
  }
  else if (cVar1 == '\x02') {
    uVar6 = (uint)*(byte *)(DAT_0046c6a8 + 0x16);
  }
  else {
    uVar6 = 0;
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(2,PTR_s_service_settings_0046c664,DAT_0046c660,DAT_0046c6ec,0x1f8,DAT_0046c6f4,
                   cVar1);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_0046c6f8,DAT_0046c6f8,cVar1);
    }
  }
  if (10 < uVar6) {
    uVar6 = 10;
  }
  fVar8 = (float)VectorUnsignedToFloat((uVar6 * 0x834) / 10,(byte)(in_fpscr >> 0x16) & 3);
  fVar8 = afStack_44[bVar5] * DAT_0046c508 - fVar8;
  iVar7 = (uint)(0.0 < fVar8) * (int)fVar8;
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    if (cVar1 == '\x01') {
      puVar4 = &DAT_0046c5f4;
    }
    else if (cVar1 == '\x02') {
      puVar4 = &DAT_0046c5f8;
    }
    else {
      puVar4 = &LAB_0046c5fc;
    }
    FUN_0043d574(3,PTR_s_service_settings_0046c664,DAT_0046c660,DAT_0046c6ec,0x204,DAT_0046c6fc,
                 puVar4,*pcVar2,bVar5,uVar6,iVar7);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    if (cVar1 == '\x01') {
      puVar4 = &DAT_0046c5f4;
    }
    else if (cVar1 == '\x02') {
      puVar4 = &DAT_0046c5f8;
    }
    else {
      puVar4 = &LAB_0046c5fc;
    }
    compress_log_output(0xd400000,DAT_0046c700,DAT_0046c700,puVar4,*pcVar2,bVar5,uVar6,iVar7);
  }
  return iVar7;
}

