
void i2c_irq_handler(int param_1)

{
  undefined4 uVar1;
  char cVar2;
  
  if (param_1 << 0x1a < 0) {
    if (-1 < param_1 << 0x19) {
      cVar2 = i2c_rx_position_get(DAT_000038a8,DAT_000038a0);
      if (((byte)(cVar2 - 1U) < 0x10) && (*DAT_000038a4 < 9)) {
                    /* WARNING: Could not recover jumptable at 0x00003744. Too many branches */
                    /* WARNING: Treating indirect jump as call */
        (**(code **)(DAT_000038ac + (uint)*DAT_000038a4 * 4))();
        return;
      }
    }
    i2c_rx_descriptor_arm(DAT_000038a8,DAT_000038a4,0x10,DAT_000038a0);
  }
  uVar1 = DAT_000038b4;
  if (param_1 << 0x1b < 0) {
    memset(DAT_000038b4,0x5a,0x10);
    i2c_tx_descriptor_arm(DAT_000038a8,uVar1,0x10,DAT_000038a0);
    *(undefined4 *)(DAT_000038dc + 0x40) = 1;
  }
  return;
}

