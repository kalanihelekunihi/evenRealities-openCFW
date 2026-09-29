
void FUN_000037c8(uint param_1)

{
  undefined1 *puVar1;
  int unaff_r4;
  short sStack00000004;
  
  sStack00000004 = 0;
  if (2 < param_1) {
    memcpy(&stack0x00000004,DAT_000038c8,2);
  }
  puVar1 = DAT_000038b4;
  if (sStack00000004 == 0) {
    *DAT_000038b4 = 7;
    puVar1[1] = 0xff;
    puVar1[2] = 0x17;
  }
  else {
    *(short *)(DAT_000038b8 + 6) = sStack00000004;
    *DAT_000038cc = sStack00000004;
    *DAT_000038d0 = 1;
    *DAT_000038d4 = 1;
    puVar1 = DAT_000038b4;
    *DAT_000038b4 = 7;
    puVar1[1] = 0;
    puVar1[2] = 0x17;
    logger_stub(DAT_000038d8,sStack00000004,DAT_000038c0);
  }
  i2c_tx_descriptor_arm(DAT_000038a8,DAT_000038b4,0x10,DAT_000038a0);
  i2c_rx_descriptor_arm(DAT_000038a8,DAT_000038a4,0x10,DAT_000038a0);
  puVar1 = DAT_000038b4;
  if (unaff_r4 << 0x1b < 0) {
    memset(DAT_000038b4,0x5a,0x10);
    i2c_tx_descriptor_arm(DAT_000038a8,puVar1,0x10,DAT_000038a0);
    *(undefined4 *)(DAT_000038dc + 0x40) = 1;
  }
  return;
}

