
int tfp_format(undefined4 param_1,uint *param_2,int *param_3)

{
  bool bVar1;
  bool bVar2;
  int iVar3;
  uint uVar4;
  bool bVar5;
  uint uVar6;
  int iVar7;
  uint *puVar8;
  undefined1 uVar9;
  undefined1 auStack_38 [12];
  int iStack_2c;
  undefined1 uStack_28;
  undefined1 uStack_27;
  bool bStack_26;
  undefined1 uStack_25;
  byte bStack_24;
  undefined1 *puStack_20;
  
  puStack_20 = auStack_38;
  iVar7 = 0;
LAB_10206a94:
  while( true ) {
    puVar8 = (uint *)((int)param_2 + 1);
    uVar4 = *param_2;
    if ((byte)uVar4 == 0) {
      return iVar7;
    }
    param_2 = puVar8;
    if ((byte)uVar4 == 0x25) break;
LAB_10206aa8:
    iVar3 = putf(param_1);
    iVar7 = iVar7 + iVar3;
  }
  uStack_28 = 0;
  bStack_26 = false;
  bVar1 = false;
  iStack_2c = 0;
  uStack_27 = 0;
  bVar5 = false;
  uVar9 = 0;
  bVar2 = false;
  while( true ) {
    uVar4 = (uint)(byte)*param_2;
    param_2 = (uint *)((int)param_2 + 1);
    if (uVar4 == 0) break;
    if (uVar4 == 0x23) {
      bVar1 = true;
      bVar2 = bVar1;
    }
    else {
      if (uVar4 != 0x30) break;
      bVar5 = true;
      uVar9 = 1;
    }
  }
  if (bVar5) {
    uStack_28 = uVar9;
  }
  if (bVar1) {
    bStack_26 = bVar2;
  }
  if ((uVar4 - 0x30 & 0xff) < 10) {
    iStack_2c = 0;
    do {
      uVar6 = uVar4 - 0x30;
      if (9 < (uVar6 & 0xff)) {
        if ((uVar4 - 0x61 & 0xff) < 6) {
          uVar6 = uVar4 - 0x57;
        }
        else {
          if (5 < (uVar4 - 0x41 & 0xff)) break;
          uVar6 = uVar4 - 0x37;
        }
        if (10 < (int)uVar6) break;
      }
      iStack_2c = uVar6 + iStack_2c * 10;
      uVar4 = *param_2;
      param_2 = (uint *)((int)param_2 + 1);
    } while( true );
  }
  if (uVar4 == 0x6c) {
    uVar4 = (uint)(byte)*param_2;
    param_2 = (uint *)((int)param_2 + 1);
  }
  if (uVar4 == 100) {
LAB_10206bde:
    iVar3 = *param_3;
    uStack_25 = 10;
    if (iVar3 < 0) {
      iVar3 = -iVar3;
      uStack_27 = 0x2d;
    }
LAB_10206bfa:
    ui2a(iVar3,&iStack_2c);
    iVar3 = putchw(param_1,&iStack_2c);
LAB_10206c08:
    param_3 = param_3 + 1;
    iVar7 = iVar7 + iVar3;
    goto LAB_10206a94;
  }
  if (uVar4 < 0x65) {
    if (uVar4 == 0x25) goto LAB_10206aa8;
    if (uVar4 < 0x26) {
      if (uVar4 == 0) {
        return iVar7;
      }
    }
    else {
      if (uVar4 == 0x58) {
LAB_10206bbc:
        uStack_25 = 0x10;
        bStack_24 = ~(uVar4 != 0x58);
        goto LAB_10206bcc;
      }
      if (uVar4 == 99) {
        iVar3 = putf(param_1,(char)*param_3);
        goto LAB_10206c08;
      }
    }
    goto LAB_10206a94;
  }
  if (uVar4 == 0x73) {
    puStack_20 = (undefined1 *)*param_3;
    iVar3 = putchw(param_1,&iStack_2c);
    puStack_20 = auStack_38;
    goto LAB_10206c08;
  }
  if (uVar4 < 0x74) {
    if (uVar4 == 0x69) goto LAB_10206bde;
    if (uVar4 != 0x6f) goto LAB_10206a94;
    uStack_25 = 8;
  }
  else {
    if (uVar4 != 0x75) {
      if (uVar4 == 0x78) goto LAB_10206bbc;
      goto LAB_10206a94;
    }
    uStack_25 = 10;
  }
LAB_10206bcc:
  iVar3 = *param_3;
  goto LAB_10206bfa;
}

