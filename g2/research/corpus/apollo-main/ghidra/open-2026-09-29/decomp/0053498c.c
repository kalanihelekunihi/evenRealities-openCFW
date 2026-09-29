
uint attsDataCback(undefined2 param_1,ushort param_2,int param_3,uint param_4)

{
  byte bVar1;
  byte bVar2;
  int iVar3;
  code *pcVar4;
  uint uVar5;
  short sVar6;
  uint uStack_20;
  
  iVar3 = attsCcbByHandle(param_1,0);
  uStack_20 = param_4;
  if ((iVar3 != 0) && (param_2 != 0)) {
    bVar1 = *(byte *)(param_3 + 8);
    if ((bVar1 < 0x13) || (bVar1 - 0x16 < 9)) {
      uVar5 = (bVar1 & 0xfffffffe) / 2;
    }
    else if (bVar1 == 0x52) {
      uVar5 = 10;
    }
    else if (bVar1 == 0x20) {
      uVar5 = 0x10;
    }
    else if (bVar1 == 0xd2) {
      uVar5 = 0x11;
    }
    else {
      uVar5 = 0;
    }
    if ((-1 < (int)((uint)*(byte *)(*(int *)(iVar3 + 0x10) + 2) << 0x1c)) || (uVar5 == 0xf)) {
      bVar2 = attsCsfActClientState(*(byte *)(iVar3 + 0x24) - 1,bVar1,param_3);
      if (bVar2 == 0) {
        sVar6 = 0;
      }
      else {
        if (param_2 < 3) {
          return param_4;
        }
        sVar6 = (ushort)*(byte *)(param_3 + 10) * 0x100 + (ushort)*(byte *)(param_3 + 9);
      }
      if (bVar2 == 0) {
        pcVar4 = *(code **)(DAT_00535440 + uVar5 * 4);
        if (pcVar4 == (code *)0x0) {
          bVar2 = 6;
        }
        else if (param_2 < *(byte *)(DAT_00535444 + uVar5)) {
          bVar2 = 4;
        }
        else {
          (*pcVar4)(iVar3,param_2,param_3);
          bVar2 = 0;
        }
      }
      if ((((bVar2 != 0) && (bVar1 != 2)) && (bVar1 != 0x1e)) && (-1 < (int)((uint)bVar1 << 0x19)))
      {
        uStack_20 = (uint)bVar2;
        attsErrRsp(*(undefined4 *)(iVar3 + 0x10),0,bVar1,sVar6);
      }
    }
  }
  return uStack_20;
}

