
undefined8 FT_Stream_ReadFields(int param_1,byte *param_2,int param_3,undefined4 param_4)

{
  byte bVar1;
  bool bVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  uint *puVar6;
  ushort *puVar7;
  
  bVar2 = false;
  if (param_2 == (byte *)0x0) {
    iVar3 = 6;
  }
  else {
    if (param_1 != 0) {
      puVar7 = *(ushort **)(param_1 + 0x20);
      iVar3 = 0;
LAB_00528c54:
      for (; uVar4 = (uint)*param_2, uVar4 == 4; param_2 = param_2 + 4) {
        iVar3 = FT_Stream_EnterFrame(param_1,*(undefined2 *)(param_2 + 2));
        if (iVar3 != 0) goto LAB_00528ca6;
        bVar2 = true;
        puVar7 = *(ushort **)(param_1 + 0x20);
      }
      if (uVar4 - 8 < 2) {
        uVar4 = (uint)(byte)*puVar7;
        puVar7 = (ushort *)((int)puVar7 + 1);
        iVar5 = 0x18;
      }
      else if (uVar4 - 0xc < 2) {
        uVar4 = (uint)CONCAT11((byte)*puVar7,*(byte *)((int)puVar7 + 1));
        iVar5 = 0x10;
        puVar7 = puVar7 + 1;
      }
      else if (uVar4 - 0xe < 2) {
        uVar4 = (uint)*puVar7;
        iVar5 = 0x10;
        puVar7 = puVar7 + 1;
      }
      else if (uVar4 - 0x10 < 2) {
        uVar4 = (uint)*(byte *)((int)puVar7 + 3) |
                (uint)*(byte *)((int)puVar7 + 1) << 0x10 | (uint)(byte)*puVar7 << 0x18 |
                (uint)(byte)puVar7[1] << 8;
        iVar5 = 0;
        puVar7 = puVar7 + 2;
      }
      else if (uVar4 - 0x12 < 2) {
        uVar4 = (uint)(byte)*puVar7 |
                (uint)(byte)puVar7[1] << 0x10 | (uint)*(byte *)((int)puVar7 + 3) << 0x18 |
                (uint)*(byte *)((int)puVar7 + 1) << 8;
        iVar5 = 0;
        puVar7 = puVar7 + 2;
      }
      else if (uVar4 - 0x14 < 2) {
        uVar4 = (uint)(byte)puVar7[1] |
                (uint)*(byte *)((int)puVar7 + 1) << 8 | (uint)(byte)*puVar7 << 0x10;
        iVar5 = 8;
        puVar7 = (ushort *)((int)puVar7 + 3);
      }
      else {
        if (1 < uVar4 - 0x16) {
          if (uVar4 - 0x18 < 2) {
            uVar4 = (uint)param_2[1];
            if (*(byte **)(param_1 + 0x24) < (byte *)((int)puVar7 + uVar4)) {
              iVar3 = 0x55;
              goto LAB_00528ca6;
            }
            if (*param_2 == 0x18) {
              FUN_00439be4(param_3 + (uint)*(ushort *)(param_2 + 2),puVar7,uVar4);
            }
            puVar7 = (ushort *)((int)puVar7 + uVar4);
            param_2 = param_2 + 4;
            goto LAB_00528c54;
          }
          *(ushort **)(param_1 + 0x20) = puVar7;
LAB_00528ca6:
          if (bVar2) {
            FT_Stream_ExitFrame(param_1);
          }
          goto LAB_00528cb8;
        }
        uVar4 = (uint)(byte)*puVar7 |
                (uint)*(byte *)((int)puVar7 + 1) << 8 | (uint)(byte)puVar7[1] << 0x10;
        iVar5 = 8;
        puVar7 = (ushort *)((int)puVar7 + 3);
      }
      if ((int)((uint)*param_2 << 0x1f) < 0) {
        uVar4 = (int)(uVar4 << iVar5) >> iVar5;
      }
      puVar6 = (uint *)((uint)*(ushort *)(param_2 + 2) + param_3);
      bVar1 = param_2[1];
      if (bVar1 == 1) {
        *(char *)puVar6 = (char)uVar4;
      }
      else if (bVar1 == 2) {
        *(short *)puVar6 = (short)uVar4;
      }
      else if (bVar1 == 4) {
        *puVar6 = uVar4;
      }
      else {
        *puVar6 = uVar4;
      }
      param_2 = param_2 + 4;
      goto LAB_00528c54;
    }
    iVar3 = 0x28;
  }
LAB_00528cb8:
  return CONCAT44(param_4,iVar3);
}

