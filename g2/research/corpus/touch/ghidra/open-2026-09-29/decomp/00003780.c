
void FUN_00003780(void)

{
  undefined2 uVar1;
  undefined2 *puVar2;
  int unaff_r4;
  
  puVar2 = DAT_000038b4;
  uVar1 = *(undefined2 *)(DAT_000038b8 + 6);
  memset(DAT_000038b4,0,0x10);
  *puVar2 = uVar1;
  i2c_tx_descriptor_arm(DAT_000038a8,puVar2,0x10,DAT_000038a0);
  i2c_rx_descriptor_arm(DAT_000038a8,DAT_000038a4,0x10,DAT_000038a0);
  puVar2 = DAT_000038b4;
  if (unaff_r4 << 0x1b < 0) {
    memset(DAT_000038b4,0x5a,0x10);
    i2c_tx_descriptor_arm(DAT_000038a8,puVar2,0x10,DAT_000038a0);
    *(undefined4 *)(DAT_000038dc + 0x40) = 1;
  }
  return;
}

