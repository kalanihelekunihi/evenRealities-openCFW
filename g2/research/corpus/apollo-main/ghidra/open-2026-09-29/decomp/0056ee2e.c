
undefined8 smpActPairingCmpl(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  ushort uStack_10;
  undefined1 uStack_e;
  undefined1 uStack_d;
  undefined4 uStack_c;
  
  uStack_10 = (ushort)param_3;
  uStack_e = (undefined1)((uint)param_3 >> 0x10);
  uStack_d = (undefined1)((uint)param_3 >> 0x18);
  uStack_c = param_4;
  smpCleanup(param_1);
  DmConnSetIdle(*(undefined1 *)(param_1 + 0x3d),1,0);
  uStack_c = CONCAT31(uStack_c._1_3_,*(undefined1 *)(param_1 + 0x40));
  uStack_10 = (ushort)*(byte *)(param_1 + 0x3d);
  uStack_e = 0x2a;
  DmSmpCbackExec(&uStack_10);
  return CONCAT44(uStack_c,CONCAT13(uStack_d,CONCAT12(uStack_e,uStack_10)));
}

