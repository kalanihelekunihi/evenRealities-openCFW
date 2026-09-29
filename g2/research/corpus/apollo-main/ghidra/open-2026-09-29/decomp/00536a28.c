
undefined8 dmConnOpen(undefined4 param_1,undefined1 param_2,undefined4 param_3)

{
  int iVar1;
  byte bVar2;
  uint uVar3;
  uint uVar4;
  
  uVar3 = DmScanPhyToIdx(1);
  iVar1 = DAT_00536ab0;
  bVar2 = DmLlAddrType(*(undefined1 *)(DAT_00536ab0 + 0xd));
  uVar4 = (uint)bVar2;
  HciLeCreateConnCmd(*(undefined2 *)(DAT_00536ab4 + (uVar3 & 0xff) * 2 + 0xbc),
                     *(undefined2 *)(DAT_00536ab4 + (uVar3 & 0xff) * 2 + 0xc0),
                     *(undefined1 *)(iVar1 + 0x14),param_2,param_3,uVar4,
                     DAT_00536ab4 + (uVar3 & 0xff) * 0xc + 0xa4);
  dmDevPassEvtToDevPriv(0xe,0,0,0);
  return CONCAT44(uVar4,param_3);
}

