
int gx8002_digital_voltage(int param_1)

{
  byte abStack_8 [4];
  
  if (param_1 != -1) {
    abStack_8[0] = abStack_8[0] & 0xe0 | (byte)param_1 & 0xf | 0x10;
    gx8002_platform_config(8,abStack_8);
    param_1 = 0;
  }
  return param_1;
}

