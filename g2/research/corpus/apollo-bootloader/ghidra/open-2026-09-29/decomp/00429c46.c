
uint FUN_00429c46(int param_1,int param_2,undefined4 param_3)

{
  int iVar1;
  uint uVar2;
  uint *puVar3;
  uint *puVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  bool bVar8;
  undefined4 local_28;
  
  puVar4 = (uint *)(DAT_0042a084 + param_1 * 4 + 4);
  puVar3 = (uint *)(DAT_0042a084 + 100);
  local_28 = CONCAT13((char)(*puVar3 >> 0x15),
                      CONCAT12((char)(*puVar3 >> 0xe),
                               CONCAT11((char)(*puVar3 >> 7),*(undefined1 *)puVar3))) & 0x7f7f7f7f;
  uVar5 = *(byte *)(DAT_0042a084 + param_2 * 4 + 4) & 0x7f;
  uVar2 = *puVar4;
  uVar6 = *(byte *)puVar4 & 0x7f;
  if (*DAT_0042a088 << 0x1f < 0) {
    uVar7 = 0;
    while ((uVar7 < 0x3c && (-1 < *DAT_0042a1b4 << 1))) {
      delay_us(1);
      uVar7 = uVar7 + 1;
    }
    spotmgr_timer_irq_service_42a04a();
  }
  *DAT_0042a1b8 = param_3;
  *DAT_0042a2a4 = param_1;
  *DAT_0042a2a8 = (*puVar4 & 0x1ffff) >> 7;
  *DAT_0042a2ac = (*puVar4 & 0x1fffff) >> 0x11;
  *DAT_0042a2b0 = (uVar2 & 0xfffffff) >> 0x15;
  *DAT_0042a07c = uVar6;
  *DAT_0042a54c = 1;
  spotmgr_power_ton_adjust_42a1bc(param_3,param_1);
  if ((int)(uVar6 - uVar5) < 1) {
    iVar1 = 0;
  }
  else {
    iVar1 = (uVar6 - uVar5) * 2;
  }
  if (iVar1 + uVar5 < 0x80) {
    *DAT_00429da0 = *DAT_00429da0 & 0xffffff80 | iVar1 + uVar5 & 0x7f;
  }
  else {
    *DAT_00429da0 = *DAT_00429da0 | 0x7f;
  }
  delay_us(0x32);
  *DAT_00429da0 = uVar6 | *DAT_00429da0 & 0xffffff80;
  bVar8 = *DAT_0042a860 << 0xe < 0;
  if (bVar8) {
    FUN_0041e22e();
  }
  puVar3 = DAT_0042a864;
  *DAT_0042a864 = *DAT_0042a864 | 0x10000;
  *puVar3 = *puVar3 | 0x2000000;
  delay_us(0x14);
  if (bVar8) {
    FUN_0041e1e8();
  }
  return local_28;
}

