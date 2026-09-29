
void ring_battery_state_set(byte param_1,char param_2)

{
  byte *pbVar1;
  
  pbVar1 = DAT_004ffa58;
  if (100 < param_1) {
    param_1 = 100;
  }
  *DAT_004ffa58 = param_1;
  pbVar1[1] = param_2 != '\0';
  return;
}

