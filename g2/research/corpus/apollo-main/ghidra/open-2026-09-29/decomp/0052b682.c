
undefined8 HciResetCmd(void)

{
  int iVar1;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  undefined2 uStack_10;
  undefined1 local_e;
  undefined1 uStack_d;
  
  uStack_10 = (undefined2)unaff_r5;
  uStack_d = (undefined1)((uint)unaff_r5 >> 0x18);
  local_e = 0x14;
  (**(code **)(DAT_0052b6b8 + 0xc))(&uStack_10);
  hciClearCmdQueue();
  iVar1 = hciCmdAlloc(0xc03,0);
  if (iVar1 != 0) {
    hciCmdSend(iVar1);
  }
  return CONCAT44(unaff_r6,CONCAT13(uStack_d,CONCAT12(local_e,uStack_10)));
}

