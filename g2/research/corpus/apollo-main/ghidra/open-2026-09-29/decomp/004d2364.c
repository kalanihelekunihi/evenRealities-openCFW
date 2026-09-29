
void dmSecHciHandler(ushort *param_1)

{
  int iVar1;
  int iVar2;
  undefined1 auStack_98 [4];
  ushort uStack_94;
  undefined1 uStack_92;
  char cStack_91;
  undefined1 uStack_90;
  
  iVar1 = dmConnCcbByHandle(*param_1);
  if (iVar1 != 0) {
    if ((char)param_1[1] == '\x10') {
      if ((param_1[7] == 0) && (iVar2 = FUN_004751c8(param_1 + 3,DAT_004d2530,8), iVar2 == 0)) {
        iVar2 = SmpDmGetStk(*(undefined1 *)(iVar1 + 0x10),auStack_98);
        if (iVar2 != 0) {
          *(undefined1 *)(iVar1 + 0x18) = auStack_98[0];
          *(undefined1 *)(iVar1 + 0x12) = 0;
          HciLeLtkReqReplCmd(*param_1,iVar2);
          return;
        }
      }
      else {
        iVar2 = SmpDmLescEnabled(*(undefined1 *)(iVar1 + 0x10));
        if (iVar2 == 1) {
          HciLeLtkReqNegReplCmd(*param_1);
          return;
        }
      }
      DmConnSetIdle(*(undefined1 *)(iVar1 + 0x10),2,1);
      *(undefined1 *)(iVar1 + 0x12) = 1;
      *param_1 = (ushort)*(byte *)(iVar1 + 0x10);
      *(undefined1 *)(param_1 + 1) = 0x30;
      (**(code **)(DAT_004d252c + 8))(param_1);
    }
    else if (((char)param_1[1] == '\x0e') || ((char)param_1[1] == '\x0f')) {
      DmConnSetIdle(*(undefined1 *)(iVar1 + 0x10),2,0);
      uStack_94 = (ushort)*(byte *)(iVar1 + 0x10);
      cStack_91 = *(char *)((int)param_1 + 3);
      if (cStack_91 == '\0') {
        uStack_92 = 0x2c;
        *(undefined1 *)(iVar1 + 0x17) = *(undefined1 *)(iVar1 + 0x18);
        uStack_90 = *(undefined1 *)(iVar1 + 0x12);
      }
      else {
        uStack_92 = 0x2d;
      }
      DmSmpCbackExec(&uStack_94);
      uStack_94 = (ushort)*(byte *)(iVar1 + 0x10);
      cStack_91 = *(undefined1 *)((int)param_1 + 3);
      SmpDmEncryptInd(&uStack_94);
    }
  }
  return;
}

