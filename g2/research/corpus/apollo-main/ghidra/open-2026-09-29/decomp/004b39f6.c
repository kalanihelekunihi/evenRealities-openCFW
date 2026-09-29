
undefined8 FUN_004b39f6(int param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  byte bVar2;
  int *piVar3;
  undefined1 uVar4;
  undefined4 uVar5;
  int iVar6;
  byte bVar7;
  
  *(undefined1 *)(DAT_004b3c8c + 0x54) = 1;
  piVar3 = DAT_004b4508;
  *(byte *)((int)param_2 + 7) = *(byte *)(param_1 + 4) & 1 & *(byte *)*DAT_004b4508 & 1;
  if ((*(char *)((int)param_2 + 7) != '\0') && (*param_2 == 0)) {
    uVar5 = DmConnPeerAddr((char)param_2[1]);
    uVar4 = DmConnPeerAddrType((char)param_2[1]);
    iVar6 = FUN_0047a71c(uVar4,uVar5,0);
    *param_2 = iVar6;
  }
  *(undefined1 *)((int)param_2 + 0xb) = 0;
  bVar2 = *(byte *)(*piVar3 + 2);
  bVar7 = *(byte *)(*piVar3 + 1);
  iVar6 = DmConnPeerAddrType((char)param_2[1]);
  if (iVar6 == 1) {
    bVar7 = bVar7 | 2;
  }
  bVar1 = *(byte *)(param_1 + 7);
  DmSecPairRsp((char)param_2[1],*(undefined1 *)(*piVar3 + 3),*(undefined1 *)*piVar3,
               bVar7 & *(byte *)(param_1 + 6));
  return CONCAT44(param_4,(uint)(bVar1 & bVar2));
}

