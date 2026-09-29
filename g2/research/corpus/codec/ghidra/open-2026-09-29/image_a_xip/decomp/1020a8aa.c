
/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Removing unreachable block (ram,0x1020a4fa) */
/* WARNING: Removing unreachable block (ram,0x1020a500) */

uint gx8002_messages_gain(int param_1,undefined4 param_2,uint param_3,uint param_4)

{
  bool bVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  int unaff_r7;
  uint unaff_r8;
  int unaff_r9;
  uint in_r12;
  uint in_r13;
  byte in_psr;
  int iStack00000008;
  int iStack0000000c;
  uint uStack00000010;
  
  if ((bool)(in_psr & 1)) {
    param_1 = 0x2a;
    param_3 = param_3 << 1;
  }
  if (param_1 + 0xe8 <= unaff_r9) {
    if (unaff_r8 < param_4 + param_1 + 0xe8 + 100) {
      stub();
      stub();
      stub();
      stub();
      stub();
      stub();
      stub();
      stub();
      stub();
      stub();
      stub();
      stub();
      stub();
      stub();
      stub();
      stub();
      stub();
      stub();
      stub();
      stub();
      stub();
                    /* WARNING: Bad instruction - Truncating control flow here */
      halt_baddata();
    }
    uStack00000010 = unaff_r7 + 4U >> (in_r13 & 0x3f);
    iStack0000000c = (int)PTR_LAB_1020acc0 << (in_r12 & 0x3f);
    iStack00000008 = 0x3c - in_r12;
    uVar2 = gx8002_pack_double();
    return uVar2;
  }
  if (param_3 != 0 || param_4 != 0) {
    iVar4 = *(int *)(param_1 + 0xf0);
    if (-0x3ff < iVar4) {
      if (iVar4 < 0x400) {
        if ((param_3 & 0xff) == 0x80) {
          if ((param_3 & 0x100) != 0) {
            bVar1 = 0xffffff7f < param_3;
            param_3 = param_3 + 0x80;
            param_4 = param_4 + bVar1;
          }
        }
        else {
          bVar1 = 0xffffff80 < param_3;
          param_3 = param_3 + 0x7f;
          param_4 = param_4 + bVar1;
        }
        if (0x1fffffff < param_4) {
          uVar2 = param_4 << 0x1f;
          param_4 = param_4 >> 1;
          param_3 = uVar2 | param_3 >> 1;
        }
        return param_3 >> 8 | param_4 << 0x18;
      }
      return 0;
    }
    uVar2 = -iVar4 - 0x3fe;
    if ((int)uVar2 < 0x39) {
      uVar3 = -iVar4 - 0x41e;
      bVar1 = (uVar3 & 0x80000000) == 0;
      uVar5 = param_3 >> (uVar2 & 0x3f) | (param_4 << 1) << (0x1f - uVar2 & 0x3f);
      if (bVar1) {
        uVar5 = param_4 >> (uVar3 & 0x3f);
      }
      iVar4 = 1 << (uVar2 & 0x3f);
      uVar6 = param_4 >> (uVar2 & 0x3f);
      uVar2 = 0;
      if (bVar1) {
        iVar4 = 0;
        uVar6 = 0;
        uVar2 = 1 << (uVar3 & 0x3f);
      }
      if (iVar4 == 0) {
        uVar2 = uVar2 - 1;
      }
      uVar2 = (uint)((param_3 & iVar4 - 1U) != 0 || (param_4 & uVar2) != 0);
      uVar3 = uVar5 | uVar2;
      if ((uVar5 & 0xff | uVar2) == 0x80) {
        if ((uVar5 & 0x100) == 0) {
          return uVar5 >> 8 | uVar6 << 0x18;
        }
        uVar2 = 0x80;
      }
      else {
        uVar2 = 0x7f;
      }
      return uVar3 + uVar2 >> 8 | (uVar6 + CARRY4(uVar3,uVar2)) * 0x1000000;
    }
  }
  return 0;
}

