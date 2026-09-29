
undefined8 FUN_0042059e(uint *param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint local_10;
  
  uVar2 = 3;
  local_10 = param_4;
  iVar1 = FUN_004205f4(0x9f,0,0,&local_10,3,param_3);
  if (iVar1 == 0) {
    *param_1 = (local_10 >> 8 & 0xff) << 8 | (local_10 & 0xff) << 0x10 | local_10 >> 0x10 & 0xff;
  }
  else {
    uVar2 = 0x2d8;
    elog_output(1,DAT_00420adc,DAT_00420978,DAT_00420e04,0x2d8,DAT_00420e00);
  }
  return CONCAT44(uVar2,iVar1);
}

