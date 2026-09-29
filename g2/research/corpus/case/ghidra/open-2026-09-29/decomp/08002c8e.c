
void glasses_channel_command_pack(int param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  uint local_8;
  
  local_8 = param_4 & 0xffffff00;
  if (param_1 != 0) {
    local_8._0_1_ = 0x3b;
    local_8._1_3_ = (int3)(param_4 >> 8);
    gls_frame_pack_r(5,1);
    local_8 = CONCAT31(local_8._1_3_,7);
  }
  gls_frame_pack_r(4,1,&local_8);
  return;
}

