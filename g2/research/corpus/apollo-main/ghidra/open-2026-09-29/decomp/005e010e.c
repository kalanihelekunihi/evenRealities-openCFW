
undefined8 FUN_005e010e(int param_1,uint param_2,undefined4 *param_3,undefined4 param_4)

{
  ushort uVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  
  if (param_1 == 0) {
    uVar2 = 0x23;
  }
  else if (param_2 < *(ushort *)(param_1 + 0x108)) {
    iVar4 = *(int *)(param_1 + 0x220);
    if (iVar4 == 0) {
      uVar2 = 7;
    }
    else {
      uVar2 = (**(code **)(iVar4 + 0x10))(0);
      *param_3 = uVar2;
      iVar3 = *(int *)(param_1 + 0x1dc);
      if (iVar3 == 0x10000) {
        if (param_2 < 0x102) {
          uVar2 = (**(code **)(iVar4 + 0x10))(param_2);
          *param_3 = uVar2;
        }
      }
      else if (iVar3 == 0x20000) {
        if (((*(char *)(param_1 + 0x278) != '\0') || (iVar3 = FUN_005e0002(param_1), iVar3 == 0)) &&
           (param_2 < *(ushort *)(param_1 + 0x27c))) {
          uVar1 = *(ushort *)(*(int *)(param_1 + 0x280) + param_2 * 2);
          if (uVar1 < 0x102) {
            uVar2 = (**(code **)(iVar4 + 0x10))(uVar1);
            *param_3 = uVar2;
          }
          else {
            *param_3 = *(undefined4 *)(*(int *)(param_1 + 0x284) + (uint)uVar1 * 4 + -0x408);
          }
        }
      }
      else if ((iVar3 == 0x25000) &&
              (((*(char *)(param_1 + 0x278) != '\0' || (iVar3 = FUN_005e0002(param_1), iVar3 == 0))
               && (param_2 < *(ushort *)(param_1 + 0x27c))))) {
        uVar2 = (**(code **)(iVar4 + 0x10))
                          (param_2 + (int)*(char *)(*(int *)(param_1 + 0x280) + param_2));
        *param_3 = uVar2;
      }
      uVar2 = 0;
    }
  }
  else {
    uVar2 = 0x10;
  }
  return CONCAT44(param_4,uVar2);
}

