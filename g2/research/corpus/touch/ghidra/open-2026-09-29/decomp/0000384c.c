
void FUN_0000384c(void)

{
  undefined4 *puVar1;
  int unaff_r4;
  undefined4 in_stack_00000004;
  undefined4 in_stack_00000008;
  undefined2 in_stack_0000000c;
  
  memset(&stack0x00000004,0,10);
  sensor_read_mux(1,&stack0x00000004);
  sensor_read_mux(2,&stack0x0000000c);
  puVar1 = DAT_000038b4;
  *DAT_000038b4 = in_stack_00000004;
  puVar1[1] = in_stack_00000008;
  *(undefined2 *)(puVar1 + 2) = in_stack_0000000c;
  i2c_tx_descriptor_arm(DAT_000038a8,puVar1,0x10,DAT_000038a0);
  i2c_rx_descriptor_arm(DAT_000038a8,DAT_000038a4,0x10,DAT_000038a0);
  puVar1 = DAT_000038b4;
  if (unaff_r4 << 0x1b < 0) {
    memset(DAT_000038b4,0x5a,0x10);
    i2c_tx_descriptor_arm(DAT_000038a8,puVar1,0x10,DAT_000038a0);
    *(undefined4 *)(DAT_000038dc + 0x40) = 1;
  }
  return;
}

