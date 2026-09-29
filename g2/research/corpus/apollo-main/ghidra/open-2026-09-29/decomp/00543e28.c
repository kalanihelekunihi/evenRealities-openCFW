
undefined4 FUN_00543e28(int param_1,undefined4 param_2,undefined4 param_3,undefined4 *param_4)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  undefined1 auStack_60 [64];
  
  uVar1 = FUN_00585840(0,param_2,param_3);
  uVar3 = 0;
  do {
    if (0x3f < uVar3) {
      return 0;
    }
    if ((*(int *)(param_1 + uVar3 * 8 + 0xac) != -1) &&
       ((uint)*(ushort *)(param_1 + uVar3 * 8 + 0xa8) == uVar1 >> 0x10)) {
      FUN_0043c0e4(auStack_60,0x40,0);
      FUN_00585a12(param_1,*(int *)(param_1 + uVar3 * 8 + 0xac) + 0x18,auStack_60,0x40);
      iVar2 = FUN_0044b610(param_2,auStack_60,param_3);
      if (iVar2 == 0) {
        *param_4 = *(undefined4 *)(param_1 + uVar3 * 8 + 0xac);
        if (*(ushort *)(param_1 + uVar3 * 8 + 0xaa) < 0xffbf) {
          *(short *)(param_1 + uVar3 * 8 + 0xaa) = *(short *)(param_1 + uVar3 * 8 + 0xaa) + 0x40;
        }
        else {
          *(undefined2 *)(param_1 + uVar3 * 8 + 0xaa) = 0xffff;
        }
        return 1;
      }
    }
    uVar3 = uVar3 + 1;
  } while( true );
}

