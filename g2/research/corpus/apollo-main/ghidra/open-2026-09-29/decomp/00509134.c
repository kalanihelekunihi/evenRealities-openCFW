
void FUN_00509134(void)

{
  undefined1 *puVar1;
  int iVar2;
  undefined4 extraout_r1;
  undefined4 in_r3;
  byte bVar3;
  uint in_fpscr;
  uint uVar4;
  uint uVar5;
  float fVar6;
  undefined4 local_48;
  undefined1 local_44;
  undefined1 local_43;
  undefined1 local_42;
  undefined1 local_41;
  undefined1 local_40;
  undefined1 local_3f;
  undefined1 local_3e;
  undefined4 local_3c;
  int local_38;
  int local_34;
  undefined1 local_30 [4];
  undefined4 local_2c;
  undefined1 local_28;
  undefined1 local_27;
  undefined1 local_26;
  undefined1 local_25;
  undefined4 local_24;
  undefined4 uStack_20;
  float local_1c;
  float local_18;
  float local_14;
  undefined4 local_10;
  undefined4 uStack_c;
  
  local_3c = 1;
  uStack_c = in_r3;
  FUN_00480f0c(0x10,*DAT_00509470);
  iVar2 = FUN_0055d94c(0,&local_48);
  if (iVar2 != 0) {
    FUN_004733ee(DAT_00509474);
  }
  local_14 = DAT_005093d0;
  local_18 = DAT_005093d0;
  local_1c = DAT_005093d0;
  local_10 = DAT_00509478;
  FUN_0055dc88(local_48,3,&local_1c);
  FUN_004733ee(DAT_0050947c,extraout_r1,SUB84((double)local_1c,0),
               (int)((ulonglong)(double)local_1c >> 0x20),(double)local_18);
  iVar2 = FUN_0055e09c(local_48,0,0);
  if (iVar2 != 0) {
    FUN_004733ee(DAT_00509480);
  }
  local_24 = *DAT_00509484;
  uStack_20 = DAT_00509484[1];
  FUN_0055dbf0(local_48,&local_24);
  local_44 = 2;
  local_42 = 0;
  local_41 = 7;
  local_40 = 1;
  local_3f = 0;
  local_3e = 1;
  local_43 = 1;
  iVar2 = FUN_0055dae4(local_48,&local_44);
  if (iVar2 != 0) {
    FUN_004733ee(DAT_00509488);
  }
  local_30[0] = 7;
  local_2c = 0x20;
  local_28 = 0;
  local_27 = 3;
  local_26 = 0;
  local_25 = 1;
  iVar2 = FUN_0055db72(local_48,3,local_30);
  if (iVar2 != 0) {
    FUN_004733ee(DAT_0050948c);
  }
  iVar2 = FUN_0055dddc(local_48);
  if (iVar2 != 0) {
    FUN_004733ee(DAT_00509490);
  }
  FUN_0055dc26(local_48);
  FUN_0055e070(local_48);
  bVar3 = 0;
  do {
    do {
      if (2 < bVar3) {
        FUN_0055e09c(local_48,2,0);
        FUN_0055daae(local_48);
        FUN_00480f0c(0x10,*DAT_005094a0);
        return;
      }
      do {
      } while ((*DAT_0050949c & 0xfffffff) >> 0x14 == 0);
      local_3c = 1;
      FUN_0055deec(local_48,0,0,&local_3c,&local_38);
      if (local_34 == 3) {
        bVar3 = bVar3 + 1;
      }
    } while (bVar3 < 3);
    FUN_0055dc5e(local_48);
    FUN_0055de1c(local_48);
    puVar1 = DAT_00509494;
    fVar6 = (float)VectorUnsignedToFloat
                             ((uint)(local_38 * 0x4a6) >> 0xc,(byte)(in_fpscr >> 0x16) & 3);
    in_fpscr = in_fpscr & 0xfffffff;
    uVar5 = in_fpscr | (uint)(fVar6 < DAT_00509448) << 0x1f;
    uVar4 = uVar5 | (uint)(NAN(fVar6) || NAN(DAT_00509448)) << 0x1c;
    if ((byte)(uVar5 >> 0x1f) == ((byte)(uVar4 >> 0x1c) & 1)) {
      uVar4 = in_fpscr;
      if (DAT_0050944c <= fVar6) goto LAB_005092f4;
      *DAT_00509494 = 1;
      puVar1[1] = 6;
    }
    else {
LAB_005092f4:
      in_fpscr = uVar4 & 0xfffffff;
      uVar5 = in_fpscr | (uint)(fVar6 < DAT_00509450) << 0x1f;
      uVar4 = uVar5 | (uint)(NAN(fVar6) || NAN(DAT_00509450)) << 0x1c;
      if ((byte)(uVar5 >> 0x1f) == ((byte)(uVar4 >> 0x1c) & 1)) {
        uVar4 = in_fpscr;
        if (fVar6 < DAT_00509454) {
          *DAT_00509494 = 1;
          puVar1[1] = 3;
          goto LAB_0050925a;
        }
      }
      in_fpscr = uVar4 & 0xfffffff;
      uVar4 = in_fpscr | (uint)(fVar6 < DAT_00509458) << 0x1f;
      uVar5 = uVar4 | (uint)(NAN(fVar6) || NAN(DAT_00509458)) << 0x1c;
      if ((byte)(uVar4 >> 0x1f) == ((byte)(uVar5 >> 0x1c) & 1)) {
        uVar5 = in_fpscr;
        if (fVar6 < DAT_0050945c) {
          *DAT_00509494 = 1;
          puVar1[1] = 4;
          goto LAB_0050925a;
        }
      }
      uVar5 = uVar5 & 0xfffffff;
      uVar4 = uVar5 | (uint)(fVar6 < DAT_00509460) << 0x1f;
      in_fpscr = uVar4 | (uint)(NAN(fVar6) || NAN(DAT_00509460)) << 0x1c;
      if ((byte)(uVar4 >> 0x1f) == ((byte)(in_fpscr >> 0x1c) & 1)) {
        in_fpscr = uVar5;
        if (fVar6 < DAT_00509464) {
          *DAT_00509494 = 1;
          puVar1[1] = 5;
          goto LAB_0050925a;
        }
      }
      *DAT_00509494 = 1;
      puVar1[1] = 0xff;
    }
LAB_0050925a:
    *(short *)(DAT_00509494 + 2) = (short)(int)fVar6;
    FUN_004733ee(DAT_00509498,local_38,SUB84((double)fVar6,0),
                 (int)((ulonglong)(double)fVar6 >> 0x20));
  } while( true );
}

