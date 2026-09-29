
undefined8 FUN_0048f4b8(int param_1,uint *param_2,undefined1 *param_3,uint param_4)

{
  bool bVar1;
  int iVar2;
  undefined4 uVar3;
  byte bVar4;
  uint uVar5;
  uint uVar6;
  uint local_18;
  
  local_18 = param_4;
  iVar2 = FUN_0048f454(param_1,&local_18);
  if (iVar2 == 0) {
    if ((*(int *)(param_1 + 8) == 0) && (param_3 != (undefined1 *)0x0)) {
      *param_3 = 1;
    }
    uVar3 = 0;
  }
  else {
    if ((int)(local_18 << 0x18) < 0) {
      uVar5 = 7;
      uVar6 = local_18 & 0x7f;
      do {
        iVar2 = FUN_0048f454(param_1,&local_18);
        if (iVar2 == 0) {
          uVar3 = 0;
          goto LAB_0048f5ac;
        }
        if (uVar5 < 0x20) {
          if (uVar5 == 0x1c) {
            if (((local_18 & 0x70) != 0) && ((local_18 & 0x78) != 0x78)) {
              uVar3 = DAT_0048fc84;
              if (*(int *)(param_1 + 0xc) != 0) {
                uVar3 = *(undefined4 *)(param_1 + 0xc);
              }
              *(undefined4 *)(param_1 + 0xc) = uVar3;
              uVar3 = 0;
              goto LAB_0048f5ac;
            }
            uVar6 = uVar6 | local_18 << 0x1c;
          }
          else {
            uVar6 = uVar6 | (local_18 & 0x7f) << (uVar5 & 0xff);
          }
        }
        else {
          if (uVar5 < 0x3f) {
            bVar4 = 0xff;
          }
          else {
            bVar4 = 1;
          }
          if (((local_18 & 0x7f) == 0) || (((int)uVar6 < 0 && ((local_18 & 0xff) == (uint)bVar4))))
          {
            bVar1 = true;
          }
          else {
            bVar1 = false;
          }
          if ((0x3f < uVar5) || (!bVar1)) {
            uVar3 = DAT_0048fc84;
            if (*(int *)(param_1 + 0xc) != 0) {
              uVar3 = *(undefined4 *)(param_1 + 0xc);
            }
            *(undefined4 *)(param_1 + 0xc) = uVar3;
            uVar3 = 0;
            goto LAB_0048f5ac;
          }
        }
        uVar5 = uVar5 + 7;
      } while ((int)(local_18 << 0x18) < 0);
    }
    else {
      uVar6 = local_18 & 0xff;
    }
    *param_2 = uVar6;
    uVar3 = 1;
  }
LAB_0048f5ac:
  return CONCAT44(local_18,uVar3);
}

