
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00554fae(int param_1,int param_2)

{
  undefined1 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  bool bVar5;
  bool bVar6;
  
  iVar3 = DAT_00555754;
  if ((*(char *)(_DAT_005555a0 + 0x2c) == '\x02') || (*(int *)(DAT_00555754 + 0x40) != 0)) {
    bVar6 = true;
  }
  else {
    bVar6 = false;
  }
  bVar5 = *(char *)(_DAT_005555a0 + 0x2c) == '\x01';
  if (param_1 == 10) {
    if ((*(char *)(DAT_00555754 + 0x21) != '\x01') && (*(int *)(DAT_00555754 + 0x18) != 0)) {
      if (*(int *)(DAT_00555754 + 0x40) == 0) {
        FUN_00589b68(7,1);
        func_0x00554102(2);
      }
      else {
        FUN_00589b68(8,0);
        func_0x00554102(3);
      }
    }
  }
  else if (param_1 == 0x44) {
    if (!bVar6) {
      if (bVar5) {
        *(undefined1 *)(DAT_00555754 + 0x45) = 1;
      }
      else if ((*(int *)(DAT_00555754 + 0x18) != 0) && (*(char *)(DAT_00555754 + 0x21) == '\0')) {
        iVar4 = FUN_005548c4(*(undefined4 *)(DAT_00555754 + 0x18),
                             -(*(undefined4 **)(param_2 + 0x10))[1],
                             **(undefined4 **)(param_2 + 0x10));
        iVar3 = FUN_0044e498(*(undefined4 *)(iVar3 + 0x18));
        if (iVar4 == iVar3) {
          FUN_00555200(1);
        }
        else {
          FUN_00589b68(0xc,iVar4);
        }
      }
    }
  }
  else if (param_1 == 0x45) {
    if (!bVar6) {
      if (bVar5) {
        *(undefined1 *)(DAT_00555754 + 0x45) = 2;
      }
      else if ((*(int *)(DAT_00555754 + 0x18) != 0) && (*(char *)(DAT_00555754 + 0x21) == '\0')) {
        iVar4 = FUN_005548c4(*(undefined4 *)(DAT_00555754 + 0x18),
                             (*(undefined4 **)(param_2 + 0x10))[1],**(undefined4 **)(param_2 + 0x10)
                            );
        iVar3 = FUN_0044e498(*(undefined4 *)(iVar3 + 0x18));
        if (iVar4 == iVar3) {
          FUN_00555200(1);
        }
        else {
          FUN_00589b68(0xd,iVar4);
        }
      }
    }
  }
  else if (param_1 == 0x48) {
    system_close_page_factory_0046ae9c(1,6);
  }
  else if (param_1 == 0x4a) {
    if ((((bool)(bVar5 & (bVar6 ^ 1U))) && (*(int *)(DAT_00555754 + 0x18) != 0)) &&
       (*(char *)(DAT_00555754 + 0x21) != '\x01')) {
      if (*(char *)(DAT_00555754 + 0x45) != '\0') {
        bVar6 = *(char *)(DAT_00555754 + 0x45) != '\x01';
        iVar2 = func_0x005540f0();
        iVar4 = iVar2 * 0x1c;
        *(undefined1 *)(iVar3 + 0x45) = 0;
        if (!bVar6) {
          iVar4 = iVar2 * -0x1c;
        }
        iVar4 = FUN_005548c4(*(undefined4 *)(iVar3 + 0x18),iVar4,0);
        iVar3 = FUN_0044e498(*(undefined4 *)(iVar3 + 0x18));
        if (iVar4 == iVar3) {
          FUN_00555200(1);
        }
        else {
          if (bVar6) {
            uVar1 = 0xd;
          }
          else {
            uVar1 = 0xc;
          }
          FUN_00589b68(uVar1,iVar4);
        }
      }
    }
    else {
      *(undefined1 *)(DAT_00555754 + 0x45) = 0;
    }
  }
  return;
}

