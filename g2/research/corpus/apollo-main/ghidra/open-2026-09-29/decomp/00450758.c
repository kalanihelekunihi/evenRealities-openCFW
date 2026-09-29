
undefined4 FUN_00450758(void)

{
  int iVar1;
  undefined4 *puVar2;
  int iVar3;
  uint uVar4;
  undefined4 uVar5;
  bool bVar6;
  undefined4 in_r3;
  int iVar7;
  int iVar8;
  
  iVar1 = DAT_00450b30;
  *(bool *)(DAT_00450b30 + 0xa5) = *(char *)(DAT_00450b30 + 0xa5) == '\0';
  iVar7 = iVar1 + 0xac;
  puVar2 = (undefined4 *)FUN_00482cd8(iVar7);
  while (puVar2 != (undefined4 *)0x0) {
    iVar3 = FUN_004734a0(puVar2[0x14]);
    if ((int)((uint)*(byte *)(puVar2 + 0x17) << 0x1f) < 0) {
      uVar4 = FUN_004734a0(puVar2[0x15]);
      if ((puVar2[0x16] == -1) || (uVar4 < (uint)puVar2[0x16])) {
        bVar6 = false;
      }
      else {
        bVar6 = true;
      }
      if (bVar6) {
        *(byte *)(puVar2 + 0x17) = *(byte *)(puVar2 + 0x17) & 0xfe;
        puVar2[0xd] = (uVar4 - puVar2[0x16]) + puVar2[0xd];
        *(byte *)(puVar2 + 0x17) =
             *(byte *)(puVar2 + 0x17) & 0xfb | (*(char *)(iVar1 + 0xa5) == '\0') << 2;
      }
    }
    else {
      puVar2[0xd] = iVar3 + puVar2[0xd];
    }
    uVar5 = FUN_00473482();
    puVar2[0x14] = uVar5;
    *(undefined1 *)(iVar1 + 0xa4) = 0;
    if ((-1 < (int)((uint)*(byte *)(puVar2 + 0x17) << 0x1f)) &&
       ((*(byte *)(puVar2 + 0x17) & 7) >> 2 != (uint)*(byte *)(iVar1 + 0xa5))) {
      *(byte *)(puVar2 + 0x17) =
           *(byte *)(puVar2 + 0x17) & 0xfb | (*(byte *)(iVar1 + 0xa5) & 1) << 2;
      if (((*(byte *)(puVar2 + 0x17) & 0xf) >> 3 == 0) && (-1 < (int)puVar2[0xd])) {
        if (((*(byte *)(puVar2 + 0x17) & 0x1f) >> 4 == 0) && (puVar2[6] != 0)) {
          iVar3 = (*(code *)puVar2[6])(puVar2);
          puVar2[9] = iVar3 + puVar2[9];
          puVar2[0xb] = iVar3 + puVar2[0xb];
        }
        FUN_00450a3e(puVar2);
        if (puVar2[3] != 0) {
          (*(code *)puVar2[3])(puVar2);
        }
        *(byte *)(puVar2 + 0x17) = *(byte *)(puVar2 + 0x17) | 8;
        FUN_00450a74(puVar2);
      }
      if (-1 < (int)puVar2[0xd]) {
        uVar5 = puVar2[0xd];
        if ((int)puVar2[0xc] < (int)puVar2[0xd]) {
          puVar2[0xd] = puVar2[0xc];
        }
        iVar8 = puVar2[0xd];
        iVar3 = (*(code *)puVar2[8])(puVar2);
        if (iVar3 != puVar2[10]) {
          puVar2[10] = iVar3;
          if (puVar2[1] != 0) {
            (*(code *)puVar2[1])(*puVar2,iVar3);
          }
          if ((*(char *)(iVar1 + 0xa4) == '\0') && (puVar2[2] != 0)) {
            (*(code *)puVar2[2])(puVar2,iVar3);
          }
        }
        if (*(char *)(iVar1 + 0xa4) == '\0') {
          if (puVar2[0xd] == iVar8) {
            puVar2[0xd] = uVar5;
          }
          if ((int)puVar2[0xc] <= (int)puVar2[0xd]) {
            FUN_00450910(puVar2);
          }
        }
      }
    }
    if (*(char *)(iVar1 + 0xa4) == '\0') {
      puVar2 = (undefined4 *)FUN_00482cf0(iVar7,puVar2);
    }
    else {
      puVar2 = (undefined4 *)FUN_00482cd8(iVar7);
    }
  }
  return in_r3;
}

