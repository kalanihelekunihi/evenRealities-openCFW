
undefined8 FUN_0049e448(undefined1 param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined1 uStack_14;
  undefined1 uStack_13;
  undefined1 uStack_12;
  undefined1 uStack_11;
  
  uStack_14 = (undefined1)param_4;
  uStack_13 = (undefined1)((uint)param_4 >> 8);
  uStack_12 = (undefined1)((uint)param_4 >> 0x10);
  uStack_11 = (undefined1)((uint)param_4 >> 0x18);
  FUN_0043c0e4(&uStack_14,3,0,param_4,param_3);
  FUN_0043c0e4(&uStack_14,3,0);
  uStack_14 = 0x13;
  uVar1 = 5;
  uStack_13 = param_1;
  uStack_12 = param_2;
  FUN_00464f76(1,&uStack_14,3,0);
  return CONCAT17(uStack_11,CONCAT16(uStack_12,CONCAT15(uStack_13,CONCAT14(uStack_14,uVar1))));
}

