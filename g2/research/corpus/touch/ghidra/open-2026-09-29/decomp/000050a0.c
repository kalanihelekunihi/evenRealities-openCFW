
void touch_pipeline_1da0_filter_chain(int param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  uint uVar1;
  
  uVar1 = (uint)*(ushort *)(param_1 + 0x74);
  if ((int)(uVar1 << 0x1b) < 0) {
    touch_pipeline_1cc2_median_shift();
    param_3 = param_3 + 4;
  }
  if ((int)(uVar1 << 0x18) < 0) {
    touch_pipeline_1d54_blend(param_1,param_2,param_3,param_4);
    param_3 = param_3 + 2;
  }
  if ((int)(uVar1 << 0x15) < 0) {
    touch_record_1c6e_history_filter(param_1,param_2,param_3);
  }
  return;
}

