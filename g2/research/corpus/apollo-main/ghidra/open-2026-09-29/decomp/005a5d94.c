
undefined1 attsExecPrepWrite(int param_1,int param_2,undefined4 param_3,int param_4)

{
  undefined1 uVar1;
  int iVar2;
  int iVar3;
  int local_1c;
  
  uVar1 = 0;
  iVar3 = param_2 + 10;
  local_1c = param_4;
  iVar2 = attsFindByHandle(*(undefined2 *)(param_2 + 6),&local_1c,param_3,param_4,param_1,param_2,
                           param_3);
  if (iVar2 == 0) {
    uVar1 = 0xe;
  }
  else if ((int)((uint)*(byte *)(iVar2 + 0xf) << 0x1b) < 0) {
    if (((int)((uint)*(byte *)(iVar2 + 0xe) << 0x1e) < 0) && (*(int *)(local_1c + 0xc) != 0)) {
      uVar1 = (**(code **)(local_1c + 0xc))
                        (*(undefined1 *)(param_1 + 0x24),*(undefined2 *)(param_2 + 6),0x18,
                         *(undefined2 *)(param_2 + 8),*(undefined2 *)(param_2 + 4),iVar3,iVar2);
    }
    else if (((int)((uint)*(byte *)(iVar2 + 0xe) << 0x1a) < 0) &&
            (*(int *)(DAT_005a6258 + 0x26c) != 0)) {
      uVar1 = (**(code **)(DAT_005a6258 + 0x26c))
                        (*(undefined1 *)(param_1 + 0x24),9,*(undefined2 *)(param_2 + 6),iVar3);
    }
    else {
      FUN_00439be4(*(int *)(iVar2 + 4) + (uint)*(ushort *)(param_2 + 8),iVar3,
                   *(undefined2 *)(param_2 + 4));
      if ((int)((uint)*(byte *)(iVar2 + 0xe) << 0x1c) < 0) {
        **(short **)(iVar2 + 8) = *(short *)(param_2 + 8) + *(short *)(param_2 + 4);
      }
    }
  }
  else {
    uVar1 = 3;
  }
  return uVar1;
}

