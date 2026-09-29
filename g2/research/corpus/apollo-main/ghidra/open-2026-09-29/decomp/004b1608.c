
void FUN_004b1608(undefined4 param_1,uint param_2,int param_3,uint param_4,uint param_5,int param_6)

{
  int *piVar1;
  undefined4 *puVar2;
  int iVar3;
  uint uVar4;
  undefined4 uVar5;
  
  piVar1 = DAT_004b178c;
  if (param_5 == 0xffffffff) {
    uVar4 = param_4 & 0x7f;
    param_5 = param_2;
    if (param_6 << 0x1b < 0) {
      param_5 = param_2 + 3 + ((uint)((int)(param_2 + 3) >> 1) >> 0x1e) & 0xfffffffc;
    }
    if ((uVar4 == 0x12 || uVar4 == 0x16) || (uVar4 == 0x17 || uVar4 == 0x4e)) {
      param_5 = param_5 + 3 + ((uint)((int)(param_5 + 3) >> 1) >> 0x1e) & 0xfffffffc;
    }
    if (uVar4 == 0x4c || uVar4 == 0x4d) {
      param_5 = (param_5 + 1) - ((int)(param_5 + 1) >> 0x1f) & 0xfffffffe;
    }
    switch(uVar4) {
    case 0xb:
    case 0xc:
    case 0x27:
    case 0x2a:
      param_5 = (int)(param_5 + 7 + ((uint)((int)(param_5 + 7) >> 2) >> 0x1d)) >> 3;
      break;
    default:
      iVar3 = 4;
      switch(uVar4) {
      case 4:
      case 5:
      case 6:
      case 0xd:
      case 0x13:
      case 0x1d:
      case 0x3d:
      case 0x3e:
      case 0x3f:
      case 0x44:
      case 0x46:
      case 0x47:
      case 0x48:
      case 0x49:
      case 0x4a:
      case 0x4b:
      case 0x4c:
      case 0x4d:
        iVar3 = 2;
        break;
      case 7:
      case 8:
      case 9:
      case 0xc:
      case 0x12:
      case 0x16:
      case 0x17:
      case 0x18:
      case 0x19:
      case 0x1a:
      case 0x27:
      case 0x28:
      case 0x30:
      case 0x31:
      case 0x34:
      case 0x35:
      case 0x38:
      case 0x40:
      case 0x41:
      case 0x42:
      case 0x43:
      case 0x45:
      case 0x4e:
        iVar3 = 1;
        break;
      case 0x39:
      case 0x3c:
        iVar3 = 3;
      }
      param_5 = param_5 * iVar3;
      break;
    case 0x12:
      param_5 = param_5 << 1;
      break;
    case 0x16:
    case 0x17:
    case 0x4c:
    case 0x4d:
    case 0x4e:
      param_5 = param_5 * 3;
      break;
    case 0x28:
    case 0x2b:
    case 0x30:
    case 0x31:
      iVar3 = param_5 * 2 + 7;
      param_5 = (int)(iVar3 + ((uint)(iVar3 >> 2) >> 0x1d)) >> 3;
      break;
    case 0x29:
    case 0x2c:
    case 0x34:
    case 0x35:
      iVar3 = param_5 * 4 + 7;
      param_5 = (int)(iVar3 + ((uint)(iVar3 >> 2) >> 0x1d)) >> 3;
    }
  }
  iVar3 = *DAT_004b178c;
  *(uint *)(iVar3 + 0x5c) = param_5 & 0xffff | param_6 << 0x10 | param_4 << 0x18;
  *(undefined4 *)(iVar3 + 0x50) = param_1;
  *(uint *)(iVar3 + 0x54) = param_2;
  *(int *)(iVar3 + 0x58) = param_3;
  *(undefined4 *)(iVar3 + 0x60) = 1;
  *(uint *)(iVar3 + 100) = param_4;
  puVar2 = (undefined4 *)FUN_00514aec(3);
  if (puVar2 != (undefined4 *)0x0) {
    *puVar2 = 0x10;
    puVar2[1] = param_1;
    puVar2[2] = 0x14;
    uVar5 = *(undefined4 *)(*piVar1 + 0x5c);
    puVar2[4] = 0x18;
    puVar2[3] = uVar5;
    puVar2[5] = param_2 | param_3 << 0x10;
  }
  return;
}

