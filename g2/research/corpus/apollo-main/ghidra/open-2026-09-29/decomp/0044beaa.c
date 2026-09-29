
undefined8 FUN_0044beaa(int param_1,undefined1 param_2,undefined4 param_3,uint param_4)

{
  undefined4 uVar1;
  uint uVar2;
  
  uVar2 = 0;
  do {
    if ((*(ushort *)(param_1 + 0x2a) & 0x3ff) >> 4 <= uVar2) {
      uVar1 = 0;
LAB_0044bef0:
      return CONCAT44(param_4,uVar1);
    }
    if ((*(int *)(*(int *)(param_1 + 0xc) + uVar2 * 8 + 4) << 7 < 0) &&
       ((*(uint *)(*(int *)(param_1 + 0xc) + uVar2 * 8 + 4) & 0xffffff) == param_4)) {
      uVar1 = FUN_00482946(*(undefined4 *)(*(int *)(param_1 + 0xc) + uVar2 * 8),param_2);
      goto LAB_0044bef0;
    }
    uVar2 = uVar2 + 1;
  } while( true );
}

