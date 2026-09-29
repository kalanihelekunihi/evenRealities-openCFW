
undefined8 FUN_0042962c(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  byte bVar2;
  uint uVar3;
  uint *puVar4;
  uint *puVar5;
  uint uVar6;
  byte local_28 [4];
  undefined4 uStack_24;
  
  uStack_24 = param_4;
  puVar5 = (uint *)(DAT_0042a084 + param_1 * 4 + 4);
  puVar4 = (uint *)(DAT_0042a084 + 100);
  local_28[0] = *(byte *)puVar4 & 0x7f;
  local_28[1] = (byte)(*puVar4 >> 7) & 0x7f;
  local_28[2] = (byte)(*puVar4 >> 0xe) & 0x7f;
  local_28[3] = (byte)(*puVar4 >> 0x15) & 0x7f;
  uVar3 = *puVar5;
  bVar1 = *(byte *)puVar5;
  bVar2 = local_28[param_1 & 3];
  if (*DAT_0042a088 << 0x1f < 0) {
    uVar6 = 0;
    while ((uVar6 < 0x3c && (-1 < *DAT_00429700 << 1))) {
      delay_us(1);
      uVar6 = uVar6 + 1;
    }
    spotmgr_timer_irq_service_42a04a();
  }
  *DAT_00429704 = param_3;
  *DAT_00429708 = param_1;
  *DAT_0042970c = (*puVar5 & 0x1ffff) >> 7;
  *DAT_00429710 = (*puVar5 & 0x1fffff) >> 0x11;
  *DAT_00429714 = (uVar3 & 0xfffffff) >> 0x15;
  *DAT_0042a07c = bVar1 & 0x7f;
  *DAT_0042a080 = *DAT_0042a080 & 0xffffff80 | bVar2 & 0x7f;
  return CONCAT44(uStack_24,
                  CONCAT13(local_28[3],CONCAT12(local_28[2],CONCAT11(local_28[1],local_28[0]))));
}

