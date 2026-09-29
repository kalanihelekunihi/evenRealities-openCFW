
int FUN_004b3416(byte param_1,uint param_2,undefined4 param_3,int param_4)

{
  bool bVar1;
  int iVar2;
  undefined1 uVar3;
  int iVar4;
  ushort uVar5;
  ushort uVar6;
  undefined4 local_20;
  
  iVar2 = DAT_004b3c8c;
  bVar1 = true;
  iVar4 = *(int *)((uint)param_1 * 0x10 + DAT_004b3c8c + (param_2 & 0xff) * 4);
  uVar5 = *(short *)(DAT_004b3c8c + (uint)param_1 * 8 + (param_2 & 0xff) * 2 + 0x20) -
          *(short *)(DAT_004b3c8c + (uint)param_1 * 8 + (param_2 & 0xff) * 2 + 0x40);
  local_20 = param_4;
  if (*(ushort *)(DAT_004b3c8c + (uint)param_1 * 2 + 0x50) < uVar5) {
    uVar5 = *(ushort *)(DAT_004b3c8c + (uint)param_1 * 2 + 0x50);
  }
  for (; uVar5 != 0; uVar5 = uVar5 - uVar6) {
    if (uVar5 < 0xfc) {
      uVar6 = uVar5;
      if (bVar1) {
        uVar3 = 3;
      }
      else {
        uVar3 = 2;
      }
    }
    else if (bVar1) {
      uVar3 = 1;
      uVar6 = 0xfb;
    }
    else {
      uVar3 = 0;
      uVar6 = 0xfb;
    }
    local_20 = (uint)*(ushort *)(iVar2 + (uint)param_1 * 8 + (param_2 & 0xff) * 2 + 0x40) + iVar4;
    DmAdvSetData(param_1,uVar3,param_2 & 1,uVar6 & 0xff);
    *(ushort *)(iVar2 + (uint)param_1 * 8 + (param_2 & 0xff) * 2 + 0x40) =
         uVar6 + *(short *)(iVar2 + (uint)param_1 * 8 + (param_2 & 0xff) * 2 + 0x40);
    bVar1 = false;
  }
  return local_20;
}

