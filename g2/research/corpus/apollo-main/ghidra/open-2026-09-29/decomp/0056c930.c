
undefined8 attsProcFindInfoReq(int param_1,undefined4 param_2,uint param_3,int *param_4)

{
  ushort uVar1;
  undefined1 uVar2;
  uint uVar3;
  int unaff_r4;
  uint uVar4;
  uint uVar5;
  byte bVar6;
  undefined1 *unaff_r10;
  uint uStack_28;
  int *piStack_24;
  
  bVar6 = 0;
  uVar1 = *(ushort *)(*(int *)(param_1 + 0x10) + (uint)*(byte *)(param_1 + 0x25) * 4);
  uVar4 = (uint)*(byte *)(param_3 + 10) * 0x100 + (uint)*(byte *)(param_3 + 9);
  uVar5 = (uint)*(byte *)(param_3 + 0xc) * 0x100 + (uint)*(byte *)(param_3 + 0xb);
  if ((uVar4 == 0) || (uVar5 < uVar4)) {
    bVar6 = 1;
  }
  piStack_24 = param_4;
  if (bVar6 == 0) {
    unaff_r4 = attMsgAlloc(uVar1 + 8);
    if (unaff_r4 == 0) {
      bVar6 = 0x11;
    }
    else {
      *(undefined1 *)(unaff_r4 + 8) = 5;
      *(undefined1 *)(unaff_r4 + 9) = 1;
      unaff_r10 = (undefined1 *)(unaff_r4 + 10);
      uVar3 = uVar4;
      while (uVar3 = attsFindInRange(uVar3 & 0xffff,uVar5,&piStack_24), (uVar3 & 0xffff) != 0) {
        uVar2 = (undefined1)(uVar3 >> 8);
        if ((int)((uint)*(byte *)((int)piStack_24 + 0xe) << 0x1f) < 0) {
          if (unaff_r10 == (undefined1 *)(unaff_r4 + 10)) {
            unaff_r10[-1] = 2;
            *unaff_r10 = (char)uVar3;
            unaff_r10[1] = uVar2;
            FUN_00439be4(unaff_r10 + 2,*piStack_24,0x10);
            unaff_r10 = unaff_r10 + 0x12;
          }
          break;
        }
        if ((undefined1 *)((uint)uVar1 + unaff_r4 + 8) < unaff_r10 + 4) break;
        *unaff_r10 = (char)uVar3;
        unaff_r10[1] = uVar2;
        unaff_r10[2] = *(undefined1 *)*piStack_24;
        unaff_r10[3] = *(undefined1 *)(*piStack_24 + 1);
        unaff_r10 = unaff_r10 + 4;
        if (((uVar3 & 0xffff) == 0xffff) || (uVar3 = uVar3 + 1, uVar5 < (uVar3 & 0xffff))) break;
      }
      if (unaff_r10 == (undefined1 *)(unaff_r4 + 10)) {
        WsfMsgFree(unaff_r4);
        bVar6 = 10;
      }
    }
  }
  attsDiscBusy(param_1);
  if (bVar6 == 0) {
    attL2cDataReq(*(undefined4 *)(param_1 + 0x10),*(undefined1 *)(param_1 + 0x25),
                  (int)unaff_r10 - (unaff_r4 + 8) & 0xffff,unaff_r4);
    uStack_28 = param_3;
  }
  else {
    uStack_28 = (uint)bVar6;
    attsErrRsp(*(undefined4 *)(param_1 + 0x10),*(undefined1 *)(param_1 + 0x25),4,uVar4);
  }
  return CONCAT44(piStack_24,uStack_28);
}

