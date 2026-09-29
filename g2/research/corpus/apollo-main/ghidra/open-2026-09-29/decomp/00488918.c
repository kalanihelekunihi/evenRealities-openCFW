
undefined8 FUN_00488918(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 local_10;
  undefined4 uStack_c;
  
  local_10 = param_3;
  uStack_c = param_4;
  FUN_0048890c(param_1,0x6c);
  local_10 = FUN_004410a6();
  FUN_00439be4(param_1 + 0x4c,&local_10,3);
  *(undefined1 *)(param_1 + 0x50) = 0xff;
  *(undefined4 *)(param_1 + 0x34) = 0x100;
  *(undefined4 *)(param_1 + 0x38) = 0x100;
  *(ushort *)(param_1 + 0x50) = *(ushort *)(param_1 + 0x50) & 0xf7ff;
  *(undefined4 *)(param_1 + 0x60) = DAT_00488f18;
  *(undefined4 *)(param_1 + 0x14) = 0x6c;
  return CONCAT44(uStack_c,local_10);
}

