
undefined8 semantic_TouchFormatVersion(uint param_1,undefined4 param_2,undefined4 param_3)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = param_1 >> 8 & 0xff;
  uVar1 = param_1 >> 0x10 & 0xff;
  FUN_0044b728(param_2,param_3,DAT_00561740,param_1 >> 0x18,uVar1,uVar2,param_1 & 0xff);
  return CONCAT44(uVar2,uVar1);
}

