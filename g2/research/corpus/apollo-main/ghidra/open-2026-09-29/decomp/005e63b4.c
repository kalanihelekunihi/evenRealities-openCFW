
longlong FUN_005e63b4(undefined4 param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  undefined4 uStack_18;
  uint uStack_14;
  undefined4 uStack_10;
  
  uStack_18 = param_2;
  uStack_14 = param_3;
  uStack_10 = param_4;
  FUN_0043c0e4(&uStack_18,8,0);
  uVar1 = param_2 >> 0x14 & 0xf;
  uStack_18 = CONCAT22(uStack_18._2_2_,CONCAT11((byte)(param_2 >> 0x1e),1)) & 0xffff01ff;
  uStack_14 = param_2 & 0xffff;
  if (uVar1 != 0) {
    FUN_005eadd4(uVar1,param_2 >> 0x18 & 0x3f,&uStack_18);
  }
  return (ulonglong)uStack_18 << 0x20;
}

