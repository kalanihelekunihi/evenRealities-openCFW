
undefined8 FUN_005cfb62(char *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = 0;
  do {
    iVar1 = DAT_005d0700;
    if (0x49 < (int)uVar3) {
      uVar3 = 0x4b;
LAB_005cfbb2:
      return CONCAT44(param_4,uVar3);
    }
    if (**(char **)(DAT_005d0700 + uVar3 * 4) == *param_1) {
      for (; (int)uVar3 < 0x4a; uVar3 = uVar3 + 1) {
        if (**(char **)(iVar1 + uVar3 * 4) != *param_1) {
          uVar3 = 0x4b;
          goto LAB_005cfbb2;
        }
        iVar2 = FUN_0044b610(*(undefined4 *)(iVar1 + uVar3 * 4),param_1,param_2);
        if (iVar2 == 0) {
          uVar3 = uVar3 & 0xff;
          goto LAB_005cfbb2;
        }
      }
    }
    uVar3 = uVar3 + 1;
  } while( true );
}

