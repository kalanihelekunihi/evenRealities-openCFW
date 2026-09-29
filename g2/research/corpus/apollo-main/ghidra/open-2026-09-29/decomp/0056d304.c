
undefined8
smpScFailWithReattempt(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  uStack_10 = param_3;
  uStack_c = param_4;
  SmpScGetCancelMsgWithReattempt(*(undefined1 *)(param_1 + 0x3d),&uStack_10,4);
  smpSmExecute(param_1,&uStack_10);
  return CONCAT44(uStack_c,uStack_10);
}

