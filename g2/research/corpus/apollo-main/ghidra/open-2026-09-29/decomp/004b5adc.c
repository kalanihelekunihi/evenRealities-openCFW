
longlong GattReadCback(undefined1 param_1,short param_2,uint param_3,undefined4 param_4,int param_5)

{
  uint uStack_10;
  undefined4 uStack_c;
  
  uStack_10 = param_3;
  if (param_2 == 0x15) {
    uStack_c = param_4;
    AttsCsfGetFeatures(param_1,&uStack_10,1);
    FUN_00439be4(*(undefined4 *)(param_5 + 4),&uStack_10,1);
  }
  return (ulonglong)uStack_10 << 0x20;
}

