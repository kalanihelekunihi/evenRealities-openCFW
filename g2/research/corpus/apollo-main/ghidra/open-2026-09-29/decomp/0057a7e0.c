
undefined8
gx8002_i2s_rx_buffer_get
          (undefined4 *param_1,undefined4 *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 local_18;
  undefined4 local_14;
  undefined4 uStack_10;
  
  local_18 = *DAT_0057a8f0;
  local_14 = DAT_0057a8f0[1];
  uStack_10 = param_4;
  local_18 = FUN_00590b6c(*DAT_0057a880,0);
  FUN_00475014(&local_18,0);
  *param_1 = local_18;
  *param_2 = local_14;
  return CONCAT44(local_14,local_18);
}

