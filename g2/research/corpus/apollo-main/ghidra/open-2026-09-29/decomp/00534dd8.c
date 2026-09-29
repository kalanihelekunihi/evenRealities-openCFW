
undefined8
attsCheckPendDbHashReadRsp
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  byte bVar3;
  short *psVar4;
  undefined4 local_28;
  undefined4 uStack_24;
  undefined4 uStack_20;
  
  local_28 = param_2;
  uStack_24 = param_3;
  uStack_20 = param_4;
  for (bVar3 = 0; bVar3 < 3; bVar3 = bVar3 + 1) {
    psVar4 = (short *)(DAT_00535464 + (uint)bVar3 * 0x14);
    if (*(int *)(psVar4 + 8) != 0) {
      iVar1 = attMsgAlloc(*psVar4 + 8);
      if (iVar1 == 0) {
        local_28 = 0x11;
        attsErrRsp(psVar4,0,8,**(undefined2 **)(psVar4 + 8));
      }
      else {
        *(undefined1 *)(iVar1 + 8) = 9;
        *(undefined1 *)(iVar1 + 9) = 0x12;
        *(char *)(iVar1 + 10) = (char)*(undefined2 *)(*(int *)(psVar4 + 8) + 2);
        *(char *)(iVar1 + 0xb) = (char)((ushort)*(undefined2 *)(*(int *)(psVar4 + 8) + 2) >> 8);
        iVar2 = attsFindByHandle(*(undefined2 *)(*(int *)(psVar4 + 8) + 2),&uStack_24);
        if (iVar2 == 0) {
          local_28 = 10;
          attsErrRsp(psVar4,0,8,**(undefined2 **)(psVar4 + 8));
        }
        else {
          FUN_00439be4(iVar1 + 0xc,*(undefined4 *)(iVar2 + 4),**(undefined2 **)(iVar2 + 8));
          L2cDataReq(4,psVar4[6],
                     (iVar1 + 0xc + (uint)**(ushort **)(iVar2 + 8)) - (iVar1 + 8) & 0xffff,iVar1);
        }
      }
      WsfBufFree(*(undefined4 *)(psVar4 + 8));
      psVar4[8] = 0;
      psVar4[9] = 0;
    }
  }
  return CONCAT44(uStack_24,local_28);
}

