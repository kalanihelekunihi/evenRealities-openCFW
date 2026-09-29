
void FUN_005e4e32(int param_1,int param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  undefined1 uVar5;
  undefined1 uVar6;
  
  uVar6 = 0;
  uVar5 = 0;
  uVar3 = 0;
  uVar4 = 0;
  if ((param_1 == 0) || (*(int *)(param_1 + 500) == 0)) {
    FUN_005e4dd8(param_3,0,0,0,0,param_4);
  }
  else {
    if (param_2 == 0x44) {
      if (*(char *)(param_1 + 0x278) == '\0') {
        iVar1 = FUN_0044e498(*(undefined4 *)(param_1 + 500));
        if (0 < iVar1) {
          uVar4 = 1;
          uVar6 = 1;
        }
      }
      else if (*(char *)(param_1 + 0x278) == '\x01') {
        uVar5 = 1;
      }
      else {
        uVar6 = 1;
      }
    }
    else if (param_2 == 0x45) {
      if (*(char *)(param_1 + 0x278) == '\0') {
        uVar3 = 1;
      }
      else if (*(char *)(param_1 + 0x278) != '\x01') {
        uVar6 = 1;
        iVar1 = FUN_0044e498(*(undefined4 *)(param_1 + 500));
        iVar2 = FUN_0044e4bc(*(undefined4 *)(param_1 + 500));
        if (iVar2 + iVar1 <= param_3) {
          uVar5 = 1;
        }
      }
    }
    FUN_005e4dd8(param_3,uVar6,uVar5,uVar3,uVar4,param_4);
  }
  return;
}

