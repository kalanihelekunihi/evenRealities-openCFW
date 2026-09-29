
undefined8 FUN_0055b6dc(uint *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte *pbVar1;
  undefined4 uVar2;
  undefined4 local_10;
  
  local_10 = param_4;
  FUN_0043c0e4(&local_10,4,0);
  if (param_1 == (uint *)0x0) {
    uVar2 = 0xffffffff;
  }
  else {
    uVar2 = FUN_0055b374(DAT_0055ba00,&local_10,4);
    pbVar1 = DAT_0055ba10;
    *DAT_0055ba10 = (byte)local_10;
    pbVar1[1] = local_10._1_1_;
    pbVar1[2] = local_10._2_1_;
    pbVar1[3] = local_10._3_1_;
    *param_1 = (uint)pbVar1[1] << 0x10 | (uint)*pbVar1 << 0x18 | (uint)pbVar1[2] << 8 |
               (uint)pbVar1[3];
  }
  return CONCAT44(local_10,uVar2);
}

