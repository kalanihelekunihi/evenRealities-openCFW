
undefined8 UX_SendRingStatusToPeer(void)

{
  undefined1 uVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  int iVar4;
  undefined4 uVar5;
  undefined1 uStack_9;
  
  uVar5 = *(undefined4 *)PTR_DAT_0047d904;
  uStack_9 = (undefined1)((uint)*(undefined4 *)(PTR_DAT_0047d904 + 4) >> 0x18);
  uVar1 = FUN_0045a568();
  iVar4 = FUN_0045a568();
  if (iVar4 == 1) {
    uVar2 = 2;
  }
  else {
    uVar2 = 1;
  }
  if ((*DAT_0047d900 & 0x1f) >> 4 == 0) {
    uVar3 = 2;
  }
  else {
    uVar3 = 3;
  }
  FUN_004651e0(0x103,&stack0xfffffff0,8,0);
  return CONCAT17(uStack_9,CONCAT16(uVar3,CONCAT15(uVar2,CONCAT14(uVar1,uVar5))));
}

