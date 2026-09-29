
undefined8 bl_runtime_register(int param_1,uint param_2,int param_3,int *param_4)

{
  int iVar1;
  int *piVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  bool bVar7;
  uint uVar8;
  int iVar9;
  int *piVar10;
  
  iVar4 = 0;
  uVar8 = param_2;
  iVar9 = param_3;
  piVar10 = param_4;
  iVar1 = FUN_0041602a();
  if ((iVar1 == 0) && (param_1 != 0)) {
    piVar2 = (int *)0x0;
    uVar6 = 0;
    if ((param_4 != (int *)0x0) && ((param_4[2] != 0 && (0x33 < (uint)param_4[3])))) {
      piVar2 = (int *)(param_4[2] + 0x2c);
    }
    if ((piVar2 == (int *)0x0) && (piVar2 = (int *)FUN_00419730(8), piVar2 != (int *)0x0)) {
      uVar6 = 1;
    }
    if (piVar2 != (int *)0x0) {
      *piVar2 = param_1;
      piVar2[1] = param_3;
      bVar7 = (param_2 & 0xff) != 0;
      iVar1 = -1;
      iVar5 = 0;
      if (param_4 == (int *)0x0) {
        iVar1 = 0;
      }
      else {
        if (*param_4 != 0) {
          iVar5 = *param_4;
        }
        if ((param_4[2] == 0) || ((uint)param_4[3] < 0x2c)) {
          if ((param_4[2] == 0) && (param_4[3] == 0)) {
            iVar1 = 0;
          }
        }
        else {
          iVar1 = 1;
        }
      }
      uVar3 = uVar6 | (uint)piVar2;
      if (iVar1 == 1) {
        uVar8 = DAT_004169a0;
        iVar4 = FUN_004192de(iVar5,1,bVar7,uVar3,DAT_004169a0,param_4[2]);
      }
      else if (iVar1 == 0) {
        uVar8 = DAT_004169a0;
        iVar4 = FUN_004192a8(iVar5,1,bVar7,uVar3,DAT_004169a0,iVar9,piVar10);
      }
      if (((iVar4 == 0) && (uVar3 != 0)) && (uVar6 == 1)) {
        FUN_00419830((uint)piVar2 & 0xfffffffe);
      }
    }
  }
  return CONCAT44(uVar8,iVar4);
}

