
undefined8 FUN_00482ef6(undefined4 param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined3 uVar2;
  undefined4 uVar3;
  uint uVar4;
  undefined4 local_10;
  undefined4 local_c;
  
  local_c._3_1_ = (byte)((uint)param_1 >> 0x18);
  uVar3 = param_1;
  uVar1 = local_10;
  if (((local_c._3_1_ < 0xfd) &&
      (local_10._3_1_ = (byte)((uint)param_2 >> 0x18), uVar1 = param_2, 2 < local_10._3_1_)) &&
     (uVar3 = param_2, uVar1 = param_2, 2 < local_c._3_1_)) {
    if (local_10._3_1_ == 0xff) {
      uVar3 = FUN_00482e4c(param_1,param_2);
      uVar1 = uVar3;
    }
    else {
      uVar4 = 0xff - ((int)((0xff - (uint)local_10._3_1_) * (0xff - (uint)local_c._3_1_)) >> 8);
      local_c = CONCAT13((char)(((uint)local_c._3_1_ * 0xff) / (uVar4 & 0xff)),(int3)param_1);
      uVar2 = FUN_00482e4c(local_c,param_2);
      local_10 = CONCAT13((char)uVar4,uVar2);
      uVar3 = local_10;
      uVar1 = local_10;
    }
  }
  local_10 = uVar1;
  return CONCAT44(local_10,uVar3);
}

