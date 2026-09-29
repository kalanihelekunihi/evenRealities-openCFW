
undefined8 cff_parser_run(int param_1,byte *param_2,byte *param_3)

{
  char cVar1;
  undefined4 *puVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  uint *puVar7;
  int *piVar8;
  int iVar9;
  int iVar10;
  
  iVar6 = 0;
  *(undefined4 *)(param_1 + 0x14) = *(undefined4 *)(param_1 + 0x10);
  *(byte **)(param_1 + 4) = param_2;
  *(byte **)(param_1 + 8) = param_3;
  *(byte **)(param_1 + 0xc) = param_2;
  do {
    if (param_3 <= param_2) {
LAB_005ad744:
      return CONCAT44(param_3,iVar6);
    }
    uVar4 = (uint)*param_2;
    if (((uVar4 < 0x1b) || (uVar4 == 0x1f)) || (uVar4 == 0xff)) {
      if (*(uint *)(param_1 + 0x18) <=
          (uint)(*(int *)(param_1 + 0x14) - *(int *)(param_1 + 0x10) >> 2)) {
LAB_005ad6da:
        iVar6 = 6;
        goto LAB_005ad744;
      }
      uVar5 = *(int *)(param_1 + 0x14) - *(int *)(param_1 + 0x10) >> 2;
      **(undefined4 **)(param_1 + 0x14) = param_2;
      if (uVar4 == 0xc) {
        param_2 = param_2 + 1;
        if (param_3 <= param_2) {
          iVar6 = 6;
          goto LAB_005ad744;
        }
        uVar4 = *param_2 | 0x100;
      }
      puVar7 = DAT_005ae110;
LAB_005ad5fc:
      if (*puVar7 != 0) {
        if (puVar7[1] != (uVar4 | *(uint *)(param_1 + 0x1c))) break;
        piVar8 = (int *)(*(int *)(param_1 + 0x20) + puVar7[2]);
        if ((*puVar7 != 6) && (uVar5 == 0)) {
          iVar6 = 6;
          goto LAB_005ad744;
        }
        uVar4 = *puVar7;
        if (uVar4 == 1) {
LAB_005ad626:
          iVar9 = cff_parse_num(param_1,*(undefined4 *)(param_1 + 0x10));
          goto LAB_005ad644;
        }
        if (uVar4 == 0) {
LAB_005ad688:
          iVar6 = (*(code *)puVar7[4])(param_1);
          if (iVar6 != 0) goto LAB_005ad744;
        }
        else if (uVar4 == 3) {
          iVar9 = cff_parse_fixed_scaled(param_1,*(undefined4 *)(param_1 + 0x10),3);
LAB_005ad644:
          cVar1 = (char)puVar7[3];
          if (cVar1 == '\x01') {
            *(char *)piVar8 = (char)iVar9;
          }
          else if (cVar1 == '\x02') {
            *(short *)piVar8 = (short)iVar9;
          }
          else if (cVar1 == '\x04') {
            *piVar8 = iVar9;
          }
          else {
            *piVar8 = iVar9;
          }
        }
        else {
          if (uVar4 < 3) {
            iVar9 = cff_parse_fixed(param_1,*(undefined4 *)(param_1 + 0x10));
            goto LAB_005ad644;
          }
          if ((uVar4 == 5) || (uVar4 < 5)) goto LAB_005ad626;
          if (uVar4 != 6) goto LAB_005ad688;
          iVar9 = *(int *)(param_1 + 0x10);
          if (puVar7[5] < uVar5) {
            uVar5 = puVar7[5];
          }
          *(char *)(*(int *)(param_1 + 0x20) + puVar7[6]) = (char)uVar5;
          iVar10 = 0;
          for (; uVar5 != 0; uVar5 = uVar5 - 1) {
            iVar3 = cff_parse_num(param_1,iVar9);
            iVar9 = iVar9 + 4;
            iVar10 = iVar3 + iVar10;
            cVar1 = (char)puVar7[3];
            if (cVar1 == '\x01') {
              *(char *)piVar8 = (char)iVar10;
            }
            else if (cVar1 == '\x02') {
              *(short *)piVar8 = (short)iVar10;
            }
            else if (cVar1 == '\x04') {
              *piVar8 = iVar10;
            }
            else {
              *piVar8 = iVar10;
            }
            piVar8 = (int *)((int)piVar8 + (uint)(byte)puVar7[3]);
          }
        }
      }
      if (*puVar7 != 8) {
        *(undefined4 *)(param_1 + 0x14) = *(undefined4 *)(param_1 + 0x10);
      }
      goto LAB_005ad6a2;
    }
    if (*(uint *)(param_1 + 0x18) <=
        (uint)(*(int *)(param_1 + 0x14) - *(int *)(param_1 + 0x10) >> 2)) goto LAB_005ad6da;
    puVar2 = *(undefined4 **)(param_1 + 0x14);
    *(undefined4 **)(param_1 + 0x14) = puVar2 + 1;
    *puVar2 = param_2;
    if (uVar4 == 0x1e) {
      do {
        param_2 = param_2 + 1;
        if (param_3 <= param_2) goto LAB_005ad744;
      } while ((*param_2 >> 4 != 0xf) && ((*param_2 & 0xf) != 0xf));
    }
    else if (uVar4 == 0x1c) {
      param_2 = param_2 + 2;
    }
    else if (uVar4 == 0x1d) {
      param_2 = param_2 + 4;
    }
    else if (0xf6 < uVar4) {
      param_2 = param_2 + 1;
    }
LAB_005ad6a2:
    param_2 = param_2 + 1;
  } while( true );
  puVar7 = puVar7 + 7;
  goto LAB_005ad5fc;
}

