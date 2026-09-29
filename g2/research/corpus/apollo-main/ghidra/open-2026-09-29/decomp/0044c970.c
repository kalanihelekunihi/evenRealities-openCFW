
undefined4 FUN_0044c970(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  undefined4 uVar2;
  uint uVar3;
  
  uVar1 = 0;
  do {
    if ((*(ushort *)(param_2 + 0x2a) & 0x3ff) >> 4 <= uVar1) {
LAB_0044c9ba:
      uVar1 = FUN_0044ddea(param_2);
      for (uVar3 = 0; uVar3 < uVar1; uVar3 = uVar3 + 1) {
        FUN_0044c970(param_1,*(undefined4 *)(**(int **)(param_2 + 8) + uVar3 * 4));
      }
      return param_4;
    }
    if ((param_1 == 0) || (*(int *)(*(int *)(param_2 + 0xc) + uVar1 * 8) == param_1)) {
      uVar2 = FUN_0044b860(*(uint *)(*(int *)(param_2 + 0xc) + uVar1 * 8 + 4) & 0xffffff);
      FUN_0044ce2a(param_2,uVar2);
      FUN_0044bc8c(param_2,0xf0000,0xff);
      goto LAB_0044c9ba;
    }
    uVar1 = uVar1 + 1;
  } while( true );
}

