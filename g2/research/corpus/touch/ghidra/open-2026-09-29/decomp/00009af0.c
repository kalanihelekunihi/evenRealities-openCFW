
void i2c_rx_descriptor_arm(undefined4 param_1,int param_2,int param_3,int param_4)

{
  if ((param_3 != 0) && (param_2 == 0)) {
    software_bkpt(1);
  }
  *(int *)(param_4 + 0x38) = param_2;
  *(int *)(param_4 + 0x3c) = param_3;
  *(undefined4 *)(param_4 + 0x40) = 0;
  return;
}

