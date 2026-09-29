
undefined8 FUN_00429524(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  byte bVar2;
  uint *puVar3;
  uint *puVar4;
  uint uVar5;
  uint uVar6;
  byte local_28 [4];
  undefined4 uStack_24;
  
  uStack_24 = param_4;
  puVar4 = (uint *)(DAT_00429624 + param_1 * 4 + 4);
  puVar3 = (uint *)(DAT_00429624 + 100);
  local_28[0] = *(byte *)puVar3 & 0x7f;
  local_28[1] = (byte)(*puVar3 >> 7) & 0x7f;
  local_28[2] = (byte)(*puVar3 >> 0xe) & 0x7f;
  local_28[3] = (byte)(*puVar3 >> 0x15) & 0x7f;
  uVar5 = (*puVar4 & 0xfffffff) >> 0x15;
  bVar1 = *(byte *)puVar4;
  bVar2 = local_28[param_1 & 3];
  if (*DAT_00429628 << 0x1f < 0) {
    uVar6 = 0;
    while ((uVar6 < 0x3c && (-1 < *DAT_00429700 << 1))) {
      delay_us(1);
      uVar6 = uVar6 + 1;
    }
    spotmgr_timer_irq_service_42a04a();
  }
  *DAT_00429704 = param_3;
  *DAT_00429708 = param_1;
  *DAT_0042970c = (*puVar4 & 0x1ffff) >> 7;
  *DAT_00429710 = (*puVar4 & 0x1fffff) >> 0x11;
  *DAT_00429714 = uVar5;
  *DAT_0042a07c = bVar1 & 0x7f;
  *DAT_0042a080 = *DAT_0042a080 & 0xffffff80 | bVar2 & 0x7f;
  puVar3 = DAT_00429a28;
  *DAT_00429a28 = *DAT_00429a28 & 0xffffc3ff | ((*puVar4 & 0x1fffff) >> 0x11) << 10;
  *puVar3 = (*puVar4 & 0x1ffff) >> 7 | *puVar3 & 0xfffffc00;
  *DAT_00429a2c = uVar5 | *DAT_00429a2c & 0xffffff80;
  return CONCAT44(uStack_24,
                  CONCAT13(local_28[3],CONCAT12(local_28[2],CONCAT11(local_28[1],local_28[0]))));
}

