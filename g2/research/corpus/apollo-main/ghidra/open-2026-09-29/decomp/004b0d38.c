
uint FUN_004b0d38(uint *param_1,uint param_2,byte param_3,undefined4 param_4)

{
  undefined4 uVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  
  uVar3 = 0;
  iVar4 = 0;
  uVar1 = FUN_004b05a4(*param_1 >> 8 & 0xff);
  if (((((*param_1 & 0xffff) >> 8 != 7) && ((*param_1 & 0xffff) >> 8 != 8)) &&
      ((*param_1 & 0xffff) >> 8 != 9)) && ((*param_1 & 0xffff) >> 8 != 10)) goto LAB_004b0dd0;
  uVar3 = 0x200000;
  uVar2 = (*param_1 & 0xffff) >> 8;
  if (uVar2 == 7) {
    iVar4 = 2;
  }
  else if (uVar2 < 7) {
LAB_004b0db4:
    iVar4 = 0x100;
  }
  else if (uVar2 == 9) {
    iVar4 = 0x10;
  }
  else {
    if (8 < uVar2) goto LAB_004b0db4;
    iVar4 = 4;
  }
  FUN_004b1298(2,param_1[4],iVar4,1,0x10,0,4,param_4);
LAB_004b0dd0:
  if ((((*param_1 & 0xffff) >> 8 == 0xb) || ((*param_1 & 0xffff) >> 8 == 0xc)) ||
     (((*param_1 & 0xffff) >> 8 == 0xd || ((*param_1 & 0xffff) >> 8 == 0xe)))) {
    FUN_004b146c(param_2 | 0xff000000);
  }
  else {
    FUN_004b146c(0);
  }
  if ((*param_1 & 0xffff) >> 8 == 0x14) {
    FUN_004b1298(3,(param_1[2] & 0xffff) * (param_1[1] >> 0x10) + param_1[4],param_1[1] & 0xffff,
                 param_1[1] >> 0x10,8,0xffffffff,8,param_4);
    uVar3 = uVar3 | 0x800000;
  }
  if (param_2 >> 0x18 < 0xfd) {
    uVar3 = uVar3 | 0x8000000;
    FUN_00513e2e(param_2 & 0xff000000);
  }
  FUN_004b1298(1,param_1[4] + iVar4 * 4,param_1[1] & 0xffff,param_1[1] >> 0x10,uVar1,
               param_1[2] & 0xffff,param_3 | 1);
  return uVar3;
}

