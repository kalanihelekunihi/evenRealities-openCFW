
undefined4 FUN_00511002(undefined4 param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined1 local_c;
  undefined1 local_b;
  undefined2 uStack_a;
  
  uStack_a = (undefined2)(param_4 >> 0x10);
  _local_c = CONCAT11((char)param_2,(char)((uint)param_2 >> 8));
  uVar3 = DAT_00511948;
  if ((param_4 < 0x21) &&
     (iVar1 = hal_i2c_transfer_full(7,0x6b,&local_c,2,param_3,param_4,param_3), uVar3 = DAT_00511964
     , iVar1 != 0)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00511958,DAT_00511954,DAT_00511950,0xf1,DAT_0051194c,iVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), uVar3 = DAT_00511960, iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_0051195c,DAT_0051195c,iVar1);
      uVar3 = DAT_00511960;
    }
  }
  return uVar3;
}

