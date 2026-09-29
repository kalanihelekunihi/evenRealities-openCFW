
undefined4
L2cDmConnUpdateReq(undefined2 param_1,undefined2 *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  byte bVar3;
  int iVar4;
  char cVar5;
  
  bVar3 = DmConnIdByHandle(param_1);
  iVar1 = DAT_00536f90;
  if (bVar3 != 0) {
    *(undefined1 *)((uint)bVar3 + DAT_00536f90 + 0x10) = 0x12;
    WsfTimerStartSec(iVar1,0x1e);
    *(undefined2 *)(iVar1 + 8) = param_1;
    iVar4 = l2cMsgAlloc(0x14);
    if (iVar4 != 0) {
      *(undefined1 *)(iVar4 + 8) = 0x12;
      iVar2 = DAT_00536fa0;
      *(undefined1 *)(iVar4 + 9) = *(undefined1 *)(DAT_00536fa0 + 0x24);
      *(undefined1 *)((uint)bVar3 + iVar1 + 0x13) = *(undefined1 *)(iVar2 + 0x24);
      if (*(char *)(iVar2 + 0x24) == -1) {
        cVar5 = '\x01';
      }
      else {
        cVar5 = *(char *)(iVar2 + 0x24) + '\x01';
      }
      *(char *)(iVar2 + 0x24) = cVar5;
      *(undefined1 *)(iVar4 + 10) = 8;
      *(undefined1 *)(iVar4 + 0xb) = 0;
      *(char *)(iVar4 + 0xc) = (char)*param_2;
      *(char *)(iVar4 + 0xd) = (char)((ushort)*param_2 >> 8);
      *(char *)(iVar4 + 0xe) = (char)param_2[1];
      *(char *)(iVar4 + 0xf) = (char)((ushort)param_2[1] >> 8);
      *(char *)(iVar4 + 0x10) = (char)param_2[2];
      *(char *)(iVar4 + 0x11) = (char)((ushort)param_2[2] >> 8);
      *(char *)(iVar4 + 0x12) = (char)param_2[3];
      *(char *)(iVar4 + 0x13) = (char)((ushort)param_2[3] >> 8);
      L2cDataReq(5,param_1,0xc);
    }
  }
  return param_4;
}

