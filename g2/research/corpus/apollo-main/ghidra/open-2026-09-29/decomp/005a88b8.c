
undefined8 af_glyph_hints_align_weak_points(int param_1,char param_2,ushort *param_3)

{
  undefined4 *puVar1;
  ushort *puVar2;
  ushort *puVar3;
  ushort *puVar4;
  undefined4 *puVar5;
  ushort uVar6;
  ushort *puVar7;
  ushort *puVar8;
  ushort *puVar9;
  ushort *puVar10;
  ushort *local_2c;
  
  puVar4 = *(ushort **)(param_1 + 0x1c);
  puVar3 = puVar4 + *(int *)(param_1 + 0x18) * 0x14;
  puVar5 = *(undefined4 **)(param_1 + 0x28);
  puVar1 = puVar5 + *(int *)(param_1 + 0x24);
  local_2c = param_3;
  if (param_2 == '\0') {
    uVar6 = 4;
    for (puVar2 = puVar4; puVar2 < puVar3; puVar2 = puVar2 + 0x14) {
      *(undefined4 *)(puVar2 + 0xc) = *(undefined4 *)(puVar2 + 8);
      *(undefined4 *)(puVar2 + 0xe) = *(undefined4 *)(puVar2 + 2);
    }
  }
  else {
    uVar6 = 8;
    for (puVar2 = puVar4; puVar2 < puVar3; puVar2 = puVar2 + 0x14) {
      *(undefined4 *)(puVar2 + 0xc) = *(undefined4 *)(puVar2 + 10);
      *(undefined4 *)(puVar2 + 0xe) = *(undefined4 *)(puVar2 + 4);
    }
  }
  do {
    if (puVar1 <= puVar5) {
      if (param_2 == '\0') {
        for (; puVar4 < puVar3; puVar4 = puVar4 + 0x14) {
          *(undefined4 *)(puVar4 + 8) = *(undefined4 *)(puVar4 + 0xc);
        }
      }
      else {
        for (; puVar4 < puVar3; puVar4 = puVar4 + 0x14) {
          *(undefined4 *)(puVar4 + 10) = *(undefined4 *)(puVar4 + 0xc);
        }
      }
      return CONCAT44(local_2c,puVar3);
    }
    local_2c = (ushort *)*puVar5;
    puVar10 = *(ushort **)(local_2c + 0x12);
    for (puVar2 = local_2c; puVar2 <= puVar10; puVar2 = puVar2 + 0x14) {
      puVar7 = puVar2;
      if ((*puVar2 & uVar6) != 0) {
        do {
          for (; (puVar8 = puVar7, puVar7 < puVar10 && ((puVar7[0x14] & uVar6) != 0));
              puVar7 = puVar7 + 0x14) {
          }
          do {
            puVar9 = puVar8;
            puVar8 = puVar9 + 0x14;
            if (puVar10 < puVar8) {
              if (puVar7 == puVar2) {
                af_iup_shift(local_2c,puVar10,puVar2);
              }
              else {
                if (puVar7 < puVar10) {
                  af_iup_interp(puVar7 + 0x14,puVar10,puVar7,puVar2);
                }
                if (puVar4 < puVar2) {
                  af_iup_interp(local_2c,puVar2 + -0x14,puVar7,puVar2);
                }
              }
              goto LAB_005a8990;
            }
          } while ((*puVar8 & uVar6) == 0);
          af_iup_interp(puVar7 + 0x14,puVar9,puVar7,puVar8);
          puVar7 = puVar8;
        } while( true );
      }
    }
LAB_005a8990:
    puVar5 = puVar5 + 1;
  } while( true );
}

