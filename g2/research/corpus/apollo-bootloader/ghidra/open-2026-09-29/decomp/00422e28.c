
undefined8 FUN_00422e28(int param_1,int param_2,uint *param_3)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  uint uVar4;
  uint uVar5;
  undefined8 uVar6;
  
  iVar1 = DAT_00423440;
  uVar2 = *(uint *)(DAT_00423440 + param_1 * 0x1000 + 0x30) >> 4 & 7;
  uVar5 = DAT_00423840;
  if ((uVar2 == 1) ||
     ((uVar2 != 0 &&
      ((((uVar5 = DAT_00423848, uVar2 == 3 || (uVar5 = DAT_00423844, uVar2 < 3)) ||
        (uVar5 = DAT_0042383c, uVar2 == 5)) ||
       ((uVar5 = DAT_004236fc, uVar2 < 5 || (uVar5 = DAT_00423834, uVar2 == 6)))))))) {
    uVar4 = uVar5 / (uint)(param_2 << 4);
    uVar6 = FUN_0042287c(uVar5 << 6,uVar5 >> 0x1a,param_2 << 4,0);
    uVar2 = (uint)uVar6 + uVar4 * -0x40;
    param_2 = ((int)((ulonglong)uVar6 >> 0x20) - (uVar4 >> 0x1a)) -
              (uint)((uint)uVar6 < uVar4 * 0x40);
    if (uVar4 == 0) {
      *param_3 = 0;
      uVar3 = DAT_00423838;
    }
    else {
      param_2 = iVar1 + param_1 * 0x1000;
      *(uint *)(param_2 + 0x24) = uVar4;
      *(uint *)(iVar1 + param_1 * 0x1000 + 0x28) = uVar2;
      *param_3 = uVar5 / ((uVar2 >> 2) + uVar4 * 0x10);
      uVar3 = 0;
    }
  }
  else {
    *param_3 = 0;
    uVar3 = DAT_0042384c;
  }
  return CONCAT44(param_2,uVar3);
}

