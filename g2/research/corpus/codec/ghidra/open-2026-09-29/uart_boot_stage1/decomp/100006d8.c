
void gx8002_uart_stage1_handshake(void)

{
  undefined4 *puVar1;
  int iVar2;
  uint *puVar3;
  uint *puVar4;
  uint uVar5;
  int iVar6;
  
  gx8002_uart_stage1_railcfg();
  iVar2 = gx8002_uart_stage1_pmu_get_bit0();
  if ((iVar2 == 1) || (iVar2 = gx8002_uart_stage1_pmu_get_bit1(), iVar2 == 1)) {
    gx8002_uart_stage1_bringup(0,*puRam10000774);
  }
  else {
    gx8002_uart_stage1_bringup(1,0);
  }
  iVar2 = iRam1000077c;
  puVar1 = puRam10000778;
  uVar5 = 0x4f;
  iVar6 = 0;
  while( true ) {
    puVar3 = (uint *)*puVar1;
    puVar4 = puVar3 + 5;
    do {
    } while ((*puVar4 & 0x40) == 0);
    *puVar3 = 0x47;
    do {
    } while ((*puVar4 & 0x40) == 0);
    *puVar3 = 0x45;
    do {
    } while ((*puVar4 & 0x40) == 0);
    *puVar3 = 0x54;
    while ((*puVar4 & 1) != 0) {
      if ((*puVar3 & 0xff) == uVar5) {
        iVar6 = iVar6 + 1;
        uVar5 = (uint)*(byte *)(iVar2 + iVar6);
        if (uVar5 == 0) {
          return;
        }
      }
      else {
        uVar5 = 0x4f;
        iVar6 = 0;
      }
    }
    if (uVar5 == 0) break;
    gx8002_uart_stage1_mdelay(1);
  }
  return;
}

