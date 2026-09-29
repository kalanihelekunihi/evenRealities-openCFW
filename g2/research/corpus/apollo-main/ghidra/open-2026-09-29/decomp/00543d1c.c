
int FUN_00543d1c(int param_1,undefined4 param_2,undefined4 param_3,int param_4)

{
  undefined2 uVar1;
  uint uVar2;
  uint uVar3;
  ushort uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  
  uVar7 = 0x40;
  uVar2 = FUN_00585840(0);
  uVar4 = 0xffff;
  uVar3 = 0;
  uVar6 = 0x40;
  do {
    if (0x3f < uVar3) {
      uVar1 = (undefined2)(uVar2 >> 0x10);
      if (uVar6 < 0x40) {
        *(int *)(param_1 + uVar6 * 8 + 0xac) = param_4;
        *(undefined2 *)(param_1 + uVar6 * 8 + 0xa8) = uVar1;
        *(undefined2 *)(param_1 + uVar6 * 8 + 0xaa) = 0x40;
      }
      else if (uVar7 < 0x40) {
        *(int *)(param_1 + uVar7 * 8 + 0xac) = param_4;
        *(undefined2 *)(param_1 + uVar7 * 8 + 0xa8) = uVar1;
        *(undefined2 *)(param_1 + uVar7 * 8 + 0xaa) = 0x40;
      }
      return param_4;
    }
    if (param_4 == -1) {
      uVar5 = uVar6;
      if ((uint)*(ushort *)(param_1 + uVar3 * 8 + 0xa8) == uVar2 >> 0x10) {
        *(undefined4 *)(param_1 + uVar3 * 8 + 0xac) = 0xffffffff;
        *(undefined2 *)(param_1 + uVar3 * 8 + 0xaa) = 0;
        return -1;
      }
    }
    else {
      if ((uint)*(ushort *)(param_1 + uVar3 * 8 + 0xa8) == uVar2 >> 0x10) {
        *(int *)(param_1 + uVar3 * 8 + 0xac) = param_4;
        return param_4;
      }
      if (((*(int *)(param_1 + uVar3 * 8 + 0xac) != -1) || (uVar5 = uVar3, uVar6 != 0x40)) &&
         (uVar5 = uVar6, *(int *)(param_1 + uVar3 * 8 + 0xac) != -1)) {
        if (*(short *)(param_1 + uVar3 * 8 + 0xaa) != 0) {
          *(short *)(param_1 + uVar3 * 8 + 0xaa) = *(short *)(param_1 + uVar3 * 8 + 0xaa) + -1;
        }
        if (*(ushort *)(param_1 + uVar3 * 8 + 0xaa) < uVar4) {
          uVar4 = *(ushort *)(param_1 + uVar3 * 8 + 0xaa);
          uVar7 = uVar3;
        }
      }
    }
    uVar3 = uVar3 + 1;
    uVar6 = uVar5;
  } while( true );
}

