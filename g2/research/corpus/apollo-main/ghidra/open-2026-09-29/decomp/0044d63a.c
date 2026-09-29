
undefined8 FUN_0044d63a(int param_1,code *param_2,code *param_3,code *param_4)

{
  bool bVar1;
  bool bVar2;
  char cVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  int *piVar7;
  int *piVar8;
  undefined4 local_28;
  
  if ((int)((uint)*(byte *)(param_1 + 0x1c) << 0x1f) < 0) {
    uVar4 = 0;
    local_28 = param_4;
  }
  else {
    piVar8 = *(int **)(param_1 + 0xc);
    piVar7 = (int *)0x0;
    bVar2 = true;
    do {
      do {
        bVar1 = true;
        local_28 = param_2;
        if (piVar8 == (int *)0x0) {
          if (((*(byte *)(param_1 + 0x1c) & 0xf) >> 3 == 0) && (piVar7 != (int *)0x0)) {
            uVar4 = 0;
            goto LAB_0044d776;
          }
          if (!bVar2) {
            uVar4 = 0;
            goto LAB_0044d776;
          }
          piVar8 = (int *)(*param_2)(param_1);
          bVar1 = false;
          bVar2 = false;
        }
        if ((piVar7 == (int *)0x0) && (piVar7 = piVar8, piVar8 == (int *)0x0)) {
          uVar4 = 0;
          goto LAB_0044d776;
        }
        if ((bVar1) && (piVar8 = (int *)(*param_3)(param_1,piVar8), piVar8 == piVar7)) {
          uVar4 = 0;
          goto LAB_0044d776;
        }
      } while ((piVar8 == (int *)0x0) || (iVar5 = FUN_0043e156(*piVar8), iVar5 << 0x18 < 0));
      iVar5 = *piVar8;
      while ((iVar5 != 0 && (iVar6 = FUN_0043e0e0(iVar5,1), iVar6 == 0))) {
        iVar5 = FUN_0044dca2(iVar5);
      }
    } while ((iVar5 != 0) && (iVar5 = FUN_0043e0e0(iVar5,1), iVar5 != 0));
    if (piVar8 == *(int **)(param_1 + 0xc)) {
      uVar4 = 0;
    }
    else {
      if (*(int *)(param_1 + 0xc) != 0) {
        uVar4 = FUN_0044d77a(param_1);
        cVar3 = FUN_00451670(**(undefined4 **)(param_1 + 0xc),0x14,uVar4);
        if (cVar3 != '\x01') {
          uVar4 = 0;
          goto LAB_0044d776;
        }
        FUN_00440656(**(undefined4 **)(param_1 + 0xc));
      }
      *(int **)(param_1 + 0xc) = piVar8;
      uVar4 = FUN_0044d77a(param_1);
      cVar3 = FUN_00451670(**(undefined4 **)(param_1 + 0xc),0x13,uVar4);
      if (cVar3 == '\x01') {
        FUN_00440656(**(undefined4 **)(param_1 + 0xc));
        if (*(int *)(param_1 + 0x10) != 0) {
          (**(code **)(param_1 + 0x10))(param_1);
        }
        uVar4 = 1;
      }
      else {
        uVar4 = 0;
      }
    }
  }
LAB_0044d776:
  return CONCAT44(local_28,uVar4);
}

