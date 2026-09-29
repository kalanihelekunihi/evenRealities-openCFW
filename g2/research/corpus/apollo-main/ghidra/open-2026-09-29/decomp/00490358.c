
undefined8 FUN_00490358(int param_1,int param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined2 *puVar3;
  uint local_10;
  
  local_10 = param_4;
  iVar1 = FUN_0048f5ae(param_1,&local_10);
  if (iVar1 == 0) {
    uVar2 = 0;
  }
  else if (local_10 < 0x10000) {
    if (local_10 + 2 < local_10) {
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
    else if ((uint)*(ushort *)(param_2 + 0x12) < local_10 + 2) {
      uVar2 = DAT_004905cc;
      if (*(int *)(param_1 + 0xc) != 0) {
        uVar2 = *(undefined4 *)(param_1 + 0xc);
      }
      *(undefined4 *)(param_1 + 0xc) = uVar2;
      uVar2 = 0;
    }
    else {
      puVar3 = *(undefined2 **)(param_2 + 0x1c);
      *puVar3 = (short)local_10;
      uVar2 = FUN_0048f3be(param_1,puVar3 + 1,local_10);
    }
  }
  else {
    uVar2 = DAT_004905cc;
    if (*(int *)(param_1 + 0xc) != 0) {
      uVar2 = *(undefined4 *)(param_1 + 0xc);
    }
    *(undefined4 *)(param_1 + 0xc) = uVar2;
    uVar2 = 0;
  }
  return CONCAT44(local_10,uVar2);
}

