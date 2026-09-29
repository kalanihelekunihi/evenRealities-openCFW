
undefined8 FUN_004ce3bc(int param_1,uint param_2,uint param_3,int param_4)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint local_20;
  uint local_1c;
  int iStack_18;
  
  uVar4 = param_3;
  local_20 = param_2;
  local_1c = param_3;
  iStack_18 = param_4;
  if (param_4 != 0) {
    if (param_4 == 1) {
      uVar4 = param_3 + *(int *)(param_2 + 0x34);
    }
    else {
      uVar4 = *(uint *)(param_2 + 0x34);
      if (param_4 == 2) {
        iVar1 = lfs_file_size_(param_1,param_2);
        uVar4 = param_3 + iVar1;
      }
    }
  }
  if (*(uint *)(param_1 + 0x74) < uVar4) {
    uVar3 = 0xffffffea;
  }
  else {
    uVar3 = uVar4;
    if (*(uint *)(param_2 + 0x34) != uVar4) {
      if ((*(int *)(param_2 + 0x30) << 0xd < 0) &&
         (*(int *)(param_2 + 0x3c) != *(int *)(*(int *)(param_1 + 0x68) + 0x1c))) {
        local_1c = *(uint *)(param_2 + 0x34);
        iVar1 = FUN_004cd6e4(param_1,&local_1c);
        local_20 = uVar4;
        iVar2 = FUN_004cd6e4(param_1,&local_20);
        if ((iVar1 == iVar2) &&
           ((*(uint *)(param_2 + 0x44) <= local_20 &&
            (local_20 < (uint)(*(int *)(param_2 + 0x48) + *(int *)(param_2 + 0x44)))))) {
          *(uint *)(param_2 + 0x34) = uVar4;
          *(uint *)(param_2 + 0x3c) = local_20;
          goto LAB_004ce45a;
        }
      }
      uVar3 = FUN_004cde54(param_1,param_2);
      if (uVar3 == 0) {
        *(uint *)(param_2 + 0x34) = uVar4;
        uVar3 = uVar4;
      }
    }
  }
LAB_004ce45a:
  return CONCAT44(local_20,uVar3);
}

