
void FUN_005c8b04(int *param_1)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  int local_40;
  int local_3c;
  int local_38;
  int local_34;
  undefined1 auStack_30 [8];
  int local_28;
  int local_24;
  
  iVar2 = FUN_00452ef8();
  if ((((iVar2 != 0) && (iVar3 = *param_1, (*(byte *)(iVar3 + 100) & 3) >> 1 != 0)) &&
      (iVar4 = FUN_00452f00(iVar2), iVar4 != 2)) && (iVar4 = FUN_00452f00(iVar2), iVar4 != 4)) {
    FUN_0043fc2a(*(undefined4 *)(iVar3 + 0x2c),&local_28);
    FUN_00452f5e(iVar2,&local_38);
    FUN_00452fca(iVar2,auStack_30);
    if ((-1 < local_38) && (-1 < local_34)) {
      local_40 = local_38 - local_28;
      local_3c = local_34 - local_24;
      iVar2 = FUN_00450286(param_1);
      iVar4 = FUN_0043fd9e(*(undefined4 *)(iVar3 + 0x2c));
      iVar5 = *(int *)(iVar3 + 0x2c);
      if (local_40 < 0) {
        uVar6 = 0;
        bVar1 = true;
      }
      else if (local_40 < iVar4) {
        uVar6 = FUN_00499a5c(*(undefined4 *)(iVar3 + 0x2c),&local_40,1);
        iVar4 = FUN_00499c9e(*(undefined4 *)(iVar3 + 0x2c),&local_40);
        if (iVar4 == 0) {
          bVar1 = true;
        }
        else {
          bVar1 = false;
        }
      }
      else {
        uVar6 = 0x7fff;
        bVar1 = true;
      }
      if ((*(byte *)(iVar3 + 0x70) & 3) >> 1 != 0) {
        if ((bVar1 || (*(byte *)(iVar3 + 0x70) & 1) != 0) || (iVar2 != 1)) {
          if (((int)((uint)*(byte *)(iVar3 + 0x70) << 0x1f) < 0) && (iVar2 == 2)) {
            *(undefined4 *)(iVar3 + 0x6c) = uVar6;
          }
          else if (((int)((uint)*(byte *)(iVar3 + 0x70) << 0x1f) < 0) &&
                  ((iVar2 == 3 || (iVar2 == 0xb)))) {
            FUN_0043ded4(iVar3,0x300);
          }
        }
        else {
          *(undefined4 *)(iVar3 + 0x68) = uVar6;
          *(undefined4 *)(iVar3 + 0x6c) = 0xffff;
          *(byte *)(iVar3 + 0x70) = *(byte *)(iVar3 + 0x70) | 1;
          FUN_0043dfa4(iVar3,0x300);
        }
      }
      if (((int)((uint)*(byte *)(iVar3 + 0x70) << 0x1f) < 0) || (iVar2 == 1)) {
        FUN_005c7ec4(iVar3,uVar6);
      }
      if ((int)((uint)*(byte *)(iVar3 + 0x70) << 0x1f) < 0) {
        if (*(uint *)(iVar3 + 0x6c) < *(uint *)(iVar3 + 0x68)) {
          if ((*(int *)(iVar5 + 0x44) != *(int *)(iVar3 + 0x6c)) ||
             (*(int *)(iVar5 + 0x48) != *(int *)(iVar3 + 0x68))) {
            *(undefined4 *)(iVar5 + 0x44) = *(undefined4 *)(iVar3 + 0x6c);
            *(undefined4 *)(iVar5 + 0x48) = *(undefined4 *)(iVar3 + 0x68);
            FUN_00440656(iVar3);
          }
        }
        else if (*(uint *)(iVar3 + 0x68) < *(uint *)(iVar3 + 0x6c)) {
          if ((*(int *)(iVar5 + 0x44) != *(int *)(iVar3 + 0x68)) ||
             (*(int *)(iVar5 + 0x48) != *(int *)(iVar3 + 0x6c))) {
            *(undefined4 *)(iVar5 + 0x44) = *(undefined4 *)(iVar3 + 0x68);
            *(undefined4 *)(iVar5 + 0x48) = *(undefined4 *)(iVar3 + 0x6c);
            FUN_00440656(iVar3);
          }
        }
        else if ((*(int *)(iVar5 + 0x44) != 0xffff) || (*(int *)(iVar5 + 0x48) != 0xffff)) {
          *(undefined4 *)(iVar5 + 0x44) = 0xffff;
          *(undefined4 *)(iVar5 + 0x48) = 0xffff;
          FUN_00440656(iVar3);
        }
        if ((iVar2 == 3) || (iVar2 == 0xb)) {
          *(byte *)(iVar3 + 0x70) = *(byte *)(iVar3 + 0x70) & 0xfe;
        }
      }
    }
  }
  return;
}

