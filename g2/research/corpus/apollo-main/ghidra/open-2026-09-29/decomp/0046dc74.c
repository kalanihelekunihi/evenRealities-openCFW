
undefined8
dmSlaveAdvFormatData(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  uStack_10 = param_3;
  uStack_c = param_4;
  FUN_004b4728(&uStack_10,DAT_0046e024,(uint)param_1 % 100);
  uVar1 = FUN_0044a43c(&uStack_10);
  FUN_00439be4(DAT_0046e028,&uStack_10,uVar1);
  return CONCAT44(uStack_c,uStack_10);
}

