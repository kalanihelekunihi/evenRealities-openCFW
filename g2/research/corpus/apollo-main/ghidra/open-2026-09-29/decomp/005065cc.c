
undefined8 FUN_005065cc(undefined4 param_1,char param_2,byte *param_3,int param_4)

{
  undefined4 uVar1;
  undefined4 local_10;
  
  local_10 = param_4;
  if (param_2 == '\0') {
    uVar1 = 0x19;
  }
  else {
    if (param_2 != '\x01') {
      uVar1 = 0xfffffff5;
      goto LAB_00506682;
    }
    uVar1 = 0x59;
  }
  uVar1 = FUN_00508e5c(param_1,uVar1,2,&local_10);
  *param_3 = (byte)local_10 & 1;
  param_3[1] = (byte)((uint)(local_10 << 0x1e) >> 0x1f);
  param_3[2] = (byte)((uint)(local_10 << 0x1d) >> 0x1f);
  param_3[3] = (byte)((uint)(local_10 << 0x1c) >> 0x1f);
  param_3[4] = (byte)((uint)(local_10 << 0x1b) >> 0x1f);
  param_3[5] = (byte)((uint)(local_10 << 0x1a) >> 0x1f);
  param_3[6] = (byte)((uint)(local_10 << 0x19) >> 0x1f);
  param_3[7] = (byte)local_10 >> 7;
  param_3[8] = local_10._1_1_ & 1;
  param_3[9] = (byte)(((uint)local_10._1_1_ << 0x1e) >> 0x1f);
  param_3[10] = (byte)(((uint)local_10._1_1_ << 0x1d) >> 0x1f);
  param_3[0xb] = (byte)(((uint)local_10._1_1_ << 0x1c) >> 0x1f);
  param_3[0xc] = (byte)(((uint)local_10._1_1_ << 0x1b) >> 0x1f);
  param_3[0xd] = (byte)(((uint)local_10._1_1_ << 0x1a) >> 0x1f);
  param_3[0xe] = (byte)(((uint)local_10._1_1_ << 0x19) >> 0x1f);
LAB_00506682:
  return CONCAT44(local_10,uVar1);
}

