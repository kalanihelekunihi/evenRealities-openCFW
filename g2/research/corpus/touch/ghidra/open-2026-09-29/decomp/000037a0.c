
void FUN_000037a0(void)

{
  undefined1 *puVar1;
  int unaff_r4;
  
  *DAT_000038bc = 1;
  puVar1 = DAT_000038b4;
  *DAT_000038b4 = 5;
  puVar1[1] = 0;
  puVar1[2] = 0x17;
  i2c_tx_descriptor_arm(DAT_000038a8,puVar1,0x10,DAT_000038a0);
  logger_stub(DAT_000038c4,DAT_000038c0);
  i2c_rx_descriptor_arm(DAT_000038a8,DAT_000038a4,0x10,DAT_000038a0);
  puVar1 = DAT_000038b4;
  if (unaff_r4 << 0x1b < 0) {
    memset(DAT_000038b4,0x5a,0x10);
    i2c_tx_descriptor_arm(DAT_000038a8,puVar1,0x10,DAT_000038a0);
    *(undefined4 *)(DAT_000038dc + 0x40) = 1;
  }
  return;
}

