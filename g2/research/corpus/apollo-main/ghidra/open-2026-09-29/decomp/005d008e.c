
int FUN_005d008e(undefined4 *param_1,byte *param_2,int param_3)

{
  char cVar1;
  bool bVar2;
  int iVar3;
  byte *pbVar4;
  bool bVar5;
  
  pbVar4 = (byte *)*param_1;
  iVar3 = 0;
  bVar5 = false;
  bVar2 = false;
  if (pbVar4 < param_2) {
    if (0x22 < param_3 - 2U) {
      return 0;
    }
    if ((*pbVar4 == 0x2d) || (*pbVar4 == 0x2b)) {
      bVar5 = *pbVar4 == 0x2d;
      pbVar4 = pbVar4 + 1;
      if (pbVar4 == param_2) goto LAB_005d00a0;
      if ((*pbVar4 == 0x2d) || (*pbVar4 == 0x2b)) {
        return 0;
      }
    }
    while (((((((pbVar4 < param_2 && (*pbVar4 != 0x20)) && (*pbVar4 != 0xd)) &&
              ((*pbVar4 != 10 && (*pbVar4 != 9)))) &&
             ((*pbVar4 != 0xc && ((*pbVar4 != 0 && (*pbVar4 < 0x80)))))) &&
            (cVar1 = *(char *)(DAT_005d070c + (*pbVar4 & 0x7f)), -1 < cVar1)) && (cVar1 < param_3)))
    {
      if ((0x7fffffff / param_3 < iVar3) ||
         ((iVar3 == 0x7fffffff / param_3 &&
          ((char)(-1 - (char)param_3 * (char)(0x7fffffff / param_3)) < cVar1)))) {
        bVar2 = true;
      }
      else {
        iVar3 = param_3 * iVar3 + (int)cVar1;
      }
      pbVar4 = pbVar4 + 1;
    }
    *param_1 = pbVar4;
    if (bVar2) {
      iVar3 = 0x7fffffff;
    }
    if (bVar5) {
      iVar3 = -iVar3;
    }
  }
  else {
LAB_005d00a0:
    iVar3 = 0;
  }
  return iVar3;
}

