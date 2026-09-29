
undefined8 FUN_00470028(uint *param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  uint local_10;
  
  uVar3 = 3;
  local_10 = param_4;
  iVar1 = FUN_00470168(0x9f,0,0,&local_10,3,param_3);
  if (iVar1 == 0) {
    *param_1 = (local_10 >> 8 & 0xff) << 8 | (local_10 & 0xff) << 0x10 | local_10 >> 0x10 & 0xff;
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uVar3 = 0x2d8;
      FUN_0043d574(1,DAT_004700a8,DAT_004700a4,DAT_004708a0,0x2d8,DAT_0047089c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00470a74);
    }
  }
  return CONCAT44(uVar3,iVar1);
}

