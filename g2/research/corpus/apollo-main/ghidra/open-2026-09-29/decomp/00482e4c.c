
uint FUN_00482e4c(uint param_1,uint param_2)

{
  undefined4 local_8;
  undefined4 local_4;
  
  local_8._3_1_ = (byte)(param_1 >> 0x18);
  if (local_8._3_1_ < 0xfd) {
    if (2 < local_8._3_1_) {
      local_4._0_2_ =
           CONCAT11((char)((uint)local_8._3_1_ * (param_1 >> 8 & 0xff) +
                           (0xff - (uint)local_8._3_1_) * (param_2 >> 8 & 0xff) >> 8),(char)param_2)
      ;
      local_4 = CONCAT31((int3)(CONCAT22((short)((uint)local_8._3_1_ * (param_1 >> 0x10 & 0xff) +
                                                 (0xff - (uint)local_8._3_1_) *
                                                 (param_2 >> 0x10 & 0xff) >> 8),(ushort)local_4) >>
                               8),(char)((uint)local_8._3_1_ * (param_1 & 0xff) +
                                         (0xff - (uint)local_8._3_1_) * ((ushort)local_4 & 0xff) >>
                                        8)) & 0xffffff;
      param_2 = local_4;
    }
  }
  else {
    local_8 = param_1 & 0xffffff;
    param_2 = local_8;
  }
  return param_2;
}

