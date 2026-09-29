
undefined8
am_hal_mspi_device_configure(uint *param_1,byte *param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  uint *puVar3;
  uint uVar4;
  uint uVar5;
  undefined1 uVar6;
  uint uVar7;
  char cVar8;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_004251b0)) {
    iVar2 = 2;
    goto LAB_0042502c;
  }
  if ((char)param_1[2] == '\0') {
    iVar2 = 7;
    goto LAB_0042502c;
  }
  uVar7 = param_1[1];
  if ((uVar7 == 1) || (uVar7 == 2)) {
    if (param_2[0xb] - 0x15 < 3) {
      iVar2 = 5;
      goto LAB_0042502c;
    }
    if (param_2[8] - 10 < 2) {
      iVar2 = 5;
      goto LAB_0042502c;
    }
  }
  mspi_clkgen_ctrl(uVar7,0,0,0);
  if (param_2[0x11] == 0) {
    bVar1 = param_2[0xb];
    if (((((((bVar1 == 3) || (bVar1 == 5)) || (bVar1 == 7)) || ((bVar1 == 9 || (bVar1 == 0xb)))) ||
         ((bVar1 == 0xd || ((bVar1 == 0xf || (bVar1 == 0x11)))))) || (bVar1 == 0x13)) ||
       ((bVar1 == 0x15 || (bVar1 == 0x17)))) {
      cVar8 = '\x05';
    }
    else {
      cVar8 = '\x04';
    }
    if ((*(char *)((int)param_1 + 0x8c9) != cVar8) &&
       ((iVar2 = clock_release(*(undefined1 *)((int)param_1 + 0x8c9),param_1[1] + 0x10 & 0xff),
        iVar2 != 0 || (iVar2 = clock_request(cVar8,param_1[1] + 0x10 & 0xff), iVar2 != 0))))
    goto LAB_0042502c;
    *(char *)((int)param_1 + 0x8c9) = cVar8;
    bVar1 = param_2[0xb];
    if (bVar1 == 1) {
      uVar6 = 7;
    }
    else {
      if (bVar1 == 0) {
LAB_00424dba:
        iVar2 = 5;
        goto LAB_0042502c;
      }
      if (bVar1 == 3) {
LAB_00424d84:
        uVar6 = 10;
      }
      else {
        if (2 < bVar1) {
          if (bVar1 == 5) goto LAB_00424d84;
          if (4 < bVar1) {
            if (bVar1 == 7) goto LAB_00424d84;
            if (6 < bVar1) {
              if (bVar1 == 9) goto LAB_00424d84;
              if (8 < bVar1) {
                if (bVar1 == 0xb) goto LAB_00424d84;
                if (10 < bVar1) {
                  if (bVar1 == 0xd) goto LAB_00424d84;
                  if (0xc < bVar1) {
                    if (bVar1 == 0xf) goto LAB_00424d84;
                    if (0xe < bVar1) {
                      if (bVar1 == 0x11) goto LAB_00424d84;
                      if (0x10 < bVar1) {
                        if (bVar1 == 0x13) goto LAB_00424d84;
                        if (0x12 < bVar1) {
                          if (bVar1 == 0x15) goto LAB_00424d84;
                          if (0x14 < bVar1) {
                            if (bVar1 == 0x17) goto LAB_00424d84;
                            if (0x16 < bVar1) goto LAB_00424dba;
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
        uVar6 = 8;
      }
    }
    mspi_clkgen_ctrl(uVar7,1,1,uVar6);
    if ((param_2[0xb] == 0x17) || (param_2[0xb] == 0x16)) {
      puVar3 = (uint *)(DAT_004251a4 + uVar7 * 0x1000 + 0x8c);
      *puVar3 = *puVar3 | 0x40000000;
    }
    else {
      puVar3 = (uint *)(DAT_004251a4 + uVar7 * 0x1000 + 0x8c);
      *puVar3 = *puVar3 & 0xbfffffff;
    }
  }
  else {
    if ((param_2[0xb] == 0x15) || (param_2[0xb] == 0x17)) {
      cVar8 = '\x05';
    }
    else {
      cVar8 = '\x04';
    }
    if ((*(char *)((int)param_1 + 0x8c9) != cVar8) &&
       ((iVar2 = clock_release(*(undefined1 *)((int)param_1 + 0x8c9),param_1[1] + 0x10 & 0xff),
        iVar2 != 0 || (iVar2 = clock_request(cVar8,param_1[1] + 0x10 & 0xff), iVar2 != 0))))
    goto LAB_0042502c;
    *(char *)((int)param_1 + 0x8c9) = cVar8;
    bVar1 = param_2[0xb];
    if (bVar1 == 0x14) {
      uVar6 = 7;
    }
    else {
      if (bVar1 < 0x14) {
LAB_00424cc8:
        iVar2 = 5;
        goto LAB_0042502c;
      }
      if (bVar1 == 0x16) {
        uVar6 = 8;
      }
      else if (bVar1 < 0x16) {
        uVar6 = 9;
      }
      else {
        if (bVar1 != 0x17) goto LAB_00424cc8;
        uVar6 = 10;
      }
    }
    mspi_clkgen_ctrl(uVar7,1,1,uVar6);
    puVar3 = (uint *)(DAT_004251a4 + uVar7 * 0x1000 + 0x8c);
    *puVar3 = *puVar3 & 0xbfffffff;
  }
  iVar2 = DAT_004251a4;
  uVar5 = (param_2[1] & 3) << 5 | (param_2[2] & 1) << 7 | (*param_2 & 0x3f) << 8;
  bVar1 = param_2[10];
  if (bVar1 != 0) {
    if (bVar1 == 2) {
      uVar5 = uVar5 | 0x4000;
    }
    else if (bVar1 < 2) {
      uVar5 = uVar5 | 0x8000;
    }
    else if (bVar1 == 3) {
      uVar5 = uVar5 | 0xc000;
    }
  }
  if (param_2[0x11] == 0) {
    uVar4 = (uint)param_2[0xb];
    if (uVar4 - 1 < 3) {
      uVar5 = uVar5 | 0x200000;
    }
    else if (uVar4 - 4 < 2) {
      uVar5 = uVar5 | 0x180000;
    }
    else if (uVar4 - 6 < 2) {
      uVar5 = uVar5 | 0x100000;
    }
    else if (uVar4 - 8 < 2) {
      uVar5 = uVar5 | 0xc0000;
    }
    else if (uVar4 - 10 < 2) {
      uVar5 = uVar5 | 0x80000;
    }
    else if (uVar4 - 0xc < 2) {
      uVar5 = uVar5 | 0x60000;
    }
    else if (uVar4 - 0xe < 2) {
      uVar5 = uVar5 | 0x40000;
    }
    else if (uVar4 - 0x10 < 2) {
      uVar5 = uVar5 | 0x30000;
    }
    else if (uVar4 - 0x12 < 2) {
      uVar5 = uVar5 | 0x20000;
    }
    else {
      if (3 < uVar4 - 0x14) {
        iVar2 = 5;
        goto LAB_0042502c;
      }
      uVar5 = uVar5 | 0x10000;
    }
    if (0x12 < param_2[0xb] - 1) {
      if (3 < param_2[0xb] - 0x14) {
        iVar2 = 5;
        goto LAB_0042502c;
      }
      uVar5 = uVar5 | 0x1000000;
    }
  }
  *(uint *)(DAT_004251a4 + uVar7 * 0x1000 + 0x84) = uVar5 | (uint)param_2[9] << 0x1a;
  if (param_2[0x11] == 0) {
    puVar3 = (uint *)(iVar2 + uVar7 * 0x1000 + 0x88);
    *puVar3 = *puVar3 & 0xfffffffe | (uint)(param_2[0x10] != 0);
  }
  else {
    puVar3 = (uint *)(iVar2 + uVar7 * 0x1000 + 0x88);
    *puVar3 = *puVar3 | 1;
    puVar3 = (uint *)(iVar2 + uVar7 * 0x1000 + 0x8c);
    *puVar3 = *puVar3 | 0x80000000;
  }
  puVar3 = (uint *)(iVar2 + uVar7 * 0x1000 + 0x8c);
  *puVar3 = *puVar3 & 0xfff9ffff | (param_2[0x12] & 3) << 0x11;
  puVar3 = (uint *)(iVar2 + uVar7 * 0x1000 + 0x30);
  *puVar3 = *puVar3 & 0xfffffffe;
  uVar5 = DAT_004251b8 & *(uint *)(iVar2 + uVar7 * 0x1000 + 0x90) | 0xc |
          (uint)*(byte *)((int)param_1 + 0xd) << 4;
  if (param_2[0xf] != 0) {
    uVar5 = (*param_2 & 0x3f) << 0xe | uVar5 | 0x20;
  }
  if (param_2[0xd] != 0) {
    uVar5 = uVar5 | 0x40;
  }
  if (param_2[0xe] != 0) {
    uVar5 = uVar5 | 0x80;
  }
  *(uint *)(iVar2 + uVar7 * 0x1000 + 0x90) =
       uVar5 | (uint)param_2[0xc] << 0xd | (param_2[9] & 0x3f) << 0x14;
  *(uint *)(iVar2 + uVar7 * 0x1000 + 0x94) =
       CONCAT22(*(undefined2 *)(param_2 + 4),*(undefined2 *)(param_2 + 6));
  *(uint *)(iVar2 + uVar7 * 0x1000 + 0x98) =
       *(ushort *)(param_2 + 0x14) & 0xfff | (param_2[0x16] & 0xf) << 0xc;
  puVar3 = (uint *)(iVar2 + uVar7 * 0x1000 + 0x30);
  *puVar3 = *puVar3 & 0xffffff0f | 0x70;
  *(undefined1 *)((int)param_1 + 0xd) = 0;
  if (param_1[6] != 0) {
    *(undefined4 *)(iVar2 + uVar7 * 0x1000 + 0x114) = 0x20;
    if (param_2[0xb] - 1 < 0x11) {
      puVar3 = (uint *)(iVar2 + uVar7 * 0x1000 + 0x118);
      *puVar3 = *puVar3 & 0xffffffe0 | 8;
      puVar3 = (uint *)(iVar2 + uVar7 * 0x1000 + 0x20);
      *puVar3 = *puVar3 & 0xffffc0ff | 0x1e00;
      puVar3 = (uint *)(iVar2 + uVar7 * 0x1000 + 0x118);
      *puVar3 = *puVar3 & 0xffffe0ff | 0x800;
    }
    else {
      if (5 < param_2[0xb] - 0x12) {
        iVar2 = 5;
        goto LAB_0042502c;
      }
      puVar3 = (uint *)(iVar2 + uVar7 * 0x1000 + 0x118);
      *puVar3 = *puVar3 & 0xffffffe0 | 0xc;
      puVar3 = (uint *)(iVar2 + uVar7 * 0x1000 + 0x20);
      *puVar3 = *puVar3 & 0xffffc0ff | 0x1e00;
      puVar3 = (uint *)(iVar2 + uVar7 * 0x1000 + 0x118);
      *puVar3 = *puVar3 & 0xffffe0ff | 0x800;
    }
  }
  *(byte *)((int)param_1 + 10) = param_2[8];
  mspi_device_configure(param_1);
  *(undefined1 *)((int)param_1 + 0xd) = 0;
  *(byte *)(param_1 + 3) = param_2[0xb];
  param_1[4] = 10000;
  mspi_get_xip_off_min_delay(param_1);
  iVar2 = 0;
LAB_0042502c:
  return CONCAT44(param_4,iVar2);
}

