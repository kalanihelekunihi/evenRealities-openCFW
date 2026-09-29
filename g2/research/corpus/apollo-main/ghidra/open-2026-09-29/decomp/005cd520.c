
undefined8 FUN_005cd520(int param_1,uint *param_2,uint *param_3,int param_4)

{
  byte bVar1;
  byte bVar2;
  char cVar3;
  uint uVar4;
  undefined4 uVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  uint *local_28;
  int local_24;
  
  local_28 = param_3;
  local_24 = param_4;
  FUN_00452ef8();
  cVar3 = FUN_00452f00();
  if ((cVar3 == '\x01') || (cVar3 == '\x03')) {
    uVar5 = FUN_00452ef8();
    FUN_00452f5e(uVar5,&local_28);
    bVar2 = 0;
    bVar1 = 0;
    if (param_3 != (uint *)0x0) {
      iVar6 = FUN_0044e486(param_1);
      iVar6 = iVar6 + (int)local_28;
      iVar7 = FUN_005ccb9a(param_1,0);
      if (iVar7 == 1) {
        iVar7 = FUN_005ccb68(param_1,0);
        iVar6 = (*(int *)(param_1 + 0x1c) - iVar7) - iVar6;
      }
      else {
        iVar7 = *(int *)(param_1 + 0x14);
        iVar8 = FUN_005ccb5e(param_1,0);
        iVar6 = (iVar6 - iVar7) - iVar8;
      }
      *param_3 = 0;
      iVar7 = 0;
      *param_3 = 0;
      while (*param_3 < *(uint *)(param_1 + 0x2c)) {
        iVar7 = *(int *)(*(int *)(param_1 + 0x3c) + *param_3 * 4) + iVar7;
        if (iVar6 < iVar7) {
          bVar2 = 1;
          break;
        }
        *param_3 = *param_3 + 1;
      }
    }
    if (param_2 != (uint *)0x0) {
      iVar6 = FUN_0044e498(param_1);
      iVar6 = iVar6 + local_24;
      iVar7 = *(int *)(param_1 + 0x18);
      iVar8 = FUN_005ccb4a(param_1,0);
      *param_2 = 0;
      iVar9 = 0;
      *param_2 = 0;
      while (*param_2 < *(uint *)(param_1 + 0x30)) {
        iVar9 = *(int *)(*(int *)(param_1 + 0x38) + *param_2 * 4) + iVar9;
        if ((iVar6 - iVar7) - iVar8 < iVar9) {
          bVar1 = 1;
          break;
        }
        *param_2 = *param_2 + 1;
      }
    }
    uVar4 = (uint)(bVar2 & bVar1);
  }
  else {
    if (param_3 != (uint *)0x0) {
      *param_3 = 0xffff;
    }
    if (param_2 != (uint *)0x0) {
      *param_2 = 0xffff;
    }
    uVar4 = 0;
  }
  return CONCAT44(local_28,uVar4);
}

