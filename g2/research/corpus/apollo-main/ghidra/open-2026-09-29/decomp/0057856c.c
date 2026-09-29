
undefined8 semantic_CodecFormatVersion(uint param_1,uint param_2,uint param_3)

{
  uint uVar1;
  uint uVar2;
  
  if ((param_2 != 0) && (0xf < param_3)) {
    uVar2 = param_1 >> 8 & 0xff;
    uVar1 = param_1 >> 0x10 & 0xff;
    FUN_0044b728(param_2,param_3,DAT_00579130,param_1 >> 0x18,uVar1,uVar2,param_1 & 0xff);
    param_2 = uVar1;
    param_3 = uVar2;
  }
  return CONCAT44(param_3,param_2);
}

