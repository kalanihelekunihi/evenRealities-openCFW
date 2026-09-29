
uint FUN_00429f68(int param_1,undefined4 param_2,undefined4 param_3)

{
  byte bVar1;
  uint uVar2;
  uint *puVar3;
  uint *puVar4;
  uint uVar5;
  undefined4 local_20;
  
  puVar4 = (uint *)(DAT_0042a084 + param_1 * 4 + 4);
  puVar3 = (uint *)(DAT_0042a084 + 100);
  local_20 = CONCAT13((char)(*puVar3 >> 0x15),
                      CONCAT12((char)(*puVar3 >> 0xe),
                               CONCAT11((char)(*puVar3 >> 7),*(undefined1 *)puVar3))) & 0x7f7f7f7f;
  uVar2 = *puVar4;
  bVar1 = *(byte *)puVar4;
  if (*DAT_0042a088 << 0x1f < 0) {
    uVar5 = 0;
    while ((uVar5 < 0x3c && (-1 < *DAT_0042a1b4 << 1))) {
      delay_us(1);
      uVar5 = uVar5 + 1;
    }
    spotmgr_timer_irq_service_42a04a();
  }
  *DAT_0042a1b8 = param_3;
  *DAT_0042a2a4 = param_1;
  *DAT_0042a2a8 = (*puVar4 & 0x1ffff) >> 7;
  *DAT_0042a2ac = (*puVar4 & 0x1fffff) >> 0x11;
  *DAT_0042a2b0 = (uVar2 & 0xfffffff) >> 0x15;
  *DAT_0042a07c = bVar1 & 0x7f;
  spotmgr_power_ton_adjust_42a1bc(param_3,param_1);
  return local_20;
}

