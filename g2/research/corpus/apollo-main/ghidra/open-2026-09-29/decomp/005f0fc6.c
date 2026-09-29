
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

uint TT_Load_Glyph(int param_1,int param_2,undefined4 param_3,int param_4)

{
  uint uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 uVar5;
  undefined2 uStack_fc;
  undefined2 uStack_fa;
  short sStack_f8;
  short sStack_f6;
  undefined1 auStack_f4 [12];
  int iStack_e8;
  undefined4 uStack_b8;
  int iStack_b0;
  int iStack_58;
  undefined4 uStack_44;
  int iStack_20;
  
  iStack_20 = param_4;
  if ((((*(int *)(param_1 + 0x74) != -1) && (-1 < param_4 << 0x1c)) &&
      ((*(uint *)(*(int *)(param_2 + 4) + 4) & _DAT_005f1ba4) == 0)) &&
     (-1 < *(int *)(*(int *)(param_2 + 4) + 8) << 0x10)) {
    uVar3 = *(undefined4 *)(param_1 + 0x10);
    uVar5 = *(undefined4 *)(param_1 + 0x14);
    uVar1 = load_sbit_image(param_1,param_2,param_3,param_4);
    if ((uVar1 & 0xff) == 0x9d) {
      if (-1 < (int)((uint)*(byte *)(*(int *)(param_2 + 4) + 8) << 0x1f)) {
        iVar4 = *(int *)(param_2 + 4);
        sStack_f6 = 0;
        sStack_f8 = 0;
        uStack_fa = 0;
        uStack_fc = 0;
        if (*(int *)(iVar4 + 0x2cc) == 0) {
          return uVar1;
        }
        TT_Get_HMetrics(iVar4,param_3,&sStack_f6,&uStack_fa);
        TT_Get_VMetrics(iVar4,param_3,0,&sStack_f8,&uStack_fc);
        *(undefined2 *)(param_2 + 0x6e) = 0;
        *(undefined2 *)(param_2 + 0x6c) = 0;
        *(undefined4 *)(param_2 + 0x18) = 0;
        *(undefined4 *)(param_2 + 0x1c) = 0;
        uVar2 = FT_MulFix((int)sStack_f6,uVar3);
        *(undefined4 *)(param_2 + 0x20) = uVar2;
        *(undefined4 *)(param_2 + 0x24) = 0;
        uVar3 = FT_MulFix(uStack_fa,uVar3);
        *(undefined4 *)(param_2 + 0x28) = uVar3;
        *(undefined4 *)(param_2 + 0x2c) = 0;
        uVar3 = FT_MulFix((int)sStack_f8,uVar5);
        *(undefined4 *)(param_2 + 0x30) = uVar3;
        uVar3 = FT_MulFix(uStack_fc,uVar5);
        *(undefined4 *)(param_2 + 0x34) = uVar3;
        *(undefined4 *)(param_2 + 0x48) = DAT_005f1560;
        *(undefined1 *)(param_2 + 0x5e) = 1;
        *(undefined4 *)(param_2 + 100) = 0;
        *(undefined4 *)(param_2 + 0x68) = 0;
        return 0;
      }
    }
    else {
      if (uVar1 == 0) {
        if ((int)((uint)*(byte *)(*(int *)(param_2 + 4) + 8) << 0x1f) < 0) {
          tt_loader_init(auStack_f4,param_1,param_2,param_4,1);
          load_truetype_glyph(auStack_f4,param_3,0,1);
          tt_loader_done(auStack_f4);
          *(undefined4 *)(param_2 + 0x38) = uStack_b8;
          *(undefined4 *)(param_2 + 0x3c) = uStack_44;
          if ((*(int *)(param_2 + 0x28) == 0) && (*(int *)(param_2 + 0x38) != 0)) {
            uVar3 = FT_MulFix(*(undefined4 *)(param_2 + 0x38),uVar3);
            *(undefined4 *)(param_2 + 0x28) = uVar3;
          }
          if ((*(int *)(param_2 + 0x34) == 0) && (*(int *)(param_2 + 0x3c) != 0)) {
            uVar3 = FT_MulFix(*(undefined4 *)(param_2 + 0x3c),uVar5);
            *(undefined4 *)(param_2 + 0x34) = uVar3;
          }
        }
        return 0;
      }
      if (-1 < (int)((uint)*(byte *)(*(int *)(param_2 + 4) + 8) << 0x1f)) {
        return uVar1;
      }
    }
  }
  if ((param_4 << 0x1f < 0) || (*(char *)(param_1 + 0x70) != '\0')) {
    if (param_4 << 0x11 < 0) {
      uVar1 = 6;
    }
    else {
      uVar1 = tt_loader_init(auStack_f4,param_1,param_2,param_4,0);
      if (uVar1 == 0) {
        *(undefined4 *)(param_2 + 0x48) = _DAT_005f1ba8;
        *(undefined4 *)(param_2 + 0x80) = 0;
        *(undefined4 *)(param_2 + 0x7c) = 0;
        uVar1 = load_truetype_glyph(auStack_f4,param_3,0,0);
        if (uVar1 == 0) {
          if (*(int *)(param_2 + 0x48) == DAT_005f1558) {
            *(undefined4 *)(param_2 + 0x80) = *(undefined4 *)(iStack_e8 + 0x30);
            *(undefined4 *)(param_2 + 0x84) = *(undefined4 *)(iStack_e8 + 0x34);
          }
          else {
            FUN_00439c04(param_2 + 0x6c,iStack_e8 + 0x14,0x14);
            *(uint *)(param_2 + 0x7c) = *(uint *)(param_2 + 0x7c) & 0xfffffdff;
            if (iStack_b0 != 0) {
              FT_Outline_Translate(param_2 + 0x6c,-iStack_b0,0);
            }
          }
          if (-1 < param_4 << 0x1e) {
            if (*(char *)(iStack_58 + 0x155) == '\0') {
              *(uint *)(param_2 + 0x7c) = *(uint *)(param_2 + 0x7c) | 8;
            }
            else {
              iVar4 = *(int *)(iStack_58 + 0x158);
              if (iVar4 == 0) {
                *(uint *)(param_2 + 0x7c) = *(uint *)(param_2 + 0x7c) | 0x20;
              }
              else if (iVar4 != 1) {
                if (iVar4 == 4) {
                  *(uint *)(param_2 + 0x7c) = *(uint *)(param_2 + 0x7c) | 0x30;
                }
                else if (iVar4 == 5) {
                  *(uint *)(param_2 + 0x7c) = *(uint *)(param_2 + 0x7c) | 0x10;
                }
                else {
                  *(uint *)(param_2 + 0x7c) = *(uint *)(param_2 + 0x7c) | 8;
                }
              }
            }
          }
          uVar1 = compute_glyph_metrics(auStack_f4,param_3);
        }
        tt_loader_done(auStack_f4);
        if ((-1 < param_4 << 0x1f) && (*(ushort *)(*(int *)(param_1 + 0x2c) + 2) < 0x18)) {
          *(uint *)(param_2 + 0x7c) = *(uint *)(param_2 + 0x7c) | 0x100;
        }
      }
    }
  }
  else {
    uVar1 = 0x24;
  }
  return uVar1;
}

