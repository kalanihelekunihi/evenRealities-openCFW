
undefined8 FUN_004903ea(int param_1,int param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  uint local_18;
  undefined4 uStack_14;
  
  iVar3 = *(int *)(param_2 + 0x1c);
  local_18 = param_3;
  uStack_14 = param_4;
  iVar1 = FUN_0048f5ae(param_1,&local_18);
  if (iVar1 == 0) {
    uVar2 = 0;
  }
  else if (local_18 == 0xffffffff) {
    uVar2 = DAT_004905d0;
    if (*(int *)(param_1 + 0xc) != 0) {
      uVar2 = *(undefined4 *)(param_1 + 0xc);
    }
    *(undefined4 *)(param_1 + 0xc) = uVar2;
    uVar2 = 0;
  }
  else if (local_18 + 1 < local_18) {
    uVar2 = DAT_004905d0;
    if (*(int *)(param_1 + 0xc) != 0) {
      uVar2 = *(undefined4 *)(param_1 + 0xc);
    }
    *(undefined4 *)(param_1 + 0xc) = uVar2;
    uVar2 = 0;
  }
  else if ((*(byte *)(param_2 + 0x16) & 0xc0) == 0x80) {
    uVar2 = DAT_004905ac;
    if (*(int *)(param_1 + 0xc) != 0) {
      uVar2 = *(undefined4 *)(param_1 + 0xc);
    }
    *(undefined4 *)(param_1 + 0xc) = uVar2;
    uVar2 = 0;
  }
  else if ((uint)*(ushort *)(param_2 + 0x12) < local_18 + 1) {
    uVar2 = DAT_004905d4;
    if (*(int *)(param_1 + 0xc) != 0) {
      uVar2 = *(undefined4 *)(param_1 + 0xc);
    }
    *(undefined4 *)(param_1 + 0xc) = uVar2;
    uVar2 = 0;
  }
  else {
    *(undefined1 *)(iVar3 + local_18) = 0;
    iVar1 = FUN_0048f3be(param_1,iVar3,local_18);
    if (iVar1 == 0) {
      uVar2 = 0;
    }
    else {
      uVar2 = 1;
    }
  }
  return CONCAT44(local_18,uVar2);
}

