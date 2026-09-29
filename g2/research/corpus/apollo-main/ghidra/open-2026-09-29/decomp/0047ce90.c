
undefined8 UX_SendBLEStatusToPeer(void)

{
  byte bVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  int iVar4;
  undefined4 uVar5;
  undefined1 uStack_9;
  
  uVar5 = *DAT_0047d8fc;
  uStack_9 = (undefined1)((uint)DAT_0047d8fc[1] >> 0x18);
  uVar2 = FUN_0045a568();
  iVar4 = FUN_0045a568();
  if (iVar4 == 1) {
    uVar3 = 2;
  }
  else {
    uVar3 = 1;
  }
  bVar1 = *DAT_0047d900;
  FUN_004651e0(0x103,&stack0xfffffff0,8,0);
  return CONCAT17(uStack_9,CONCAT16((byte)(((uint)bVar1 << 0x1d) >> 0x1f),
                                    CONCAT15(uVar3,CONCAT14(uVar2,uVar5))));
}

