
undefined8 FUN_0048834c(byte param_1,byte param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 local_10;
  uint local_c;
  
  if (param_1 < 0x13) {
    if ((param_2 == 0) || (4 < param_2)) {
      local_c = (uint)param_2;
      local_10 = DAT_004883e8;
      FUN_0044d25c(2,DAT_004883d0,0x7b,DAT_004883e4);
      local_10 = FUN_004410a6();
    }
    else {
      local_10 = param_3;
      local_c = param_4;
      FUN_00439be4(&local_10,(uint)param_1 * 0xc + DAT_004883ec + (uint)(byte)(param_2 - 1) * 3,3);
    }
  }
  else {
    local_c = (uint)param_1;
    local_10 = DAT_004883c8;
    FUN_0044d25c(2,DAT_004883d0,0x76,DAT_004883e4);
    local_10 = FUN_004410a6();
  }
  return CONCAT44(local_10,local_10);
}

