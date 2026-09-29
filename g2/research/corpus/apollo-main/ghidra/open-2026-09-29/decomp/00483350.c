
/* WARNING: Removing unreachable block (ram,0x0048336e) */

void FUN_00483350(void)

{
  bool bVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  uint in_fpscr;
  uint uVar6;
  double in_d0;
  double dVar7;
  double dVar8;
  uint in_stack_00000000;
  uint in_stack_00000004;
  uint in_stack_00000008;
  char local_40 [32];
  
  uVar5 = 0;
  uVar6 = in_fpscr & 0xfffffff;
  if (DAT_00483618 <= in_d0) {
    if (in_d0 == DAT_00483620) {
      FUN_0048306c();
    }
    else if ((!NAN(in_d0) && !NAN(DAT_0048362c)) || (in_d0 < DAT_00483634)) {
      FUN_0048364c();
    }
    else {
      bVar1 = in_d0 < DAT_0048363c;
      if (bVar1) {
        in_d0 = -in_d0;
      }
      if (-1 < (int)(in_stack_00000008 << 0x15)) {
        in_stack_00000000 = 6;
      }
      for (; (uVar5 < 0x20 && (9 < in_stack_00000000)); in_stack_00000000 = in_stack_00000000 - 1) {
        local_40[uVar5] = '0';
        uVar5 = uVar5 + 1;
      }
      iVar4 = (int)(longlong)in_d0;
      dVar7 = (double)VectorSignedToFloat(iVar4,(byte)(uVar6 >> 0x16) & 3);
      dVar7 = (in_d0 - dVar7) * *(double *)(DAT_00484000 + in_stack_00000000 * 8);
      uVar3 = (uint)(0.0 < dVar7) * (int)(longlong)dVar7;
      dVar8 = (double)VectorUnsignedToFloat(uVar3,(byte)(uVar6 >> 0x16) & 3);
      dVar7 = dVar7 - dVar8;
      uVar2 = uVar6 | (uint)(dVar7 < DAT_00483644) << 0x1f;
      if (SUB41(uVar2 >> 0x1f,0) == (NAN(dVar7) || NAN(DAT_00483644))) {
        uVar3 = uVar3 + 1;
        dVar7 = (double)VectorUnsignedToFloat(uVar3,(byte)(uVar2 >> 0x16) & 3);
        dVar8 = *(double *)(DAT_00484000 + in_stack_00000000 * 8);
        uVar6 = uVar6 | (uint)(dVar7 < dVar8) << 0x1f;
        if (SUB41(uVar6 >> 0x1f,0) == (NAN(dVar7) || NAN(dVar8))) {
          uVar3 = 0;
          iVar4 = iVar4 + 1;
        }
      }
      else if ((0.5 <= dVar7) && ((uVar3 == 0 || ((int)(uVar3 * -0x80000000) < 0)))) {
        uVar3 = uVar3 + 1;
      }
      if (in_stack_00000000 == 0) {
        dVar7 = (double)VectorSignedToFloat(iVar4,(byte)(uVar6 >> 0x16) & 3);
        if (((-1 < (int)((uint)(in_d0 - dVar7 < 0.5) << 0x1f)) || (DAT_00483644 <= in_d0 - dVar7))
           && (iVar4 << 0x1f < 0)) {
          iVar4 = iVar4 + 1;
        }
      }
      else {
        do {
          if (0x1f < uVar5) break;
          in_stack_00000000 = in_stack_00000000 - 1;
          local_40[uVar5] = (char)uVar3 + (char)(uVar3 / 10) * -10 + '0';
          uVar5 = uVar5 + 1;
          uVar3 = uVar3 / 10;
        } while (uVar3 != 0);
        while ((uVar5 < 0x20 && (in_stack_00000000 != 0))) {
          local_40[uVar5] = '0';
          uVar5 = uVar5 + 1;
          in_stack_00000000 = in_stack_00000000 - 1;
        }
        if (uVar5 < 0x20) {
          local_40[uVar5] = '.';
          uVar5 = uVar5 + 1;
        }
      }
      do {
        if (0x1f < uVar5) break;
        local_40[uVar5] = (char)iVar4 + (char)(iVar4 / 10) * -10 + '0';
        uVar5 = uVar5 + 1;
        iVar4 = iVar4 / 10;
      } while (iVar4 != 0);
      if ((in_stack_00000008 & 3) == 1) {
        if ((in_stack_00000004 != 0) && ((bVar1 || ((in_stack_00000008 & 0xc) != 0)))) {
          in_stack_00000004 = in_stack_00000004 - 1;
        }
        for (; (uVar5 < in_stack_00000004 && (uVar5 < 0x20)); uVar5 = uVar5 + 1) {
          local_40[uVar5] = '0';
        }
      }
      if (uVar5 < 0x20) {
        if (bVar1) {
          local_40[uVar5] = '-';
        }
        else if ((int)(in_stack_00000008 << 0x1d) < 0) {
          local_40[uVar5] = '+';
        }
        else if ((int)(in_stack_00000008 << 0x1c) < 0) {
          local_40[uVar5] = ' ';
        }
      }
      FUN_0048306c();
    }
  }
  else {
    FUN_0048306c();
  }
  return;
}

