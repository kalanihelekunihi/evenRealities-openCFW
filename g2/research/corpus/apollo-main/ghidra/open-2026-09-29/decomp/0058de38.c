
undefined8 FUN_0058de38(int param_1,int param_2,uint *param_3)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  uint uVar4;
  uint uVar5;
  undefined8 uVar6;
  
  iVar1 = DAT_0058e450;
  uVar2 = *(uint *)(DAT_0058e450 + param_1 * 0x1000 + 0x30) >> 4 & 7;
  uVar5 = DAT_0058e924;
  if ((uVar2 == 1) ||
     ((uVar2 != 0 &&
      ((((uVar5 = DAT_0058e92c, uVar2 == 3 || (uVar5 = DAT_0058e928, uVar2 < 3)) ||
        (uVar5 = DAT_0058e920, uVar2 == 5)) ||
       ((uVar5 = DAT_0058e7e0, uVar2 < 5 || (uVar5 = DAT_0058e918, uVar2 == 6)))))))) {
    uVar4 = uVar5 / (uint)(param_2 << 4);
    uVar6 = FUN_0047cc60(uVar5 << 6,uVar5 >> 0x1a,param_2 << 4,0);
    uVar2 = (uint)uVar6 + uVar4 * -0x40;
    param_2 = ((int)((ulonglong)uVar6 >> 0x20) - (uVar4 >> 0x1a)) -
              (uint)((uint)uVar6 < uVar4 * 0x40);
    if (uVar4 == 0) {
      *param_3 = 0;
      uVar3 = DAT_0058e91c;
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
    uVar3 = DAT_0058e930;
  }
  return CONCAT44(param_2,uVar3);
}

