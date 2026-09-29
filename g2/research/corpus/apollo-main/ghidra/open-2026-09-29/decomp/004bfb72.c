
undefined8 FUN_004bfb72(uint param_1,int param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  undefined4 uVar5;
  
  uVar2 = 0;
  uVar4 = param_3;
  if (param_1 < 4) {
    uVar5 = param_4;
    for (iVar3 = 0; iVar1 = DAT_004c0754, (uint)(iVar3 << 2) < param_3; iVar3 = iVar3 + 1) {
      *(undefined4 *)(DAT_004c0754 + param_1 * 0x1000 + 0x10) = *(undefined4 *)(param_2 + iVar3 * 4)
      ;
      uVar4 = 0;
      uVar2 = FUN_00480826(param_4,iVar1 + param_1 * 0x1000 + 0x18,0x3f,0x10,0,uVar5);
    }
  }
  else {
    uVar2 = 5;
  }
  return CONCAT44(uVar4,uVar2);
}

