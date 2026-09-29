
undefined8 FUN_005d2828(int param_1,int param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  byte bVar3;
  uint uVar4;
  int iVar5;
  
  iVar2 = *(int *)(param_1 + 0x14);
  iVar5 = 0;
  bVar3 = 0;
  uVar4 = 0;
  do {
    if (*(uint *)(param_1 + 4) <= uVar4) {
LAB_005d29c8:
      if (bVar3 != 0) {
        iVar2 = FUN_005d3644(param_2);
        if (iVar2 != 0) {
          *(int *)(param_2 + 0xc) = iVar5 + *(int *)(param_2 + 0xc);
          FUN_005d36ae(param_2);
        }
        iVar2 = FUN_005d3644(param_3);
        if (iVar2 != 0) {
          *(int *)(param_3 + 0xc) = iVar5 + *(int *)(param_3 + 0xc);
          FUN_005d36ae(param_3);
        }
      }
      return CONCAT44(param_4,(uint)bVar3);
    }
    if ((((*(char *)(uVar4 * 0x14 + param_1 + 0x54) != '\0') &&
         (iVar1 = FUN_005d3684(param_2), iVar1 != 0)) &&
        (*(int *)(uVar4 * 0x14 + param_1 + 0x44) - iVar2 <= *(int *)(param_2 + 8))) &&
       (*(int *)(param_2 + 8) <= iVar2 + *(int *)(uVar4 * 0x14 + param_1 + 0x48))) {
      if (*(char *)(param_1 + 8) == '\0') {
        if (*(int *)(uVar4 * 0x14 + param_1 + 0x48) - *(int *)(param_2 + 8) <
            *(int *)(param_1 + 0x10)) {
          uVar4 = *(int *)(param_2 + 0xc) + 0x8000U & 0xffff0000;
        }
        else if ((int)(*(int *)(param_2 + 0xc) + 0x8000U & 0xffff0000) <
                 *(int *)(uVar4 * 0x14 + param_1 + 0x50) + -0x10000) {
          uVar4 = *(int *)(param_2 + 0xc) + 0x8000U & 0xffff0000;
        }
        else {
          uVar4 = *(int *)(param_1 + uVar4 * 0x14 + 0x50) - 0x10000;
        }
      }
      else {
        uVar4 = *(uint *)(param_1 + uVar4 * 0x14 + 0x50);
      }
      iVar5 = uVar4 - *(int *)(param_2 + 0xc);
      bVar3 = 1;
      goto LAB_005d29c8;
    }
    if (((*(char *)(uVar4 * 0x14 + param_1 + 0x54) == '\0') &&
        (iVar1 = FUN_005d3672(param_3), iVar1 != 0)) &&
       ((*(int *)(uVar4 * 0x14 + param_1 + 0x44) - iVar2 <= *(int *)(param_3 + 8) &&
        (*(int *)(param_3 + 8) <= iVar2 + *(int *)(uVar4 * 0x14 + param_1 + 0x48))))) {
      if (*(char *)(param_1 + 8) == '\0') {
        if (*(int *)(param_3 + 8) - *(int *)(uVar4 * 0x14 + param_1 + 0x44) <
            *(int *)(param_1 + 0x10)) {
          uVar4 = *(int *)(param_3 + 0xc) + 0x8000U & 0xffff0000;
        }
        else if (*(int *)(uVar4 * 0x14 + param_1 + 0x50) + 0x10000 <
                 (int)(*(int *)(param_3 + 0xc) + 0x8000U & 0xffff0000)) {
          uVar4 = *(int *)(param_3 + 0xc) + 0x8000U & 0xffff0000;
        }
        else {
          uVar4 = *(int *)(param_1 + uVar4 * 0x14 + 0x50) + 0x10000;
        }
      }
      else {
        uVar4 = *(uint *)(param_1 + uVar4 * 0x14 + 0x50);
      }
      iVar5 = uVar4 - *(int *)(param_3 + 0xc);
      bVar3 = 1;
      goto LAB_005d29c8;
    }
    uVar4 = uVar4 + 1;
  } while( true );
}

