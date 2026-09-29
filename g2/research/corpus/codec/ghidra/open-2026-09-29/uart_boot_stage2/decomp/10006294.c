
undefined4 FUN_10006294(byte *param_1,byte *param_2,int param_3)

{
  byte bVar1;
  undefined4 uVar2;
  byte *pbVar3;
  byte bVar4;
  
  if (param_3 != 0) {
    bVar4 = *param_2;
    bVar1 = *param_1;
    if (bVar1 != bVar4) {
LAB_100062ce:
      uVar2 = 1;
      if (bVar1 < bVar4) {
        uVar2 = 0xffffffff;
      }
      return uVar2;
    }
    if (bVar1 != 0) {
      pbVar3 = param_2 + param_3;
      do {
        param_1 = param_1 + 1;
        param_2 = param_2 + 1;
        if (param_2 == pbVar3) {
          return 0;
        }
        bVar1 = *param_1;
        bVar4 = *param_2;
        if (bVar1 != bVar4) goto LAB_100062ce;
      } while (bVar1 != 0);
    }
  }
  return 0;
}

