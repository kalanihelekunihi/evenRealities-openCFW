
undefined8 FUN_004882d2(byte param_1,byte param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 local_10;
  uint local_c;
  
  if (param_1 < 0x13) {
    if ((param_2 == 0) || (5 < param_2)) {
      local_c = (uint)param_2;
      local_10 = DAT_004883dc;
      FUN_0044d25c(2,DAT_004883d0,0x54,DAT_004883d8);
      local_10 = FUN_004410a6();
    }
    else {
      local_10 = param_3;
      local_c = param_4;
      FUN_00439be4(&local_10,(uint)param_1 * 0xf + DAT_004883e0 + (uint)(byte)(param_2 - 1) * 3,3);
    }
  }
  else {
    local_c = (uint)param_1;
    local_10 = DAT_004883c8;
    FUN_0044d25c(2,DAT_004883d0,0x4f,DAT_004883d8);
    local_10 = FUN_004410a6();
  }
  return CONCAT44(local_10,local_10);
}

