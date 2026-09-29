
uint FUN_005059c0(undefined4 param_1,byte *param_2,int param_3,undefined4 param_4)

{
  uint uVar1;
  uint uVar2;
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 uStack_14;
  
  local_20 = param_1;
  local_1c = param_2;
  local_18 = param_3;
  uStack_14 = param_4;
  uVar1 = FUN_00508e5c(param_1,0x1d,6,&local_1c);
  param_2[6] = (byte)local_1c >> 6;
  if ((((uint)local_1c & 0x3f) == 0x1e) || (((uint)local_1c & 0x3f) == 7)) {
    param_2[7] = (byte)local_1c & 0x3f;
  }
  else {
    param_2[7] = 7;
  }
  *(undefined2 *)(param_2 + 4) = local_1c._1_2_;
  param_2[8] = (byte)((((uint)local_1c >> 0x18) << 0x1c) >> 0x1f);
  param_2[10] = (byte)((uint)(local_18 << 0x1a) >> 0x1f);
  param_2[0xb] = (byte)((uint)(local_18 << 0x1b) >> 0x1f);
  param_2[2] = (byte)((uint)(local_18 << 0x1c) >> 0x1f);
  *param_2 = (byte)((uint)(local_18 << 0x1d) >> 0x1f);
  param_2[1] = (byte)((uint)(local_18 << 0x1e) >> 0x1f);
  param_2[0xe] = (byte)(((uint)local_18._1_1_ << 0x1a) >> 0x1d);
  param_2[0xd] = (byte)(((uint)local_18._1_1_ << 0x1d) >> 0x1f);
  param_2[9] = (byte)(((uint)local_18._1_1_ << 0x1e) >> 0x1f);
  param_2[0xc] = local_18._1_1_ & 1;
  uVar2 = FUN_00508e5c(param_1,0x28,1,&local_20);
  param_2[0xf] = (byte)local_20 >> 4;
  param_2[0x10] = (byte)local_20 & 0xf;
  return uVar1 | uVar2;
}

