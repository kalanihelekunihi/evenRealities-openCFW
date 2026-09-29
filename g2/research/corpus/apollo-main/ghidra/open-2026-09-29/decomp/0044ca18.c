
undefined8 FUN_0044ca18(int param_1,uint param_2,char param_3,int *param_4)

{
  undefined4 uVar1;
  int *piVar2;
  int *piVar3;
  byte bVar4;
  uint uVar5;
  
  uVar1 = DAT_0044cadc;
  bVar4 = 0;
  piVar2 = (int *)FUN_00482ce4(DAT_0044cadc);
  while ((piVar3 = piVar2, piVar3 != (int *)0x0 && (piVar3 != param_4))) {
    piVar2 = (int *)FUN_00482cfa(uVar1,piVar3);
    if (((*piVar3 == param_1) && ((param_2 == piVar3[2] || (param_2 == 0xf0000)))) &&
       ((param_3 == (char)piVar3[1] || (param_3 == -1)))) {
      for (uVar5 = 0; uVar5 < (*(ushort *)(param_1 + 0x2a) & 0x3ff) >> 4; uVar5 = uVar5 + 1) {
        if ((*(int *)(*(int *)(param_1 + 0xc) + uVar5 * 8 + 4) << 6 < 0) &&
           ((param_2 == 0xf0000 ||
            ((*(uint *)(*(int *)(param_1 + 0xc) + uVar5 * 8 + 4) & 0xffffff) == param_2)))) {
          FUN_004827b0(*(undefined4 *)(*(int *)(param_1 + 0xc) + uVar5 * 8),(char)piVar3[1]);
        }
      }
      FUN_00450500(piVar3,0);
      FUN_00482c0e(uVar1,piVar3);
      FUN_0044f758(piVar3);
      bVar4 = 1;
    }
  }
  return CONCAT44(param_4,(uint)bVar4);
}

