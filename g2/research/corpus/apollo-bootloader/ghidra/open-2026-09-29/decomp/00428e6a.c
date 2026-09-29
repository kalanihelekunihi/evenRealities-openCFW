
ulonglong FUN_00428e6a(int param_1,int param_2,undefined4 param_3)

{
  undefined1 uVar1;
  uint *puVar2;
  int iVar3;
  uint *puVar4;
  uint *puVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  bool bVar13;
  
  puVar4 = (uint *)(DAT_00429624 + param_1 * 4 + 4);
  puVar5 = (uint *)(DAT_00429624 + 100);
  uVar1 = *(undefined1 *)puVar5;
  uVar7 = *puVar5;
  uVar8 = *puVar5;
  uVar6 = *puVar5;
  uVar9 = *(byte *)(DAT_00429624 + param_2 * 4 + 4) & 0x7f;
  uVar10 = (*puVar4 & 0xfffffff) >> 0x15;
  uVar11 = *(byte *)puVar4 & 0x7f;
  if (*DAT_00429628 << 0x1f < 0) {
    uVar12 = 0;
    while ((uVar12 < 0x3c && (-1 < *DAT_00429700 << 1))) {
      delay_us(1);
      uVar12 = uVar12 + 1;
    }
    spotmgr_timer_irq_service_42a04a();
  }
  *DAT_00429704 = param_3;
  *DAT_00429708 = param_1;
  *DAT_0042970c = (*puVar4 & 0x1ffff) >> 7;
  *DAT_00429710 = (*puVar4 & 0x1fffff) >> 0x11;
  *DAT_00429714 = uVar10;
  *DAT_00429520 = uVar11;
  puVar5 = DAT_004291e0;
  *DAT_004291e0 = *DAT_004291e0 & 0xfffffffc | 1;
  uVar12 = 0;
  while ((puVar2 = DAT_00429a24, uVar12 < 0x14 && ((*puVar5 & 7) >> 2 == 0))) {
    delay_us(1);
    uVar12 = uVar12 + 1;
  }
  *DAT_00429a24 = *DAT_00429a24 & 0xffffffbf;
  *puVar2 = *puVar2 & 0xfffffff7;
  *puVar2 = *puVar2 | 0x2000000;
  puVar2 = DAT_004291e4;
  bVar13 = -1 < (int)(*DAT_004291e4 << 0x1a);
  if (bVar13) {
    *DAT_004291e4 = *DAT_004291e4 | 0x20;
    delay_us(1);
    delay_status_change(0xf,DAT_004291e8,0x1000000,0x1000000);
  }
  if (*DAT_004291e8 << 7 < 0) {
    *puVar5 = *puVar5 & 0xfffffffc | 2;
    uVar12 = 0;
    while ((uVar12 < 0x14 && ((*puVar5 & 7) >> 2 == 0))) {
      delay_us(1);
      uVar12 = uVar12 + 1;
    }
  }
  if (bVar13) {
    *puVar2 = *puVar2 & 0xffffffdf;
  }
  puVar5 = DAT_00429a28;
  *DAT_00429a28 = *DAT_00429a28 & 0xffffc3ff | ((*puVar4 & 0x1fffff) >> 0x11) << 10;
  *puVar5 = (*puVar4 & 0x1ffff) >> 7 | *puVar5 & 0xfffffc00;
  *DAT_00429a2c = uVar10 | *DAT_00429a2c & 0xffffff80;
  if ((int)(uVar11 - uVar9) < 1) {
    iVar3 = 0;
  }
  else {
    iVar3 = (uVar11 - uVar9) * 2;
  }
  if (iVar3 + uVar9 < 0x80) {
    *DAT_00429da0 = *DAT_00429da0 & 0xffffff80 | iVar3 + uVar9 & 0x7f;
  }
  else {
    *DAT_00429da0 = *DAT_00429da0 | 0x7f;
  }
  delay_us(0x32);
  *DAT_00429da0 = uVar11 | *DAT_00429da0 & 0xffffff80;
  spotmgr_power_ton_adjust_42a1bc(param_3,param_1);
  return CONCAT17((char)(uVar6 >> 0x15),
                  CONCAT16((char)(uVar8 >> 0xe),CONCAT15((char)(uVar7 >> 7),CONCAT14(uVar1,puVar4)))
                 ) & 0x7f7f7f7fffffffff;
}

