
undefined4 FUN_00542c20(undefined4 param_1,undefined4 param_2,int param_3,undefined4 *param_4)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  undefined4 *puVar4;
  uint in_fpscr;
  undefined4 uVar5;
  double dVar6;
  undefined4 extraout_s1;
  double dVar7;
  int local_2c;
  undefined4 local_28;
  undefined4 auStack_24 [3];
  
  if (param_4 != (undefined4 *)0x0) {
    *param_4 = 0;
  }
  auStack_24[2] = param_1;
  uVar1 = FUN_00585134(auStack_24 + 2);
  uVar2 = uVar1 & 0xfffffff7;
  if (uVar2 == 1) {
    iVar3 = FUN_00585258(param_1,auStack_24[2],param_2,&local_2c,2);
    dVar7 = DAT_00542d1c;
    if ((iVar3 != 0) &&
       (dVar7 = (double)VectorSignedToFloat(local_28,(byte)(in_fpscr >> 0x16) & 3), 1 < iVar3)) {
      iVar3 = iVar3 + -1;
      puVar4 = auStack_24;
      do {
        dVar6 = (double)VectorSignedToFloat(*puVar4,(byte)(in_fpscr >> 0x16) & 3);
        iVar3 = iVar3 + -1;
        dVar7 = dVar6 + dVar7 * DAT_00542d24;
        puVar4 = puVar4 + 1;
      } while (iVar3 != 0);
    }
    uVar5 = SUB84(dVar7,0);
    param_3 = local_2c + param_3;
  }
  else {
    if (uVar2 != 2) {
      dVar7 = DAT_00542d34;
      if ((uVar2 != 3) && (dVar7 = DAT_00542d3c, uVar2 != 4)) {
        dVar7 = DAT_00542d1c;
      }
      goto LAB_00542d00;
    }
    iVar3 = FUN_00585410(param_1,auStack_24[2],param_2,&local_2c,2);
    dVar7 = DAT_00542d1c;
    if ((iVar3 != 0) &&
       (dVar7 = (double)VectorSignedToFloat(local_28,(byte)(in_fpscr >> 0x16) & 3), 1 < iVar3)) {
      iVar3 = iVar3 + -1;
      puVar4 = auStack_24;
      do {
        dVar6 = (double)VectorSignedToFloat(*puVar4,(byte)(in_fpscr >> 0x16) & 3);
        iVar3 = iVar3 + -1;
        dVar7 = dVar6 + dVar7 * DAT_00542d2c;
        puVar4 = puVar4 + 1;
      } while (iVar3 != 0);
    }
    uVar5 = FUN_004d4208(SUB84(dVar7,0),local_2c);
  }
  uVar5 = FUN_00542a80(uVar5,param_3,param_4);
  dVar7 = (double)CONCAT44(extraout_s1,uVar5);
LAB_00542d00:
  if (((int)uVar1 >> 3 & 1U) != 0) {
    dVar7 = -dVar7;
  }
  return SUB84(dVar7,0);
}

