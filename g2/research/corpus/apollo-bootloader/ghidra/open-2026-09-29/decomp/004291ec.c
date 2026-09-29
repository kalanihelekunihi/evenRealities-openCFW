
ulonglong FUN_004291ec(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  uint *puVar3;
  uint *puVar4;
  uint uVar5;
  uint uVar6;
  uint extraout_r3;
  uint *puVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  bool bVar13;
  uint in_fpscr;
  float fVar14;
  int iVar15;
  
  iVar15 = DAT_00429624;
  puVar7 = (uint *)(DAT_00429624 + param_1 * 4 + 4);
  puVar3 = (uint *)(DAT_00429624 + param_2 * 4 + 4);
  puVar4 = (uint *)(DAT_00429624 + 100);
  bVar1 = *(byte *)puVar4 & 0x7f;
  uVar8 = *puVar4;
  uVar9 = *puVar4;
  uVar5 = *puVar4;
  uVar6 = *(byte *)puVar3 & 0x7f;
  uVar10 = (*puVar3 & 0xfffffff) >> 0x15;
  uVar11 = (*puVar7 & 0xfffffff) >> 0x15;
  uVar12 = *(byte *)puVar7 & 0x7f;
  if (*DAT_00429628 << 0x1f < 0) {
    uVar6 = 0;
    while ((uVar6 < 0x3c && (-1 < *DAT_00429700 << 1))) {
      delay_us(1);
      uVar6 = uVar6 + 1;
    }
    spotmgr_timer_irq_service_42a04a();
    uVar6 = extraout_r3;
  }
  *DAT_00429704 = param_3;
  *DAT_00429708 = param_1;
  *DAT_0042970c = (*puVar7 & 0x1ffff) >> 7;
  puVar3 = DAT_00429710;
  *DAT_00429710 = (*puVar7 & 0x1fffff) >> 0x11;
  *DAT_00429714 = uVar11;
  *DAT_00429520 = uVar12;
  spotmgr_power_ton_adjust_42a1bc(param_3,param_1,puVar3,uVar6,param_2,bVar1,param_4);
  fVar14 = (float)VectorUnsignedToFloat
                            (uVar12 - (*(byte *)(iVar15 + 8) & 0x7f),(byte)(in_fpscr >> 0x16) & 3);
  iVar15 = (uint)(0.0 < fVar14 * DAT_0042951c) * (int)(fVar14 * DAT_0042951c);
  if (iVar15 + uVar12 < 0x80) {
    *DAT_00429a20 = *DAT_00429a20 & 0xffffff80 | iVar15 + uVar12 & 0x7f;
  }
  else {
    *DAT_00429a20 = *DAT_00429a20 | 0x7f;
  }
  if ((int)(uVar11 - uVar10) < 1) {
    iVar2 = 0;
  }
  else {
    iVar2 = (uVar11 - uVar10) * 2;
  }
  if (iVar2 + uVar10 < 0x80) {
    *DAT_00429a2c = *DAT_00429a2c & 0xffffff80 | iVar2 + uVar10 & 0x7f;
  }
  else {
    *DAT_00429a2c = *DAT_00429a2c | 0x7f;
  }
  delay_us(0x32);
  *DAT_00429a2c = uVar11 | *DAT_00429a2c & 0xffffff80;
  puVar3 = DAT_00429a28;
  *DAT_00429a28 = *DAT_00429a28 & 0xffffc3ff | ((*puVar7 & 0x1fffff) >> 0x11) << 10;
  *puVar3 = (*puVar7 & 0x1ffff) >> 7 | *puVar3 & 0xfffffc00;
  delay_us(5);
  *DAT_00429a20 = uVar12 | *DAT_00429a20 & 0xffffff80;
  puVar3 = DAT_00429df8;
  *DAT_00429df8 = *DAT_00429df8 & 0xfffffffc | 1;
  uVar6 = 0;
  while ((puVar4 = DAT_00429a24, uVar6 < 0x14 && ((*puVar3 & 7) >> 2 == 0))) {
    delay_us(1);
    uVar6 = uVar6 + 1;
  }
  *DAT_00429a24 = *DAT_00429a24 | 0x40;
  *puVar4 = *puVar4 | 8;
  *puVar4 = *puVar4 & 0xfdffffff;
  puVar4 = DAT_00429dfc;
  bVar13 = -1 < (int)(*DAT_00429dfc << 0x1a);
  if (bVar13) {
    *DAT_00429dfc = *DAT_00429dfc | 0x20;
    delay_us(1);
    delay_status_change(0xf,DAT_0042a078,0x1000000,0x1000000);
  }
  if (*DAT_0042a078 << 7 < 0) {
    *puVar3 = *puVar3 & 0xfffffffc | 2;
    uVar6 = 0;
    while ((uVar6 < 0x14 && ((*puVar3 & 7) >> 2 == 0))) {
      delay_us(1);
      uVar6 = uVar6 + 1;
    }
  }
  if (bVar13) {
    *puVar4 = *puVar4 & 0xffffffdf;
  }
  return CONCAT17((char)(uVar5 >> 0x15),
                  CONCAT16((char)(uVar9 >> 0xe),CONCAT15((char)(uVar8 >> 7),CONCAT14(bVar1,iVar15)))
                 ) & 0x7f7f7fffffffffff;
}

