
undefined8 FUN_0048e900(void)

{
  undefined4 uVar1;
  uint uVar2;
  undefined4 in_r3;
  uint uVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;
  
  uVar3 = DAT_0048ed78[3];
  uVar4 = DAT_0048ed78[2];
  if ((*DAT_0048ed78 == DAT_0048ed7c) && (DAT_0048ed78[1] == 0x1000)) {
    if (((DAT_0048ed78[4] | uVar3 | uVar4) & 3) == 0) {
      if (uVar4 - uVar3 < 0x1001) {
        if (uVar4 - uVar3 < DAT_0048ed78[4] - uVar3) {
          uVar1 = 0;
        }
        else {
          iVar5 = 0x202;
          uVar6 = uVar3;
          do {
            if (uVar6 == uVar4) {
              uVar1 = 1;
              goto LAB_0048e99a;
            }
            if (iVar5 == 0) {
              uVar1 = 0;
              goto LAB_0048e99a;
            }
            uVar2 = FUN_0048e8e2(uVar6);
            if (((uVar2 & 0xf0) != 0xa0) || (8 < (uVar2 & 0xf))) {
              uVar1 = 0;
              goto LAB_0048e99a;
            }
            uVar6 = (uVar2 & 0xf) * 4 + uVar6 + 8;
            iVar5 = iVar5 + -1;
          } while (uVar6 - uVar3 <= uVar4 - uVar3);
          uVar1 = 0;
        }
      }
      else {
        uVar1 = 0;
      }
    }
    else {
      uVar1 = 0;
    }
  }
  else {
    uVar1 = 0;
  }
LAB_0048e99a:
  return CONCAT44(in_r3,uVar1);
}

