
undefined8
hciCoreTxAclContinue(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  ushort uVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  
  if (param_1 == 0) {
    param_1 = hciCoreNextConnFragment();
  }
  if (param_1 != 0) {
    uVar1 = HciGetBufSize();
    if (*(ushort *)(param_1 + 0x12) < uVar1) {
      uVar4 = (uint)*(ushort *)(param_1 + 0x12);
    }
    else {
      uVar4 = HciGetBufSize();
    }
    if ((uVar4 & 0xffff) != 0) {
      **(undefined1 **)(param_1 + 4) = (char)*(undefined2 *)(param_1 + 0x10);
      *(byte *)(*(int *)(param_1 + 4) + 1) =
           (byte)((ushort)*(undefined2 *)(param_1 + 0x10) >> 8) | 0x10;
      *(char *)(*(int *)(param_1 + 4) + 2) = (char)uVar4;
      *(char *)(*(int *)(param_1 + 4) + 3) = (char)(uVar4 >> 8);
      iVar2 = hciCoreSendAclData(param_1,*(undefined4 *)(param_1 + 4));
      if (iVar2 == 1) {
        *(short *)(param_1 + 0x12) = *(short *)(param_1 + 0x12) - (short)uVar4;
        if (*(short *)(param_1 + 0x12) != 0) {
          *(uint *)(param_1 + 4) = *(int *)(param_1 + 4) + (uVar4 & 0xffff);
        }
        hciCoreTxAclComplete(param_1,*(undefined4 *)(param_1 + 4));
        uVar3 = 1;
      }
      else {
        uVar3 = 0;
      }
      goto LAB_0052a934;
    }
  }
  uVar3 = 0;
LAB_0052a934:
  return CONCAT44(param_4,uVar3);
}

