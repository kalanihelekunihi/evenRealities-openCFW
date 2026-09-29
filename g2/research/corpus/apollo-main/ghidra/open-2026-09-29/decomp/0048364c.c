
int FUN_0048364c(code *param_1,undefined4 param_2,int param_3,undefined4 param_4,int param_5,
                uint param_6,uint param_7)

{
  undefined1 uVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  bool bVar5;
  uint in_fpscr;
  double in_d0;
  double dVar6;
  double dVar7;
  uint uVar8;
  
  uVar4 = in_fpscr & 0xfffffff;
  if ((in_d0 == DAT_00483908) || (in_d0 < DAT_00483910)) {
    iVar2 = FUN_00483350(param_1,param_2,param_3,param_4,param_5,param_6,param_7);
  }
  else {
    if (in_d0 < DAT_00483918) {
      in_d0 = -in_d0;
    }
    if (-1 < (int)(param_7 << 0x15)) {
      param_5 = 6;
    }
    uVar8 = (uint)((ulonglong)in_d0 >> 0x20);
    dVar6 = (double)VectorSignedToFloat((uVar8 >> 0x14 & 0x7ff) - 0x3ff,(byte)(uVar4 >> 0x16) & 3);
    iVar3 = (int)(longlong)
                 (DAT_00483928 + dVar6 * DAT_00483920 +
                 ((double)CONCAT44(uVar8 & DAT_00484004 | DAT_00484008,SUB84(in_d0,0)) + -1.5) *
                 DAT_00483930);
    dVar6 = (double)VectorSignedToFloat(iVar3,(byte)(uVar4 >> 0x16) & 3);
    iVar2 = (int)(longlong)(dVar6 * DAT_00483938 + 0.5);
    dVar6 = (double)VectorSignedToFloat(iVar3,(byte)(uVar4 >> 0x16) & 3);
    dVar7 = (double)VectorSignedToFloat(iVar2,(byte)(uVar4 >> 0x16) & 3);
    dVar7 = dVar6 * DAT_00483940 + dVar7 * DAT_00483948;
    dVar6 = dVar7 * dVar7;
    if ((int)((uint)(in_d0 < ((dVar7 * 2.0) /
                              ((2.0 - dVar7) + dVar6 / (dVar6 / (dVar6 / 14.0 + 10.0) + 6.0)) + 1.0)
                             * (double)((ulonglong)(uint)((iVar2 + 0x3ff) * 0x100000) << 0x20)) <<
             0x1f) < 0) {
      iVar3 = iVar3 + -1;
    }
    if (iVar3 + 99U < 199) {
      uVar4 = 4;
    }
    else {
      uVar4 = 5;
    }
    if ((int)(param_7 << 0x14) < 0) {
      if ((in_d0 < DAT_00483950) || (-1 < (int)((uint)(in_d0 < DAT_00483958) << 0x1f))) {
        if ((param_5 != 0) && ((int)(param_7 << 0x15) < 0)) {
          param_5 = param_5 + -1;
        }
      }
      else {
        if (iVar3 < param_5) {
          param_5 = (param_5 - iVar3) + -1;
        }
        else {
          param_5 = 0;
        }
        param_7 = param_7 | 0x400;
        uVar4 = 0;
        iVar3 = 0;
      }
    }
    if (uVar4 < param_6) {
      iVar2 = param_6 - uVar4;
    }
    else {
      iVar2 = 0;
    }
    if (((int)(param_7 << 0x1e) < 0) && (uVar4 != 0)) {
      iVar2 = 0;
    }
    iVar2 = FUN_00483350(param_1,param_2,param_3,param_4,param_5,iVar2,param_7 & 0xfffff7ff);
    if (uVar4 != 0) {
      if ((int)(param_7 << 0x1a) < 0) {
        uVar1 = 0x45;
      }
      else {
        uVar1 = 0x65;
      }
      (*param_1)(uVar1,param_2,iVar2,param_4);
      bVar5 = iVar3 < 0;
      if (iVar3 < 0) {
        iVar3 = -iVar3;
      }
      iVar2 = FUN_0048320a(param_1,param_2,iVar2 + 1,param_4,iVar3,bVar5,10,0,uVar4 - 1,5);
      if ((int)(param_7 << 0x1e) < 0) {
        for (; (uint)(iVar2 - param_3) < param_6; iVar2 = iVar2 + 1) {
          (*param_1)(0x20,param_2,iVar2,param_4);
        }
      }
    }
  }
  return iVar2;
}

