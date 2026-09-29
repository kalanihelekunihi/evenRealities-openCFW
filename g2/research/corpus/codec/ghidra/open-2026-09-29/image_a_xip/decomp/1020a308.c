
/* WARNING: Removing unreachable block (ram,0x1020a3ea) */
/* WARNING: Removing unreachable block (ram,0x1020a3f2) */
/* WARNING: Removing unreachable block (ram,0x1020a3f8) */

void gx8002_divdf3_fixed(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4
                        )

{
  bool bVar1;
  uint *puVar2;
  int iVar3;
  undefined4 local_54;
  undefined4 uStack_50;
  undefined4 uStack_4c;
  undefined4 uStack_48;
  uint uStack_44;
  uint uStack_40;
  int iStack_3c;
  uint uStack_38;
  uint uStack_34;
  uint local_30;
  uint uStack_2c;
  int iStack_28;
  uint uStack_24;
  uint uStack_20;
  
  local_54 = param_1;
  uStack_50 = param_2;
  uStack_4c = param_3;
  uStack_48 = param_4;
  gx8002_unpack_double(&local_54,&uStack_44);
  gx8002_unpack_double(&uStack_4c,&local_30);
  if (1 < uStack_44) {
    if (local_30 < 2) {
      puVar2 = &local_30;
      goto LAB_1020a3cc;
    }
    uStack_40 = uStack_40 ^ uStack_2c;
    if ((uStack_44 == 4) || (uStack_44 == 2)) {
      puVar2 = (uint *)PTR_gx8002_fpadd_parts_nan_1020a41c;
      if (uStack_44 == local_30) goto LAB_1020a3cc;
    }
    else {
      if (local_30 == 4) {
        uStack_38 = 0;
        uStack_34 = 0;
        iStack_3c = 0;
        puVar2 = &uStack_44;
        goto LAB_1020a3cc;
      }
      if (local_30 == 2) {
        uStack_44 = 4;
        puVar2 = &uStack_44;
        goto LAB_1020a3cc;
      }
      iStack_3c = iStack_3c - iStack_28;
      if ((uStack_34 < uStack_20) || ((uStack_20 == uStack_34 && (uStack_38 < uStack_24)))) {
        iStack_3c = iStack_3c + -1;
        bVar1 = CARRY4(uStack_38,uStack_38);
        uStack_38 = uStack_38 * 2;
        uStack_34 = uStack_34 * 2 + (uint)bVar1;
      }
      iVar3 = 0x3d;
      do {
        if ((uStack_20 <= uStack_34) && ((uStack_20 != uStack_34 || (uStack_24 <= uStack_38)))) {
          bVar1 = uStack_24 <= uStack_38;
          uStack_38 = uStack_38 - uStack_24;
          uStack_34 = (uStack_34 - uStack_20) - (bVar1 ^ 1);
        }
        iVar3 = iVar3 + -1;
        bVar1 = CARRY4(uStack_38,uStack_38);
        uStack_38 = uStack_38 * 2;
        uStack_34 = uStack_34 * 2 + (uint)bVar1;
      } while (iVar3 != 0);
      uStack_38 = 0;
      uStack_34 = 0;
    }
  }
  puVar2 = &uStack_44;
LAB_1020a3cc:
  gx8002_pack_double(puVar2);
  return;
}

