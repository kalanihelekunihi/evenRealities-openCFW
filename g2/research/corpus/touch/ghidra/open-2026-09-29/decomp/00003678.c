
void i2c_slave_init(void)

{
  int iVar1;
  uint *puVar2;
  undefined4 *puVar3;
  uint uVar4;
  
  puVar2 = DAT_000036e4;
  iVar1 = DAT_000036dc;
  Cy_SCB_I2C_Init(DAT_000036e4,DAT_000036e0,DAT_000036dc);
  Cy_SysInt_Init(DAT_000036ec,DAT_000036e8);
  i2c_tx_descriptor_arm(puVar2,DAT_000036f0,0x10,iVar1);
  i2c_rx_descriptor_arm(puVar2,DAT_000036f4,0x10,iVar1);
  *(undefined4 *)(iVar1 + 0x44) = DAT_000036f8;
  puVar3 = DAT_000036fc;
  DAT_000036fc[0x60] = 0x80;
  *puVar3 = 0x80;
  *puVar2 = *puVar2 | 0x80000000;
  if (*(char *)(iVar1 + 2) == '\0') {
    uVar4 = 0;
  }
  else {
    uVar4 = 0x100;
  }
  DAT_000036e4[0x1b] = puVar2[0x1b] | uVar4;
  return;
}

