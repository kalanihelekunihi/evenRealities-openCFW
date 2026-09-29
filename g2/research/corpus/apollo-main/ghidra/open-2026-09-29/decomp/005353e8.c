
undefined8 AttsRemoveGroup(undefined2 param_1,ushort param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  byte bVar2;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  
  bVar2 = 0;
  uStack_20 = param_3;
  uStack_1c = param_4;
  WsfTaskLock();
  iVar1 = attsFindByHandle(param_1,&uStack_20);
  if (iVar1 == 0) {
    bVar2 = 10;
  }
  else if (*(ushort *)(iVar1 + 0xc) < param_2) {
    bVar2 = 0xd;
  }
  else {
    FUN_00439be4(*(undefined4 *)(iVar1 + 4),param_3,param_2);
    if ((int)((uint)*(byte *)(iVar1 + 0xe) << 0x1c) < 0) {
      **(ushort **)(iVar1 + 8) = param_2;
    }
  }
  WsfTaskUnlock();
  return CONCAT44(uStack_20,(uint)bVar2);
}

