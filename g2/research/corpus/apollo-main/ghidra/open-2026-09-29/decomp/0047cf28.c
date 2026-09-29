
undefined8 UX_SendRingQueryToPeer(void)

{
  undefined1 uVar1;
  undefined1 uVar2;
  int iVar3;
  undefined4 uVar4;
  undefined2 uStack_a;
  
  uVar4 = *(undefined4 *)PTR_DAT_0047d908;
  uStack_a = (undefined2)((uint)*(undefined4 *)(PTR_DAT_0047d908 + 4) >> 0x10);
  uVar1 = FUN_0045a568();
  iVar3 = FUN_0045a568();
  if (iVar3 == 1) {
    uVar2 = 2;
  }
  else {
    uVar2 = 1;
  }
  FUN_004651e0(0x103,&stack0xfffffff0,8,0);
  return CONCAT26(uStack_a,CONCAT15(uVar2,CONCAT14(uVar1,uVar4)));
}

