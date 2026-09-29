
void FUN_004539b6(void)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  undefined1 local_40 [4];
  int local_3c;
  int local_34;
  undefined1 local_30 [4];
  int local_2c;
  int local_24;
  
  iVar1 = DAT_00454168;
  if (*(int *)(*(int *)(DAT_00454168 + 0x10) + 0x260) != 0) {
    iVar6 = *(int *)(*(int *)(DAT_00454168 + 0x10) + 0x260);
    do {
      iVar6 = iVar6 + -1;
      iVar7 = 0;
      if (iVar6 < 0) break;
      iVar7 = iVar6;
    } while (*(char *)(*(int *)(DAT_00454168 + 0x10) + iVar6 + 0x240) != '\0');
    FUN_0044fdbe(*(undefined4 *)(DAT_00454168 + 0x10),0x3b,0);
    *(uint *)(*(int *)(iVar1 + 0x10) + 0x38) = *(uint *)(*(int *)(iVar1 + 0x10) + 0x38) & 0xfffffffe
    ;
    *(uint *)(*(int *)(iVar1 + 0x10) + 0x38) = *(uint *)(*(int *)(iVar1 + 0x10) + 0x38) & 0xfffffffd
    ;
    *(uint *)(*(int *)(iVar1 + 0x10) + 0x38) = *(uint *)(*(int *)(iVar1 + 0x10) + 0x38) | 0x2000000;
    for (iVar6 = 0; iVar6 < *(int *)(*(int *)(iVar1 + 0x10) + 0x260); iVar6 = iVar6 + 1) {
      if (*(char *)(*(int *)(iVar1 + 0x10) + iVar6 + 0x240) == '\0') {
        if (iVar6 == iVar7) {
          *(uint *)(*(int *)(iVar1 + 0x10) + 0x38) = *(uint *)(*(int *)(iVar1 + 0x10) + 0x38) | 1;
        }
        *(uint *)(*(int *)(iVar1 + 0x10) + 0x38) =
             *(uint *)(*(int *)(iVar1 + 0x10) + 0x38) & 0xfffffffd;
        FUN_00439c04(local_30,*(int *)(iVar1 + 0x10) + iVar6 * 0x10 + 0x40,0x10);
        if (*(char *)(*(int *)(iVar1 + 0x10) + 0x39) == '\0') {
          uVar3 = FUN_00451598(local_30);
          uVar4 = FUN_004515a4(local_30);
          iVar5 = FUN_004544ae(*(undefined4 *)(iVar1 + 0x10),uVar3,uVar4);
          iVar10 = 0;
          iVar9 = 0;
          for (iVar8 = local_2c; iVar5 + iVar8 + -1 <= local_24; iVar8 = iVar5 + iVar8) {
            local_34 = iVar5 + iVar8 + -1;
            if (local_24 < local_34) {
              local_34 = local_24;
            }
            iVar10 = local_34;
            if (local_24 == local_34) {
              *(uint *)(*(int *)(iVar1 + 0x10) + 0x38) =
                   *(uint *)(*(int *)(iVar1 + 0x10) + 0x38) | 2;
            }
            local_3c = iVar8;
            FUN_00453bce(local_40,iVar9);
            iVar2 = FUN_004515a4(local_40);
            iVar9 = iVar2 + iVar9;
            FUN_00454574(*(undefined4 *)(iVar1 + 0x10));
          }
          if (local_24 != iVar10) {
            local_34 = local_24;
            *(uint *)(*(int *)(iVar1 + 0x10) + 0x38) = *(uint *)(*(int *)(iVar1 + 0x10) + 0x38) | 2;
            local_3c = iVar8;
            FUN_00453bce(local_40,iVar9);
            FUN_004515a4(local_40);
            FUN_00454574(*(undefined4 *)(iVar1 + 0x10));
          }
        }
        else if ((*(char *)(*(int *)(iVar1 + 0x10) + 0x39) == '\x02') ||
                (*(char *)(*(int *)(iVar1 + 0x10) + 0x39) == '\x01')) {
          *(uint *)(*(int *)(iVar1 + 0x10) + 0x38) = *(uint *)(*(int *)(iVar1 + 0x10) + 0x38) | 2;
          FUN_00453bce(*(int *)(iVar1 + 0x10) + iVar6 * 0x10 + 0x40,0);
          FUN_00454574(*(undefined4 *)(iVar1 + 0x10));
        }
      }
    }
    FUN_0044fdbe(*(undefined4 *)(iVar1 + 0x10),0x3c,0);
    *(uint *)(*(int *)(iVar1 + 0x10) + 0x38) = *(uint *)(*(int *)(iVar1 + 0x10) + 0x38) & 0xfdffffff
    ;
  }
  return;
}

