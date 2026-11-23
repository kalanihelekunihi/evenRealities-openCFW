/* Fix 48: stock flash 0x5232d0..0x523303, two overlapping float tables (+0 and +0x18) read at
 * byte offset iVar13 in {8..0x18} (stock image words). */
/* Wave20 evidence (replaces the wave8 audit note): there are no ambient VFP/FPSCR or
 * unaff-register temps left. The .waves/inventory.py nvg_leftover pattern counts 0 here,
 * and every former carrier is a plain compare with a per-site stock vcmp/vmrs citation
 * (wave19, g2/docs/wave19-markers.md). */
/* Evidence (returns): FUN_00514846 @ 0x514846 (678 B sha 53d0c598…),
 * FUN_0052294c @ 0x52294c (10 B sha f227809f…) corpus
 * apollo-main/ghidra/open-2026-09-29 — return paths checked in decomp.
 * The only remaining FPSCR use is the RMode argument of VectorSignedToFloat. It is
 * RN (0) by stock evidence: a full-image scan found 5 vmsr fpscr, all of them
 * save/clear-exceptions/restore writers (see below), so RMode is never changed. */
#pragma clang diagnostic ignored "-Wint-conversion"
#pragma clang diagnostic ignored "-Wpointer-sign"
#pragma clang diagnostic ignored "-Wpointer-to-int-cast"
#pragma clang diagnostic ignored "-Wint-to-pointer-cast"
#pragma clang diagnostic ignored "-Wunused-variable"
#pragma clang diagnostic ignored "-Wunused-but-set-variable"
#pragma clang diagnostic ignored "-Wparentheses"
#pragma clang diagnostic ignored "-Wempty-body"
#pragma clang diagnostic ignored "-Wunused-value"
#pragma clang diagnostic ignored "-Wbuiltin-requires-header"
#pragma clang diagnostic ignored "-Winvalid-unary-operand-type"
#pragma clang diagnostic ignored "-Wbad-function-cast"
#pragma clang diagnostic ignored "-Wvarargs"
/* Stock (IAR, FPv5) uses only single-precision, non-fused VMUL/VMLA/VMLS in this module:
 * no .f64 and no VFMA anywhere in its stock bodies. Forbid FMA contraction so rounding matches. */
#pragma clang fp contract(off)
typedef unsigned char undefined1, byte;
typedef unsigned short undefined2, ushort;
typedef unsigned int undefined4, uint, undefined, uintptr_t;
typedef unsigned long long undefined8, ulonglong;
typedef long long longlong;
typedef int bool;
#define true 1
#define false 0
/* NAN() carrier macro removed in wave19: every use was rewritten to a stock-cited compare. */
#define ABS(x) ((x) < 0 ? -(x) : (x))
static inline ulonglong CONCAT44(uint a, uint b){return ((ulonglong)a<<32)|b;}
static inline uint CONCAT31(uint a, byte b){return (a<<8)|b;}
static inline byte SUB41(uint a, int n){return (byte)(a>>(n*8));}
static inline int SBORROW4(int a, int b){return ((a^b)&(a^(a-b)))<0;}
static inline float VectorSignedToFloat(int v, int r){(void)r;return (float)v;}
static inline float VectorUnsignedToFloat(uint v, int r){(void)r;return (float)v;}
static inline uint VectorFloatToUnsigned(float v, int r){(void)r;return (uint)v;}
static inline float VectorSignedFixedToFloat(int v, int bits, int r){(void)r;return (float)v/(float)(1u<<(bits&31));}
static inline float g2c_bits_to_float(uint u){union{uint u;float f;}x;x.u=u;return x.f;}
static inline uint g2c_float_to_bits(float f){union{uint u;float f;}x;x.f=f;return x.u;}
/* Float<->pointer punning at bad decomp sites (documented residual). */
static inline float g2c_ptr_as_float(const void *p){return g2c_bits_to_float((uint)(uintptr_t)p);}
static inline void *g2c_float_as_ptr(float f){return (void *)(uintptr_t)g2c_float_to_bits(f);}

/* Evidence (wave10): FPSCR.RMode is RN (0) for the whole image. Stock
 * 2.2.6.10 writes FPSCR = 0x02040000 (DN, LTPSIZE=4, RMode 0) once at
 * 0x5e428c after enabling CP10/CP11 in CPACR (0xE000ED88). The only other vmsr
 * writers (0x4d42e0/0x4d42ec, 0x59d2ea/0x59d2f6) clear the cumulative exception
 * bits [12:8],[4:0] and restore the saved value. A full-image objdump scan
 * found 5 vmsr fpscr in total. */
#define G2C_FPSCR_RMODE_RN 0
/* g2c_fpscr_* NZCV stand-ins removed in wave19: all uses replaced by stock-cited compares. */
extern volatile uint audio_uart_nema_context_cell[];
/* The first stock table word points to RAM 0x20074efc. Bind it to the same
 * source object used by the NemaVG code when the image is relocated. */
static const uint g2_nema_arc_table_5232d0[13]={
  (uint)(uintptr_t)&audio_uart_nema_context_cell[0],
  0x3f6c835eu, 0x3f7b14beu, 0x3f7dcf55u, 0x3f7ec46du, 0x3f7f35f9u,
  0x3f7f73afu, 0x3ec3ef15u, 0x3e47c5c2u, 0x3e05a8a8u, 0x3dc8bd36u,
  0x3da0af2au, 0x3d85f213u};
extern volatile uint audio_uart_nema_vg_context_cell;
extern volatile uint audio_uart_nema_vg_framebuffer_context_cell_20074f08;
void *memcpy(void *, const void *, uint);
void *memset(void *, int, uint);
void lv_log_add(int, char *, int, char *, char *, ...);
void *lv_malloc(uint);
void lv_free(void *);
static void g2c_nemavg_area_copy_540024(int *dst, int *src){dst[0]=src[0];dst[1]=src[1];dst[2]=src[2];dst[3]=src[3];}
static const float g2c_nvg_zero_pair_0[2]={0.f,0.f};
static const float g2c_nvg_zero_pair_1[2]={0.f,0.f};
static const float g2c_nvg_zero_pair_2[2]={0.f,0.f};
/* Residual FPSCR scratchs: prefer g2c_fpscr_* / local floats; remain for
 * unreduced sites. */
/* Evidence (wave10): the file-scope FPSCR scratch is removed; every function now uses either a local or a recovered compare. */

extern float audio_uart_float_sqrt_4397a8(float value);
extern uint audio_uart_display_area_copy_439c04(uint out, uint in, uint count);
extern void audio_uart_lv_area_expand_450b98(uint area, int w_extra, int h_extra);
extern byte audio_uart_lv_area_intersect_450bcc(uint res, uint a1, uint a2);
extern uint audio_uart_lv_area_contains_450f28(uint inner,uint outer,uint radius);
extern int audio_uart_lv_area_width_451598(uint area);
extern int audio_uart_lv_area_height_4515a4(uint area);
extern void audio_uart_lv_memzero_48949c(uint destination,uint size);
extern uint audio_uart_ambiq_color_resolve_4b06a8(uint color, uint alpha);
extern void audio_uart_ambiq_texture_setup_4b06c0(uint unit,uint mode, uint target,uint surface, uint alternate,uint force);
extern void display_driver_gpu_enable_4b0748(uint unit, uint mode);
extern uint audio_uart_ambiq_stencil_adjust_4b0b5a(uint cell,uint width,uint height);
extern int audio_uart_nema_error_set_4b127c(uint error); /* Evidence: stock 0x4b127c; used by FUN_00514846 */
extern void audio_uart_nema_bind_tex_4b1298(uint unit,uint address,uint width,uint height,int format,uint stride,uint flags);
extern void audio_uart_ambiq_texture_color_4b146c(uint color);
extern void audio_uart_display_graphics_target_4b1516(int x, int y, uint width, uint height);
extern void audio_uart_display_graphics_finish_4b1548(void);
extern float audio_uart_float_trig_mode1_50968c(float angle);
extern float audio_uart_float_trig_mode0_509690(float angle);
extern float audio_uart_float_two_input_angle_50969c(float y, float x);
extern void audio_uart_display_graphics_blend_513924(uint mode, uint target, uint blend, uint source);
extern void audio_uart_ambiq_image_alpha_513e2e(uint alpha);
extern uint audio_uart_nema_reg_read_51403c(uint offset);
extern void audio_uart_nema_buffer_create_514070(uint out,uint id,uint size);
extern uint audio_uart_nema_node_allocate_51416c(uint size);
extern int audio_uart_nema_cl_node_release_514178(void *node); /* Proven: returns 0 after pool_free (0x514178) */
extern void audio_uart_nema_cl_rewind_514384(uint cell);
extern void audio_uart_nema_cl_unbind_5144ba(void);
extern uint audio_uart_nema_cl_get_bound_5144fa(void);
extern void audio_uart_nema_sector_rollover_5147b0(uint cell);
extern void audio_uart_nema_child_514846(uint reg,uint value);
extern uint audio_uart_nema_cl_get_space_514aec(uint pairs);
extern void audio_uart_nema_cl_submit_514cf2(uint cell);
extern int audio_uart_nema_cl_wait_514d00(uint cell);
extern int g2c_nema_cl_enough_space_514d2c(int words);
extern void audio_uart_nema_vg_path_shape_514f3c(uint path,uint segment_count,uint segments,uint data_count,uint data);
extern void audio_uart_nema_vg_set_error_51565c(uint error);
extern uint audio_uart_nema_child_52261a(void);
extern void audio_uart_nema_child_52262e(uint enabled);
extern void audio_uart_nema_child_52264e(uint enabled);
extern uint audio_uart_nema_stencil_save_52266e(uint a, uint b, uint c, uint d);
extern uint audio_uart_nema_stencil_restore_5226b2(uint previous);
extern void audio_uart_nema_matrix_upload_5226e8(uint matrix);
extern void audio_uart_nema_float_position_5228b0(float x, float y);
extern void audio_uart_nema_instruction_upload_522920(uint words,uint count,uint address);
/* Evidence: FUN_0052294c @ 0x52294c decomp → FUN_00514846(0x11c, param). */
void display_driver_nema_mode_commit_52294c(uint value) {
  audio_uart_nema_child_514846(0x11cu, value);
}
extern void audio_uart_nema_rop_blend_mode_522956(uint value);
extern void display_driver_nema_select_522a16(uint color);
extern void g2c_nema_raster_triangle_f_522a24(float x0, float y0, float x1, float y1, float x2, float y2);
extern uint audio_uart_nema_mask_rectangle_522ae0(int x, int y, int width, int height);
extern void g2c_nema_raster_rounded_rect_522b30(int x, int y, int w, int h, int r);
extern void audio_uart_nema_register_emit_523e92(uint reg,uint value);
extern float audio_uart_nema_sin_52405c(float degrees);
extern float audio_uart_nema_cos_524130(float degrees);
extern int audio_uart_nema_float_fixed_5242cc(float value);
extern void audio_uart_nema_matrix_identity_561810(uint cell);
extern void audio_uart_nema_matrix_copy_561830(uint destination, uint source);
extern void audio_uart_nema_matrix_translate_561856(float x,float y,uint matrix);
extern uint audio_uart_nema_matrix_finalize_561b38(uint matrix);
extern float audio_uart_float_tangent_563f40(float angle);

int g2c_nema_cl_submit_node_4b14ca(uint a, int b, int c, int d);
uint g2c_nema_cl_get_error_4b14fe(void);
void g2c_nema_vg_fill_4b1794(uint a, uint b, int c, uint d, uint e, uint f, uint g, int h);
void g2c_nema_vg_path_reset_515148(int *path);
uint g2c_nema_vg_path_alloc_51520c(int a);
uint g2c_nema_vg_path_cmd_5156b8(uint *path, uint cmd, float *coords);
uint g2c_nema_vg_emit_verts_516b34(float a, float b, float c, float d, float e, float f, float g, float h);
uint g2c_nema_vg_emit_tri_516bde(float a, float b, float c, float d, int e, int f);
void g2c_nema_vg_paint_setup_516c82(uint *paint);
uint g2c_nema_vg_tess_516cf8(int a);
uint g2c_nema_vg_tess_fill_516e0c(uint *a);
uint g2c_nema_vg_tess_stroke_5171f8(uint *a);
void g2c_nema_vg_set_aa_51778c(uint a);
void g2c_nema_vg_set_aa2_517796(uint a);
int g2c_nema_vg_near_5177a4(float *a, float *b);
int g2c_nema_vg_near2_51785c(float *a, float *b);
uint g2c_nema_vg_stroke_join_5179d0(float *a, uint *b, float *c, uint *d, int e);
uint g2c_nema_vg_stroke_path_517e18(float a, float b, float c, float d, float e, float f, float g, float h);
uint g2c_nema_vg_fill_path_519290(float a, float b, float c, float d, float e, float f);
void g2c_nema_vg_quad_to_51a660(float a, float b, float c, float d, float e, float f, float *out);
uint g2c_nema_vg_cubic_to_51a694(float a, float b, float c, float d, float e, float f, uint g, int h, int i);
uint g2c_nema_vg_arc_to_51a8ec(uint a, int b);
void g2c_nema_vg_bezier_subdiv_51b140(float a, float b, float c, int d);
uint g2c_nema_vg_arc_seg_51b8f0(float a, float b, float c, float d, float e);
uint g2c_nema_vg_arc_seg2_51bf7c(float a, float b, float c, float d, float e);
uint g2c_nema_vg_arc_seg3_51c5ec(float a, float b, float c, float d, float e);
uint g2c_nema_vg_draw_fill_51d2e0(uint *a);
uint g2c_nema_vg_draw_stroke_51f798(uint *a);
uint audio_uart_ambiq_vector_shape_draw_5202ec(uint *path, int paint);
void g2c_nema_vg_set_flag_522622(uint a);
uint g2c_nema_vg_f2u_522f1c(float a);
int g2c_nema_vg_cubic_approx_522f50(float a, float b, float c, float d, float e, float f, float g, float h, float *out0, float *out1);
void g2c_nema_vg_move_to_522fb4(float a, float b, float c);
void g2c_nema_vg_line_to_523284(float a, float b, float c);
void g2c_nema_vg_path_transform_523a34(float *m, int a, int b);
float g2c_nema_vg_sqrt_524218(float x);
void audio_uart_ambiq_draw_box_shadow_540036(int task, int dsc, int *coords, uint color);
void g2c_nema_vg_mat_mul_5619f2(float *a, float *b);
void g2c_nema_vg_path_clear_56395c(void);
uint g2c_nema_vg_path_bounds_5639e8(float a, float b, float c, float d);
uint g2c_nema_vg_ellipse_5640e4(float a, float b, float c, float d, float *out);
uint g2c_nema_vg_arc_build_564974(float a, float b, float c, float d);
uint g2c_nema_vg_arc_draw_5653a0(float a, float b, float c, float d, float e, float f, float g, float h);
uint g2c_nema_vg_draw_path_inner_5657d8(uint *a);
uint g2c_nema_vg_paint_apply_567230(uint a, int b);


/* ---- lifted 0x4b14ca ---- */

/* Stock 0x4b14ca..0x4b14fe (52 B): emit register 0x158 = clipped (a, b) origin, then tail-call
 * 0x514846(0x15c, pkhbt(a + c, (b + d) << 16)) (b.w at 0x4b14fa). The earlier Ghidra lift had
 * merged a private copy of 0x514846's body specialised for 0x15c here, and that copy diverged from
 * the real 0x514846 (e.g. it emitted via 0x523e92 when no command list was bound); nvg-a caught it.
 * The stock return value is 0x514846's r0, which no caller (all in this file) reads. */
int g2c_nema_cl_submit_node_4b14ca(uint a,int b,int c,int d)
{
  uint origin = (int)a < 1 ? 0u : (a & 0xffffu);
  if (0 < b) origin |= (uint)b << 0x10;
  audio_uart_nema_child_514846(0x158, origin);
  audio_uart_nema_child_514846(0x15c, ((uint)c + a) & 0xffffu | ((uint)d + (uint)b) << 0x10);
  return 0;
}


  

/* ---- lifted 0x4b14fe ---- */

uint g2c_nema_cl_get_error_4b14fe(void)

{
  uint uVar1;
  
  uVar1 = audio_uart_nema_reg_read_51403c(0x15c);
  return ~-(uint)(uVar1 == 0) >> 0x1f;
}

  

/* ---- lifted 0x4b1794 ---- */

void g2c_nema_vg_fill_4b1794(uint a,uint b,int c,uint d,uint e,uint f,uint g,int h)

{
  int *piVar1;
  undefined4 *puVar2;
  int iVar3;
  uint uVar4;
  undefined4 uVar5;
  uint uVar6;
  
  piVar1 = (((int *)audio_uart_nema_context_cell));
  if (d == 0xb || d == 0x2a) {
    uVar6 = 2;
    goto LAB_004b17cc;
  }
  if (d == 0x2b) {
LAB_004b17c0:
    uVar6 = 4;
  }
  else {
    if (d != 0x2c) {
      if (d == 0x31) goto LAB_004b17c0;
      if (d != 0x35) {
        uVar6 = 0x100;
        goto LAB_004b17cc;
      }
    }
    uVar6 = 0x10;
  }
LAB_004b17cc:
  if ((int)(f << 0x1f) < 0) {
    f = f & 0xfe;
  }
  iVar3 = *(((int *)audio_uart_nema_context_cell));
  *(uint *)(iVar3 + 0x68) = g;
  *(uint *)(iVar3 + 0x6c) = uVar6;
  *(int *)(iVar3 + 0x7c) = h;
  *(undefined4 *)(iVar3 + 0x70) = 1;
  *(uint *)(iVar3 + 0x74) = h << 0x18 | 0x40000;
  *(undefined4 *)(iVar3 + 0x78) = 1;
  puVar2 = (undefined4 *)audio_uart_nema_cl_get_space_514aec(3);
  if (puVar2 != (undefined4 *)0x0) {
    *puVar2 = 0x20;
    puVar2[1] = g;
    puVar2[2] = 0x24;
    uVar5 = *(undefined4 *)(*piVar1 + 0x74);
    puVar2[4] = 0x28;
    puVar2[3] = uVar5;
    puVar2[5] = uVar6 | 0x10000;
  }
  if (e == 0xffffffff) {
    uVar4 = d & 0x7f;
    uVar6 = b;
    if ((int)(f << 0x1b) < 0) {
      uVar6 = b + 3 + ((uint)((int)(b + 3) >> 1) >> 0x1e) & 0xfffffffc;
    }
    if ((uVar4 == 0x12 || uVar4 == 0x16) || (uVar4 == 0x17 || uVar4 == 0x4e)) {
      uVar6 = uVar6 + 3 + ((uint)((int)(uVar6 + 3) >> 1) >> 0x1e) & 0xfffffffc;
    }
    if (uVar4 == 0x4c || uVar4 == 0x4d) {
      uVar6 = (uVar6 + 1) - ((int)(uVar6 + 1) >> 0x1f) & 0xfffffffe;
    }
    switch(uVar4) {
    case 0xb:
    case 0xc:
    case 0x27:
    case 0x2a:
      e = (int)(uVar6 + 7 + ((uint)((int)(uVar6 + 7) >> 2) >> 0x1d)) >> 3;
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
      e = uVar6 * iVar3;
      break;
    case 0x12:
      e = uVar6 << 1;
      break;
    case 0x16:
    case 0x17:
    case 0x4c:
    case 0x4d:
    case 0x4e:
      e = uVar6 * 3;
      break;
    case 0x28:
    case 0x2b:
    case 0x30:
    case 0x31:
      iVar3 = uVar6 * 2 + 7;
      e = (int)(iVar3 + ((uint)(iVar3 >> 2) >> 0x1d)) >> 3;
      break;
    case 0x29:
    case 0x2c:
    case 0x34:
    case 0x35:
      iVar3 = uVar6 * 4 + 7;
      e = (int)(iVar3 + ((uint)(iVar3 >> 2) >> 0x1d)) >> 3;
    }
  }
  iVar3 = *piVar1;
  *(uint *)(iVar3 + 0x50) = a;
  *(uint *)(iVar3 + 0x54) = b;
  *(int *)(iVar3 + 0x58) = c;
  *(uint *)(iVar3 + 0x5c) = e & 0xffff | f << 0x10 | d << 0x18;
  *(undefined4 *)(iVar3 + 0x60) = 1;
  *(uint *)(iVar3 + 100) = d;
  puVar2 = (undefined4 *)audio_uart_nema_cl_get_space_514aec(3);
  if (puVar2 != (undefined4 *)0x0) {
    *puVar2 = 0x10;
    puVar2[1] = a;
    puVar2[2] = 0x14;
    uVar5 = *(undefined4 *)(*piVar1 + 0x5c);
    puVar2[4] = 0x18;
    puVar2[3] = uVar5;
    puVar2[5] = b | c << 0x10;
  }
  return;
}

  

/* ---- lifted 0x515148 ---- */

void g2c_nema_vg_path_reset_515148(int *path)

{
  int iVar1;
  uint uVar2;
  uint address;
  int iVar3;
  uint width;
  uint height;
  uint format;
  uint stride;
  
  switch(*(undefined1 *)((int)path + 0xd5)) {
  case 1:
  case 4:
    uVar2 = *(byte *)(path + 0x33) | 1;
    stride = 0;
    format = 1;
    height = 1;
    width = 0x40;
    address = *(uint *)(path[0xc] + 0xc);
    break;
  case 2:
    iVar1 = *path;
    if (iVar1 != 0) {
      if ((char)path[0xb] == '\0') {
        uVar2 = (uint)*(byte *)(iVar1 + 0x1d);
        stride = *(uint *)(iVar1 + 0x14);
        format = (uint)*(byte *)(iVar1 + 0x1c);
        height = (uint)*(ushort *)(iVar1 + 0x12);
        width = (uint)*(ushort *)(iVar1 + 0x10);
        address = *(uint *)(iVar1 + 0xc);
        break;
      }
      iVar3 = path[1];
      if (iVar3 != 0) {
        g2c_nema_vg_fill_4b1794
                  (*(uint *)(iVar1 + 0xc),(uint)*(ushort *)(iVar1 + 0x10),
                   (uint)*(ushort *)(iVar1 + 0x12),(uint)*(byte *)(iVar1 + 0x1c),
                   *(uint *)(iVar1 + 0x14),(uint)*(byte *)(iVar1 + 0x1d),*(uint *)(iVar3 + 0xc),
                   (uint)*(byte *)(iVar3 + 0x1c));
        return;
      }
    }
    *(uint *)(*(((int *)&audio_uart_nema_vg_context_cell)) + 0x80) = *(uint *)(*(((int *)&audio_uart_nema_vg_context_cell)) + 0x80) | 2;
    return;
  case 3:
    uVar2 = audio_uart_nema_child_52261a();
    if (-1 < (int)(uVar2 << 0x17)) {
      audio_uart_nema_vg_set_error_51565c(0x20);
      *(undefined1 *)((int)path + 0xd5) = 0;
      return;
    }
    width = 1;
    uVar2 = *(byte *)(path + 0x33) | 0x81;
    stride = 4;
    format = 1;
    height = 0x40;
    address = *(uint *)(path[0xc] + 0xc);
    break;
  default:
    return;
  }
  audio_uart_nema_bind_tex_4b1298(1,address,width,height,format,stride,uVar2);
  return;
}

  

/* ---- lifted 0x51520c ---- */

uint g2c_nema_vg_path_alloc_51520c(int a)

{
  byte bVar1;
  char cVar2;
  int *piVar3;
  uint uVar4;
  int iVar5;
  float *b;
  bool bVar6;
  float afStack_58 [9];
  float afStack_34 [10];
  
  piVar3 = (((int *)&audio_uart_nema_vg_context_cell));
  bVar1 = *(byte *)(a + 0xd5);
  if (bVar1 == 1) {
LAB_0051522e:
    iVar5 = *(((int *)&audio_uart_nema_vg_context_cell));
    if ((*(byte *)(a + 0xd4) & 1) != 0) {
      bVar6 = *(char *)(iVar5 + 0x1bc) != '\x01';
      cVar2 = '\x01';
      if (bVar6) {
        cVar2 = *(char *)(iVar5 + 0x1bd);
      }
      if (bVar6 && cVar2 != '\x01') {
        uVar4 = a + 0x34;
LAB_005152d6:
        audio_uart_nema_matrix_upload_5226e8(uVar4);
        return 0;
      }
      audio_uart_nema_matrix_copy_561830((uint)afStack_34,iVar5 + 0xec);
      uVar4 = audio_uart_nema_matrix_finalize_561b38((uint)afStack_34);
      if (uVar4 != 0) {
LAB_005152ae:
        g2c_nema_vg_set_aa_51778c(0);
        g2c_nema_vg_set_aa2_517796(0);
        audio_uart_nema_vg_set_error_51565c(0x40000);
        return 0x40000;
      }
      audio_uart_nema_matrix_copy_561830((uint)afStack_58,a + 0x34);
      b = afStack_34;
      goto LAB_005152ec;
    }
    if (-1 < (int)((uint)*(byte *)(iVar5 + 0x90) << 0x1f)) {
      uVar4 = a + 0x34;
      goto LAB_005152d6;
    }
    iVar5 = 0x34;
  }
  else {
    if (bVar1 == 0) {
      return 0;
    }
    if (bVar1 == 3) goto LAB_0051522e;
    if (2 < bVar1) {
      return 0;
    }
    iVar5 = *(((int *)&audio_uart_nema_vg_context_cell));
    if ((*(byte *)(a + 0xd4) & 1) != 0) {
      bVar6 = *(char *)(iVar5 + 0x1bc) != '\x01';
      cVar2 = '\x01';
      if (bVar6) {
        cVar2 = *(char *)(iVar5 + 0x1bd);
      }
      if (!bVar6 || cVar2 == '\x01') {
        audio_uart_nema_matrix_copy_561830((uint)afStack_34,iVar5 + 0xec);
        uVar4 = audio_uart_nema_matrix_finalize_561b38((uint)afStack_34);
        if (uVar4 != 0) goto LAB_005152ae;
        audio_uart_nema_matrix_copy_561830((uint)afStack_58,a + 8);
        b = afStack_34;
        goto LAB_005152ec;
      }
LAB_005152d2:
      uVar4 = a + 8;
      goto LAB_005152d6;
    }
    if (-1 < (int)((uint)*(byte *)(iVar5 + 0x90) << 0x1f)) goto LAB_005152d2;
    iVar5 = 8;
  }
  audio_uart_nema_matrix_copy_561830((uint)afStack_58,a + iVar5);
  b = (float *)(*piVar3 + 200);
LAB_005152ec:
  g2c_nema_vg_mat_mul_5619f2(afStack_58,b);
  audio_uart_nema_matrix_upload_5226e8((uint)afStack_58);
  return 0;
}

  

/* ---- lifted 0x5156b8 ---- */


uint g2c_nema_vg_path_cmd_5156b8(uint *path,uint cmd,float *coords)

{
  char cVar1;
  uint *puVar2;
  undefined4 uVar3;
  undefined1 uVar4;
  undefined1 uVar5;
  undefined4 *puVar6;
  uint uVar7;
  int iVar8;
  float fVar9;
  uint uVar10;
  undefined4 uVar11;
  undefined4 uVar12;
  bool bVar13;
  bool bVar14;
  float fVar15;
  float fVar16;
  float fVar17;
  uint *h;
  float fVar18;
  float fVar19;
  float fVar20;
  float fVar21;
  float fVar22;
  float fVar23;
  float fVar24;
  float fVar25;
  undefined8 uVar26;
  undefined8 uVar27;
  float fVar28;
  float fVar29;
  /* Stock frame of 0x5156b8 as one block: locals keep the entry-SP offsets Ghidra named them by
   * (X_Stack_NN at g2c_frame_5156b8[0x98-0xNN]) so &local passed to callees spans its stock neighbours. */
  unsigned char g2c_frame_5156b8[0x98] __attribute__((aligned(8)));
  typedef float __attribute__((may_alias)) g2c_fa_float;
#define fStack_94 (*(g2c_fa_float *)(void *)&g2c_frame_5156b8[0x98-0x94])
  typedef uint *__attribute__((may_alias)) g2c_fa_uint_p;
#define puStack_90 (*(g2c_fa_uint_p *)(void *)&g2c_frame_5156b8[0x98-0x90])
#define fStack_8c (*(g2c_fa_float *)(void *)&g2c_frame_5156b8[0x98-0x8c])
#define fStack_88 (*(g2c_fa_float *)(void *)&g2c_frame_5156b8[0x98-0x88])
#define fStack_84 (*(g2c_fa_float *)(void *)&g2c_frame_5156b8[0x98-0x84])
#define fStack_80 (*(g2c_fa_float *)(void *)&g2c_frame_5156b8[0x98-0x80])
#define fStack_7c (*(g2c_fa_float *)(void *)&g2c_frame_5156b8[0x98-0x7c])
#define fStack_78 (*(g2c_fa_float *)(void *)&g2c_frame_5156b8[0x98-0x78])
#define fStack_74 (*(g2c_fa_float *)(void *)&g2c_frame_5156b8[0x98-0x74])
#define fStack_70 (*(g2c_fa_float *)(void *)&g2c_frame_5156b8[0x98-0x70])
  
  coords[3] = coords[5];
  coords[4] = coords[6];
  puVar2 = (((int *)&audio_uart_nema_vg_context_cell));
  bVar13 = -1 < (int)(cmd << 0x1b);
  uVar10 = cmd & 0x6f;
  uVar7 = *(byte *)(coords + 0x11) & 0x6f;
  uVar5 = (undefined1)cmd;
  if (uVar10 == 1) {
    if (*(char *)((int)coords + 1) == '\x01') {
      cVar1 = '\0';
      if (g2c_float_to_bits(coords[1]) != 0u) {
        uVar7 = *(((int *)&audio_uart_nema_vg_context_cell));
        cVar1 = *(char *)(uVar7 + 0x7c);
      }
      if (g2c_float_to_bits(coords[1]) != 0u && cVar1 != '\0') {
        uVar26 = CONCAT44((0x0u),(0x0u));
        if (*(char *)coords == '\0') {
          uVar26 = *(undefined8 *)(coords + 0xf);
        }
        uVar11 = *(undefined4 *)(uVar7 + 0x2d4);
        uVar12 = *(undefined4 *)(uVar7 + 0x2d0);
        puVar6 = (undefined4 *)audio_uart_nema_cl_get_space_514aec(7);
        if (puVar6 != (undefined4 *)0x0) {
          /* Evidence (wave10): this read is reachable only when coords[1]!=0 and
           * cVar1!=0, which is the branch that set r6 = &audio_uart_nema_vg_context_cell.
           * So r6 is the VG context cell (stock decomp 005156b8.c:60 loads it from literal DAT_00516230). */
          uVar7 = *(uint *)(*(((int *)&audio_uart_nema_vg_context_cell)) + 0x8c) & 0x7800000;
          if (*(char *)(*(((int *)audio_uart_nema_context_cell)) + 8) == '\x01') {
            uVar7 = uVar7 | *(uint *)(*(((int *)audio_uart_nema_context_cell)) + 0xc) & 0xc0000000;
          }
          *puVar6 = 800;
          fVar9 = coords[3];
          puVar6[2] = 0x324;
          puVar6[1] = g2c_float_to_bits(fVar9);
          fVar9 = coords[4];
          puVar6[4] = 0x330;
          puVar6[3] = g2c_float_to_bits(fVar9);
          puVar6[6] = 0x334;
          puVar6[8] = 0x140;
          uVar3 = (0xff000100u);
          puVar6[5] = (int)uVar26;
          puVar6[7] = (int)((ulonglong)uVar26 >> 0x20);
          puVar6[9] = uVar12;
          puVar6[10] = 0x144;
          puVar6[0xb] = uVar11;
          puVar6[0xc] = uVar3;
          puVar6[0xd] = uVar7 | 4;
        }
      }
    }
    *(undefined4 *)(*(((int *)&audio_uart_nema_vg_context_cell)) + 0x120) = 0xffffffff;
    *(undefined1 *)coords = 0;
    *(undefined1 *)((int)coords + 2) = 1;
    coords[2] = coords[1];
    fVar9 = coords[1];
    uVar7 = path[3];
    fVar15 = *(float *)(uVar7 + (int)g2c_float_to_bits(fVar9) * 4);
    if (bVar13) {
      coords[5] = fVar15;
      coords[1] = (float)g2c_bits_to_float((uint)(((int)g2c_float_to_bits(fVar9) + 1)));
      coords[6] = *(float *)(uVar7 + ((int)g2c_float_to_bits(fVar9) + 1) * 4);
    }
    else {
      coords[5] = coords[0xb] + fVar15;
      coords[1] = (float)g2c_bits_to_float((uint)(((int)g2c_float_to_bits(fVar9) + 1)));
      coords[6] = coords[0xc] + *(float *)(uVar7 + ((int)g2c_float_to_bits(fVar9) + 1) * 4);
    }
    coords[1] = (float)g2c_bits_to_float((uint)(((int)g2c_float_to_bits(fVar9) + 2)));
    coords[0xb] = coords[5];
    coords[0xc] = coords[6];
    coords[0xf] = coords[5];
    coords[0x10] = coords[6];
    goto LAB_00516b1a;
  }
  if (cmd == 0 || cmd == 0x80) {
    if (*(char *)coords == '\x01') {
      coords[5] = 0.0f;
      coords[6] = 0.0f;
    }
    else {
      coords[5] = coords[0xf];
      coords[6] = coords[0x10];
    }
    coords[0xb] = coords[5];
    uVar4 = 0;
    coords[0xc] = coords[6];
    *(undefined1 *)((int)coords + 2) = 0;
  }
  else {
    if (g2c_float_to_bits(coords[1]) == 0u) {
      *(undefined4 *)(*(((int *)&audio_uart_nema_vg_context_cell)) + 0x120) = 0xffffffff;
      *(undefined1 *)coords = 1;
    }
    fVar9 = coords[10];
    *(undefined1 *)((int)coords + 2) = 0;
    if (uVar10 == 6) {
      fVar15 = coords[1];
      uVar7 = path[3];
      fVar16 = *(float *)(uVar7 + (int)g2c_float_to_bits(fVar15) * 4);
      coords[7] = fVar16;
      fVar18 = *(float *)(uVar7 + ((int)g2c_float_to_bits(fVar15) + 1) * 4);
      coords[8] = fVar18;
      fVar20 = *(float *)(uVar7 + ((int)g2c_float_to_bits(fVar15) + 2) * 4);
      coords[9] = fVar20;
      fVar9 = *(float *)(uVar7 + ((int)g2c_float_to_bits(fVar15) + 3) * 4);
      coords[1] = (float)g2c_bits_to_float((uint)(((int)g2c_float_to_bits(fVar15) + 4)));
      if (!bVar13) {
        coords[7] = fVar16 + coords[0xb];
        coords[8] = fVar18 + coords[0xc];
        fVar20 = fVar20 + coords[0xb];
        fVar9 = fVar9 + coords[0xc];
      }
      coords[9] = fVar20;
      coords[0xd] = coords[9];
      coords[0xe] = fVar9;
    }
    else {
      if (uVar10 == 5) {
        fVar18 = coords[1];
        uVar7 = path[3];
        fVar15 = *(float *)(uVar7 + (int)g2c_float_to_bits(fVar18) * 4);
        coords[7] = fVar15;
        fVar16 = *(float *)(uVar7 + ((int)g2c_float_to_bits(fVar18) + 1) * 4);
        coords[1] = (float)g2c_bits_to_float((uint)(((int)g2c_float_to_bits(fVar18) + 2)));
        if (!bVar13) {
          fVar15 = fVar15 + coords[0xb];
          fVar16 = fVar16 + coords[0xc];
        }
      }
      else {
        if (uVar10 != 7) {
          if (uVar10 == 8) {
            if ((uVar7 == 5 || uVar7 == 7) || (uVar7 == 6 || uVar7 == 8)) {
              fVar9 = coords[0xb] * 2.0f - coords[0xd];
              fVar15 = coords[0xc] * 2.0f - coords[0xe];
            }
            else {
              fVar9 = coords[0xb];
              fVar15 = coords[0xc];
            }
            coords[7] = fVar9;
            coords[8] = fVar15;
            fVar15 = coords[1];
            uVar7 = path[3];
            fVar16 = *(float *)(uVar7 + (int)g2c_float_to_bits(fVar15) * 4);
            coords[9] = fVar16;
            fVar9 = *(float *)(uVar7 + ((int)g2c_float_to_bits(fVar15) + 1) * 4);
            coords[1] = (float)g2c_bits_to_float((uint)(((int)g2c_float_to_bits(fVar15) + 2)));
            if (!bVar13) {
              fVar16 = fVar16 + coords[0xb];
              fVar9 = fVar9 + coords[0xc];
            }
            coords[9] = fVar16;
            coords[0xd] = coords[9];
            coords[0xe] = fVar9;
          }
          else if ((cmd & 0xf) == 9) {
            fVar15 = coords[1];
            uVar7 = path[3];
            coords[7] = *(float *)(uVar7 + (int)g2c_float_to_bits(fVar15) * 4);
            coords[8] = *(float *)(uVar7 + ((int)g2c_float_to_bits(fVar15) + 1) * 4);
            fVar16 = *(float *)(uVar7 + ((int)g2c_float_to_bits(fVar15) + 2) * 4);
            coords[1] = (float)g2c_bits_to_float((uint)(((int)g2c_float_to_bits(fVar15) + 3)));
            coords[9] = fVar16;
            fVar15 = audio_uart_float_two_input_angle_50969c
                               (*(float *)(*puVar2 + 0xf8),*(float *)(*puVar2 + 0xec));
            coords[9] = fVar15 + fVar16;
            coords[0xd] = coords[0xb];
            coords[0xe] = coords[0xc];
            *(undefined1 *)((int)coords + 3) = uVar5;
          }
          goto LAB_00515a4c;
        }
        if ((uVar7 == 5 || uVar7 == 7) || (uVar7 == 6 || uVar7 == 8)) {
          fVar15 = coords[0xb] * 2.0f - coords[0xd];
          fVar16 = coords[0xc] * 2.0f - coords[0xe];
        }
        else {
          fVar15 = coords[0xb];
          fVar16 = coords[0xc];
        }
      }
      coords[7] = fVar15;
      coords[8] = fVar16;
      coords[0xd] = coords[7];
      coords[0xe] = coords[8];
    }
LAB_00515a4c:
    coords[10] = fVar9;
    if (uVar10 == 4) {
      coords[5] = coords[0xb];
      fVar15 = coords[1];
      if (bVar13) {
        coords[6] = *(float *)(path[3] + (int)g2c_float_to_bits(fVar15) * 4);
      }
      else {
        coords[6] = coords[0xc] + *(float *)(path[3] + (int)g2c_float_to_bits(fVar15) * 4);
      }
      fVar15 = (float)g2c_bits_to_float((uint)(((int)g2c_float_to_bits(fVar15) + 1)));
LAB_00515a7c:
      coords[1] = fVar15;
    }
    else {
      if (uVar10 != 3) {
        fVar9 = coords[1];
        uVar7 = path[3];
        fVar15 = *(float *)(uVar7 + (int)g2c_float_to_bits(fVar9) * 4);
        if (uVar10 == 10) {
          coords[1] = (float)g2c_bits_to_float((uint)(((int)g2c_float_to_bits(fVar9) + 1)));
          fVar9 = (0.05000000447034836f);
          iVar8 = (int)fVar15 / 2;
          if (0 < iVar8) {
            ((byte *)&fStack_94)[0] = uVar5; /* stock 0x515b22 strb.w sl,[sp,#4] (sp+4 = fStack_94: frame entry-0x98 per 0x5156b8..0x5156ca); read back as a byte at 0x515b8a ldrb [sp,#4]. Upper bytes unchanged, so this is a byte store and not CONCAT/(float) (wave17; sites matched by order) */
            puStack_90 = path;
            do {
              fVar15 = coords[1];
              uVar7 = puStack_90[3];
              fVar16 = *(float *)(uVar7 + (int)g2c_float_to_bits(fVar15) * 4);
              if (bVar13) {
                coords[5] = fVar16;
                coords[1] = (float)g2c_bits_to_float((uint)(((int)g2c_float_to_bits(fVar15) + 1)));
                coords[6] = *(float *)(uVar7 + ((int)g2c_float_to_bits(fVar15) + 1) * 4);
              }
              else {
                coords[5] = fVar16 + coords[0xb];
                coords[1] = (float)g2c_bits_to_float((uint)(((int)g2c_float_to_bits(fVar15) + 1)));
                coords[6] = *(float *)(uVar7 + ((int)g2c_float_to_bits(fVar15) + 1) * 4) + coords[0xc];
              }
              coords[1] = (float)g2c_bits_to_float((uint)(((int)g2c_float_to_bits(fVar15) + 2)));
              coords[0xb] = coords[5];
              coords[0xc] = coords[6];
              *(undefined1 *)(coords + 0x11) = ((byte *)&(fStack_94))[0];
              uVar7 = *puVar2;
              if (*(char *)(uVar7 + 0x7c) == '\0') {
                if (*(char *)(uVar7 + 0x2e4) == '\0') {
                  fVar20 = coords[3];
                  fVar15 = coords[4];
                  fVar16 = coords[5];
                  fVar18 = coords[6];
                  if (*(int *)(uVar7 + 0x110) == 0) {
                    uVar10 = 0;
                    if (*(int *)(uVar7 + 0x88) != 0) {
                      uVar10 = 0x7800000;
                    }
                    uVar10 = uVar10 & *(uint *)(uVar7 + 0x8c);
                    if (*(char *)(*(((int *)audio_uart_nema_context_cell)) + 8) == '\x01') {
                      uVar10 = uVar10 | *(uint *)(*(((int *)audio_uart_nema_context_cell)) + 0xc) & 0xc0000000;
                    }
                    puVar6 = (undefined4 *)audio_uart_nema_cl_get_space_514aec(5);
                    if (puVar6 != (undefined4 *)0x0) {
                      *puVar6 = 800;
                      puVar6[2] = 0x324;
                      puVar6[4] = 0x330;
                      uVar11 = (0xff000100u);
                      puVar6[1] = g2c_float_to_bits(fVar20);
                      puVar6[3] = g2c_float_to_bits(fVar15);
                      puVar6[5] = g2c_float_to_bits(fVar16);
                      puVar6[6] = 0x334;
                      puVar6[7] = g2c_float_to_bits(fVar18);
                      puVar6[8] = uVar11;
                      puVar6[9] = uVar10 | 10;
                    }
                  }
                  else {
                    fVar29 = fVar16 - fVar20;
                    fVar17 = fVar18 - fVar15;
                    fVar28 = fVar29 * fVar29 + fVar17 * fVar17;
                    if ((ABS(fVar28) < (1.0000000656873453e-05f))) {
                      *(float *)(uVar7 + 0x198) = fVar20;
                      *(float *)(uVar7 + 0x19c) = fVar15 + *(float *)(uVar7 + 0x130) * -0.5f;
                      *(float *)(uVar7 + 0x1a0) = fVar20;
                      *(float *)(uVar7 + 0x1a4) = fVar15 + *(float *)(uVar7 + 0x130) * 0.5f;
                      *(undefined4 *)(uVar7 + 400) = *(undefined4 *)(uVar7 + 0x198);
                      *(undefined4 *)(uVar7 + 0x194) = *(undefined4 *)(uVar7 + 0x19c);
                      uVar7 = *puVar2;
                      *(undefined4 *)(uVar7 + 0x1a8) = *(undefined4 *)(uVar7 + 0x1a0);
                      *(undefined4 *)(uVar7 + 0x1ac) = *(undefined4 *)(uVar7 + 0x1a4);
                    }
                    else {
                      fVar28 = audio_uart_float_sqrt_4397a8(fVar28);
                      fVar29 = fVar29 * (1.0f / fVar28);
                      fVar17 = fVar17 * (1.0f / fVar28);
                      fVar19 = *(float *)(uVar7 + 0x130) * 0.5f * fVar17;
                      fVar23 = fVar20 - fVar19;
                      fVar22 = *(float *)(uVar7 + 0x134) * 0.5f * fVar29;
                      fVar24 = fVar22 + fVar15;
                      uVar26 = CONCAT44(g2c_float_to_bits(fVar24),g2c_float_to_bits(fVar23));
                      *(float *)(uVar7 + 400) = fVar23;
                      *(float *)(uVar7 + 0x194) = fVar24;
                      uVar7 = *puVar2;
                      fVar25 = fVar16 - fVar19;
                      fVar21 = fVar22 + fVar18;
                      *(float *)(uVar7 + 0x198) = fVar25;
                      *(float *)(uVar7 + 0x19c) = fVar21;
                      uVar7 = *puVar2;
                      fVar16 = fVar19 + fVar16;
                      fVar18 = fVar18 - fVar22;
                      *(float *)(uVar7 + 0x1a0) = fVar16;
                      *(float *)(uVar7 + 0x1a4) = fVar18;
                      uVar7 = *puVar2;
                      fVar19 = fVar19 + fVar20;
                      fVar15 = fVar15 - fVar22;
                      uVar27 = CONCAT44(g2c_float_to_bits(fVar15),g2c_float_to_bits(fVar19));
                      *(float *)(uVar7 + 0x1a8) = fVar19;
                      *(float *)(uVar7 + 0x1ac) = fVar15;
                      uVar7 = *puVar2;
                      if (*(int *)(uVar7 + 0x110) == 0) {
                        uVar7 = audio_uart_nema_stencil_restore_5226b2(*(uint *)(uVar7 + 0x8c));
                        g2c_nema_vg_emit_verts_516b34
                                  (fVar23,fVar24,fVar25,fVar21,fVar16,fVar18,fVar19,fVar15);
                      }
                      else {
                        bVar14 = -1 < (int)((uint)*(byte *)(uVar7 + 0x7d) << 0x1b);
                        uVar7 = audio_uart_nema_stencil_save_52266e((uint)bVar14,0,(uint)bVar14,0);
                        uVar10 = *puVar2;
                        if (0.0f < *(float *)(uVar10 + 0x184)) {
                          fStack_74 = *(float *)(uVar10 + 0x164);
                          fStack_70 = *(float *)(uVar10 + 0x168);
                          fStack_7c = *(float *)(uVar10 + 0x16c);
                          fStack_78 = *(float *)(uVar10 + 0x170);
                          fStack_84 = *(float *)(uVar10 + 0x174);
                          fStack_80 = *(float *)(uVar10 + 0x178);
                          fStack_8c = *(float *)(uVar10 + 0x17c);
                          fStack_88 = *(float *)(uVar10 + 0x180);
                          g2c_nema_vg_emit_verts_516b34
                                    (fStack_74,fStack_70,fStack_7c,fStack_78,fStack_84,fStack_80,
                                     fStack_8c,fStack_88);
                          uVar10 = *puVar2;
                          if ((int)((uint)(ABS(*(float *)(uVar10 + 0x188) * fVar17 -
                                               *(float *)(uVar10 + 0x18c) * fVar29) < fVar9) << 0x1f
                                   ) < 0) {
                            uVar26 = *(undefined8 *)(uVar10 + 0x16c);
                            uVar27 = *(undefined8 *)(uVar10 + 0x174);
                            goto LAB_00515e32;
                          }
                          fStack_74 = *(float *)(uVar10 + 0x16c);
                          fStack_70 = *(float *)(uVar10 + 0x170);
                          fStack_84 = *(float *)(uVar10 + 0x174);
                          fStack_80 = *(float *)(uVar10 + 0x178);
                          fStack_8c = fVar19;
                          fStack_88 = fVar15;
                          fStack_7c = fVar23;
                          fStack_78 = fVar24;
                          uVar10 = g2c_nema_vg_stroke_join_5179d0
                                             (&fStack_74,(uint *)&fStack_7c,&fStack_84,
                                              (uint *)&fStack_8c,0);
                          if (uVar10 == 0) goto LAB_00515e32;
LAB_00516006:
                          uVar7 = *puVar2;
                          *(undefined4 *)(uVar7 + 0x114) = 0;
                          *(undefined4 *)(uVar7 + 0x118) = 0;
                          audio_uart_nema_vg_set_error_51565c(uVar10);
                          goto LAB_00516018;
                        }
LAB_00515e32:
                        uVar10 = *puVar2;
                        if ((0.0f < *(float *)(uVar10 + 0x158)) && (*(int *)(uVar10 + 0x128) == 1)) {
                          if ((int)((uint)(ABS(*(float *)(uVar10 + 0x15c) * fVar17 -
                                               *(float *)(uVar10 + 0x160) * fVar29) < fVar9) << 0x1f
                                   ) < 0) {
                            uVar26 = *(undefined8 *)(uVar10 + 0x140);
                            uVar27 = *(undefined8 *)(uVar10 + 0x148);
                          }
                          else {
                            fStack_74 = *(float *)(uVar10 + 0x140);
                            fStack_70 = *(float *)(uVar10 + 0x144);
                            fStack_7c = (float)g2c_bits_to_float((uint)(uVar26));
                            fStack_78 = (float)g2c_bits_to_float((uint)(((ulonglong)uVar26 >> 0x20)));
                            fStack_84 = *(float *)(uVar10 + 0x148);
                            fStack_80 = *(float *)(uVar10 + 0x14c);
                            fStack_8c = (float)g2c_bits_to_float((uint)(uVar27));
                            fStack_88 = (float)g2c_bits_to_float((uint)(((ulonglong)uVar27 >> 0x20)));
                            uVar10 = g2c_nema_vg_stroke_join_5179d0
                                               (&fStack_74,(uint *)&fStack_7c,&fStack_84,
                                                (uint *)&fStack_8c,0);
                            if (uVar10 != 0) goto LAB_00516006;
                          }
                        }
                        uVar10 = *puVar2;
                        *(int *)(uVar10 + 0x128) = *(int *)(uVar10 + 0x128) + 1;
                        uVar12 = (undefined4)((ulonglong)uVar26 >> 0x20);
                        uVar11 = (undefined4)((ulonglong)uVar27 >> 0x20);
                        if (*(float *)(uVar10 + 0x158) == 0.0f) {
                          *(int *)(uVar10 + 0x138) = (int)uVar26;
                          *(undefined4 *)(uVar10 + 0x13c) = uVar12;
                          uVar10 = *puVar2;
                          *(float *)(uVar10 + 0x140) = fVar25;
                          *(float *)(uVar10 + 0x144) = fVar21;
                          uVar10 = *puVar2;
                          *(float *)(uVar10 + 0x148) = fVar16;
                          *(float *)(uVar10 + 0x14c) = fVar18;
                          uVar10 = *puVar2;
                          *(int *)(uVar10 + 0x150) = (int)uVar27;
                          *(undefined4 *)(uVar10 + 0x154) = uVar11;
                          uVar10 = *puVar2;
                          *(float *)(uVar10 + 0x158) = fVar28;
                          *(float *)(uVar10 + 0x15c) = fVar29;
                          *(float *)(uVar10 + 0x160) = fVar17;
                        }
                        else {
                          *(int *)(uVar10 + 0x164) = (int)uVar26;
                          *(undefined4 *)(uVar10 + 0x168) = uVar12;
                          uVar10 = *puVar2;
                          *(float *)(uVar10 + 0x16c) = fVar25;
                          *(float *)(uVar10 + 0x170) = fVar21;
                          uVar10 = *puVar2;
                          *(float *)(uVar10 + 0x174) = fVar16;
                          *(float *)(uVar10 + 0x178) = fVar18;
                          uVar10 = *puVar2;
                          *(int *)(uVar10 + 0x17c) = (int)uVar27;
                          *(undefined4 *)(uVar10 + 0x180) = uVar11;
                          uVar10 = *puVar2;
                          *(float *)(uVar10 + 0x184) = fVar28;
                          *(float *)(uVar10 + 0x188) = fVar29;
                          *(float *)(uVar10 + 0x18c) = fVar17;
                        }
                      }
                      audio_uart_nema_stencil_restore_5226b2(uVar7);
                    }
                  }
                }
                else {
                  g2c_nema_vg_path_bounds_5639e8(coords[3],coords[4],coords[5],coords[6]);
                }
              }
              else {
                uVar11 = *(undefined4 *)(uVar7 + 0x2d4);
                uVar12 = *(undefined4 *)(uVar7 + 0x2d0);
                puVar6 = (undefined4 *)audio_uart_nema_cl_get_space_514aec(7);
                if (puVar6 != (undefined4 *)0x0) {
                  uVar7 = *(uint *)(*puVar2 + 0x8c) & 0x7800000;
                  if (*(char *)(*(((int *)audio_uart_nema_context_cell)) + 8) == '\x01') {
                    uVar7 = uVar7 | *(uint *)(*(((int *)audio_uart_nema_context_cell)) + 0xc) & 0xc0000000;
                  }
                  *puVar6 = 800;
                  fVar15 = coords[3];
                  puVar6[2] = 0x324;
                  puVar6[1] = g2c_float_to_bits(fVar15);
                  fVar15 = coords[4];
                  puVar6[4] = 0x330;
                  puVar6[3] = g2c_float_to_bits(fVar15);
                  fVar15 = coords[5];
                  puVar6[6] = 0x334;
                  puVar6[5] = g2c_float_to_bits(fVar15);
                  fVar15 = coords[6];
                  puVar6[8] = 0x140;
                  puVar6[7] = g2c_float_to_bits(fVar15);
                  puVar6[9] = uVar12;
                  puVar6[10] = 0x144;
                  puVar6[0xb] = uVar11;
                  puVar6[0xc] = (0xff000100u);
                  puVar6[0xd] = uVar7 | 4;
                }
              }
LAB_00516018:
              coords[3] = coords[5];
              coords[4] = coords[6];
              iVar8 = iVar8 + -1;
            } while (iVar8 != 0);
          }
          if ((coords[0xb] - coords[0xf] == 0.0f) && (coords[0xc] - coords[0x10] == 0.0f)) {
LAB_00516558:
            *(undefined1 *)((int)coords + 1) = 0;
            return 0;
          }
          coords[3] = coords[5];
          coords[4] = coords[6];
          coords[5] = coords[0xf];
          coords[6] = coords[0x10];
          coords[0xb] = coords[0xf];
          coords[0xc] = coords[6];
          uVar7 = *puVar2;
          if (*(char *)(uVar7 + 0x7c) != '\0') {
            uVar12 = *(undefined4 *)(uVar7 + 0x2d4);
            uVar11 = *(undefined4 *)(uVar7 + 0x2d0);
            puVar6 = (undefined4 *)audio_uart_nema_cl_get_space_514aec(7);
            if (puVar6 != (undefined4 *)0x0) {
              uVar7 = *(uint *)(*puVar2 + 0x8c) & 0x7800000;
              if (*(char *)(*(((int *)audio_uart_nema_context_cell)) + 8) == '\x01') {
                uVar7 = uVar7 | *(uint *)(*(((int *)audio_uart_nema_context_cell)) + 0xc) & 0xc0000000;
              }
              *puVar6 = 800;
              fVar9 = coords[3];
              puVar6[2] = 0x324;
              puVar6[1] = g2c_float_to_bits(fVar9);
              fVar9 = coords[4];
              puVar6[4] = 0x330;
              puVar6[3] = g2c_float_to_bits(fVar9);
              fVar9 = coords[5];
              puVar6[6] = 0x334;
              puVar6[5] = g2c_float_to_bits(fVar9);
              fVar9 = coords[6];
              puVar6[8] = 0x140;
              puVar6[7] = g2c_float_to_bits(fVar9);
              uVar3 = (0xff000100u);
              puVar6[9] = uVar11;
              puVar6[10] = 0x144;
              puVar6[0xb] = uVar12;
              puVar6[0xc] = uVar3;
              puVar6[0xd] = uVar7 | 4;
              *(undefined1 *)((int)coords + 1) = 0;
              return 0;
            }
            goto LAB_00516558;
          }
          if (*(char *)(uVar7 + 0x2e4) != '\0') {
            g2c_nema_vg_path_bounds_5639e8(coords[3],coords[4],coords[5],coords[6]);
            goto LAB_00516558;
          }
          fVar16 = coords[3];
          fVar18 = coords[4];
          fVar9 = coords[5];
          fVar15 = coords[6];
          if (*(int *)(uVar7 + 0x110) == 0) {
            uVar10 = 0;
            if (*(int *)(uVar7 + 0x88) != 0) {
              uVar10 = 0x7800000;
            }
            uVar10 = *(uint *)(uVar7 + 0x8c) & uVar10;
            if (*(char *)(*(((int *)audio_uart_nema_context_cell)) + 8) == '\x01') {
              uVar10 = *(uint *)(*(((int *)audio_uart_nema_context_cell)) + 0xc) & 0xc0000000 | uVar10;
            }
            puVar6 = (undefined4 *)audio_uart_nema_cl_get_space_514aec(5);
            if (puVar6 != (undefined4 *)0x0) {
              *puVar6 = 800;
              puVar6[2] = 0x324;
              puVar6[4] = 0x330;
              uVar11 = (0xff000100u);
              puVar6[1] = g2c_float_to_bits(fVar16);
              puVar6[3] = g2c_float_to_bits(fVar18);
              puVar6[5] = g2c_float_to_bits(fVar9);
              puVar6[6] = 0x334;
              puVar6[7] = g2c_float_to_bits(fVar15);
              puVar6[8] = uVar11;
              puVar6[9] = uVar10 | 10;
              *(undefined1 *)((int)coords + 1) = 0;
              return 0;
            }
            goto LAB_00516558;
          }
          fVar28 = fVar9 - fVar16;
          fVar29 = fVar15 - fVar18;
          fVar20 = fVar28 * fVar28 + fVar29 * fVar29;
          if ((ABS(fVar20) < (1.0000000656873453e-05f))) {
            *(float *)(uVar7 + 0x198) = fVar16;
            *(float *)(uVar7 + 0x19c) = fVar18 + *(float *)(uVar7 + 0x130) * -0.5f;
            *(float *)(uVar7 + 0x1a0) = fVar16;
            *(float *)(uVar7 + 0x1a4) = fVar18 + *(float *)(uVar7 + 0x130) * 0.5f;
            *(undefined4 *)(uVar7 + 400) = *(undefined4 *)(uVar7 + 0x198);
            *(undefined4 *)(uVar7 + 0x194) = *(undefined4 *)(uVar7 + 0x19c);
            uVar7 = *puVar2;
            *(undefined4 *)(uVar7 + 0x1a8) = *(undefined4 *)(uVar7 + 0x1a0);
            *(undefined4 *)(uVar7 + 0x1ac) = *(undefined4 *)(uVar7 + 0x1a4);
            *(undefined1 *)((int)coords + 1) = 0;
            return 0;
          }
          fVar20 = audio_uart_float_sqrt_4397a8(fVar20);
          fVar28 = fVar28 * (1.0f / fVar20);
          fVar29 = fVar29 * (1.0f / fVar20);
          fVar17 = *(float *)(uVar7 + 0x130) * 0.5f * fVar29;
          fVar22 = fVar16 - fVar17;
          fVar19 = *(float *)(uVar7 + 0x134) * 0.5f * fVar28;
          fVar23 = fVar19 + fVar18;
          uVar26 = CONCAT44(g2c_float_to_bits(fVar23),g2c_float_to_bits(fVar22));
          *(float *)(uVar7 + 400) = fVar22;
          *(float *)(uVar7 + 0x194) = fVar23;
          uVar7 = *puVar2;
          fVar24 = fVar9 - fVar17;
          fVar25 = fVar19 + fVar15;
          *(float *)(uVar7 + 0x198) = fVar24;
          *(float *)(uVar7 + 0x19c) = fVar25;
          uVar7 = *puVar2;
          fVar9 = fVar17 + fVar9;
          fVar15 = fVar15 - fVar19;
          *(float *)(uVar7 + 0x1a0) = fVar9;
          *(float *)(uVar7 + 0x1a4) = fVar15;
          uVar7 = *puVar2;
          fVar17 = fVar17 + fVar16;
          h = (uint *)g2c_float_as_ptr((fVar18)-(fVar19));
          uVar27 = CONCAT44(h,g2c_float_to_bits(fVar17));
          *(float *)(uVar7 + 0x1a8) = fVar17;
          *(uint **)(uVar7 + 0x1ac) = h;
          uVar7 = *puVar2;
          if (*(int *)(uVar7 + 0x110) == 0) {
            uVar7 = audio_uart_nema_stencil_restore_5226b2(*(uint *)(uVar7 + 0x8c));
            g2c_nema_vg_emit_verts_516b34(fVar22,fVar23,fVar24,fVar25,fVar9,fVar15,fVar17,g2c_ptr_as_float(h));
          }
          else {
            bVar13 = -1 < (int)((uint)*(byte *)(uVar7 + 0x7d) << 0x1b);
            uVar7 = audio_uart_nema_stencil_save_52266e((uint)bVar13,0,(uint)bVar13,0);
            uVar10 = *puVar2;
            if (0.0f < *(float *)(uVar10 + 0x184)) {
              fStack_7c = *(float *)(uVar10 + 0x164);
              fStack_78 = *(float *)(uVar10 + 0x168);
              fStack_84 = *(float *)(uVar10 + 0x16c);
              fStack_80 = *(float *)(uVar10 + 0x170);
              fStack_8c = *(float *)(uVar10 + 0x174);
              fStack_88 = *(float *)(uVar10 + 0x178);
              fStack_94 = *(float *)(uVar10 + 0x17c);
              puStack_90 = *(uint **)(uVar10 + 0x180);
              g2c_nema_vg_emit_verts_516b34
                        (fStack_7c,fStack_78,fStack_84,fStack_80,fStack_8c,fStack_88,fStack_94,
                         g2c_ptr_as_float(puStack_90));
              uVar10 = *puVar2;
              if ((ABS(*(float *)(uVar10 + 0x188) * fVar29 -
                                   *(float *)(uVar10 + 0x18c) * fVar28) < (0.05000000447034836f))) {
                uVar26 = *(undefined8 *)(uVar10 + 0x16c);
                uVar27 = *(undefined8 *)(uVar10 + 0x174);
              }
              else {
                fStack_7c = *(float *)(uVar10 + 0x16c);
                fStack_78 = *(float *)(uVar10 + 0x170);
                fStack_8c = *(float *)(uVar10 + 0x174);
                fStack_88 = *(float *)(uVar10 + 0x178);
                fStack_94 = fVar17;
                puStack_90 = h;
                fStack_84 = fVar22;
                fStack_80 = fVar23;
                uVar10 = g2c_nema_vg_stroke_join_5179d0
                                   (&fStack_7c,(uint *)&fStack_84,&fStack_8c,(uint *)&fStack_94,0);
                if (uVar10 != 0) goto LAB_005164da;
              }
            }
            uVar10 = *puVar2;
            if ((0.0f < *(float *)(uVar10 + 0x158)) && (*(int *)(uVar10 + 0x128) == 1)) {
              if ((ABS(*(float *)(uVar10 + 0x15c) * fVar29 -
                                   *(float *)(uVar10 + 0x160) * fVar28) < (0.05000000447034836f))) {
                uVar26 = *(undefined8 *)(uVar10 + 0x140);
                uVar27 = *(undefined8 *)(uVar10 + 0x148);
              }
              else {
                fStack_7c = *(float *)(uVar10 + 0x140);
                fStack_78 = *(float *)(uVar10 + 0x144);
                fStack_84 = (float)g2c_bits_to_float((uint)(uVar26));
                fStack_80 = (float)g2c_bits_to_float((uint)(((ulonglong)uVar26 >> 0x20)));
                fStack_8c = *(float *)(uVar10 + 0x148);
                fStack_88 = *(float *)(uVar10 + 0x14c);
                fStack_94 = (float)g2c_bits_to_float((uint)(uVar27));
                puStack_90 = (uint *)((ulonglong)uVar27 >> 0x20);
                uVar10 = g2c_nema_vg_stroke_join_5179d0
                                   (&fStack_7c,(uint *)&fStack_84,&fStack_8c,(uint *)&fStack_94,0);
                if (uVar10 != 0) {
LAB_005164da:
                  uVar7 = *puVar2;
                  *(undefined4 *)(uVar7 + 0x114) = 0;
                  *(undefined4 *)(uVar7 + 0x118) = 0;
                  audio_uart_nema_vg_set_error_51565c(uVar10);
                  *(undefined1 *)((int)coords + 1) = 0;
                  return 0;
                }
              }
            }
            uVar10 = *puVar2;
            *(int *)(uVar10 + 0x128) = *(int *)(uVar10 + 0x128) + 1;
            uVar12 = (undefined4)((ulonglong)uVar26 >> 0x20);
            uVar11 = (undefined4)((ulonglong)uVar27 >> 0x20);
            if (*(float *)(uVar10 + 0x158) == 0.0f) {
              *(int *)(uVar10 + 0x138) = (int)uVar26;
              *(undefined4 *)(uVar10 + 0x13c) = uVar12;
              uVar10 = *puVar2;
              *(float *)(uVar10 + 0x140) = fVar24;
              *(float *)(uVar10 + 0x144) = fVar25;
              uVar10 = *puVar2;
              *(float *)(uVar10 + 0x148) = fVar9;
              *(float *)(uVar10 + 0x14c) = fVar15;
              uVar10 = *puVar2;
              *(int *)(uVar10 + 0x150) = (int)uVar27;
              *(undefined4 *)(uVar10 + 0x154) = uVar11;
              uVar10 = *puVar2;
              *(float *)(uVar10 + 0x158) = fVar20;
              *(float *)(uVar10 + 0x15c) = fVar28;
              *(float *)(uVar10 + 0x160) = fVar29;
            }
            else {
              *(int *)(uVar10 + 0x164) = (int)uVar26;
              *(undefined4 *)(uVar10 + 0x168) = uVar12;
              uVar10 = *puVar2;
              *(float *)(uVar10 + 0x16c) = fVar24;
              *(float *)(uVar10 + 0x170) = fVar25;
              uVar10 = *puVar2;
              *(float *)(uVar10 + 0x174) = fVar9;
              *(float *)(uVar10 + 0x178) = fVar15;
              uVar10 = *puVar2;
              *(int *)(uVar10 + 0x17c) = (int)uVar27;
              *(undefined4 *)(uVar10 + 0x180) = uVar11;
              uVar10 = *puVar2;
              *(float *)(uVar10 + 0x184) = fVar20;
              *(float *)(uVar10 + 0x188) = fVar28;
              *(float *)(uVar10 + 0x18c) = fVar29;
            }
          }
          audio_uart_nema_stencil_restore_5226b2(uVar7);
          *(undefined1 *)((int)coords + 1) = 0;
          return 0;
        }
        if (uVar10 == 0xb) {
          coords[1] = (float)g2c_bits_to_float((uint)(((int)g2c_float_to_bits(fVar9) + 1)));
          fVar9 = (0.05000000447034836f);
          iVar8 = (int)fVar15 / 2;
          if (0 < iVar8) {
            ((byte *)&fStack_94)[0] = uVar5; /* stock 0x516588 strb.w sl,[sp,#4] (sp+4 = fStack_94: frame entry-0x98 per 0x5156b8..0x5156ca); read back as a byte at 0x5165ee ldrb [sp,#4]. Upper bytes unchanged, so this is a byte store and not CONCAT/(float) (wave17; sites matched by order) */
            puStack_90 = path;
            do {
              fVar15 = coords[1];
              uVar7 = puStack_90[3];
              fVar16 = *(float *)(uVar7 + (int)g2c_float_to_bits(fVar15) * 4);
              if (bVar13) {
                coords[5] = fVar16;
                coords[1] = (float)g2c_bits_to_float((uint)(((int)g2c_float_to_bits(fVar15) + 1)));
                coords[6] = *(float *)(uVar7 + ((int)g2c_float_to_bits(fVar15) + 1) * 4);
              }
              else {
                coords[5] = fVar16 + coords[0xb];
                coords[1] = (float)g2c_bits_to_float((uint)(((int)g2c_float_to_bits(fVar15) + 1)));
                coords[6] = *(float *)(uVar7 + ((int)g2c_float_to_bits(fVar15) + 1) * 4) + coords[0xc];
              }
              coords[1] = (float)g2c_bits_to_float((uint)(((int)g2c_float_to_bits(fVar15) + 2)));
              coords[0xb] = coords[5];
              coords[0xc] = coords[6];
              *(undefined1 *)(coords + 0x11) = ((byte *)&(fStack_94))[0];
              uVar7 = *puVar2;
              if (*(char *)(uVar7 + 0x7c) == '\0') {
                if (*(char *)(uVar7 + 0x2e4) == '\0') {
                  fVar20 = coords[3];
                  fVar15 = coords[4];
                  fVar16 = coords[5];
                  fVar18 = coords[6];
                  if (*(int *)(uVar7 + 0x110) == 0) {
                    uVar10 = 0;
                    if (*(int *)(uVar7 + 0x88) != 0) {
                      uVar10 = 0x7800000;
                    }
                    uVar10 = uVar10 & *(uint *)(uVar7 + 0x8c);
                    if (*(char *)(*(((int *)audio_uart_nema_context_cell)) + 8) == '\x01') {
                      uVar10 = uVar10 | *(uint *)(*(((int *)audio_uart_nema_context_cell)) + 0xc) & 0xc0000000;
                    }
                    puVar6 = (undefined4 *)audio_uart_nema_cl_get_space_514aec(5);
                    if (puVar6 != (undefined4 *)0x0) {
                      *puVar6 = 800;
                      puVar6[2] = 0x324;
                      puVar6[4] = 0x330;
                      uVar11 = (0xff000100u);
                      puVar6[1] = g2c_float_to_bits(fVar20);
                      puVar6[3] = g2c_float_to_bits(fVar15);
                      puVar6[5] = g2c_float_to_bits(fVar16);
                      puVar6[6] = 0x334;
                      puVar6[7] = g2c_float_to_bits(fVar18);
                      puVar6[8] = uVar11;
                      puVar6[9] = uVar10 | 10;
                    }
                  }
                  else {
                    fVar29 = fVar16 - fVar20;
                    fVar17 = fVar18 - fVar15;
                    fVar28 = fVar29 * fVar29 + fVar17 * fVar17;
                    if ((ABS(fVar28) < (1.0000000656873453e-05f))) {
                      *(float *)(uVar7 + 0x198) = fVar20;
                      *(float *)(uVar7 + 0x19c) = fVar15 + *(float *)(uVar7 + 0x130) * -0.5f;
                      *(float *)(uVar7 + 0x1a0) = fVar20;
                      *(float *)(uVar7 + 0x1a4) = fVar15 + *(float *)(uVar7 + 0x130) * 0.5f;
                      *(undefined4 *)(uVar7 + 400) = *(undefined4 *)(uVar7 + 0x198);
                      *(undefined4 *)(uVar7 + 0x194) = *(undefined4 *)(uVar7 + 0x19c);
                      uVar7 = *puVar2;
                      *(undefined4 *)(uVar7 + 0x1a8) = *(undefined4 *)(uVar7 + 0x1a0);
                      *(undefined4 *)(uVar7 + 0x1ac) = *(undefined4 *)(uVar7 + 0x1a4);
                    }
                    else {
                      fVar28 = audio_uart_float_sqrt_4397a8(fVar28);
                      fVar29 = fVar29 * (1.0f / fVar28);
                      fVar17 = fVar17 * (1.0f / fVar28);
                      fVar19 = *(float *)(uVar7 + 0x130) * 0.5f * fVar17;
                      fVar23 = fVar20 - fVar19;
                      fVar22 = *(float *)(uVar7 + 0x134) * 0.5f * fVar29;
                      fVar24 = fVar22 + fVar15;
                      uVar26 = CONCAT44(g2c_float_to_bits(fVar24),g2c_float_to_bits(fVar23));
                      *(float *)(uVar7 + 400) = fVar23;
                      *(float *)(uVar7 + 0x194) = fVar24;
                      uVar7 = *puVar2;
                      fVar25 = fVar16 - fVar19;
                      fVar21 = fVar22 + fVar18;
                      *(float *)(uVar7 + 0x198) = fVar25;
                      *(float *)(uVar7 + 0x19c) = fVar21;
                      uVar7 = *puVar2;
                      fVar16 = fVar19 + fVar16;
                      fVar18 = fVar18 - fVar22;
                      *(float *)(uVar7 + 0x1a0) = fVar16;
                      *(float *)(uVar7 + 0x1a4) = fVar18;
                      uVar7 = *puVar2;
                      fVar19 = fVar19 + fVar20;
                      fVar15 = fVar15 - fVar22;
                      uVar27 = CONCAT44(g2c_float_to_bits(fVar15),g2c_float_to_bits(fVar19));
                      *(float *)(uVar7 + 0x1a8) = fVar19;
                      *(float *)(uVar7 + 0x1ac) = fVar15;
                      uVar7 = *puVar2;
                      if (*(int *)(uVar7 + 0x110) == 0) {
                        uVar7 = audio_uart_nema_stencil_restore_5226b2(*(uint *)(uVar7 + 0x8c));
                        g2c_nema_vg_emit_verts_516b34
                                  (fVar23,fVar24,fVar25,fVar21,fVar16,fVar18,fVar19,fVar15);
                      }
                      else {
                        bVar14 = -1 < (int)((uint)*(byte *)(uVar7 + 0x7d) << 0x1b);
                        uVar7 = audio_uart_nema_stencil_save_52266e((uint)bVar14,0,(uint)bVar14,0);
                        uVar10 = *puVar2;
                        if (0.0f < *(float *)(uVar10 + 0x184)) {
                          fStack_74 = *(float *)(uVar10 + 0x164);
                          fStack_70 = *(float *)(uVar10 + 0x168);
                          fStack_7c = *(float *)(uVar10 + 0x16c);
                          fStack_78 = *(float *)(uVar10 + 0x170);
                          fStack_84 = *(float *)(uVar10 + 0x174);
                          fStack_80 = *(float *)(uVar10 + 0x178);
                          fStack_8c = *(float *)(uVar10 + 0x17c);
                          fStack_88 = *(float *)(uVar10 + 0x180);
                          g2c_nema_vg_emit_verts_516b34
                                    (fStack_74,fStack_70,fStack_7c,fStack_78,fStack_84,fStack_80,
                                     fStack_8c,fStack_88);
                          uVar10 = *puVar2;
                          if ((int)((uint)(ABS(*(float *)(uVar10 + 0x188) * fVar17 -
                                               *(float *)(uVar10 + 0x18c) * fVar29) < fVar9) << 0x1f
                                   ) < 0) {
                            uVar26 = *(undefined8 *)(uVar10 + 0x16c);
                            uVar27 = *(undefined8 *)(uVar10 + 0x174);
                            goto LAB_00516896;
                          }
                          fStack_74 = *(float *)(uVar10 + 0x16c);
                          fStack_70 = *(float *)(uVar10 + 0x170);
                          fStack_84 = *(float *)(uVar10 + 0x174);
                          fStack_80 = *(float *)(uVar10 + 0x178);
                          fStack_8c = fVar19;
                          fStack_88 = fVar15;
                          fStack_7c = fVar23;
                          fStack_78 = fVar24;
                          uVar10 = g2c_nema_vg_stroke_join_5179d0
                                             (&fStack_74,(uint *)&fStack_7c,&fStack_84,
                                              (uint *)&fStack_8c,0);
                          if (uVar10 == 0) goto LAB_00516896;
LAB_00516a6a:
                          uVar7 = *puVar2;
                          *(undefined4 *)(uVar7 + 0x114) = 0;
                          *(undefined4 *)(uVar7 + 0x118) = 0;
                          audio_uart_nema_vg_set_error_51565c(uVar10);
                          goto LAB_00516a7c;
                        }
LAB_00516896:
                        uVar10 = *puVar2;
                        if ((0.0f < *(float *)(uVar10 + 0x158)) && (*(int *)(uVar10 + 0x128) == 1)) {
                          if ((int)((uint)(ABS(*(float *)(uVar10 + 0x15c) * fVar17 -
                                               *(float *)(uVar10 + 0x160) * fVar29) < fVar9) << 0x1f
                                   ) < 0) {
                            uVar26 = *(undefined8 *)(uVar10 + 0x140);
                            uVar27 = *(undefined8 *)(uVar10 + 0x148);
                          }
                          else {
                            fStack_74 = *(float *)(uVar10 + 0x140);
                            fStack_70 = *(float *)(uVar10 + 0x144);
                            fStack_7c = (float)g2c_bits_to_float((uint)(uVar26));
                            fStack_78 = (float)g2c_bits_to_float((uint)(((ulonglong)uVar26 >> 0x20)));
                            fStack_84 = *(float *)(uVar10 + 0x148);
                            fStack_80 = *(float *)(uVar10 + 0x14c);
                            fStack_8c = (float)g2c_bits_to_float((uint)(uVar27));
                            fStack_88 = (float)g2c_bits_to_float((uint)(((ulonglong)uVar27 >> 0x20)));
                            uVar10 = g2c_nema_vg_stroke_join_5179d0
                                               (&fStack_74,(uint *)&fStack_7c,&fStack_84,
                                                (uint *)&fStack_8c,0);
                            if (uVar10 != 0) goto LAB_00516a6a;
                          }
                        }
                        uVar10 = *puVar2;
                        *(int *)(uVar10 + 0x128) = *(int *)(uVar10 + 0x128) + 1;
                        uVar12 = (undefined4)((ulonglong)uVar26 >> 0x20);
                        uVar11 = (undefined4)((ulonglong)uVar27 >> 0x20);
                        if (*(float *)(uVar10 + 0x158) == 0.0f) {
                          *(int *)(uVar10 + 0x138) = (int)uVar26;
                          *(undefined4 *)(uVar10 + 0x13c) = uVar12;
                          uVar10 = *puVar2;
                          *(float *)(uVar10 + 0x140) = fVar25;
                          *(float *)(uVar10 + 0x144) = fVar21;
                          uVar10 = *puVar2;
                          *(float *)(uVar10 + 0x148) = fVar16;
                          *(float *)(uVar10 + 0x14c) = fVar18;
                          uVar10 = *puVar2;
                          *(int *)(uVar10 + 0x150) = (int)uVar27;
                          *(undefined4 *)(uVar10 + 0x154) = uVar11;
                          uVar10 = *puVar2;
                          *(float *)(uVar10 + 0x158) = fVar28;
                          *(float *)(uVar10 + 0x15c) = fVar29;
                          *(float *)(uVar10 + 0x160) = fVar17;
                        }
                        else {
                          *(int *)(uVar10 + 0x164) = (int)uVar26;
                          *(undefined4 *)(uVar10 + 0x168) = uVar12;
                          uVar10 = *puVar2;
                          *(float *)(uVar10 + 0x16c) = fVar25;
                          *(float *)(uVar10 + 0x170) = fVar21;
                          uVar10 = *puVar2;
                          *(float *)(uVar10 + 0x174) = fVar16;
                          *(float *)(uVar10 + 0x178) = fVar18;
                          uVar10 = *puVar2;
                          *(int *)(uVar10 + 0x17c) = (int)uVar27;
                          *(undefined4 *)(uVar10 + 0x180) = uVar11;
                          uVar10 = *puVar2;
                          *(float *)(uVar10 + 0x184) = fVar28;
                          *(float *)(uVar10 + 0x188) = fVar29;
                          *(float *)(uVar10 + 0x18c) = fVar17;
                        }
                      }
                      audio_uart_nema_stencil_restore_5226b2(uVar7);
                    }
                  }
                }
                else {
                  g2c_nema_vg_path_bounds_5639e8(coords[3],coords[4],coords[5],coords[6]);
                }
              }
              else {
                uVar11 = *(undefined4 *)(uVar7 + 0x2d4);
                uVar12 = *(undefined4 *)(uVar7 + 0x2d0);
                puVar6 = (undefined4 *)audio_uart_nema_cl_get_space_514aec(7);
                if (puVar6 != (undefined4 *)0x0) {
                  uVar7 = *(uint *)(*puVar2 + 0x8c) & 0x7800000;
                  if (*(char *)(*(((int *)audio_uart_nema_context_cell)) + 8) == '\x01') {
                    uVar7 = uVar7 | *(uint *)(*(((int *)audio_uart_nema_context_cell)) + 0xc) & 0xc0000000;
                  }
                  *puVar6 = 800;
                  fVar15 = coords[3];
                  puVar6[2] = 0x324;
                  puVar6[1] = g2c_float_to_bits(fVar15);
                  fVar15 = coords[4];
                  puVar6[4] = 0x330;
                  puVar6[3] = g2c_float_to_bits(fVar15);
                  fVar15 = coords[5];
                  puVar6[6] = 0x334;
                  puVar6[5] = g2c_float_to_bits(fVar15);
                  fVar15 = coords[6];
                  puVar6[8] = 0x140;
                  puVar6[7] = g2c_float_to_bits(fVar15);
                  puVar6[9] = uVar12;
                  puVar6[10] = 0x144;
                  puVar6[0xb] = uVar11;
                  puVar6[0xc] = (0xff000100u);
                  puVar6[0xd] = uVar7 | 4;
                }
              }
LAB_00516a7c:
              coords[3] = coords[5];
              coords[4] = coords[6];
              iVar8 = iVar8 + -1;
            } while (iVar8 != 0);
          }
          if (((*(char *)(*puVar2 + 0x7c) == '\0') || (coords[0xb] - coords[0xf] != 0.0f)) ||
             (coords[0xc] - coords[0x10] != 0.0f)) {
            uVar5 = 1;
          }
          else {
            uVar5 = 0;
          }
          *(undefined1 *)((int)coords + 1) = uVar5;
          return 0;
        }
        if (bVar13) {
          coords[5] = fVar15;
          coords[1] = (float)g2c_bits_to_float((uint)(((int)g2c_float_to_bits(fVar9) + 1)));
          fVar15 = (float)g2c_bits_to_float((uint)(((int)g2c_float_to_bits(fVar9) + 2)));
          coords[6] = *(float *)(uVar7 + ((int)g2c_float_to_bits(fVar9) + 1) * 4);
        }
        else {
          coords[5] = fVar15 + coords[0xb];
          coords[1] = (float)g2c_bits_to_float((uint)(((int)g2c_float_to_bits(fVar9) + 1)));
          coords[6] = *(float *)(uVar7 + ((int)g2c_float_to_bits(fVar9) + 1) * 4) + coords[0xc];
          fVar15 = (float)g2c_bits_to_float((uint)(((int)g2c_float_to_bits(fVar9) + 2)));
        }
        goto LAB_00515a7c;
      }
      fVar9 = *(float *)(path[3] + (int)g2c_float_to_bits(coords[1]) * 4);
      if (!bVar13) {
        fVar9 = coords[0xb] + fVar9;
      }
      coords[5] = fVar9;
      coords[1] = (float)g2c_bits_to_float((uint)(((int)g2c_float_to_bits(coords[1]) + 1)));
      coords[6] = coords[0xc];
    }
    if (((*(char *)(*puVar2 + 0x7c) == '\0') || (coords[5] - coords[0xf] != 0.0f)) ||
       (coords[6] - coords[0x10] != 0.0f)) {
      uVar4 = 1;
    }
    else {
      uVar4 = 0;
    }
  }
  *(undefined1 *)((int)coords + 1) = uVar4;
LAB_00516b1a:
  coords[0xb] = coords[5];
  coords[0xc] = coords[6];
  *(undefined1 *)(coords + 0x11) = uVar5;
  return 0;
}
#undef fStack_94
#undef puStack_90
#undef fStack_8c
#undef fStack_88
#undef fStack_84
#undef fStack_80
#undef fStack_7c
#undef fStack_78
#undef fStack_74
#undef fStack_70


  

/* ---- lifted 0x516b34 ---- */

uint g2c_nema_vg_emit_verts_516b34(float a,float b,float c,float d,float e,float f,float g,float h)

{
  undefined4 uVar1;
  undefined4 *puVar2;
  
  puVar2 = (undefined4 *)audio_uart_nema_cl_get_space_514aec(9);
  if (puVar2 == (undefined4 *)0x0) {
    return 0x200;
  }
  *puVar2 = 800;
  puVar2[2] = 0x324;
  puVar2[4] = 0x330;
  puVar2[6] = 0x334;
  puVar2[8] = 0x340;
  puVar2[10] = 0x344;
  puVar2[0xc] = 0x350;
  puVar2[0xe] = 0x354;
  uVar1 = (0xff000100u);
  /* Stock 0x516b34 stores the float registers s16..s23 raw (vstr), not converted integers. */
  puVar2[1] = g2c_float_to_bits(a);
  puVar2[3] = g2c_float_to_bits(b);
  puVar2[5] = g2c_float_to_bits(c);
  puVar2[7] = g2c_float_to_bits(d);
  puVar2[9] = g2c_float_to_bits(e);
  puVar2[0xb] = g2c_float_to_bits(f);
  puVar2[0xd] = g2c_float_to_bits(g);
  puVar2[0xf] = g2c_float_to_bits(h);
  puVar2[0x10] = uVar1;
  puVar2[0x11] = *(uint *)(*(((int *)audio_uart_nema_context_cell)) + 0x18) | 5;
  return 0;
}

  

/* ---- lifted 0x516bde ---- */

uint g2c_nema_vg_emit_tri_516bde(float a,float b,float c,float d,int e,int f)

{
  undefined4 uVar1;
  undefined4 *puVar2;
  uint uVar3;
  uint uVar4;
  
  uVar3 = 0xb;
  if (e != 0) {
    uVar3 = 10;
  }
  uVar4 = 0;
  if (f != 0) {
    if ((*(int *)(*(((int *)&audio_uart_nema_vg_context_cell)) + 0x114) == 0) || (e != 0)) {
      uVar4 = 0x7800000;
    }
    else {
      uVar4 = 0x4000000;
    }
  }
  uVar4 = uVar4 & *(uint *)(*(((int *)&audio_uart_nema_vg_context_cell)) + 0x8c);
  if (*(char *)(*(((int *)audio_uart_nema_context_cell)) + 8) == '\x01') {
    uVar4 = uVar4 | *(uint *)(*(((int *)audio_uart_nema_context_cell)) + 0xc) & 0xc0000000;
  }
  puVar2 = (undefined4 *)audio_uart_nema_cl_get_space_514aec(5);
  if (puVar2 == (undefined4 *)0x0) {
    return 0x200;
  }
  *puVar2 = 800;
  puVar2[2] = 0x324;
  puVar2[4] = 0x330;
  uVar1 = (0xff000100u);
  /* Stock 0x516bde stores the float args raw (vstr), not converted integers. */
  puVar2[1] = g2c_float_to_bits(a);
  puVar2[3] = g2c_float_to_bits(b);
  puVar2[5] = g2c_float_to_bits(c);
  puVar2[6] = 0x334;
  puVar2[7] = g2c_float_to_bits(d);
  puVar2[8] = uVar1;
  puVar2[9] = uVar3 | uVar4;
  return 0;
}

  

/* ---- lifted 0x516c82 ---- */

void g2c_nema_vg_paint_setup_516c82(uint *paint)

{
  int *piVar1;
  undefined4 *puVar2;
  uint uVar3;
  
  piVar1 = (((int *)&audio_uart_nema_vg_context_cell));
  *(undefined1 *)(*(((int *)&audio_uart_nema_vg_context_cell)) + 0x1bd) = *(undefined1 *)(*(((int *)&audio_uart_nema_vg_context_cell)) + 0x1bc);
  if (*(char *)(*piVar1 + 0x1bc) != '\0') {
    puVar2 = (undefined4 *)audio_uart_nema_cl_get_space_514aec(7);
    if (puVar2 != (undefined4 *)0x0) {
      *puVar2 = 0x374;
      uVar3 = paint[5];
      puVar2[2] = 0x368;
      puVar2[1] = uVar3;
      uVar3 = paint[2];
      puVar2[4] = 0x360;
      puVar2[3] = uVar3;
      uVar3 = *paint;
      puVar2[6] = 0x364;
      puVar2[5] = uVar3;
      uVar3 = paint[1];
      puVar2[8] = 0x36c;
      puVar2[7] = uVar3;
      uVar3 = paint[3];
      puVar2[10] = 0x370;
      puVar2[9] = uVar3;
      puVar2[0xb] = paint[4];
      puVar2[0xc] = 0x388;
      puVar2[0xd] = 0;
    }
    *(undefined1 *)(*piVar1 + 0x1bc) = 0;
  }
  return;
}

  

/* ---- lifted 0x516cf8 ---- */

uint g2c_nema_vg_tess_516cf8(int a)

{
  bool bVar1;
  undefined4 *puVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  
  iVar3 = *(((int *)&audio_uart_nema_vg_context_cell));
  bVar1 = false;
  if (*(char *)(iVar3 + 0x7c) == '\0') {
    if (*(int *)(iVar3 + 0x110) == 1) {
      g2c_nema_vg_stroke_path_517e18
                (*(float *)(a + 0xc),*(float *)(a + 0x10),*(float *)(a + 0x1c),*(float *)(a + 0x20),
                 *(float *)(a + 0x24),*(float *)(a + 0x28),*(float *)(a + 0x14),*(float *)(a + 0x18)
                );
      return 0;
    }
    bVar1 = true;
  }
  if (*(char *)(iVar3 + 0x2e4) != '\0') {
    g2c_nema_vg_stroke_path_517e18
              (*(float *)(a + 0xc),*(float *)(a + 0x10),*(float *)(a + 0x1c),*(float *)(a + 0x20),
               *(float *)(a + 0x24),*(float *)(a + 0x28),*(float *)(a + 0x14),*(float *)(a + 0x18));
    return 0;
  }
  uVar5 = 7;
  if (bVar1) {
    uVar5 = 9;
  }
  uVar6 = 0;
  if (*(int *)(iVar3 + 0x88) != 0) {
    if ((*(int *)(iVar3 + 0x114) == 0) || (bVar1)) {
      uVar6 = 0x7800000;
    }
    else {
      uVar6 = 0x4000000;
    }
  }
  uVar6 = uVar6 & *(uint *)(iVar3 + 0x8c);
  if (*(char *)(*(((int *)audio_uart_nema_context_cell)) + 8) == '\x01') {
    uVar6 = uVar6 | *(uint *)(*(((int *)audio_uart_nema_context_cell)) + 0xc) & 0xc0000000;
  }
  puVar2 = (undefined4 *)audio_uart_nema_cl_get_space_514aec(9);
  if (puVar2 != (undefined4 *)0x0) {
    *puVar2 = 800;
    uVar4 = *(undefined4 *)(a + 0xc);
    puVar2[2] = 0x324;
    puVar2[1] = uVar4;
    uVar4 = *(undefined4 *)(a + 0x10);
    puVar2[4] = 0x330;
    puVar2[3] = uVar4;
    uVar4 = *(undefined4 *)(a + 0x1c);
    puVar2[6] = 0x334;
    puVar2[5] = uVar4;
    uVar4 = *(undefined4 *)(a + 0x20);
    puVar2[8] = 0x340;
    puVar2[7] = uVar4;
    uVar4 = *(undefined4 *)(a + 0x24);
    puVar2[10] = 0x344;
    puVar2[9] = uVar4;
    uVar4 = *(undefined4 *)(a + 0x28);
    puVar2[0xc] = 0x350;
    puVar2[0xb] = uVar4;
    uVar4 = *(undefined4 *)(a + 0x14);
    puVar2[0xe] = 0x354;
    puVar2[0xd] = uVar4;
    uVar4 = (0xff000100u);
    puVar2[0xf] = *(undefined4 *)(a + 0x18);
    puVar2[0x10] = uVar4;
    puVar2[0x11] = uVar5 | uVar6;
  }
  return 0;
}

  

/* ---- lifted 0x516e0c ---- */

uint g2c_nema_vg_tess_fill_516e0c(uint *a)

{
  undefined4 uVar1;
  int *piVar2;
  int iVar3;
  undefined4 *puVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  uint uVar8;
  uint uVar9;
  undefined4 uVar10;
  undefined4 uVar11;
  uint cmd;
  int iVar12;
  int iVar13;
  undefined8 uVar14;
  undefined4 uStack_7c;
  undefined4 uStack_70;
  undefined4 uStack_6c;
  undefined4 uStack_68;
  undefined4 uStack_64;
  undefined4 uStack_60;
  undefined4 uStack_5c;
  undefined4 uStack_58;
  undefined4 uStack_54;
  undefined8 uStack_40;
  
  piVar2 = (((int *)&audio_uart_nema_vg_context_cell));
  iVar3 = *(((int *)&audio_uart_nema_vg_context_cell));
  iVar13 = (int)(((float)g2c_bits_to_float((uint)(a[0x10])) + (float)g2c_bits_to_float((uint)(a[0x12]))) * 0.5f);
  iVar12 = (int)(((float)g2c_bits_to_float((uint)(a[0x11])) + (float)g2c_bits_to_float((uint)(a[0x13]))) * 0.5f);
  iVar7 = iVar13 << 0x10;
  iVar6 = iVar12 << 0x10;
  *(int *)(iVar3 + 0x2c8) = iVar13;
  *(int *)(iVar3 + 0x2cc) = iVar12;
  *(int *)(iVar3 + 0x2d0) = iVar7;
  *(int *)(iVar3 + 0x2d4) = iVar6;
  puVar4 = (undefined4 *)audio_uart_nema_cl_get_space_514aec(2);
  if (puVar4 != (undefined4 *)0x0) {
    *puVar4 = 0x10c;
    puVar4[1] = iVar7;
    puVar4[2] = 0x128;
    puVar4[3] = iVar6;
  }
  audio_uart_lv_memzero_48949c((uint)&uStack_7c,0x48);
  uVar1 = (0xff000100u);
  ((byte *)&(uStack_7c))[0] = '\x01';
  ((byte *)&(uStack_7c))[1] = '\x01';
  ((byte *)&(uStack_7c))[2] = '\x01';
  uVar9 = 0;
LAB_00516f82:
  while( true ) {
    do {
      if (*a <= uVar9) {
        if (((byte *)&(uStack_7c))[1] == '\x01') {
          uVar14 = CONCAT44((0x0u),(0x0u));
          if ((char)uStack_7c == '\0') {
            uVar14 = uStack_40;
          }
          uVar10 = *(undefined4 *)(*piVar2 + 0x2d4);
          uVar11 = *(undefined4 *)(*piVar2 + 0x2d0);
          puVar4 = (undefined4 *)audio_uart_nema_cl_get_space_514aec(7);
          if (puVar4 != (undefined4 *)0x0) {
            uVar9 = *(uint *)(*piVar2 + 0x8c) & 0x7800000;
            if (*(char *)(*(((int *)audio_uart_nema_context_cell)) + 8) == '\x01') {
              uVar9 = uVar9 | *(uint *)(*(((int *)audio_uart_nema_context_cell)) + 0xc) & 0xc0000000;
            }
            *puVar4 = 800;
            puVar4[2] = 0x324;
            puVar4[1] = uStack_68;
            puVar4[3] = uStack_64;
            puVar4[4] = 0x330;
            puVar4[5] = (int)uVar14;
            puVar4[6] = 0x334;
            puVar4[7] = (int)((ulonglong)uVar14 >> 0x20);
            puVar4[8] = 0x140;
            puVar4[9] = uVar11;
            puVar4[10] = 0x144;
            puVar4[0xb] = uVar10;
            puVar4[0xc] = uVar1;
            puVar4[0xd] = uVar9 | 4;
          }
        }
        return 0;
      }
      cmd = (uint)*(byte *)(a[2] + uVar9);
      uVar9 = uVar9 + 1;
      uVar5 = g2c_nema_vg_path_cmd_5156b8(a,cmd,(float *)&uStack_7c);
      uVar11 = uStack_6c;
      uVar10 = uStack_70;
      uVar8 = cmd & 0x6f;
      if (uVar5 != 0) goto LAB_00517130;
    } while (((byte *)&(uStack_7c))[2] != '\0');
    if (uVar8 != 6 && uVar8 != 8) break;
    iVar3 = *piVar2;
    uVar10 = *(undefined4 *)(iVar3 + 0x2d4);
    uVar11 = *(undefined4 *)(iVar3 + 0x2d0);
    if (*(int *)(iVar3 + 0x88) == 0) {
      uVar5 = 0;
    }
    else {
      uVar5 = 0x7800000;
    }
    if (*(char *)(*(((int *)audio_uart_nema_context_cell)) + 8) == '\x01') {
      uVar5 = uVar5 | *(uint *)(*(((int *)audio_uart_nema_context_cell)) + 0xc) & 0xc0000000;
    }
    puVar4 = (undefined4 *)audio_uart_nema_cl_get_space_514aec(0x10);
    if (puVar4 != (undefined4 *)0x0) {
      *puVar4 = 0x328;
      puVar4[2] = 0x32c;
      puVar4[1] = uStack_70;
      puVar4[4] = 800;
      puVar4[3] = uStack_6c;
      puVar4[6] = 0x324;
      puVar4[5] = uStack_70;
      puVar4[8] = 0x330;
      puVar4[7] = uStack_6c;
      puVar4[10] = 0x334;
      puVar4[9] = uStack_68;
      puVar4[0xc] = 0x140;
      puVar4[0xd] = uVar11;
      puVar4[0xb] = uStack_64;
      puVar4[0xe] = 0x144;
      puVar4[0xf] = uVar10;
      puVar4[0x10] = uVar1;
      puVar4[0x11] = uVar5 | 4;
      puVar4[0x12] = 0x330;
      puVar4[0x14] = 0x334;
      puVar4[0x13] = uStack_60;
      puVar4[0x16] = 0x340;
      puVar4[0x15] = uStack_5c;
      puVar4[0x18] = 0x344;
      puVar4[0x17] = uStack_58;
      puVar4[0x1a] = 0x350;
      puVar4[0x19] = uStack_54;
      puVar4[0x1c] = 0x354;
      puVar4[0x1b] = uStack_68;
      puVar4[0x1e] = uVar1;
      puVar4[0x1d] = uStack_64;
      puVar4[0x1f] = uVar5 | 7;
    }
  }
  if (uVar8 != 2) {
    if ((uVar8 == 5) || (uVar8 == 7)) {
      iVar3 = *piVar2;
      uVar10 = *(undefined4 *)(iVar3 + 0x2d4);
      uVar11 = *(undefined4 *)(iVar3 + 0x2d0);
      if (*(int *)(iVar3 + 0x88) == 0) {
        uVar5 = 0;
      }
      else {
        uVar5 = 0x7800000;
      }
      if (*(char *)(*(((int *)audio_uart_nema_context_cell)) + 8) == '\x01') {
        uVar5 = uVar5 | *(uint *)(*(((int *)audio_uart_nema_context_cell)) + 0xc) & 0xc0000000;
      }
      puVar4 = (undefined4 *)audio_uart_nema_cl_get_space_514aec(0xe);
      if (puVar4 != (undefined4 *)0x0) {
        *puVar4 = 0x328;
        puVar4[2] = 0x32c;
        puVar4[1] = uStack_70;
        puVar4[4] = 800;
        puVar4[3] = uStack_6c;
        puVar4[6] = 0x324;
        puVar4[5] = uStack_70;
        puVar4[8] = 0x330;
        puVar4[7] = uStack_6c;
        puVar4[10] = 0x334;
        puVar4[9] = uStack_68;
        puVar4[0xc] = 0x140;
        puVar4[0xd] = uVar11;
        puVar4[0xb] = uStack_64;
        puVar4[0xe] = 0x144;
        puVar4[0xf] = uVar10;
        puVar4[0x10] = uVar1;
        puVar4[0x11] = uVar5 | 4;
        puVar4[0x12] = 0x330;
        puVar4[0x14] = 0x334;
        puVar4[0x13] = uStack_60;
        puVar4[0x16] = 0x340;
        puVar4[0x15] = uStack_5c;
        puVar4[0x18] = 0x344;
        puVar4[0x17] = uStack_68;
        puVar4[0x1a] = uVar1;
        puVar4[0x19] = uStack_64;
        puVar4[0x1b] = uVar5 | 6;
      }
      goto LAB_00516f82;
    }
    if ((cmd & 0xf) == 9) {
      puVar4 = (undefined4 *)audio_uart_nema_cl_get_space_514aec(2);
      if (puVar4 != (undefined4 *)0x0) {
        *puVar4 = 0x328;
        puVar4[1] = uVar10;
        puVar4[2] = 0x32c;
        puVar4[3] = uVar11;
      }
      uVar5 = g2c_nema_vg_arc_to_51a8ec((uint)a,(int)&uStack_7c);
      if (uVar5 != 0) {
LAB_00517130:
        iVar3 = *piVar2;
        *(undefined4 *)(iVar3 + 0x114) = 0;
        *(undefined4 *)(iVar3 + 0x118) = 0;
        audio_uart_nema_vg_set_error_51565c(uVar5);
        return uVar5;
      }
    }
    else if (uVar8 == 10 || uVar8 == 0xb) goto LAB_00516f82;
  }
  uVar10 = *(undefined4 *)(*piVar2 + 0x2d4);
  uVar11 = *(undefined4 *)(*piVar2 + 0x2d0);
  puVar4 = (undefined4 *)audio_uart_nema_cl_get_space_514aec(7);
  if (puVar4 != (undefined4 *)0x0) {
    uVar5 = *(uint *)(*piVar2 + 0x8c) & 0x7800000;
    if (*(char *)(*(((int *)audio_uart_nema_context_cell)) + 8) == '\x01') {
      uVar5 = *(uint *)(*(((int *)audio_uart_nema_context_cell)) + 0xc) & 0xc0000000 | uVar5;
    }
    *puVar4 = 800;
    puVar4[2] = 0x324;
    puVar4[1] = uStack_70;
    puVar4[4] = 0x330;
    puVar4[3] = uStack_6c;
    puVar4[6] = 0x334;
    puVar4[5] = uStack_68;
    puVar4[8] = 0x140;
    puVar4[9] = uVar11;
    puVar4[7] = uStack_64;
    puVar4[10] = 0x144;
    puVar4[0xb] = uVar10;
    puVar4[0xc] = uVar1;
    puVar4[0xd] = uVar5 | 4;
  }
  goto LAB_00516f82;
}

  

/* ---- lifted 0x5171f8 ---- */


uint g2c_nema_vg_tess_stroke_5171f8(uint *a)

{
  float fVar1;
  int *piVar2;
  float fVar3;
  uint uVar4;
  int iVar5;
  undefined4 *puVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  bool bVar10;
  float fVar11;
  float fVar12;
  float fVar13;
  float fVar14;
  float a_00;
  float b;
  float c;
  float d;
  float fVar15;
  float fVar16;
  undefined8 uVar17;
  undefined4 uVar18;
  undefined8 uVar19;
  undefined4 uVar20;
  float fVar21;
  float fVar22;
  /* Stock frame of 0x5171f8 as one block: locals keep the entry-SP offsets Ghidra named them by
   * (X_Stack_NN at g2c_frame_5171f8[0xd8-0xNN]) so &local passed to callees spans its stock neighbours. */
  unsigned char g2c_frame_5171f8[0xd8] __attribute__((aligned(8)));
  typedef float __attribute__((may_alias)) g2c_fa_float;
#define fStack_d4 (*(g2c_fa_float *)(void *)&g2c_frame_5171f8[0xd8-0xd4])
#define fStack_d0 (*(g2c_fa_float *)(void *)&g2c_frame_5171f8[0xd8-0xd0])
#define fStack_cc (*(g2c_fa_float *)(void *)&g2c_frame_5171f8[0xd8-0xcc])
#define fStack_c8 (*(g2c_fa_float *)(void *)&g2c_frame_5171f8[0xd8-0xc8])
#define fStack_c4 (*(g2c_fa_float *)(void *)&g2c_frame_5171f8[0xd8-0xc4])
#define fStack_c0 (*(g2c_fa_float *)(void *)&g2c_frame_5171f8[0xd8-0xc0])
#define fStack_bc (*(g2c_fa_float *)(void *)&g2c_frame_5171f8[0xd8-0xbc])
#define fStack_b8 (*(g2c_fa_float *)(void *)&g2c_frame_5171f8[0xd8-0xb8])
  typedef undefined1 __attribute__((may_alias)) g2c_fa_undefined1;
#define auStack_b4 (((g2c_fa_undefined1 *)(void *)&g2c_frame_5171f8[0xd8-0xb4]))
  typedef char __attribute__((may_alias)) g2c_fa_char;
#define cStack_b2 (*(g2c_fa_char *)(void *)&g2c_frame_5171f8[0xd8-0xb2])
#define fStack_a8 (*(g2c_fa_float *)(void *)&g2c_frame_5171f8[0xd8-0xa8])
#define fStack_a4 (*(g2c_fa_float *)(void *)&g2c_frame_5171f8[0xd8-0xa4])
#define fStack_a0 (*(g2c_fa_float *)(void *)&g2c_frame_5171f8[0xd8-0xa0])
#define fStack_9c (*(g2c_fa_float *)(void *)&g2c_frame_5171f8[0xd8-0x9c])
#define fStack_98 (*(g2c_fa_float *)(void *)&g2c_frame_5171f8[0xd8-0x98])
#define fStack_94 (*(g2c_fa_float *)(void *)&g2c_frame_5171f8[0xd8-0x94])
  
  audio_uart_lv_memzero_48949c((uint)auStack_b4,0x48);
  piVar2 = (((int *)&audio_uart_nema_vg_context_cell));
  fVar1 = (0.05000000447034836f);
  auStack_b4[0] = 1;
  cStack_b2 = '\x01';
  uVar9 = 0;
LAB_0051726c:
  do {
    do {
      if (*a <= uVar9) {
        return 0;
      }
      uVar7 = (uint)*(byte *)(a[2] + uVar9);
      uVar9 = uVar9 + 1;
      uVar4 = g2c_nema_vg_path_cmd_5156b8(a,uVar7,(float *)auStack_b4);
      fVar21 = fStack_94;
      fVar11 = fStack_98;
      fVar16 = fStack_9c;
      fVar15 = fStack_a0;
      fVar13 = fStack_a4;
      fVar3 = fStack_a8;
      uVar8 = uVar7 & 0x6f;
      if (uVar4 != 0) goto LAB_00517294;
    } while ((cStack_b2 != '\0') || ((int)(uVar7 << 0x18) < 0));
    if (uVar8 == 5 || uVar8 == 7) {
      iVar5 = *piVar2;
      bVar10 = false;
      if (*(char *)(iVar5 + 0x7c) == '\0') {
        if (*(int *)(iVar5 + 0x110) == 1) {
          g2c_nema_vg_fill_path_519290(fStack_a8,fStack_a4,fStack_98,fStack_94,fStack_a0,fStack_9c);
          goto LAB_0051726c;
        }
        bVar10 = true;
      }
      uVar4 = 6;
      if (bVar10) {
        uVar4 = 8;
      }
      uVar7 = 0;
      if (*(int *)(iVar5 + 0x88) != 0) {
        if ((*(int *)(iVar5 + 0x114) == 0) || (bVar10)) {
          uVar7 = 0x7800000;
        }
        else {
          uVar7 = 0x4000000;
        }
      }
      uVar7 = uVar7 & *(uint *)(iVar5 + 0x8c);
      if (*(char *)(*(((int *)audio_uart_nema_context_cell)) + 8) == '\x01') {
        uVar7 = uVar7 | *(uint *)(*(((int *)audio_uart_nema_context_cell)) + 0xc) & 0xc0000000;
      }
      puVar6 = (undefined4 *)audio_uart_nema_cl_get_space_514aec(7);
      if (puVar6 != (undefined4 *)0x0) {
        *puVar6 = 800;
        puVar6[2] = 0x324;
        puVar6[4] = 0x330;
        puVar6[6] = 0x334;
        puVar6[8] = 0x340;
        uVar18 = (0xff000100u);
        puVar6[1] = g2c_float_to_bits(fVar3);
        puVar6[3] = g2c_float_to_bits(fVar13);
        puVar6[5] = g2c_float_to_bits(fVar11);
        puVar6[7] = g2c_float_to_bits(fVar21);
        puVar6[9] = g2c_float_to_bits(fVar15);
        puVar6[10] = 0x344;
        puVar6[0xb] = g2c_float_to_bits(fVar16);
        puVar6[0xc] = uVar18;
        puVar6[0xd] = uVar4 | uVar7;
      }
      goto LAB_0051726c;
    }
    if ((uVar8 == 6) || (uVar8 == 8)) {
      uVar4 = g2c_nema_vg_tess_516cf8((int)auStack_b4);
    }
    else {
      if ((uVar7 & 0xf) != 9) {
        if (uVar8 != 10 && uVar8 != 0xb) {
          iVar5 = *piVar2;
          if (*(int *)(iVar5 + 0x110) != 0) {
            fVar21 = fStack_a0 - fStack_a8;
            fVar22 = fStack_9c - fStack_a4;
            fVar11 = fVar21 * fVar21 + fVar22 * fVar22;
            if ((ABS(fVar11) < (1.0000000656873453e-05f))) {
              *(float *)(iVar5 + 0x198) = fStack_a8;
              *(float *)(iVar5 + 0x19c) = fStack_a4 + *(float *)(iVar5 + 0x130) * -0.5f;
              *(float *)(iVar5 + 0x1a0) = fStack_a8;
              *(float *)(iVar5 + 0x1a4) = fStack_a4 + *(float *)(iVar5 + 0x130) * 0.5f;
              *(undefined4 *)(iVar5 + 400) = *(undefined4 *)(iVar5 + 0x198);
              *(undefined4 *)(iVar5 + 0x194) = *(undefined4 *)(iVar5 + 0x19c);
              iVar5 = *piVar2;
              *(undefined4 *)(iVar5 + 0x1a8) = *(undefined4 *)(iVar5 + 0x1a0);
              *(undefined4 *)(iVar5 + 0x1ac) = *(undefined4 *)(iVar5 + 0x1a4);
              goto LAB_0051726c;
            }
            fVar11 = audio_uart_float_sqrt_4397a8(fVar11);
            fVar21 = fVar21 * (1.0f / fVar11);
            fVar22 = fVar22 * (1.0f / fVar11);
            fVar12 = *(float *)(iVar5 + 0x130) * 0.5f * fVar22;
            a_00 = fVar3 - fVar12;
            fVar14 = *(float *)(iVar5 + 0x134) * 0.5f * fVar21;
            b = fVar14 + fVar13;
            uVar19 = CONCAT44(g2c_float_to_bits(b),g2c_float_to_bits(a_00));
            *(float *)(iVar5 + 400) = a_00;
            *(float *)(iVar5 + 0x194) = b;
            iVar5 = *piVar2;
            c = fVar15 - fVar12;
            d = fVar14 + fVar16;
            *(float *)(iVar5 + 0x198) = c;
            *(float *)(iVar5 + 0x19c) = d;
            iVar5 = *piVar2;
            fVar15 = fVar12 + fVar15;
            fVar16 = fVar16 - fVar14;
            *(float *)(iVar5 + 0x1a0) = fVar15;
            *(float *)(iVar5 + 0x1a4) = fVar16;
            iVar5 = *piVar2;
            fVar12 = fVar12 + fVar3;
            fVar13 = fVar13 - fVar14;
            uVar17 = CONCAT44(g2c_float_to_bits(fVar13),g2c_float_to_bits(fVar12));
            *(float *)(iVar5 + 0x1a8) = fVar12;
            *(float *)(iVar5 + 0x1ac) = fVar13;
            iVar5 = *piVar2;
            if (*(int *)(iVar5 + 0x110) == 0) {
              uVar4 = audio_uart_nema_stencil_restore_5226b2(*(uint *)(iVar5 + 0x8c));
              g2c_nema_vg_emit_verts_516b34(a_00,b,c,d,fVar15,fVar16,fVar12,fVar13);
            }
            else {
              bVar10 = -1 < (int)((uint)*(byte *)(iVar5 + 0x7d) << 0x1b);
              uVar4 = audio_uart_nema_stencil_save_52266e((uint)bVar10,0,(uint)bVar10,0);
              iVar5 = *piVar2;
              if (0.0f < *(float *)(iVar5 + 0x184)) {
                fStack_bc = *(float *)(iVar5 + 0x164);
                fStack_b8 = *(float *)(iVar5 + 0x168);
                fStack_c4 = *(float *)(iVar5 + 0x16c);
                fStack_c0 = *(float *)(iVar5 + 0x170);
                fStack_cc = *(float *)(iVar5 + 0x174);
                fStack_c8 = *(float *)(iVar5 + 0x178);
                fStack_d4 = *(float *)(iVar5 + 0x17c);
                fStack_d0 = *(float *)(iVar5 + 0x180);
                g2c_nema_vg_emit_verts_516b34
                          (fStack_bc,fStack_b8,fStack_c4,fStack_c0,fStack_cc,fStack_c8,fStack_d4,
                           fStack_d0);
                iVar5 = *piVar2;
                if ((ABS(*(float *)(iVar5 + 0x188) * fVar22 -
                                     *(float *)(iVar5 + 0x18c) * fVar21) < fVar1)) {
                  uVar19 = *(undefined8 *)(iVar5 + 0x16c);
                  uVar17 = *(undefined8 *)(iVar5 + 0x174);
                  goto LAB_0051759a;
                }
                fStack_bc = *(float *)(iVar5 + 0x16c);
                fStack_b8 = *(float *)(iVar5 + 0x170);
                fStack_cc = *(float *)(iVar5 + 0x174);
                fStack_c8 = *(float *)(iVar5 + 0x178);
                fStack_d4 = fVar12;
                fStack_d0 = fVar13;
                fStack_c4 = a_00;
                fStack_c0 = b;
                uVar7 = g2c_nema_vg_stroke_join_5179d0
                                  (&fStack_bc,(uint *)&fStack_c4,&fStack_cc,(uint *)&fStack_d4,0);
                if (uVar7 == 0) goto LAB_0051759a;
LAB_0051772c:
                iVar5 = *piVar2;
                *(undefined4 *)(iVar5 + 0x114) = 0;
                *(undefined4 *)(iVar5 + 0x118) = 0;
                audio_uart_nema_vg_set_error_51565c(uVar7);
                goto LAB_0051726c;
              }
LAB_0051759a:
              iVar5 = *piVar2;
              if ((0.0f < *(float *)(iVar5 + 0x158)) && (*(int *)(iVar5 + 0x128) == 1)) {
                if ((ABS(*(float *)(iVar5 + 0x15c) * fVar22 -
                                     *(float *)(iVar5 + 0x160) * fVar21) < fVar1)) {
                  uVar19 = *(undefined8 *)(iVar5 + 0x140);
                  uVar17 = *(undefined8 *)(iVar5 + 0x148);
                }
                else {
                  fStack_bc = *(float *)(iVar5 + 0x140);
                  fStack_b8 = *(float *)(iVar5 + 0x144);
                  fStack_c4 = (float)g2c_bits_to_float((uint)(uVar19));
                  fStack_c0 = (float)g2c_bits_to_float((uint)(((ulonglong)uVar19 >> 0x20)));
                  fStack_cc = *(float *)(iVar5 + 0x148);
                  fStack_c8 = *(float *)(iVar5 + 0x14c);
                  fStack_d4 = (float)g2c_bits_to_float((uint)(uVar17));
                  fStack_d0 = (float)g2c_bits_to_float((uint)(((ulonglong)uVar17 >> 0x20)));
                  uVar7 = g2c_nema_vg_stroke_join_5179d0
                                    (&fStack_bc,(uint *)&fStack_c4,&fStack_cc,(uint *)&fStack_d4,0);
                  if (uVar7 != 0) goto LAB_0051772c;
                }
              }
              iVar5 = *piVar2;
              *(int *)(iVar5 + 0x128) = *(int *)(iVar5 + 0x128) + 1;
              uVar20 = (undefined4)((ulonglong)uVar19 >> 0x20);
              uVar18 = (undefined4)((ulonglong)uVar17 >> 0x20);
              if (*(float *)(iVar5 + 0x158) == 0.0f) {
                *(int *)(iVar5 + 0x138) = (int)uVar19;
                *(undefined4 *)(iVar5 + 0x13c) = uVar20;
                iVar5 = *piVar2;
                *(float *)(iVar5 + 0x140) = c;
                *(float *)(iVar5 + 0x144) = d;
                iVar5 = *piVar2;
                *(float *)(iVar5 + 0x148) = fVar15;
                *(float *)(iVar5 + 0x14c) = fVar16;
                iVar5 = *piVar2;
                *(int *)(iVar5 + 0x150) = (int)uVar17;
                *(undefined4 *)(iVar5 + 0x154) = uVar18;
                iVar5 = *piVar2;
                *(float *)(iVar5 + 0x158) = fVar11;
                *(float *)(iVar5 + 0x15c) = fVar21;
                *(float *)(iVar5 + 0x160) = fVar22;
              }
              else {
                *(int *)(iVar5 + 0x164) = (int)uVar19;
                *(undefined4 *)(iVar5 + 0x168) = uVar20;
                iVar5 = *piVar2;
                *(float *)(iVar5 + 0x16c) = c;
                *(float *)(iVar5 + 0x170) = d;
                iVar5 = *piVar2;
                *(float *)(iVar5 + 0x174) = fVar15;
                *(float *)(iVar5 + 0x178) = fVar16;
                iVar5 = *piVar2;
                *(int *)(iVar5 + 0x17c) = (int)uVar17;
                *(undefined4 *)(iVar5 + 0x180) = uVar18;
                iVar5 = *piVar2;
                *(float *)(iVar5 + 0x184) = fVar11;
                *(float *)(iVar5 + 0x188) = fVar21;
                *(float *)(iVar5 + 0x18c) = fVar22;
              }
            }
            audio_uart_nema_stencil_restore_5226b2(uVar4);
            goto LAB_0051726c;
          }
          uVar4 = 0;
          if (*(int *)(iVar5 + 0x88) != 0) {
            uVar4 = 0x7800000;
          }
          uVar4 = uVar4 & *(uint *)(iVar5 + 0x8c);
          if (*(char *)(*(((int *)audio_uart_nema_context_cell)) + 8) == '\x01') {
            uVar4 = uVar4 | *(uint *)(*(((int *)audio_uart_nema_context_cell)) + 0xc) & 0xc0000000;
          }
          puVar6 = (undefined4 *)audio_uart_nema_cl_get_space_514aec(5);
          if (puVar6 != (undefined4 *)0x0) {
            *puVar6 = 800;
            puVar6[2] = 0x324;
            puVar6[4] = 0x330;
            uVar18 = (0xff000100u);
            puVar6[1] = g2c_float_to_bits(fVar3);
            puVar6[3] = g2c_float_to_bits(fVar13);
            puVar6[5] = g2c_float_to_bits(fVar15);
            puVar6[6] = 0x334;
            puVar6[7] = g2c_float_to_bits(fVar16);
            puVar6[8] = uVar18;
            puVar6[9] = uVar4 | 10;
          }
        }
        goto LAB_0051726c;
      }
      uVar4 = g2c_nema_vg_arc_to_51a8ec((uint)a,(int)auStack_b4);
    }
    if (uVar4 != 0) {
LAB_00517294:
      iVar5 = *piVar2;
      *(undefined4 *)(iVar5 + 0x114) = 0;
      *(undefined4 *)(iVar5 + 0x118) = 0;
      audio_uart_nema_vg_set_error_51565c(uVar4);
      return uVar4;
    }
  } while( true );
}
#undef fStack_d4
#undef fStack_d0
#undef fStack_cc
#undef fStack_c8
#undef fStack_c4
#undef fStack_c0
#undef fStack_bc
#undef fStack_b8
#undef auStack_b4
#undef cStack_b2
#undef fStack_a8
#undef fStack_a4
#undef fStack_a0
#undef fStack_9c
#undef fStack_98
#undef fStack_94


  

/* ---- lifted 0x51778c ---- */

void g2c_nema_vg_set_aa_51778c(uint a)

{
  *(uint *)(*(((int *)&audio_uart_nema_vg_context_cell)) + 0x114) = a;
  return;
}

  

/* ---- lifted 0x517796 ---- */

void g2c_nema_vg_set_aa2_517796(uint a)

{
  *(uint *)(*(((int *)&audio_uart_nema_vg_context_cell)) + 0x118) = a;
  return;
}

  

/* ---- lifted 0x5177a4 ---- */

int g2c_nema_vg_near_5177a4(float *a,float *b)

{
  /* Evidence (wave10, stock 0x5177a4..0x51784e): s1 = (s0<0 ? -s0 : s0) via
   * vcmp #0 / ite mi vnegmi/vmovpl (0x5177ac..0x5177ba), s3 likewise for *b
   * (0x5177c2..0x5177d0), then s1 = min via vcmp s1,s3 / vmovpl (0x5177d4..0x5177de).
   * The former in-s1/in-s3 temps were these values, not incoming registers. */
  float abs_a0;
  float abs_b0;
  int iVar1;
  int iVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  
  iVar2 = 0;
  fVar3 = *a;
  abs_a0 = (fVar3 < 0.0f) ? -fVar3 : fVar3;
  fVar4 = *b;
  abs_b0 = (fVar4 < 0.0f) ? -fVar4 : fVar4;
  if (!(abs_a0 < abs_b0)) {
    abs_a0 = abs_b0;
  }
  fVar5 = fVar3 - fVar4;
  if ((fVar5 < 0.0f)) {
    fVar5 = fVar4 - fVar3;
  }
  if (fVar5 <= abs_a0 * (9.999999747378752e-06f)) {
    fVar3 = ABS(a[1]);
    if (!(ABS(a[1]) < ABS(b[1]))) {
      fVar3 = ABS(b[1]);
    }
    fVar4 = a[1] - b[1];
    if ((fVar4 < 0.0f)) {
      fVar4 = b[1] - a[1];
    }
    if (fVar4 <= fVar3 * (9.999999747378752e-06f)) {
      iVar2 = 1;
    }
  }
  return iVar2;
}

  

/* ---- lifted 0x51785c ---- */

int g2c_nema_vg_near2_51785c(float *a,float *b)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  int iVar5;
  float fVar6;
  float fVar7;
  float fVar8;
  float fVar9;
  float fVar10;
  float fVar11;
  float fVar12;
  float fVar13;
  float fVar14;
  
  fVar9 = a[3];
  fVar1 = a[1];
  fVar4 = b[1];
  fVar12 = *b;
  fVar2 = *a;
  fVar3 = a[2];
  iVar5 = (int)((fVar1 - fVar9) * fVar12 + (fVar9 - fVar4) * fVar2 + (fVar4 - fVar1) * fVar3);
  if (iVar5 < 0) {
    iVar5 = -iVar5;
  }
  fVar6 = (float)VectorSignedFixedToFloat(iVar5,0x20,1);
  fVar7 = a[5];
  fVar8 = a[4];
  iVar5 = (int)((fVar9 - fVar7) * fVar12 + (fVar7 - fVar4) * fVar3 + (fVar4 - fVar9) * fVar8);
  if (iVar5 < 0) {
    iVar5 = -iVar5;
  }
  fVar10 = (float)VectorSignedFixedToFloat(iVar5,0x20,1);
  fVar11 = a[7];
  fVar13 = a[6];
  iVar5 = (int)((fVar7 - fVar11) * fVar12 + (fVar11 - fVar4) * fVar8 + (fVar4 - fVar7) * fVar13);
  if (iVar5 < 0) {
    iVar5 = -iVar5;
  }
  fVar14 = (float)VectorSignedFixedToFloat(iVar5,0x20,1);
  iVar5 = (int)((fVar11 - fVar1) * fVar12 + (fVar1 - fVar4) * fVar13 + (fVar4 - fVar11) * fVar2);
  if (iVar5 < 0) {
    iVar5 = -iVar5;
  }
  fVar4 = (float)VectorSignedFixedToFloat(iVar5,0x20,1);
  iVar5 = (int)((fVar9 - fVar7) * fVar2 + (fVar7 - fVar1) * fVar3 + (fVar1 - fVar9) * fVar8);
  if (iVar5 < 0) {
    iVar5 = -iVar5;
  }
  fVar3 = (float)VectorSignedFixedToFloat(iVar5,0x20,1);
  iVar5 = (int)((fVar11 - fVar1) * fVar8 + (fVar1 - fVar7) * fVar13 + (fVar7 - fVar11) * fVar2);
  if (iVar5 < 0) {
    iVar5 = -iVar5;
  }
  fVar1 = (float)VectorSignedFixedToFloat(iVar5,0x20,1);
  return (uint)((int)fVar4 + (int)fVar14 + (int)fVar10 + (int)fVar6 <= (int)fVar1 + (int)fVar3);
}

  

/* ---- lifted 0x5179d0 ---- */

uint g2c_nema_vg_stroke_join_5179d0(float *a,uint *b,float *c,uint *d,int e)

{
  char cVar1;
  int *piVar2;
  int iVar3;
  float *pfVar4;
  int iVar5;
  int iVar6;
  float *pfVar7;
  uint previous;
  float fVar8;
  float fVar9;
  float fVar10;
  bool bVar11;
  bool bVar12;
  float fVar13;
  float fVar14;
  float a_00;
  float b_00;
  float f;
  float a_01;
  float b_01;
  float g;
  float h;
  /* Stock frame of 0x5179d0 as one block: locals keep the entry-SP offsets Ghidra named them by
   * (X_Stack_NN at g2c_frame_5179d0[0xb0-0xNN]) so &local passed to callees spans its stock neighbours. */
  unsigned char g2c_frame_5179d0[0xb0] __attribute__((aligned(8)));
  typedef float __attribute__((may_alias)) g2c_fa_float;
#define fStack_b0 (*(g2c_fa_float *)(void *)&g2c_frame_5179d0[0xb0-0xb0])
#define fStack_ac (*(g2c_fa_float *)(void *)&g2c_frame_5179d0[0xb0-0xac])
#define fStack_a8 (*(g2c_fa_float *)(void *)&g2c_frame_5179d0[0xb0-0xa8])
#define fStack_a4 (*(g2c_fa_float *)(void *)&g2c_frame_5179d0[0xb0-0xa4])
#define fStack_a0 (*(g2c_fa_float *)(void *)&g2c_frame_5179d0[0xb0-0xa0])
#define fStack_9c (*(g2c_fa_float *)(void *)&g2c_frame_5179d0[0xb0-0x9c])
#define fStack_98 (*(g2c_fa_float *)(void *)&g2c_frame_5179d0[0xb0-0x98])
#define fStack_94 (*(g2c_fa_float *)(void *)&g2c_frame_5179d0[0xb0-0x94])
#define fStack_90 (*(g2c_fa_float *)(void *)&g2c_frame_5179d0[0xb0-0x90])
#define fStack_8c (*(g2c_fa_float *)(void *)&g2c_frame_5179d0[0xb0-0x8c])
#define fStack_88 (*(g2c_fa_float *)(void *)&g2c_frame_5179d0[0xb0-0x88])
#define fStack_84 (*(g2c_fa_float *)(void *)&g2c_frame_5179d0[0xb0-0x84])
  typedef undefined4 __attribute__((may_alias)) g2c_fa_undefined4;
#define uStack_80 (*(g2c_fa_undefined4 *)(void *)&g2c_frame_5179d0[0xb0-0x80])
#define uStack_7c (*(g2c_fa_undefined4 *)(void *)&g2c_frame_5179d0[0xb0-0x7c])
#define uStack_78 (*(g2c_fa_undefined4 *)(void *)&g2c_frame_5179d0[0xb0-0x78])
#define fStack_74 (*(g2c_fa_float *)(void *)&g2c_frame_5179d0[0xb0-0x74])
#define fStack_70 (*(g2c_fa_float *)(void *)&g2c_frame_5179d0[0xb0-0x70])
#define fStack_6c (*(g2c_fa_float *)(void *)&g2c_frame_5179d0[0xb0-0x6c])
#define fStack_68 (*(g2c_fa_float *)(void *)&g2c_frame_5179d0[0xb0-0x68])
#define fStack_64 (*(g2c_fa_float *)(void *)&g2c_frame_5179d0[0xb0-0x64])
#define fStack_60 (*(g2c_fa_float *)(void *)&g2c_frame_5179d0[0xb0-0x60])
#define fStack_5c (*(g2c_fa_float *)(void *)&g2c_frame_5179d0[0xb0-0x5c])
#define fStack_58 (*(g2c_fa_float *)(void *)&g2c_frame_5179d0[0xb0-0x58])
#define uStack_54 (*(g2c_fa_undefined4 *)(void *)&g2c_frame_5179d0[0xb0-0x54])
#define uStack_50 (*(g2c_fa_undefined4 *)(void *)&g2c_frame_5179d0[0xb0-0x50])
#define uStack_4c (*(g2c_fa_undefined4 *)(void *)&g2c_frame_5179d0[0xb0-0x4c])
  
  piVar2 = (((int *)&audio_uart_nema_vg_context_cell));
  iVar3 = *(((int *)&audio_uart_nema_vg_context_cell));
  if (*(int *)(iVar3 + 0x110) == 0) {
    return 0;
  }
  cVar1 = *(char *)(iVar3 + 0x2e2);
  previous = 0;
  if ((cVar1 == '\0') || (*(int *)(iVar3 + 0x118) != 0)) {
    if (-1 < (int)((uint)*(byte *)(iVar3 + 0x7d) << 0x1b)) {
      previous = audio_uart_nema_stencil_save_52266e(1,0,1,0);
    }
    g2c_nema_vg_emit_verts_516b34(*a,a[1],(float)g2c_bits_to_float((uint)(*b)),(float)g2c_bits_to_float((uint)(b[1])),*c,c[1],(float)g2c_bits_to_float((uint)(*d)),(float)g2c_bits_to_float((uint)(d[1])));
    goto LAB_00517a30;
  }
  if (cVar1 == '\x02') {
    fStack_b0 = *(g2c_nvg_zero_pair_0);
    fStack_ac = (g2c_nvg_zero_pair_0)[1];
    iVar3 = g2c_nema_vg_cubic_approx_522f50
                      (*a,a[1],*c,c[1],(float)g2c_bits_to_float((uint)(*b)),(float)g2c_bits_to_float((uint)(b[1])),(float)g2c_bits_to_float((uint)(*d)),(float)g2c_bits_to_float((uint)(d[1])),&fStack_b0,
                       &fStack_ac);
    if (iVar3 == 0) {
      return 0;
    }
    iVar3 = *piVar2;
    fVar13 = audio_uart_float_sqrt_4397a8
                       (*(float *)(iVar3 + 0xec) * *(float *)(iVar3 + 0xec) +
                        *(float *)(iVar3 + 0xf0) * *(float *)(iVar3 + 0xf0));
    fVar14 = audio_uart_float_sqrt_4397a8
                       (*(float *)(iVar3 + 0xf8) * *(float *)(iVar3 + 0xf8) +
                        *(float *)(iVar3 + 0xfc) * *(float *)(iVar3 + 0xfc));
    fVar13 = ABS(fVar13);
    /* stock 0x517aca vcmp |a|,K; itt lt; vcmplt 0x517ad8 |b|,K; blt 0x517aec -> r4=0,
       else r4=1 + set_flag(1); 0x517b18 cmp r4,#0 -> set_flag(0). LT includes unordered,
       so r4 = ordered |a|>=K || |b|>=K. */
    bVar11 = (fVar13 >= (2.000000238418579f) || ABS(fVar14) >= (2.000000238418579f));
    if (bVar11) {
      g2c_nema_vg_set_flag_522622(1);
    }
    fVar13 = *(float *)(*piVar2 + 0x2d8) * 0.5f;
    if ((int)((uint)*(byte *)(*piVar2 + 0x7d) << 0x1b) < 0) {
      g2c_nema_vg_move_to_522fb4(fStack_b0,fStack_ac,fVar13);
    }
    else {
      g2c_nema_vg_line_to_523284(fStack_b0,fStack_ac,fVar13);
    }
    if (!bVar11) {
      return 0;
    }
    g2c_nema_vg_set_flag_522622(0);
    return 0;
  }
  if (cVar1 != '\x01') {
    return 0x1000000;
  }
  if (*(char *)(iVar3 + 0x2e4) == '\0') {
    fVar13 = *(float *)(iVar3 + 0x158);
    if ((fVar13 <= 0.0f) || (*(int *)(iVar3 + 0x128) != 1)) {
      if (e == 1) {
        /* stock 0x517b72 vcmp [0x158],#0; ittt gt; vldrgt [0x184]; vcmpgt #0; ble 0x517bac:
           enter iff both > 0 (ordered). */
        bVar11 = (fVar13 > 0.0f);
        if (bVar11) {
          fVar13 = *(float *)(iVar3 + 0x184); /* vldrgt s0 */
          bVar11 = (fVar13 > 0.0f);
        }
        if (bVar11) {
          fStack_a0 = *(float *)(iVar3 + 0x138);
          fStack_9c = *(float *)(iVar3 + 0x13c);
          fStack_98 = *(float *)(iVar3 + 0x140);
          fStack_94 = *(float *)(iVar3 + 0x144);
          fStack_90 = *(float *)(iVar3 + 0x148);
          pfVar4 = (float *)(iVar3 + 0x164);
          fStack_8c = *(float *)(iVar3 + 0x14c);
          fStack_88 = *(float *)(iVar3 + 0x150);
          fStack_84 = *(float *)(iVar3 + 0x154);
          uStack_80 = *(undefined4 *)(iVar3 + 0x158);
          uStack_7c = *(undefined4 *)(iVar3 + 0x15c);
          uStack_78 = *(undefined4 *)(iVar3 + 0x160);
          pfVar7 = &fStack_74;
          goto LAB_00517bee;
        }
      }
      fStack_74 = *(float *)(iVar3 + 0x164);
      fStack_70 = *(float *)(iVar3 + 0x168);
      fStack_6c = *(float *)(iVar3 + 0x16c);
      fStack_68 = *(float *)(iVar3 + 0x170);
      fStack_64 = *(float *)(iVar3 + 0x174);
      pfVar4 = (float *)(iVar3 + 400);
      fStack_60 = *(float *)(iVar3 + 0x178);
      fStack_5c = *(float *)(iVar3 + 0x17c);
      fStack_58 = *(float *)(iVar3 + 0x180);
      uStack_54 = *(undefined4 *)(iVar3 + 0x184);
      uStack_50 = *(undefined4 *)(iVar3 + 0x188);
      uStack_4c = *(undefined4 *)(iVar3 + 0x18c);
      pfVar7 = &fStack_a0;
    }
    else {
      fStack_74 = *(float *)(iVar3 + 0x138);
      fStack_70 = *(float *)(iVar3 + 0x13c);
      fStack_6c = *(float *)(iVar3 + 0x140);
      fStack_68 = *(float *)(iVar3 + 0x144);
      fStack_64 = *(float *)(iVar3 + 0x148);
      pfVar4 = (float *)(iVar3 + 400);
      fStack_60 = *(float *)(iVar3 + 0x14c);
      fStack_5c = *(float *)(iVar3 + 0x150);
      fStack_58 = *(float *)(iVar3 + 0x154);
      uStack_54 = *(undefined4 *)(iVar3 + 0x158);
      uStack_50 = *(undefined4 *)(iVar3 + 0x15c);
      uStack_4c = *(undefined4 *)(iVar3 + 0x160);
      pfVar7 = &fStack_a0;
    }
  }
  else {
    fStack_74 = *(float *)(iVar3 + 0x334);
    fStack_70 = *(float *)(iVar3 + 0x338);
    fStack_6c = *(float *)(iVar3 + 0x33c);
    fStack_68 = *(float *)(iVar3 + 0x340);
    fStack_64 = *(float *)(iVar3 + 0x344);
    pfVar4 = (float *)(iVar3 + 0x308);
    fStack_60 = *(float *)(iVar3 + 0x348);
    fStack_5c = *(float *)(iVar3 + 0x34c);
    fStack_58 = *(float *)(iVar3 + 0x350);
    uStack_54 = *(undefined4 *)(iVar3 + 0x354);
    uStack_50 = *(undefined4 *)(iVar3 + 0x358);
    uStack_4c = *(undefined4 *)(iVar3 + 0x35c);
    pfVar7 = &fStack_a0;
  }
LAB_00517bee:
  fVar13 = pfVar4[1];
  fVar14 = pfVar4[2];
  fVar8 = pfVar4[3];
  fVar9 = pfVar4[4];
  fVar10 = pfVar4[5];
  *pfVar7 = *pfVar4;
  pfVar7[1] = fVar13;
  pfVar7[2] = fVar14;
  pfVar7[3] = fVar8;
  pfVar7[4] = fVar9;
  pfVar7[5] = fVar10;
  fVar13 = pfVar4[7];
  fVar14 = pfVar4[8];
  fVar8 = pfVar4[9];
  fVar9 = pfVar4[10];
  pfVar7[6] = pfVar4[6];
  pfVar7[7] = fVar13;
  pfVar7[8] = fVar14;
  pfVar7[9] = fVar8;
  pfVar7[10] = fVar9;
  iVar3 = g2c_nema_vg_near_5177a4(&fStack_a0,&fStack_74);
  if ((((iVar3 == 1) && (iVar3 = g2c_nema_vg_near_5177a4(&fStack_98,&fStack_6c), iVar3 == 1)) &&
      (iVar3 = g2c_nema_vg_near_5177a4(&fStack_90,&fStack_64), iVar3 == 1)) &&
     (iVar3 = g2c_nema_vg_near_5177a4(&fStack_88,&fStack_5c), iVar3 == 1)) {
    return 0;
  }
  iVar3 = g2c_nema_vg_near2_51785c(&fStack_a0,&fStack_6c);
  if ((iVar3 != 0) || (iVar3 = g2c_nema_vg_near2_51785c(&fStack_74,&fStack_a0), iVar3 != 0))
  goto LAB_00517c84;
  iVar3 = g2c_nema_vg_near2_51785c(&fStack_a0,&fStack_64);
  fVar13 = fStack_64;
  fVar14 = fStack_60;
  fVar8 = fStack_88;
  fVar9 = fStack_84;
  fVar10 = fStack_a0;
  f = fStack_9c;
  a_00 = fStack_6c;
  b_00 = fStack_68;
  g = fStack_98;
  h = fStack_94;
  a_01 = fStack_74;
  b_01 = fStack_70;
  if ((iVar3 == 0) &&
     (iVar3 = g2c_nema_vg_near2_51785c(&fStack_74,&fStack_88), fVar13 = fStack_64,
     fVar14 = fStack_60, fVar8 = fStack_88, fVar9 = fStack_84, fVar10 = fStack_a0, f = fStack_9c,
     a_00 = fStack_6c, b_00 = fStack_68, g = fStack_98, h = fStack_94, a_01 = fStack_74,
     b_01 = fStack_70, iVar3 == 0)) {
    iVar3 = (uint)(fStack_60 < fStack_68) << 0x1f;
    if ((fStack_9c < fStack_68)) {
      if (-1 < iVar3) {
LAB_00517c84:
        fVar13 = fStack_6c;
        fVar14 = fStack_68;
        fVar8 = fStack_a0;
        fVar9 = fStack_9c;
        fVar10 = fStack_88;
        f = fStack_84;
        a_00 = fStack_64;
        b_00 = fStack_60;
        g = fStack_90;
        h = fStack_8c;
        a_01 = fStack_5c;
        b_01 = fStack_58;
      }
    }
    else if (iVar3 < 0) goto LAB_00517c84;
  }
  fStack_a8 = *(g2c_nvg_zero_pair_1);
  fStack_a4 = (g2c_nvg_zero_pair_1)[1];
  fStack_b0 = *(g2c_nvg_zero_pair_2);
  fStack_ac = (g2c_nvg_zero_pair_2)[1];
  iVar3 = g2c_nema_vg_cubic_approx_522f50
                    (a_00,b_00,fVar13,fVar14,fVar10,f,fVar8,fVar9,&fStack_a8,&fStack_a4);
  iVar5 = g2c_nema_vg_cubic_approx_522f50(a_01,b_01,a_00,b_00,fVar10,f,g,h,&fStack_b0,&fStack_ac);
  fVar13 = g2c_nema_vg_sqrt_524218
                     ((fStack_b0 - fStack_a8) * (fStack_b0 - fStack_a8) +
                      (fStack_ac - fStack_a4) * (fStack_ac - fStack_a4));
  iVar6 = *piVar2;
  if (((*(float *)(iVar6 + 0x2dc) * *(float *)(iVar6 + 0x2d8) < fVar13)) ||
     (iVar5 == 0 || iVar3 == 0)) {
    if (-1 < (int)((uint)*(byte *)(iVar6 + 0x7d) << 0x1b)) {
      previous = audio_uart_nema_stencil_save_52266e(1,0,1,0);
    }
    fVar10 = (float)g2c_bits_to_float((uint)(*d));
    f = (float)g2c_bits_to_float((uint)(d[1]));
    a_00 = (float)g2c_bits_to_float((uint)(*b));
    b_00 = (float)g2c_bits_to_float((uint)(b[1]));
    fVar13 = *a;
    fVar14 = a[1];
    fVar8 = *c;
    fVar9 = c[1];
  }
  else {
    fVar13 = fStack_a8;
    fVar14 = fStack_a4;
    fVar8 = fStack_b0;
    fVar9 = fStack_ac;
    if (-1 < (int)((uint)*(byte *)(iVar6 + 0x7d) << 0x1b)) {
      previous = audio_uart_nema_stencil_save_52266e(0,1,1,0);
      fVar13 = fStack_a8;
      fVar14 = fStack_a4;
      fVar8 = fStack_b0;
      fVar9 = fStack_ac;
    }
  }
  g2c_nema_vg_emit_verts_516b34(fVar13,fVar14,a_00,b_00,fVar8,fVar9,fVar10,f);
LAB_00517a30:
  if (-1 < (int)((uint)*(byte *)(*piVar2 + 0x7d) << 0x1b)) {
    audio_uart_nema_stencil_restore_5226b2(previous);
  }
  return 0;
}
#undef fStack_b0
#undef fStack_ac
#undef fStack_a8
#undef fStack_a4
#undef fStack_a0
#undef fStack_9c
#undef fStack_98
#undef fStack_94
#undef fStack_90
#undef fStack_8c
#undef fStack_88
#undef fStack_84
#undef uStack_80
#undef uStack_7c
#undef uStack_78
#undef fStack_74
#undef fStack_70
#undef fStack_6c
#undef fStack_68
#undef fStack_64
#undef fStack_60
#undef fStack_5c
#undef fStack_58
#undef uStack_54
#undef uStack_50
#undef uStack_4c


  

/* ---- lifted 0x517e18 ---- */


uint g2c_nema_vg_stroke_path_517e18(float a,float b,float c,float d,float e,float f,float g,float h)

{
  char cVar1;
  byte bVar2;
  bool bVar3;
  undefined8 uVar4;
  int *piVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  float *pfVar9;
  int iVar10;
  int iVar11;
  uint uVar12;
  bool bVar13;
  bool bVar14;
  float fVar15;
  float fVar16;
  float fVar17;
  float fVar18;
  float fVar19;
  float fVar20;
  float fVar21;
  float fVar22;
  float fVar23;
  float fVar24;
  float fVar25;
  float fVar26;
  float fVar27;
  float fVar28;
  float fVar29;
  float fVar30;
  float fVar31;
  float fVar32;
  float h_00;
  float f_00;
  float c_00;
  undefined8 uVar33;
  undefined4 uVar34;
  undefined8 uVar35;
  undefined4 uVar36;
  float h_01;
  float g_00;
  /* Stock frame of 0x517e18 as one block: locals keep the entry-SP offsets Ghidra named them by
   * (X_Stack_NN at g2c_frame_517e18[0x120-0xNN]) so &local passed to callees spans its stock neighbours. */
  unsigned char g2c_frame_517e18[0x120] __attribute__((aligned(8)));
  typedef float __attribute__((may_alias)) g2c_fa_float;
#define fStack_120 (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0x120])
#define fStack_11c (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0x11c])
#define fStack_118 (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0x118])
#define fStack_114 (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0x114])
#define fStack_110 (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0x110])
#define fStack_10c (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0x10c])
#define fStack_104 (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0x104])
#define fStack_100 (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0x100])
#define fStack_fc (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0xfc])
#define fStack_f8 (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0xf8])
#define fStack_f4 (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0xf4])
#define fStack_f0 (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0xf0])
#define fStack_ec (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0xec])
#define fStack_e8 (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0xe8])
#define fStack_e4 (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0xe4])
#define fStack_e0 (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0xe0])
#define fStack_dc (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0xdc])
#define fStack_d8 (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0xd8])
#define fStack_d4 (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0xd4])
#define fStack_d0 (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0xd0])
#define fStack_cc (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0xcc])
#define fStack_c8 (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0xc8])
#define fStack_c4 (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0xc4])
#define fStack_c0 (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0xc0])
#define fStack_bc (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0xbc])
#define fStack_b8 (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0xb8])
#define fStack_b4 (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0xb4])
#define fStack_b0 (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0xb0])
#define fStack_ac (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0xac])
#define fStack_a8 (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0xa8])
#define fStack_a4 (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0xa4])
#define fStack_a0 (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0xa0])
#define fStack_9c (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0x9c])
#define fStack_98 (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0x98])
#define fStack_94 (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0x94])
#define fStack_90 (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0x90])
#define fStack_8c (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0x8c])
#define fStack_88 (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0x88])
#define fStack_84 (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0x84])
#define fStack_80 (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0x80])
#define fStack_7c (*(g2c_fa_float *)(void *)&g2c_frame_517e18[0x120-0x7c])
  typedef undefined4 __attribute__((may_alias)) g2c_fa_undefined4;
#define uStack_78 (*(g2c_fa_undefined4 *)(void *)&g2c_frame_517e18[0x120-0x78])
#define uStack_74 (*(g2c_fa_undefined4 *)(void *)&g2c_frame_517e18[0x120-0x74])
#define uStack_70 (*(g2c_fa_undefined4 *)(void *)&g2c_frame_517e18[0x120-0x70])
  
  piVar5 = (((int *)&audio_uart_nema_vg_context_cell));
  iVar10 = 1;
  bVar3 = true;
  bVar13 = true;
  fStack_120 = g;
  fStack_11c = h;
  fStack_118 = f;
  fStack_114 = e;
  fStack_110 = d;
  fStack_10c = c;
  fStack_104 = a;
  fStack_100 = b;
  do {
    fVar15 = (fStack_104 + fStack_10c) * 0.5f;
    fVar17 = (fStack_100 + fStack_110) * 0.5f;
    fVar28 = (fStack_10c + fStack_114) * 0.5f;
    fVar32 = (fStack_110 + fStack_118) * 0.5f;
    fVar18 = (fStack_114 + fStack_120) * 0.5f;
    fVar20 = (fStack_118 + fStack_11c) * 0.5f;
    fVar26 = (fVar15 + fVar28) * 0.5f;
    fVar27 = (fVar17 + fVar32) * 0.5f;
    fVar29 = (fVar28 + fVar18) * 0.5f;
    fVar32 = (fVar32 + fVar20) * 0.5f;
    c_00 = (fVar26 + fVar29) * 0.5f;
    fVar28 = (fVar27 + fVar32) * 0.5f;
    iVar11 = *piVar5;
    if ((((!bVar3) && (ABS((fStack_104 + fStack_120) * 0.5f - c_00) < 0.5f)) &&
        (ABS((fStack_100 + fStack_11c) * 0.5f - fVar28) < 0.5f)) || (9 < *(int *)(iVar11 + 700))) {
      iVar10 = iVar10 + -1;
      if (*(char *)(iVar11 + 0x2e4) == '\0') {
        if ((bVar13) && (*(char *)(iVar11 + 0x1c0) == '\x01')) {
          fVar18 = c_00 - fStack_104;
          fVar17 = fVar28 - fStack_100;
          fVar15 = fVar18 * fVar18 + fVar17 * fVar17;
          if ((ABS(fVar15) < (1.0000000656873453e-05f))) {
            *(float *)(iVar11 + 0x198) = fStack_104;
            *(float *)(iVar11 + 0x19c) = fStack_100 + *(float *)(iVar11 + 0x130) * -0.5f;
            *(float *)(iVar11 + 0x1a0) = fStack_104;
            *(float *)(iVar11 + 0x1a4) = fStack_100 + *(float *)(iVar11 + 0x130) * 0.5f;
            *(undefined4 *)(iVar11 + 400) = *(undefined4 *)(iVar11 + 0x198);
            *(undefined4 *)(iVar11 + 0x194) = *(undefined4 *)(iVar11 + 0x19c);
            iVar11 = *piVar5;
            bVar13 = false;
            *(undefined4 *)(iVar11 + 0x1a8) = *(undefined4 *)(iVar11 + 0x1a0);
            *(undefined4 *)(iVar11 + 0x1ac) = *(undefined4 *)(iVar11 + 0x1a4);
          }
          else {
            fVar15 = audio_uart_float_sqrt_4397a8(fVar15);
            fVar18 = fVar18 * (1.0f / fVar15);
            fVar17 = fVar17 * (1.0f / fVar15);
            fVar20 = *(float *)(iVar11 + 0x130) * 0.5f * fVar17;
            fVar27 = fStack_104 - fVar20;
            fVar26 = *(float *)(iVar11 + 0x134) * 0.5f * fVar18;
            fVar29 = fVar26 + fStack_100;
            uVar35 = CONCAT44(g2c_float_to_bits(fVar29),g2c_float_to_bits(fVar27));
            fStack_ec = c_00 - fVar20;
            fStack_e8 = fVar26 + fVar28;
            fStack_f4 = fVar20 + c_00;
            fStack_f0 = fVar28 - fVar26;
            *(float *)(iVar11 + 400) = fVar27;
            *(float *)(iVar11 + 0x194) = fVar29;
            fVar20 = fVar20 + fStack_104;
            iVar11 = *piVar5;
            fVar26 = fStack_100 - fVar26;
            uVar33 = CONCAT44(g2c_float_to_bits(fVar26),g2c_float_to_bits(fVar20));
            *(float *)(iVar11 + 0x198) = fStack_ec;
            *(float *)(iVar11 + 0x19c) = fStack_e8;
            iVar11 = *piVar5;
            *(float *)(iVar11 + 0x1a0) = fStack_f4;
            *(float *)(iVar11 + 0x1a4) = fStack_f0;
            iVar11 = *piVar5;
            *(float *)(iVar11 + 0x1a8) = fVar20;
            *(float *)(iVar11 + 0x1ac) = fVar26;
            iVar11 = *piVar5;
            if (*(int *)(iVar11 + 0x110) == 0) {
              uVar6 = audio_uart_nema_stencil_restore_5226b2(*(uint *)(iVar11 + 0x8c));
              g2c_nema_vg_emit_verts_516b34
                        (fVar27,fVar29,fStack_ec,fStack_e8,fStack_f4,fStack_f0,fVar20,fVar26);
            }
            else {
              bVar13 = -1 < (int)((uint)*(byte *)(iVar11 + 0x7d) << 0x1b);
              uVar6 = audio_uart_nema_stencil_save_52266e((uint)bVar13,0,(uint)bVar13,0);
              iVar11 = *piVar5;
              if (0.0f < *(float *)(iVar11 + 0x184)) {
                g2c_nema_vg_emit_verts_516b34
                          (*(float *)(iVar11 + 0x164),*(float *)(iVar11 + 0x168),
                           *(float *)(iVar11 + 0x16c),*(float *)(iVar11 + 0x170),
                           *(float *)(iVar11 + 0x174),*(float *)(iVar11 + 0x178),
                           *(float *)(iVar11 + 0x17c),*(float *)(iVar11 + 0x180));
                iVar11 = *piVar5;
                if ((ABS(*(float *)(iVar11 + 0x188) * fVar17 -
                                     *(float *)(iVar11 + 0x18c) * fVar18) < (0.05000000447034836f))) {
                  uVar35 = *(undefined8 *)(iVar11 + 0x16c);
                  uVar33 = *(undefined8 *)(iVar11 + 0x174);
                }
                else {
                  uVar4 = *(undefined8 *)(iVar11 + 0x16c);
                  fStack_cc = fVar27;
                  fStack_c8 = fVar29;
                  if (*(int *)(iVar11 + 0x110) != 0) {
                    cVar1 = *(char *)(iVar11 + 0x2e2);
                    uVar12 = 0;
                    fVar25 = (float)g2c_bits_to_float((uint)(((ulonglong)*(undefined8 *)(iVar11 + 0x174) >> 0x20)));
                    fVar23 = (float)g2c_bits_to_float((uint)(((ulonglong)uVar4 >> 0x20)));
                    fVar24 = (float)g2c_bits_to_float((uint)(*(undefined8 *)(iVar11 + 0x174)));
                    fVar32 = (float)g2c_bits_to_float((uint)(uVar4));
                    if ((cVar1 == '\0') || (*(int *)(iVar11 + 0x118) != 0)) {
                      if (-1 < (int)((uint)*(byte *)(iVar11 + 0x7d) << 0x1b)) {
                        uVar12 = audio_uart_nema_stencil_save_52266e(1,0,1,0);
                      }
                      g2c_nema_vg_emit_verts_516b34
                                (fVar32,fVar23,fStack_cc,fStack_c8,fVar24,fVar25,fVar20,fVar26);
                      bVar2 = *(byte *)(*piVar5 + 0x7d);
joined_r0x005183a0:
                      if (-1 < (int)((uint)bVar2 << 0x1b)) {
                        audio_uart_nema_stencil_restore_5226b2(uVar12);
                      }
                    }
                    else if (cVar1 == '\x02') {
                      fStack_fc = *(g2c_nvg_zero_pair_0);
                      fStack_f8 = (g2c_nvg_zero_pair_0)[1];
                      iVar11 = g2c_nema_vg_cubic_approx_522f50
                                         (fVar32,fVar23,fVar24,fVar25,fVar27,fVar29,fVar20,fVar26,
                                          &fStack_fc,&fStack_f8);
                      if (iVar11 != 0) {
                        iVar11 = *piVar5;
                        fVar20 = audio_uart_float_sqrt_4397a8
                                           (*(float *)(iVar11 + 0xec) * *(float *)(iVar11 + 0xec) +
                                            *(float *)(iVar11 + 0xf0) * *(float *)(iVar11 + 0xf0));
                        fVar26 = audio_uart_float_sqrt_4397a8
                                           (*(float *)(iVar11 + 0xf8) * *(float *)(iVar11 + 0xf8) +
                                            *(float *)(iVar11 + 0xfc) * *(float *)(iVar11 + 0xfc));
                        fVar20 = ABS(fVar20);
                        /* stock 0x518474 vcmp; ittt lt; vcmplt 0x518482; iteee lt; movlt r6,#0 / movge r6,#1 (0x51848c).
                           LT includes unordered, so r6 = either ordered >= K (wave19 address-verified: Ghidra label joined_r0x005183a0 above = stock fallthrough of bl 0x516b34 at 0x518390, which is the last emit before this vcmp). */
                        bVar13 = (fVar20 >= (2.000000238418579f) || ABS(fVar26) >= (2.000000238418579f));
                        if (bVar13) {
                          g2c_nema_vg_set_flag_522622(1);
                        }
                        fVar20 = *(float *)(*piVar5 + 0x2d8) * 0.5f;
                        if ((int)((uint)*(byte *)(*piVar5 + 0x7d) << 0x1b) < 0) {
                          g2c_nema_vg_move_to_522fb4(fStack_fc,fStack_f8,fVar20);
                        }
                        else {
                          g2c_nema_vg_line_to_523284(fStack_fc,fStack_f8,fVar20);
                        }
                        if (bVar13) {
                          g2c_nema_vg_set_flag_522622(0);
                        }
                      }
                    }
                    else {
                      if (cVar1 != '\x01') goto LAB_005184da;
                      if (*(char *)(iVar11 + 0x2e4) == '\0') {
                        if ((*(float *)(iVar11 + 0x158) <= 0.0f) || (*(int *)(iVar11 + 0x128) != 1))
                        {
                          fStack_98 = *(float *)(iVar11 + 0x164);
                          fStack_94 = *(float *)(iVar11 + 0x168);
                          fStack_90 = *(float *)(iVar11 + 0x16c);
                          fStack_8c = *(float *)(iVar11 + 0x170);
                          fStack_88 = *(float *)(iVar11 + 0x174);
                          fStack_84 = *(float *)(iVar11 + 0x178);
                          pfVar9 = (float *)(iVar11 + 400);
                          fStack_80 = *(float *)(iVar11 + 0x17c);
                          fStack_7c = *(float *)(iVar11 + 0x180);
                          uStack_78 = *(undefined4 *)(iVar11 + 0x184);
                          uStack_74 = *(undefined4 *)(iVar11 + 0x188);
                          uStack_70 = *(undefined4 *)(iVar11 + 0x18c);
                        }
                        else {
                          fStack_98 = *(float *)(iVar11 + 0x138);
                          fStack_94 = *(float *)(iVar11 + 0x13c);
                          fStack_90 = *(float *)(iVar11 + 0x140);
                          fStack_8c = *(float *)(iVar11 + 0x144);
                          fStack_88 = *(float *)(iVar11 + 0x148);
                          fStack_84 = *(float *)(iVar11 + 0x14c);
                          pfVar9 = (float *)(iVar11 + 400);
                          fStack_80 = *(float *)(iVar11 + 0x150);
                          fStack_7c = *(float *)(iVar11 + 0x154);
                          uStack_78 = *(undefined4 *)(iVar11 + 0x158);
                          uStack_74 = *(undefined4 *)(iVar11 + 0x15c);
                          uStack_70 = *(undefined4 *)(iVar11 + 0x160);
                        }
                      }
                      else {
                        fStack_98 = *(float *)(iVar11 + 0x334);
                        fStack_94 = *(float *)(iVar11 + 0x338);
                        fStack_90 = *(float *)(iVar11 + 0x33c);
                        fStack_8c = *(float *)(iVar11 + 0x340);
                        fStack_88 = *(float *)(iVar11 + 0x344);
                        fStack_84 = *(float *)(iVar11 + 0x348);
                        pfVar9 = (float *)(iVar11 + 0x308);
                        fStack_80 = *(float *)(iVar11 + 0x34c);
                        fStack_7c = *(float *)(iVar11 + 0x350);
                        uStack_78 = *(undefined4 *)(iVar11 + 0x354);
                        uStack_74 = *(undefined4 *)(iVar11 + 0x358);
                        uStack_70 = *(undefined4 *)(iVar11 + 0x35c);
                      }
                      fStack_c4 = *pfVar9;
                      fStack_c0 = pfVar9[1];
                      fStack_bc = pfVar9[2];
                      fStack_b8 = pfVar9[3];
                      fStack_b4 = pfVar9[4];
                      fStack_b0 = pfVar9[5];
                      fStack_ac = pfVar9[6];
                      fStack_a8 = pfVar9[7];
                      fStack_a4 = pfVar9[8];
                      fStack_a0 = pfVar9[9];
                      fStack_9c = pfVar9[10];
                      iVar11 = g2c_nema_vg_near_5177a4(&fStack_c4,&fStack_98);
                      if ((((iVar11 != 1) ||
                           (iVar11 = g2c_nema_vg_near_5177a4(&fStack_bc,&fStack_90), iVar11 != 1))
                          || (iVar11 = g2c_nema_vg_near_5177a4(&fStack_b4,&fStack_88), iVar11 != 1))
                         || (iVar11 = g2c_nema_vg_near_5177a4(&fStack_ac,&fStack_80), iVar11 != 1))
                      {
                        iVar11 = g2c_nema_vg_near2_51785c(&fStack_c4,&fStack_90);
                        if ((iVar11 != 0) ||
                           (iVar11 = g2c_nema_vg_near2_51785c(&fStack_98,&fStack_c4), iVar11 != 0))
                        goto LAB_005185da;
                        iVar11 = g2c_nema_vg_near2_51785c(&fStack_c4,&fStack_88);
                        if ((iVar11 == 0) &&
                           (iVar11 = g2c_nema_vg_near2_51785c(&fStack_98,&fStack_ac), iVar11 == 0))
                        {
                          iVar11 = (uint)(fStack_84 < fStack_8c) << 0x1f;
                          if (fStack_c0 < fStack_8c) {
                            if (iVar11 < 0) goto LAB_005186ea;
                          }
                          else if (-1 < iVar11) goto LAB_005186ea;
LAB_005185da:
                          fStack_d0 = fStack_80;
                          fStack_d4 = fStack_7c;
                          fStack_d8 = fStack_b4;
                          fStack_dc = fStack_b0;
                          fVar29 = fStack_90;
                          fVar16 = fStack_8c;
                          fVar21 = fStack_c4;
                          fVar30 = fStack_c0;
                          fVar22 = fStack_ac;
                          fVar31 = fStack_a8;
                          fVar27 = fStack_88;
                          fVar19 = fStack_84;
                        }
                        else {
LAB_005186ea:
                          fStack_d4 = fStack_94;
                          fStack_d0 = fStack_98;
                          fStack_d8 = fStack_bc;
                          fStack_dc = fStack_b8;
                          fVar29 = fStack_88;
                          fVar16 = fStack_84;
                          fVar21 = fStack_ac;
                          fVar30 = fStack_a8;
                          fVar22 = fStack_c4;
                          fVar31 = fStack_c0;
                          fVar27 = fStack_90;
                          fVar19 = fStack_8c;
                        }
                        fStack_e4 = *(g2c_nvg_zero_pair_1);
                        fStack_e0 = (g2c_nvg_zero_pair_1)[1];
                        fStack_fc = *(g2c_nvg_zero_pair_2);
                        fStack_f8 = (g2c_nvg_zero_pair_2)[1];
                        iVar11 = g2c_nema_vg_cubic_approx_522f50
                                           (fVar27,fVar19,fVar29,fVar16,fVar22,fVar31,fVar21,fVar30,
                                            &fStack_e4,&fStack_e0);
                        iVar7 = g2c_nema_vg_cubic_approx_522f50
                                          (fStack_d0,fStack_d4,fVar27,fVar19,fVar22,fVar31,fStack_d8
                                           ,fStack_dc,&fStack_fc,&fStack_f8);
                        fVar29 = g2c_nema_vg_sqrt_524218
                                           ((fStack_fc - fStack_e4) * (fStack_fc - fStack_e4) +
                                            (fStack_f8 - fStack_e0) * (fStack_f8 - fStack_e0));
                        iVar8 = *piVar5;
                        if (((*(float *)(iVar8 + 0x2dc) * *(float *)(iVar8 + 0x2d8) < fVar29) ||
                            (iVar7 == 0)) || (iVar11 == 0)) {
                          fVar27 = fStack_cc;
                          fVar19 = fStack_c8;
                          fVar22 = fVar20;
                          fVar31 = fVar26;
                          if (-1 < (int)((uint)*(byte *)(iVar8 + 0x7d) << 0x1b)) {
                            uVar12 = audio_uart_nema_stencil_save_52266e(1,0,1,0);
                            fVar27 = fStack_cc;
                            fVar19 = fStack_c8;
                          }
                        }
                        else {
                          fVar32 = fStack_e4;
                          fVar23 = fStack_e0;
                          fVar24 = fStack_fc;
                          fVar25 = fStack_f8;
                          if (-1 < (int)((uint)*(byte *)(iVar8 + 0x7d) << 0x1b)) {
                            uVar12 = audio_uart_nema_stencil_save_52266e(0,1,1,0);
                            fVar32 = fStack_e4;
                            fVar23 = fStack_e0;
                            fVar24 = fStack_fc;
                            fVar25 = fStack_f8;
                          }
                        }
                        g2c_nema_vg_emit_verts_516b34
                                  (fVar32,fVar23,fVar27,fVar19,fVar24,fVar25,fVar22,fVar31);
                        bVar2 = *(byte *)(*piVar5 + 0x7d);
                        goto joined_r0x005183a0;
                      }
                    }
                  }
                }
              }
              iVar11 = *piVar5;
              if ((0.0f < *(float *)(iVar11 + 0x158)) && (*(int *)(iVar11 + 0x128) == 1)) {
                if ((ABS(*(float *)(iVar11 + 0x15c) * fVar17 -
                                     *(float *)(iVar11 + 0x160) * fVar18) < (0.05000000447034836f))) {
                  uVar35 = *(undefined8 *)(iVar11 + 0x140);
                  uVar33 = *(undefined8 *)(iVar11 + 0x148);
                }
                else {
                  uVar4 = *(undefined8 *)(iVar11 + 0x140);
                  fVar27 = (float)g2c_bits_to_float((uint)(uVar35));
                  fVar29 = (float)g2c_bits_to_float((uint)(((ulonglong)uVar35 >> 0x20)));
                  fVar20 = (float)g2c_bits_to_float((uint)(uVar33));
                  fVar26 = (float)g2c_bits_to_float((uint)(((ulonglong)uVar33 >> 0x20)));
                  if (*(int *)(iVar11 + 0x110) != 0) {
                    cVar1 = *(char *)(iVar11 + 0x2e2);
                    uVar12 = 0;
                    fVar25 = (float)g2c_bits_to_float((uint)(((ulonglong)*(undefined8 *)(iVar11 + 0x148) >> 0x20)));
                    fVar23 = (float)g2c_bits_to_float((uint)(((ulonglong)uVar4 >> 0x20)));
                    fVar24 = (float)g2c_bits_to_float((uint)(*(undefined8 *)(iVar11 + 0x148)));
                    fVar32 = (float)g2c_bits_to_float((uint)(uVar4));
                    if ((cVar1 == '\0') || (*(int *)(iVar11 + 0x118) != 0)) {
                      if (-1 < (int)((uint)*(byte *)(iVar11 + 0x7d) << 0x1b)) {
                        uVar12 = audio_uart_nema_stencil_save_52266e(1,0,1,0);
                      }
                      g2c_nema_vg_emit_verts_516b34
                                (fVar32,fVar23,fVar27,fVar29,fVar24,fVar25,fVar20,fVar26);
                      bVar2 = *(byte *)(*piVar5 + 0x7d);
joined_r0x00518834:
                      if (-1 < (int)((uint)bVar2 << 0x1b)) {
                        audio_uart_nema_stencil_restore_5226b2(uVar12);
                      }
                    }
                    else if (cVar1 == '\x02') {
                      fStack_fc = *(g2c_nvg_zero_pair_0);
                      fStack_f8 = (g2c_nvg_zero_pair_0)[1];
                      iVar11 = g2c_nema_vg_cubic_approx_522f50
                                         (fVar32,fVar23,fVar24,fVar25,fVar27,fVar29,fVar20,fVar26,
                                          &fStack_fc,&fStack_f8);
                      if (iVar11 != 0) {
                        iVar11 = *piVar5;
                        fVar20 = audio_uart_float_sqrt_4397a8
                                           (*(float *)(iVar11 + 0xec) * *(float *)(iVar11 + 0xec) +
                                            *(float *)(iVar11 + 0xf0) * *(float *)(iVar11 + 0xf0));
                        fVar26 = audio_uart_float_sqrt_4397a8
                                           (*(float *)(iVar11 + 0xf8) * *(float *)(iVar11 + 0xf8) +
                                            *(float *)(iVar11 + 0xfc) * *(float *)(iVar11 + 0xfc));
                        fVar20 = ABS(fVar20);
                        /* stock 0x51891c vcmp; ittt lt; vcmplt 0x51892e; iteee lt; movlt r6,#0 / movge r6,#1 (0x518938).
                           LT includes unordered, so r6 = either ordered >= K (wave19 address-verified: Ghidra label joined_r0x00518834 above = stock fallthrough of bl 0x516b34 at 0x518824, which is the last emit before this vcmp). */
                        bVar13 = (fVar20 >= (2.000000238418579f) || ABS(fVar26) >= (2.000000238418579f));
                        if (bVar13) {
                          g2c_nema_vg_set_flag_522622(1);
                        }
                        fVar20 = *(float *)(*piVar5 + 0x2d8) * 0.5f;
                        if ((int)((uint)*(byte *)(*piVar5 + 0x7d) << 0x1b) < 0) {
                          g2c_nema_vg_move_to_522fb4(fStack_fc,fStack_f8,fVar20);
                        }
                        else {
                          g2c_nema_vg_line_to_523284(fStack_fc,fStack_f8,fVar20);
                        }
                        if (bVar13) {
                          g2c_nema_vg_set_flag_522622(0);
                        }
                      }
                    }
                    else {
                      if (cVar1 != '\x01') {
LAB_005184da:
                        *(undefined4 *)(iVar11 + 0x114) = 0;
                        *(undefined4 *)(iVar11 + 0x118) = 0;
                        audio_uart_nema_vg_set_error_51565c(0x1000000);
                        iVar10 = *piVar5;
                        *(undefined4 *)(iVar10 + 0x114) = 0;
                        *(undefined4 *)(iVar10 + 0x118) = 0;
                        audio_uart_nema_vg_set_error_51565c(0x1000000);
                        return 0x1000000;
                      }
                      if (*(char *)(iVar11 + 0x2e4) == '\0') {
                        fStack_a8 = *(float *)(iVar11 + 0x138);
                        fStack_a4 = *(float *)(iVar11 + 0x13c);
                        fStack_a0 = *(float *)(iVar11 + 0x140);
                        fStack_9c = *(float *)(iVar11 + 0x144);
                        fStack_98 = *(float *)(iVar11 + 0x148);
                        fStack_94 = *(float *)(iVar11 + 0x14c);
                        pfVar9 = (float *)(iVar11 + 400);
                        fStack_90 = *(float *)(iVar11 + 0x150);
                        fStack_8c = *(float *)(iVar11 + 0x154);
                        fStack_88 = *(float *)(iVar11 + 0x158);
                        fStack_84 = *(float *)(iVar11 + 0x15c);
                        fStack_80 = *(float *)(iVar11 + 0x160);
                      }
                      else {
                        fStack_a8 = *(float *)(iVar11 + 0x334);
                        fStack_a4 = *(float *)(iVar11 + 0x338);
                        fStack_a0 = *(float *)(iVar11 + 0x33c);
                        fStack_9c = *(float *)(iVar11 + 0x340);
                        fStack_98 = *(float *)(iVar11 + 0x344);
                        fStack_94 = *(float *)(iVar11 + 0x348);
                        pfVar9 = (float *)(iVar11 + 0x308);
                        fStack_90 = *(float *)(iVar11 + 0x34c);
                        fStack_8c = *(float *)(iVar11 + 0x350);
                        fStack_88 = *(float *)(iVar11 + 0x354);
                        fStack_84 = *(float *)(iVar11 + 0x358);
                        fStack_80 = *(float *)(iVar11 + 0x35c);
                      }
                      fStack_d4 = *pfVar9;
                      fStack_d0 = pfVar9[1];
                      fStack_cc = pfVar9[2];
                      fStack_c8 = pfVar9[3];
                      fStack_c4 = pfVar9[4];
                      fStack_c0 = pfVar9[5];
                      fStack_bc = pfVar9[6];
                      fStack_b8 = pfVar9[7];
                      fStack_b4 = pfVar9[8];
                      fStack_b0 = pfVar9[9];
                      fStack_ac = pfVar9[10];
                      iVar11 = g2c_nema_vg_near_5177a4(&fStack_d4,&fStack_a8);
                      if ((((iVar11 != 1) ||
                           (iVar11 = g2c_nema_vg_near_5177a4(&fStack_cc,&fStack_a0), iVar11 != 1))
                          || (iVar11 = g2c_nema_vg_near_5177a4(&fStack_c4,&fStack_98), iVar11 != 1))
                         || (iVar11 = g2c_nema_vg_near_5177a4(&fStack_bc,&fStack_90), iVar11 != 1))
                      {
                        iVar11 = g2c_nema_vg_near2_51785c(&fStack_d4,&fStack_a0);
                        if ((iVar11 != 0) ||
                           (iVar11 = g2c_nema_vg_near2_51785c(&fStack_a8,&fStack_d4), iVar11 != 0))
                        goto LAB_00518a12;
                        iVar11 = g2c_nema_vg_near2_51785c(&fStack_d4,&fStack_98);
                        if ((iVar11 == 0) &&
                           (iVar11 = g2c_nema_vg_near2_51785c(&fStack_a8,&fStack_bc), iVar11 == 0))
                        {
                          iVar11 = (uint)(fStack_94 < fStack_9c) << 0x1f;
                          if (fStack_d0 < fStack_9c) {
                            if (iVar11 < 0) goto LAB_00518b36;
                          }
                          else if (-1 < iVar11) goto LAB_00518b36;
LAB_00518a12:
                          fStack_d8 = fStack_90;
                          fStack_dc = fStack_8c;
                          fVar16 = fStack_a0;
                          fVar21 = fStack_9c;
                          fVar30 = fStack_d4;
                          h_00 = fStack_d0;
                          h_01 = fStack_c0;
                          g_00 = fStack_c4;
                          fVar31 = fStack_bc;
                          f_00 = fStack_b8;
                          fVar19 = fStack_98;
                          fVar22 = fStack_94;
                        }
                        else {
LAB_00518b36:
                          fStack_dc = fStack_a4;
                          fStack_d8 = fStack_a8;
                          fVar16 = fStack_98;
                          fVar21 = fStack_94;
                          fVar30 = fStack_bc;
                          h_00 = fStack_b8;
                          h_01 = fStack_c8;
                          g_00 = fStack_cc;
                          fVar31 = fStack_d4;
                          f_00 = fStack_d0;
                          fVar19 = fStack_a0;
                          fVar22 = fStack_9c;
                        }
                        fStack_e4 = *(g2c_nvg_zero_pair_1);
                        fStack_e0 = (g2c_nvg_zero_pair_1)[1];
                        fStack_fc = *(g2c_nvg_zero_pair_2);
                        fStack_f8 = (g2c_nvg_zero_pair_2)[1];
                        iVar11 = g2c_nema_vg_cubic_approx_522f50
                                           (fVar19,fVar22,fVar16,fVar21,fVar31,f_00,fVar30,h_00,
                                            &fStack_e4,&fStack_e0);
                        iVar7 = g2c_nema_vg_cubic_approx_522f50
                                          (fStack_d8,fStack_dc,fVar19,fVar22,fVar31,f_00,g_00,h_01,
                                           &fStack_fc,&fStack_f8);
                        fVar16 = g2c_nema_vg_sqrt_524218
                                           ((fStack_fc - fStack_e4) * (fStack_fc - fStack_e4) +
                                            (fStack_f8 - fStack_e0) * (fStack_f8 - fStack_e0));
                        iVar8 = *piVar5;
                        if (((*(float *)(iVar8 + 0x2dc) * *(float *)(iVar8 + 0x2d8) < fVar16) ||
                            (iVar7 == 0)) || (iVar11 == 0)) {
                          fVar19 = fVar27;
                          fVar22 = fVar29;
                          fVar31 = fVar20;
                          f_00 = fVar26;
                          if (-1 < (int)((uint)*(byte *)(iVar8 + 0x7d) << 0x1b)) {
                            uVar12 = audio_uart_nema_stencil_save_52266e(1,0,1,0);
                          }
                        }
                        else {
                          fVar32 = fStack_e4;
                          fVar23 = fStack_e0;
                          fVar24 = fStack_fc;
                          fVar25 = fStack_f8;
                          if (-1 < (int)((uint)*(byte *)(iVar8 + 0x7d) << 0x1b)) {
                            uVar12 = audio_uart_nema_stencil_save_52266e(0,1,1,0);
                            fVar32 = fStack_e4;
                            fVar23 = fStack_e0;
                            fVar24 = fStack_fc;
                            fVar25 = fStack_f8;
                          }
                        }
                        g2c_nema_vg_emit_verts_516b34
                                  (fVar32,fVar23,fVar19,fVar22,fVar24,fVar25,fVar31,f_00);
                        bVar2 = *(byte *)(*piVar5 + 0x7d);
                        goto joined_r0x00518834;
                      }
                    }
                  }
                }
              }
              iVar11 = *piVar5;
              *(int *)(iVar11 + 0x128) = *(int *)(iVar11 + 0x128) + 1;
              uVar36 = (undefined4)((ulonglong)uVar35 >> 0x20);
              uVar34 = (undefined4)((ulonglong)uVar33 >> 0x20);
              if (*(float *)(iVar11 + 0x158) == 0.0f) {
                *(int *)(iVar11 + 0x138) = (int)uVar35;
                *(undefined4 *)(iVar11 + 0x13c) = uVar36;
                iVar11 = *piVar5;
                *(float *)(iVar11 + 0x140) = fStack_ec;
                *(float *)(iVar11 + 0x144) = fStack_e8;
                iVar11 = *piVar5;
                *(float *)(iVar11 + 0x148) = fStack_f4;
                *(float *)(iVar11 + 0x14c) = fStack_f0;
                iVar11 = *piVar5;
                *(int *)(iVar11 + 0x150) = (int)uVar33;
                *(undefined4 *)(iVar11 + 0x154) = uVar34;
                iVar11 = *piVar5;
                *(float *)(iVar11 + 0x158) = fVar15;
                *(float *)(iVar11 + 0x15c) = fVar18;
                *(float *)(iVar11 + 0x160) = fVar17;
              }
              else {
                *(int *)(iVar11 + 0x164) = (int)uVar35;
                *(undefined4 *)(iVar11 + 0x168) = uVar36;
                iVar11 = *piVar5;
                *(float *)(iVar11 + 0x16c) = fStack_ec;
                *(float *)(iVar11 + 0x170) = fStack_e8;
                iVar11 = *piVar5;
                *(float *)(iVar11 + 0x174) = fStack_f4;
                *(float *)(iVar11 + 0x178) = fStack_f0;
                iVar11 = *piVar5;
                *(int *)(iVar11 + 0x17c) = (int)uVar33;
                *(undefined4 *)(iVar11 + 0x180) = uVar34;
                iVar11 = *piVar5;
                *(float *)(iVar11 + 0x184) = fVar15;
                *(float *)(iVar11 + 0x188) = fVar18;
                *(float *)(iVar11 + 0x18c) = fVar17;
              }
            }
            audio_uart_nema_stencil_restore_5226b2(uVar6);
            bVar13 = false;
          }
        }
        else {
          fVar17 = c_00 - fStack_104;
          fVar18 = fVar28 - fStack_100;
          fVar15 = fVar17 * fVar17 + fVar18 * fVar18;
          if ((ABS(fVar15) < (1.0000000656873453e-05f))) {
            *(float *)(iVar11 + 0x198) = fStack_104;
            *(float *)(iVar11 + 0x19c) = fStack_100 + *(float *)(iVar11 + 0x130) * -0.5f;
            *(float *)(iVar11 + 0x1a0) = fStack_104;
            *(float *)(iVar11 + 0x1a4) = fStack_100 + *(float *)(iVar11 + 0x130) * 0.5f;
            *(undefined4 *)(iVar11 + 400) = *(undefined4 *)(iVar11 + 0x198);
            *(undefined4 *)(iVar11 + 0x194) = *(undefined4 *)(iVar11 + 0x19c);
            iVar11 = *piVar5;
            *(undefined4 *)(iVar11 + 0x1a8) = *(undefined4 *)(iVar11 + 0x1a0);
            *(undefined4 *)(iVar11 + 0x1ac) = *(undefined4 *)(iVar11 + 0x1a4);
          }
          else {
            fVar15 = audio_uart_float_sqrt_4397a8(fVar15);
            fVar17 = fVar17 * (1.0f / fVar15);
            fVar18 = fVar18 * (1.0f / fVar15);
            fVar20 = *(float *)(iVar11 + 0x130) * 0.5f * fVar18;
            fVar27 = fStack_104 - fVar20;
            fVar26 = *(float *)(iVar11 + 0x134) * 0.5f * fVar17;
            fVar29 = fVar26 + fStack_100;
            uVar35 = CONCAT44(g2c_float_to_bits(fVar29),g2c_float_to_bits(fVar27));
            *(float *)(iVar11 + 400) = fVar27;
            *(float *)(iVar11 + 0x194) = fVar29;
            iVar11 = *piVar5;
            fVar32 = c_00 - fVar20;
            fVar23 = fVar26 + fVar28;
            *(float *)(iVar11 + 0x198) = fVar32;
            *(float *)(iVar11 + 0x19c) = fVar23;
            iVar11 = *piVar5;
            fVar24 = fVar20 + c_00;
            fVar25 = fVar28 - fVar26;
            *(float *)(iVar11 + 0x1a0) = fVar24;
            *(float *)(iVar11 + 0x1a4) = fVar25;
            iVar11 = *piVar5;
            fVar20 = fVar20 + fStack_104;
            fVar26 = fStack_100 - fVar26;
            uVar33 = CONCAT44(g2c_float_to_bits(fVar26),g2c_float_to_bits(fVar20));
            *(float *)(iVar11 + 0x1a8) = fVar20;
            *(float *)(iVar11 + 0x1ac) = fVar26;
            iVar11 = *piVar5;
            if (*(int *)(iVar11 + 0x110) == 0) {
              uVar6 = audio_uart_nema_stencil_restore_5226b2(*(uint *)(iVar11 + 0x8c));
              g2c_nema_vg_emit_verts_516b34(fVar27,fVar29,fVar32,fVar23,fVar24,fVar25,fVar20,fVar26)
              ;
            }
            else {
              bVar14 = -1 < (int)((uint)*(byte *)(iVar11 + 0x7d) << 0x1b);
              uVar6 = audio_uart_nema_stencil_save_52266e((uint)bVar14,0,(uint)bVar14,0);
              iVar11 = *piVar5;
              if (0.0f < *(float *)(iVar11 + 0x184)) {
                g2c_nema_vg_emit_verts_516b34
                          (*(float *)(iVar11 + 0x164),*(float *)(iVar11 + 0x168),
                           *(float *)(iVar11 + 0x16c),*(float *)(iVar11 + 0x170),
                           *(float *)(iVar11 + 0x174),*(float *)(iVar11 + 0x178),
                           *(float *)(iVar11 + 0x17c),*(float *)(iVar11 + 0x180));
                iVar11 = *piVar5;
                if ((ABS(*(float *)(iVar11 + 0x188) * fVar18 -
                                     *(float *)(iVar11 + 0x18c) * fVar17) < (0.05000000447034836f))) {
                  uVar35 = *(undefined8 *)(iVar11 + 0x16c);
                  uVar33 = *(undefined8 *)(iVar11 + 0x174);
                }
                else {
                  g2c_nema_vg_emit_verts_516b34
                            (*(float *)(iVar11 + 0x16c),*(float *)(iVar11 + 0x170),fVar27,fVar29,
                             *(float *)(iVar11 + 0x174),*(float *)(iVar11 + 0x178),fVar20,fVar26);
                }
              }
              iVar11 = *piVar5;
              if ((0.0f < *(float *)(iVar11 + 0x158)) && (*(int *)(iVar11 + 0x128) == 1)) {
                if ((ABS(*(float *)(iVar11 + 0x15c) * fVar18 -
                                     *(float *)(iVar11 + 0x160) * fVar17) < (0.05000000447034836f))) {
                  uVar35 = *(undefined8 *)(iVar11 + 0x140);
                  uVar33 = *(undefined8 *)(iVar11 + 0x148);
                }
                else {
                  g2c_nema_vg_emit_verts_516b34
                            (*(float *)(iVar11 + 0x140),*(float *)(iVar11 + 0x144),(float)g2c_bits_to_float((uint)(uVar35)),
                             (float)g2c_bits_to_float((uint)(((ulonglong)uVar35 >> 0x20))),*(float *)(iVar11 + 0x148),
                             *(float *)(iVar11 + 0x14c),(float)g2c_bits_to_float((uint)(uVar33)),
                             (float)g2c_bits_to_float((uint)(((ulonglong)uVar33 >> 0x20))));
                }
              }
              iVar11 = *piVar5;
              *(int *)(iVar11 + 0x128) = *(int *)(iVar11 + 0x128) + 1;
              uVar36 = (undefined4)((ulonglong)uVar35 >> 0x20);
              uVar34 = (undefined4)((ulonglong)uVar33 >> 0x20);
              if (*(float *)(iVar11 + 0x158) == 0.0f) {
                *(int *)(iVar11 + 0x138) = (int)uVar35;
                *(undefined4 *)(iVar11 + 0x13c) = uVar36;
                iVar11 = *piVar5;
                *(float *)(iVar11 + 0x140) = fVar32;
                *(float *)(iVar11 + 0x144) = fVar23;
                iVar11 = *piVar5;
                *(float *)(iVar11 + 0x148) = fVar24;
                *(float *)(iVar11 + 0x14c) = fVar25;
                iVar11 = *piVar5;
                *(int *)(iVar11 + 0x150) = (int)uVar33;
                *(undefined4 *)(iVar11 + 0x154) = uVar34;
                iVar11 = *piVar5;
                *(float *)(iVar11 + 0x158) = fVar15;
                *(float *)(iVar11 + 0x15c) = fVar17;
                *(float *)(iVar11 + 0x160) = fVar18;
              }
              else {
                *(int *)(iVar11 + 0x164) = (int)uVar35;
                *(undefined4 *)(iVar11 + 0x168) = uVar36;
                iVar11 = *piVar5;
                *(float *)(iVar11 + 0x16c) = fVar32;
                *(float *)(iVar11 + 0x170) = fVar23;
                iVar11 = *piVar5;
                *(float *)(iVar11 + 0x174) = fVar24;
                *(float *)(iVar11 + 0x178) = fVar25;
                iVar11 = *piVar5;
                *(int *)(iVar11 + 0x17c) = (int)uVar33;
                *(undefined4 *)(iVar11 + 0x180) = uVar34;
                iVar11 = *piVar5;
                *(float *)(iVar11 + 0x184) = fVar15;
                *(float *)(iVar11 + 0x188) = fVar17;
                *(float *)(iVar11 + 0x18c) = fVar18;
              }
            }
            audio_uart_nema_stencil_restore_5226b2(uVar6);
          }
        }
        fVar17 = fStack_120 - c_00;
        fVar18 = fStack_11c - fVar28;
        fVar15 = fVar17 * fVar17 + fVar18 * fVar18;
        if ((ABS(fVar15) < (1.0000000656873453e-05f))) {
          iVar11 = *piVar5;
          *(float *)(iVar11 + 0x198) = c_00;
          *(float *)(iVar11 + 0x19c) = fVar28 + *(float *)(iVar11 + 0x130) * -0.5f;
          *(float *)(iVar11 + 0x1a0) = c_00;
          *(float *)(iVar11 + 0x1a4) = fVar28 + *(float *)(iVar11 + 0x130) * 0.5f;
          *(undefined4 *)(iVar11 + 400) = *(undefined4 *)(iVar11 + 0x198);
          *(undefined4 *)(iVar11 + 0x194) = *(undefined4 *)(iVar11 + 0x19c);
          iVar11 = *piVar5;
          *(undefined4 *)(iVar11 + 0x1a8) = *(undefined4 *)(iVar11 + 0x1a0);
          *(undefined4 *)(iVar11 + 0x1ac) = *(undefined4 *)(iVar11 + 0x1a4);
        }
        else {
          fVar15 = audio_uart_float_sqrt_4397a8(fVar15);
          iVar11 = *piVar5;
          fVar17 = fVar17 * (1.0f / fVar15);
          fVar18 = fVar18 * (1.0f / fVar15);
          fVar20 = *(float *)(iVar11 + 0x130) * 0.5f * fVar18;
          fVar27 = c_00 - fVar20;
          fVar26 = *(float *)(iVar11 + 0x134) * 0.5f * fVar17;
          fVar29 = fVar26 + fVar28;
          uVar35 = CONCAT44(g2c_float_to_bits(fVar29),g2c_float_to_bits(fVar27));
          *(float *)(iVar11 + 400) = fVar27;
          *(float *)(iVar11 + 0x194) = fVar29;
          iVar11 = *piVar5;
          fVar32 = fStack_120 - fVar20;
          fVar23 = fVar26 + fStack_11c;
          *(float *)(iVar11 + 0x198) = fVar32;
          *(float *)(iVar11 + 0x19c) = fVar23;
          iVar11 = *piVar5;
          fVar24 = fVar20 + fStack_120;
          fVar25 = fStack_11c - fVar26;
          *(float *)(iVar11 + 0x1a0) = fVar24;
          *(float *)(iVar11 + 0x1a4) = fVar25;
          iVar11 = *piVar5;
          fVar20 = fVar20 + c_00;
          fVar28 = fVar28 - fVar26;
          uVar33 = CONCAT44(g2c_float_to_bits(fVar28),g2c_float_to_bits(fVar20));
          *(float *)(iVar11 + 0x1a8) = fVar20;
          *(float *)(iVar11 + 0x1ac) = fVar28;
          iVar11 = *piVar5;
          if (*(int *)(iVar11 + 0x110) == 0) {
            uVar6 = audio_uart_nema_stencil_restore_5226b2(*(uint *)(iVar11 + 0x8c));
            g2c_nema_vg_emit_verts_516b34(fVar27,fVar29,fVar32,fVar23,fVar24,fVar25,fVar20,fVar28);
          }
          else {
            bVar14 = -1 < (int)((uint)*(byte *)(iVar11 + 0x7d) << 0x1b);
            uVar6 = audio_uart_nema_stencil_save_52266e((uint)bVar14,0,(uint)bVar14,0);
            iVar11 = *piVar5;
            if (0.0f < *(float *)(iVar11 + 0x184)) {
              g2c_nema_vg_emit_verts_516b34
                        (*(float *)(iVar11 + 0x164),*(float *)(iVar11 + 0x168),
                         *(float *)(iVar11 + 0x16c),*(float *)(iVar11 + 0x170),
                         *(float *)(iVar11 + 0x174),*(float *)(iVar11 + 0x178),
                         *(float *)(iVar11 + 0x17c),*(float *)(iVar11 + 0x180));
              iVar11 = *piVar5;
              if ((ABS(*(float *)(iVar11 + 0x188) * fVar18 -
                                   *(float *)(iVar11 + 0x18c) * fVar17) < (0.05000000447034836f))) {
                uVar35 = *(undefined8 *)(iVar11 + 0x16c);
                uVar33 = *(undefined8 *)(iVar11 + 0x174);
              }
              else {
                g2c_nema_vg_emit_verts_516b34
                          (*(float *)(iVar11 + 0x16c),*(float *)(iVar11 + 0x170),fVar27,fVar29,
                           *(float *)(iVar11 + 0x174),*(float *)(iVar11 + 0x178),fVar20,fVar28);
              }
            }
            iVar11 = *piVar5;
            if ((0.0f < *(float *)(iVar11 + 0x158)) && (*(int *)(iVar11 + 0x128) == 1)) {
              if ((ABS(*(float *)(iVar11 + 0x15c) * fVar18 -
                                   *(float *)(iVar11 + 0x160) * fVar17) < (0.05000000447034836f))
                 ) {
                uVar35 = *(undefined8 *)(iVar11 + 0x140);
                uVar33 = *(undefined8 *)(iVar11 + 0x148);
              }
              else {
                g2c_nema_vg_emit_verts_516b34
                          (*(float *)(iVar11 + 0x140),*(float *)(iVar11 + 0x144),(float)g2c_bits_to_float((uint)(uVar35)),
                           (float)g2c_bits_to_float((uint)(((ulonglong)uVar35 >> 0x20))),*(float *)(iVar11 + 0x148),
                           *(float *)(iVar11 + 0x14c),(float)g2c_bits_to_float((uint)(uVar33)),
                           (float)g2c_bits_to_float((uint)(((ulonglong)uVar33 >> 0x20))));
              }
            }
            iVar11 = *piVar5;
            *(int *)(iVar11 + 0x128) = *(int *)(iVar11 + 0x128) + 1;
            uVar36 = (undefined4)((ulonglong)uVar35 >> 0x20);
            uVar34 = (undefined4)((ulonglong)uVar33 >> 0x20);
            if (*(float *)(iVar11 + 0x158) == 0.0f) {
              *(int *)(iVar11 + 0x138) = (int)uVar35;
              *(undefined4 *)(iVar11 + 0x13c) = uVar36;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x140) = fVar32;
              *(float *)(iVar11 + 0x144) = fVar23;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x148) = fVar24;
              *(float *)(iVar11 + 0x14c) = fVar25;
              iVar11 = *piVar5;
              *(int *)(iVar11 + 0x150) = (int)uVar33;
              *(undefined4 *)(iVar11 + 0x154) = uVar34;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x158) = fVar15;
              *(float *)(iVar11 + 0x15c) = fVar17;
              *(float *)(iVar11 + 0x160) = fVar18;
            }
            else {
              *(int *)(iVar11 + 0x164) = (int)uVar35;
              *(undefined4 *)(iVar11 + 0x168) = uVar36;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x16c) = fVar32;
              *(float *)(iVar11 + 0x170) = fVar23;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x174) = fVar24;
              *(float *)(iVar11 + 0x178) = fVar25;
              iVar11 = *piVar5;
              *(int *)(iVar11 + 0x17c) = (int)uVar33;
              *(undefined4 *)(iVar11 + 0x180) = uVar34;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x184) = fVar15;
              *(float *)(iVar11 + 0x188) = fVar17;
              *(float *)(iVar11 + 0x18c) = fVar18;
            }
          }
          audio_uart_nema_stencil_restore_5226b2(uVar6);
        }
      }
      else {
        uVar6 = g2c_nema_vg_path_bounds_5639e8(fStack_104,fStack_100,c_00,fVar28);
        if ((uVar6 != 0) ||
           (uVar6 = g2c_nema_vg_path_bounds_5639e8(c_00,fVar28,fStack_120,fStack_11c), uVar6 != 0))
        {
          iVar10 = *piVar5;
          *(undefined4 *)(iVar10 + 0x114) = 0;
          *(undefined4 *)(iVar10 + 0x118) = 0;
          audio_uart_nema_vg_set_error_51565c(uVar6);
          return uVar6;
        }
      }
      iVar11 = *piVar5;
      if (*(int *)(iVar11 + 700) != 0) {
        iVar7 = *(int *)(iVar11 + 700) + -1;
        *(int *)(iVar11 + 700) = iVar7;
        iVar11 = iVar11 + iVar7 * 0x18;
        fStack_10c = *(float *)(iVar11 + 0x1cc);
        fStack_110 = *(float *)(iVar11 + 0x1d0);
        fStack_114 = *(float *)(iVar11 + 0x1d4);
        fStack_118 = *(float *)(iVar11 + 0x1d8);
        fStack_104 = fStack_120;
        fStack_100 = fStack_11c;
        fStack_120 = *(float *)(iVar11 + 0x1dc);
        fStack_11c = *(float *)(iVar11 + 0x1e0);
      }
    }
    else {
      bVar3 = false;
      *(float *)(iVar11 + *(int *)(iVar11 + 700) * 0x18 + 0x1cc) = fVar29;
      iVar10 = iVar10 + 1;
      *(float *)(iVar11 + *(int *)(iVar11 + 700) * 0x18 + 0x1d0) = fVar32;
      *(float *)(iVar11 + *(int *)(iVar11 + 700) * 0x18 + 0x1d4) = fVar18;
      *(float *)(iVar11 + *(int *)(iVar11 + 700) * 0x18 + 0x1d8) = fVar20;
      *(float *)(iVar11 + *(int *)(iVar11 + 700) * 0x18 + 0x1dc) = fStack_120;
      *(float *)(iVar11 + *(int *)(iVar11 + 700) * 0x18 + 0x1e0) = fStack_11c;
      *(int *)(iVar11 + 700) = *(int *)(iVar11 + 700) + 1;
      fStack_120 = c_00;
      fStack_11c = fVar28;
      fStack_118 = fVar27;
      fStack_114 = fVar26;
      fStack_110 = fVar17;
      fStack_10c = fVar15;
    }
    if (iVar10 == 0) {
      return 0;
    }
  } while( true );
}
#undef fStack_120
#undef fStack_11c
#undef fStack_118
#undef fStack_114
#undef fStack_110
#undef fStack_10c
#undef fStack_104
#undef fStack_100
#undef fStack_fc
#undef fStack_f8
#undef fStack_f4
#undef fStack_f0
#undef fStack_ec
#undef fStack_e8
#undef fStack_e4
#undef fStack_e0
#undef fStack_dc
#undef fStack_d8
#undef fStack_d4
#undef fStack_d0
#undef fStack_cc
#undef fStack_c8
#undef fStack_c4
#undef fStack_c0
#undef fStack_bc
#undef fStack_b8
#undef fStack_b4
#undef fStack_b0
#undef fStack_ac
#undef fStack_a8
#undef fStack_a4
#undef fStack_a0
#undef fStack_9c
#undef fStack_98
#undef fStack_94
#undef fStack_90
#undef fStack_8c
#undef fStack_88
#undef fStack_84
#undef fStack_80
#undef fStack_7c
#undef uStack_78
#undef uStack_74
#undef uStack_70


  

/* ---- lifted 0x519290 ---- */


uint g2c_nema_vg_fill_path_519290(float a,float b,float c,float d,float e,float f)

{
  char cVar1;
  byte bVar2;
  undefined8 uVar3;
  bool bVar4;
  int *piVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  float *pfVar9;
  int iVar10;
  int iVar11;
  uint uVar12;
  bool bVar13;
  float fVar14;
  float fVar15;
  float fVar16;
  float fVar17;
  float fVar18;
  float fVar19;
  float fVar20;
  float fVar21;
  float fVar22;
  float fVar23;
  float fVar24;
  float fVar25;
  float fVar26;
  float fVar27;
  float fVar28;
  float c_00;
  float fVar29;
  float fVar30;
  float fVar31;
  float h;
  float f_00;
  undefined8 uVar32;
  undefined4 uVar33;
  undefined8 uVar34;
  undefined4 uVar35;
  float h_00;
  float g;
  /* Stock frame of 0x519290 as one block: locals keep the entry-SP offsets Ghidra named them by
   * (X_Stack_NN at g2c_frame_519290[0x120-0xNN]) so &local passed to callees spans its stock neighbours. */
  unsigned char g2c_frame_519290[0x120] __attribute__((aligned(8)));
  typedef float __attribute__((may_alias)) g2c_fa_float;
#define fStack_120 (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0x120])
#define fStack_11c (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0x11c])
#define fStack_110 (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0x110])
#define fStack_10c (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0x10c])
#define fStack_108 (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0x108])
#define fStack_104 (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0x104])
#define fStack_fc (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0xfc])
#define fStack_f8 (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0xf8])
#define fStack_f4 (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0xf4])
#define fStack_f0 (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0xf0])
#define fStack_ec (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0xec])
#define fStack_e8 (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0xe8])
#define fStack_e4 (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0xe4])
#define fStack_e0 (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0xe0])
#define fStack_dc (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0xdc])
#define fStack_d8 (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0xd8])
#define fStack_d4 (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0xd4])
#define fStack_d0 (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0xd0])
#define fStack_cc (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0xcc])
#define fStack_c8 (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0xc8])
#define fStack_c4 (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0xc4])
#define fStack_c0 (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0xc0])
#define fStack_bc (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0xbc])
#define fStack_b8 (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0xb8])
#define fStack_b4 (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0xb4])
#define fStack_b0 (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0xb0])
#define fStack_ac (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0xac])
#define fStack_a8 (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0xa8])
#define fStack_a4 (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0xa4])
#define fStack_a0 (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0xa0])
#define fStack_9c (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0x9c])
#define fStack_98 (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0x98])
#define fStack_94 (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0x94])
#define fStack_90 (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0x90])
#define fStack_8c (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0x8c])
#define fStack_88 (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0x88])
#define fStack_84 (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0x84])
#define fStack_80 (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0x80])
#define fStack_7c (*(g2c_fa_float *)(void *)&g2c_frame_519290[0x120-0x7c])
  typedef undefined4 __attribute__((may_alias)) g2c_fa_undefined4;
#define uStack_78 (*(g2c_fa_undefined4 *)(void *)&g2c_frame_519290[0x120-0x78])
#define uStack_74 (*(g2c_fa_undefined4 *)(void *)&g2c_frame_519290[0x120-0x74])
#define uStack_70 (*(g2c_fa_undefined4 *)(void *)&g2c_frame_519290[0x120-0x70])
  
  piVar5 = (((int *)&audio_uart_nema_vg_context_cell));
  iVar10 = 1;
  bVar4 = true;
  fStack_120 = e;
  fStack_11c = f;
  fStack_110 = d;
  fStack_10c = c;
  fStack_108 = a;
  fStack_104 = b;
  do {
    fVar14 = (fStack_108 + fStack_10c) * 0.5f;
    fVar16 = (fStack_104 + fStack_110) * 0.5f;
    fVar17 = (fStack_10c + fStack_120) * 0.5f;
    fVar19 = (fStack_110 + fStack_11c) * 0.5f;
    fVar26 = (fVar16 + fVar19) * 0.5f;
    c_00 = (fVar14 + fVar17) * 0.5f;
    fVar27 = fStack_120 - fStack_108;
    fVar28 = fStack_11c - fStack_104;
    iVar11 = *piVar5;
    fVar29 = ABS((fStack_10c - fStack_120) * fVar28 + (fStack_11c - fStack_110) * fVar27);
    fVar27 = fVar27 * fVar27 + fVar28 * fVar28;
    fVar29 = fVar29 * fVar29;
    if ((int)((uint)*(byte *)(iVar11 + 0x7d) << 0x1f) < 0) {
      if (fVar27 < fVar29) goto LAB_00519384;
LAB_00519504:
      iVar10 = iVar10 + -1;
      if (*(char *)(iVar11 + 0x2e4) == '\0') {
        if (bVar4) {
          fVar17 = c_00 - fStack_108;
          fVar16 = fVar26 - fStack_104;
          fVar14 = fVar17 * fVar17 + fVar16 * fVar16;
          bVar4 = false;
          if (!(ABS(fVar14) < (1.0000000656873453e-05f))) {
            fVar14 = audio_uart_float_sqrt_4397a8(fVar14);
            fVar17 = fVar17 * (1.0f / fVar14);
            fVar16 = fVar16 * (1.0f / fVar14);
            fVar19 = *(float *)(iVar11 + 0x130) * 0.5f * fVar16;
            fVar28 = fStack_108 - fVar19;
            fVar27 = *(float *)(iVar11 + 0x134) * 0.5f * fVar17;
            fVar29 = fVar27 + fStack_104;
            uVar34 = CONCAT44(g2c_float_to_bits(fVar29),g2c_float_to_bits(fVar28));
            fStack_ec = c_00 - fVar19;
            fStack_e8 = fVar27 + fVar26;
            fStack_f4 = fVar19 + c_00;
            fStack_f0 = fVar26 - fVar27;
            *(float *)(iVar11 + 400) = fVar28;
            *(float *)(iVar11 + 0x194) = fVar29;
            fVar19 = fVar19 + fStack_108;
            iVar11 = *piVar5;
            fVar27 = fStack_104 - fVar27;
            uVar32 = CONCAT44(g2c_float_to_bits(fVar27),g2c_float_to_bits(fVar19));
            *(float *)(iVar11 + 0x198) = fStack_ec;
            *(float *)(iVar11 + 0x19c) = fStack_e8;
            iVar11 = *piVar5;
            *(float *)(iVar11 + 0x1a0) = fStack_f4;
            *(float *)(iVar11 + 0x1a4) = fStack_f0;
            iVar11 = *piVar5;
            *(float *)(iVar11 + 0x1a8) = fVar19;
            *(float *)(iVar11 + 0x1ac) = fVar27;
            iVar11 = *piVar5;
            if (*(int *)(iVar11 + 0x110) == 0) {
              uVar6 = audio_uart_nema_stencil_restore_5226b2(*(uint *)(iVar11 + 0x8c));
              g2c_nema_vg_emit_verts_516b34
                        (fVar28,fVar29,fStack_ec,fStack_e8,fStack_f4,fStack_f0,fVar19,fVar27);
              goto LAB_0051a2d0;
            }
            bVar13 = -1 < (int)((uint)*(byte *)(iVar11 + 0x7d) << 0x1b);
            uVar6 = audio_uart_nema_stencil_save_52266e((uint)bVar13,0,(uint)bVar13,0);
            iVar11 = *piVar5;
            if (0.0f < *(float *)(iVar11 + 0x184)) {
              g2c_nema_vg_emit_verts_516b34
                        (*(float *)(iVar11 + 0x164),*(float *)(iVar11 + 0x168),
                         *(float *)(iVar11 + 0x16c),*(float *)(iVar11 + 0x170),
                         *(float *)(iVar11 + 0x174),*(float *)(iVar11 + 0x178),
                         *(float *)(iVar11 + 0x17c),*(float *)(iVar11 + 0x180));
              iVar11 = *piVar5;
              if ((ABS(*(float *)(iVar11 + 0x188) * fVar16 -
                                   *(float *)(iVar11 + 0x18c) * fVar17) < (0.05000000447034836f))) {
                uVar34 = *(undefined8 *)(iVar11 + 0x16c);
                uVar32 = *(undefined8 *)(iVar11 + 0x174);
              }
              else {
                uVar3 = *(undefined8 *)(iVar11 + 0x16c);
                fStack_cc = fVar28;
                fStack_c8 = fVar29;
                if (*(int *)(iVar11 + 0x110) != 0) {
                  cVar1 = *(char *)(iVar11 + 0x2e2);
                  uVar12 = 0;
                  fVar25 = (float)g2c_bits_to_float((uint)(((ulonglong)*(undefined8 *)(iVar11 + 0x174) >> 0x20)));
                  fVar23 = (float)g2c_bits_to_float((uint)(((ulonglong)uVar3 >> 0x20)));
                  fVar24 = (float)g2c_bits_to_float((uint)(*(undefined8 *)(iVar11 + 0x174)));
                  fVar22 = (float)g2c_bits_to_float((uint)(uVar3));
                  if ((cVar1 == '\0') || (*(int *)(iVar11 + 0x118) != 0)) {
                    if (-1 < (int)((uint)*(byte *)(iVar11 + 0x7d) << 0x1b)) {
                      uVar12 = audio_uart_nema_stencil_save_52266e(1,0,1,0);
                    }
                    g2c_nema_vg_emit_verts_516b34
                              (fVar22,fVar23,fStack_cc,fStack_c8,fVar24,fVar25,fVar19,fVar27);
                    bVar2 = *(byte *)(*piVar5 + 0x7d);
joined_r0x00519764:
                    if (-1 < (int)((uint)bVar2 << 0x1b)) {
                      audio_uart_nema_stencil_restore_5226b2(uVar12);
                    }
                  }
                  else if (cVar1 == '\x02') {
                    fStack_fc = *(g2c_nvg_zero_pair_0);
                    fStack_f8 = (g2c_nvg_zero_pair_0)[1];
                    iVar11 = g2c_nema_vg_cubic_approx_522f50
                                       (fVar22,fVar23,fVar24,fVar25,fVar28,fVar29,fVar19,fVar27,
                                        &fStack_fc,&fStack_f8);
                    if (iVar11 != 0) {
                      iVar11 = *piVar5;
                      fVar19 = audio_uart_float_sqrt_4397a8
                                         (*(float *)(iVar11 + 0xec) * *(float *)(iVar11 + 0xec) +
                                          *(float *)(iVar11 + 0xf0) * *(float *)(iVar11 + 0xf0));
                      fVar27 = audio_uart_float_sqrt_4397a8
                                         (*(float *)(iVar11 + 0xf8) * *(float *)(iVar11 + 0xf8) +
                                          *(float *)(iVar11 + 0xfc) * *(float *)(iVar11 + 0xfc));
                      fVar19 = ABS(fVar19);
                      /* stock 0x519834 vcmp; ittt lt; vcmplt 0x519842; iteee lt; movlt r6,#0 / movge r6,#1 (0x51984c).
                         LT includes unordered, so r6 = either ordered >= K (wave19 address-verified: Ghidra label joined_r0x00519764 above = stock fallthrough of bl 0x516b34 at 0x519754, which is the last emit before this vcmp). */
                      bVar13 = (fVar19 >= (2.000000238418579f) || ABS(fVar27) >= (2.000000238418579f));
                      if (bVar13) {
                        g2c_nema_vg_set_flag_522622(1);
                      }
                      fVar19 = *(float *)(*piVar5 + 0x2d8) * 0.5f;
                      if ((int)((uint)*(byte *)(*piVar5 + 0x7d) << 0x1b) < 0) {
                        g2c_nema_vg_move_to_522fb4(fStack_fc,fStack_f8,fVar19);
                      }
                      else {
                        g2c_nema_vg_line_to_523284(fStack_fc,fStack_f8,fVar19);
                      }
                      if (bVar13) {
                        g2c_nema_vg_set_flag_522622(0);
                      }
                    }
                  }
                  else {
                    if (cVar1 != '\x01') goto LAB_0051989a;
                    if (*(char *)(iVar11 + 0x2e4) == '\0') {
                      if ((*(float *)(iVar11 + 0x158) <= 0.0f) || (*(int *)(iVar11 + 0x128) != 1)) {
                        fStack_98 = *(float *)(iVar11 + 0x164);
                        fStack_94 = *(float *)(iVar11 + 0x168);
                        fStack_90 = *(float *)(iVar11 + 0x16c);
                        fStack_8c = *(float *)(iVar11 + 0x170);
                        fStack_88 = *(float *)(iVar11 + 0x174);
                        fStack_84 = *(float *)(iVar11 + 0x178);
                        pfVar9 = (float *)(iVar11 + 400);
                        fStack_80 = *(float *)(iVar11 + 0x17c);
                        fStack_7c = *(float *)(iVar11 + 0x180);
                        uStack_78 = *(undefined4 *)(iVar11 + 0x184);
                        uStack_74 = *(undefined4 *)(iVar11 + 0x188);
                        uStack_70 = *(undefined4 *)(iVar11 + 0x18c);
                      }
                      else {
                        fStack_98 = *(float *)(iVar11 + 0x138);
                        fStack_94 = *(float *)(iVar11 + 0x13c);
                        fStack_90 = *(float *)(iVar11 + 0x140);
                        fStack_8c = *(float *)(iVar11 + 0x144);
                        fStack_88 = *(float *)(iVar11 + 0x148);
                        fStack_84 = *(float *)(iVar11 + 0x14c);
                        pfVar9 = (float *)(iVar11 + 400);
                        fStack_80 = *(float *)(iVar11 + 0x150);
                        fStack_7c = *(float *)(iVar11 + 0x154);
                        uStack_78 = *(undefined4 *)(iVar11 + 0x158);
                        uStack_74 = *(undefined4 *)(iVar11 + 0x15c);
                        uStack_70 = *(undefined4 *)(iVar11 + 0x160);
                      }
                    }
                    else {
                      fStack_98 = *(float *)(iVar11 + 0x334);
                      fStack_94 = *(float *)(iVar11 + 0x338);
                      fStack_90 = *(float *)(iVar11 + 0x33c);
                      fStack_8c = *(float *)(iVar11 + 0x340);
                      fStack_88 = *(float *)(iVar11 + 0x344);
                      fStack_84 = *(float *)(iVar11 + 0x348);
                      pfVar9 = (float *)(iVar11 + 0x308);
                      fStack_80 = *(float *)(iVar11 + 0x34c);
                      fStack_7c = *(float *)(iVar11 + 0x350);
                      uStack_78 = *(undefined4 *)(iVar11 + 0x354);
                      uStack_74 = *(undefined4 *)(iVar11 + 0x358);
                      uStack_70 = *(undefined4 *)(iVar11 + 0x35c);
                    }
                    fStack_c4 = *pfVar9;
                    fStack_c0 = pfVar9[1];
                    fStack_bc = pfVar9[2];
                    fStack_b8 = pfVar9[3];
                    fStack_b4 = pfVar9[4];
                    fStack_b0 = pfVar9[5];
                    fStack_ac = pfVar9[6];
                    fStack_a8 = pfVar9[7];
                    fStack_a4 = pfVar9[8];
                    fStack_a0 = pfVar9[9];
                    fStack_9c = pfVar9[10];
                    iVar11 = g2c_nema_vg_near_5177a4(&fStack_c4,&fStack_98);
                    if ((((iVar11 != 1) ||
                         (iVar11 = g2c_nema_vg_near_5177a4(&fStack_bc,&fStack_90), iVar11 != 1)) ||
                        (iVar11 = g2c_nema_vg_near_5177a4(&fStack_b4,&fStack_88), iVar11 != 1)) ||
                       (iVar11 = g2c_nema_vg_near_5177a4(&fStack_ac,&fStack_80), iVar11 != 1)) {
                      iVar11 = g2c_nema_vg_near2_51785c(&fStack_c4,&fStack_90);
                      if ((iVar11 != 0) ||
                         (iVar11 = g2c_nema_vg_near2_51785c(&fStack_98,&fStack_c4), iVar11 != 0))
                      goto LAB_0051999a;
                      iVar11 = g2c_nema_vg_near2_51785c(&fStack_c4,&fStack_88);
                      if ((iVar11 == 0) &&
                         (iVar11 = g2c_nema_vg_near2_51785c(&fStack_98,&fStack_ac), iVar11 == 0)) {
                        iVar11 = (uint)(fStack_84 < fStack_8c) << 0x1f;
                        if (fStack_c0 < fStack_8c) {
                          if (iVar11 < 0) goto LAB_00519aaa;
                        }
                        else if (-1 < iVar11) goto LAB_00519aaa;
LAB_0051999a:
                        fStack_d0 = fStack_80;
                        fStack_d4 = fStack_7c;
                        fStack_d8 = fStack_b4;
                        fStack_dc = fStack_b0;
                        fVar29 = fStack_90;
                        fVar15 = fStack_8c;
                        fVar20 = fStack_c4;
                        fVar30 = fStack_c0;
                        fVar21 = fStack_ac;
                        fVar31 = fStack_a8;
                        fVar28 = fStack_88;
                        fVar18 = fStack_84;
                      }
                      else {
LAB_00519aaa:
                        fStack_d4 = fStack_94;
                        fStack_d0 = fStack_98;
                        fStack_d8 = fStack_bc;
                        fStack_dc = fStack_b8;
                        fVar29 = fStack_88;
                        fVar15 = fStack_84;
                        fVar20 = fStack_ac;
                        fVar30 = fStack_a8;
                        fVar21 = fStack_c4;
                        fVar31 = fStack_c0;
                        fVar28 = fStack_90;
                        fVar18 = fStack_8c;
                      }
                      fStack_e4 = *(g2c_nvg_zero_pair_1);
                      fStack_e0 = (g2c_nvg_zero_pair_1)[1];
                      fStack_fc = *(g2c_nvg_zero_pair_2);
                      fStack_f8 = (g2c_nvg_zero_pair_2)[1];
                      iVar11 = g2c_nema_vg_cubic_approx_522f50
                                         (fVar28,fVar18,fVar29,fVar15,fVar21,fVar31,fVar20,fVar30,
                                          &fStack_e4,&fStack_e0);
                      iVar7 = g2c_nema_vg_cubic_approx_522f50
                                        (fStack_d0,fStack_d4,fVar28,fVar18,fVar21,fVar31,fStack_d8,
                                         fStack_dc,&fStack_fc,&fStack_f8);
                      fVar29 = g2c_nema_vg_sqrt_524218
                                         ((fStack_fc - fStack_e4) * (fStack_fc - fStack_e4) +
                                          (fStack_f8 - fStack_e0) * (fStack_f8 - fStack_e0));
                      iVar8 = *piVar5;
                      if (((*(float *)(iVar8 + 0x2dc) * *(float *)(iVar8 + 0x2d8) < fVar29) ||
                          (iVar7 == 0)) || (iVar11 == 0)) {
                        fVar28 = fStack_cc;
                        fVar18 = fStack_c8;
                        fVar21 = fVar19;
                        fVar31 = fVar27;
                        if (-1 < (int)((uint)*(byte *)(iVar8 + 0x7d) << 0x1b)) {
                          uVar12 = audio_uart_nema_stencil_save_52266e(1,0,1,0);
                          fVar28 = fStack_cc;
                          fVar18 = fStack_c8;
                        }
                      }
                      else {
                        fVar22 = fStack_e4;
                        fVar23 = fStack_e0;
                        fVar24 = fStack_fc;
                        fVar25 = fStack_f8;
                        if (-1 < (int)((uint)*(byte *)(iVar8 + 0x7d) << 0x1b)) {
                          uVar12 = audio_uart_nema_stencil_save_52266e(0,1,1,0);
                          fVar22 = fStack_e4;
                          fVar23 = fStack_e0;
                          fVar24 = fStack_fc;
                          fVar25 = fStack_f8;
                        }
                      }
                      g2c_nema_vg_emit_verts_516b34
                                (fVar22,fVar23,fVar28,fVar18,fVar24,fVar25,fVar21,fVar31);
                      bVar2 = *(byte *)(*piVar5 + 0x7d);
                      goto joined_r0x00519764;
                    }
                  }
                }
              }
            }
            iVar11 = *piVar5;
            if ((0.0f < *(float *)(iVar11 + 0x158)) && (*(int *)(iVar11 + 0x128) == 1)) {
              if ((ABS(*(float *)(iVar11 + 0x15c) * fVar16 -
                                   *(float *)(iVar11 + 0x160) * fVar17) < (0.05000000447034836f))) {
                uVar34 = *(undefined8 *)(iVar11 + 0x140);
                uVar32 = *(undefined8 *)(iVar11 + 0x148);
              }
              else {
                uVar3 = *(undefined8 *)(iVar11 + 0x140);
                fVar28 = (float)g2c_bits_to_float((uint)(uVar34));
                fVar29 = (float)g2c_bits_to_float((uint)(((ulonglong)uVar34 >> 0x20)));
                fVar19 = (float)g2c_bits_to_float((uint)(uVar32));
                fVar27 = (float)g2c_bits_to_float((uint)(((ulonglong)uVar32 >> 0x20)));
                if (*(int *)(iVar11 + 0x110) != 0) {
                  cVar1 = *(char *)(iVar11 + 0x2e2);
                  uVar12 = 0;
                  fVar25 = (float)g2c_bits_to_float((uint)(((ulonglong)*(undefined8 *)(iVar11 + 0x148) >> 0x20)));
                  fVar23 = (float)g2c_bits_to_float((uint)(((ulonglong)uVar3 >> 0x20)));
                  fVar24 = (float)g2c_bits_to_float((uint)(*(undefined8 *)(iVar11 + 0x148)));
                  fVar22 = (float)g2c_bits_to_float((uint)(uVar3));
                  if ((cVar1 == '\0') || (*(int *)(iVar11 + 0x118) != 0)) {
                    if (-1 < (int)((uint)*(byte *)(iVar11 + 0x7d) << 0x1b)) {
                      uVar12 = audio_uart_nema_stencil_save_52266e(1,0,1,0);
                    }
                    g2c_nema_vg_emit_verts_516b34
                              (fVar22,fVar23,fVar28,fVar29,fVar24,fVar25,fVar19,fVar27);
                    bVar2 = *(byte *)(*piVar5 + 0x7d);
joined_r0x00519bf4:
                    if (-1 < (int)((uint)bVar2 << 0x1b)) {
                      audio_uart_nema_stencil_restore_5226b2(uVar12);
                    }
                  }
                  else if (cVar1 == '\x02') {
                    fStack_fc = *(g2c_nvg_zero_pair_0);
                    fStack_f8 = (g2c_nvg_zero_pair_0)[1];
                    iVar11 = g2c_nema_vg_cubic_approx_522f50
                                       (fVar22,fVar23,fVar24,fVar25,fVar28,fVar29,fVar19,fVar27,
                                        &fStack_fc,&fStack_f8);
                    if (iVar11 != 0) {
                      iVar11 = *piVar5;
                      fVar19 = audio_uart_float_sqrt_4397a8
                                         (*(float *)(iVar11 + 0xec) * *(float *)(iVar11 + 0xec) +
                                          *(float *)(iVar11 + 0xf0) * *(float *)(iVar11 + 0xf0));
                      fVar27 = audio_uart_float_sqrt_4397a8
                                         (*(float *)(iVar11 + 0xf8) * *(float *)(iVar11 + 0xf8) +
                                          *(float *)(iVar11 + 0xfc) * *(float *)(iVar11 + 0xfc));
                      fVar19 = ABS(fVar19);
                      /* stock 0x519cdc vcmp; ittt lt; vcmplt 0x519cee; iteee lt; movlt r6,#0 / movge r6,#1 (0x519cf8).
                         LT includes unordered, so r6 = either ordered >= K (wave19 address-verified: Ghidra label joined_r0x00519bf4 above = stock fallthrough of bl 0x516b34 at 0x519be4, which is the last emit before this vcmp). */
                      bVar13 = (fVar19 >= (2.000000238418579f) || ABS(fVar27) >= (2.000000238418579f));
                      if (bVar13) {
                        g2c_nema_vg_set_flag_522622(1);
                      }
                      fVar19 = *(float *)(*piVar5 + 0x2d8) * 0.5f;
                      if ((int)((uint)*(byte *)(*piVar5 + 0x7d) << 0x1b) < 0) {
                        g2c_nema_vg_move_to_522fb4(fStack_fc,fStack_f8,fVar19);
                      }
                      else {
                        g2c_nema_vg_line_to_523284(fStack_fc,fStack_f8,fVar19);
                      }
                      if (bVar13) {
                        g2c_nema_vg_set_flag_522622(0);
                      }
                    }
                  }
                  else {
                    if (cVar1 != '\x01') {
LAB_0051989a:
                      *(undefined4 *)(iVar11 + 0x114) = 0;
                      *(undefined4 *)(iVar11 + 0x118) = 0;
                      audio_uart_nema_vg_set_error_51565c(0x1000000);
                      iVar10 = *piVar5;
                      *(undefined4 *)(iVar10 + 0x114) = 0;
                      *(undefined4 *)(iVar10 + 0x118) = 0;
                      audio_uart_nema_vg_set_error_51565c(0x1000000);
                      return 0x1000000;
                    }
                    if (*(char *)(iVar11 + 0x2e4) == '\0') {
                      fStack_a8 = *(float *)(iVar11 + 0x138);
                      fStack_a4 = *(float *)(iVar11 + 0x13c);
                      fStack_a0 = *(float *)(iVar11 + 0x140);
                      fStack_9c = *(float *)(iVar11 + 0x144);
                      fStack_98 = *(float *)(iVar11 + 0x148);
                      fStack_94 = *(float *)(iVar11 + 0x14c);
                      pfVar9 = (float *)(iVar11 + 400);
                      fStack_90 = *(float *)(iVar11 + 0x150);
                      fStack_8c = *(float *)(iVar11 + 0x154);
                      fStack_88 = *(float *)(iVar11 + 0x158);
                      fStack_84 = *(float *)(iVar11 + 0x15c);
                      fStack_80 = *(float *)(iVar11 + 0x160);
                    }
                    else {
                      fStack_a8 = *(float *)(iVar11 + 0x334);
                      fStack_a4 = *(float *)(iVar11 + 0x338);
                      fStack_a0 = *(float *)(iVar11 + 0x33c);
                      fStack_9c = *(float *)(iVar11 + 0x340);
                      fStack_98 = *(float *)(iVar11 + 0x344);
                      fStack_94 = *(float *)(iVar11 + 0x348);
                      pfVar9 = (float *)(iVar11 + 0x308);
                      fStack_90 = *(float *)(iVar11 + 0x34c);
                      fStack_8c = *(float *)(iVar11 + 0x350);
                      fStack_88 = *(float *)(iVar11 + 0x354);
                      fStack_84 = *(float *)(iVar11 + 0x358);
                      fStack_80 = *(float *)(iVar11 + 0x35c);
                    }
                    fStack_d4 = *pfVar9;
                    fStack_d0 = pfVar9[1];
                    fStack_cc = pfVar9[2];
                    fStack_c8 = pfVar9[3];
                    fStack_c4 = pfVar9[4];
                    fStack_c0 = pfVar9[5];
                    fStack_bc = pfVar9[6];
                    fStack_b8 = pfVar9[7];
                    fStack_b4 = pfVar9[8];
                    fStack_b0 = pfVar9[9];
                    fStack_ac = pfVar9[10];
                    iVar11 = g2c_nema_vg_near_5177a4(&fStack_d4,&fStack_a8);
                    if ((((iVar11 != 1) ||
                         (iVar11 = g2c_nema_vg_near_5177a4(&fStack_cc,&fStack_a0), iVar11 != 1)) ||
                        (iVar11 = g2c_nema_vg_near_5177a4(&fStack_c4,&fStack_98), iVar11 != 1)) ||
                       (iVar11 = g2c_nema_vg_near_5177a4(&fStack_bc,&fStack_90), iVar11 != 1)) {
                      iVar11 = g2c_nema_vg_near2_51785c(&fStack_d4,&fStack_a0);
                      if ((iVar11 != 0) ||
                         (iVar11 = g2c_nema_vg_near2_51785c(&fStack_a8,&fStack_d4), iVar11 != 0))
                      goto LAB_00519dd2;
                      iVar11 = g2c_nema_vg_near2_51785c(&fStack_d4,&fStack_98);
                      if ((iVar11 == 0) &&
                         (iVar11 = g2c_nema_vg_near2_51785c(&fStack_a8,&fStack_bc), iVar11 == 0)) {
                        iVar11 = (uint)(fStack_94 < fStack_9c) << 0x1f;
                        if (fStack_d0 < fStack_9c) {
                          if (iVar11 < 0) goto LAB_00519ef6;
                        }
                        else if (-1 < iVar11) goto LAB_00519ef6;
LAB_00519dd2:
                        fStack_d8 = fStack_90;
                        fStack_dc = fStack_8c;
                        fVar15 = fStack_a0;
                        fVar20 = fStack_9c;
                        fVar30 = fStack_d4;
                        h = fStack_d0;
                        h_00 = fStack_c0;
                        g = fStack_c4;
                        fVar31 = fStack_bc;
                        f_00 = fStack_b8;
                        fVar18 = fStack_98;
                        fVar21 = fStack_94;
                      }
                      else {
LAB_00519ef6:
                        fStack_dc = fStack_a4;
                        fStack_d8 = fStack_a8;
                        fVar15 = fStack_98;
                        fVar20 = fStack_94;
                        fVar30 = fStack_bc;
                        h = fStack_b8;
                        h_00 = fStack_c8;
                        g = fStack_cc;
                        fVar31 = fStack_d4;
                        f_00 = fStack_d0;
                        fVar18 = fStack_a0;
                        fVar21 = fStack_9c;
                      }
                      fStack_e4 = *(g2c_nvg_zero_pair_1);
                      fStack_e0 = (g2c_nvg_zero_pair_1)[1];
                      fStack_fc = *(g2c_nvg_zero_pair_2);
                      fStack_f8 = (g2c_nvg_zero_pair_2)[1];
                      iVar11 = g2c_nema_vg_cubic_approx_522f50
                                         (fVar18,fVar21,fVar15,fVar20,fVar31,f_00,fVar30,h,
                                          &fStack_e4,&fStack_e0);
                      iVar7 = g2c_nema_vg_cubic_approx_522f50
                                        (fStack_d8,fStack_dc,fVar18,fVar21,fVar31,f_00,g,h_00,
                                         &fStack_fc,&fStack_f8);
                      fVar15 = g2c_nema_vg_sqrt_524218
                                         ((fStack_fc - fStack_e4) * (fStack_fc - fStack_e4) +
                                          (fStack_f8 - fStack_e0) * (fStack_f8 - fStack_e0));
                      iVar8 = *piVar5;
                      if (((*(float *)(iVar8 + 0x2dc) * *(float *)(iVar8 + 0x2d8) < fVar15) ||
                          (iVar7 == 0)) || (iVar11 == 0)) {
                        fVar18 = fVar28;
                        fVar21 = fVar29;
                        fVar31 = fVar19;
                        f_00 = fVar27;
                        if (-1 < (int)((uint)*(byte *)(iVar8 + 0x7d) << 0x1b)) {
                          uVar12 = audio_uart_nema_stencil_save_52266e(1,0,1,0);
                        }
                      }
                      else {
                        fVar22 = fStack_e4;
                        fVar23 = fStack_e0;
                        fVar24 = fStack_fc;
                        fVar25 = fStack_f8;
                        if (-1 < (int)((uint)*(byte *)(iVar8 + 0x7d) << 0x1b)) {
                          uVar12 = audio_uart_nema_stencil_save_52266e(0,1,1,0);
                          fVar22 = fStack_e4;
                          fVar23 = fStack_e0;
                          fVar24 = fStack_fc;
                          fVar25 = fStack_f8;
                        }
                      }
                      g2c_nema_vg_emit_verts_516b34
                                (fVar22,fVar23,fVar18,fVar21,fVar24,fVar25,fVar31,f_00);
                      bVar2 = *(byte *)(*piVar5 + 0x7d);
                      goto joined_r0x00519bf4;
                    }
                  }
                }
              }
            }
            iVar11 = *piVar5;
            *(int *)(iVar11 + 0x128) = *(int *)(iVar11 + 0x128) + 1;
            uVar35 = (undefined4)((ulonglong)uVar34 >> 0x20);
            uVar33 = (undefined4)((ulonglong)uVar32 >> 0x20);
            if (*(float *)(iVar11 + 0x158) == 0.0f) {
              *(int *)(iVar11 + 0x138) = (int)uVar34;
              *(undefined4 *)(iVar11 + 0x13c) = uVar35;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x140) = fStack_ec;
              *(float *)(iVar11 + 0x144) = fStack_e8;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x148) = fStack_f4;
              *(float *)(iVar11 + 0x14c) = fStack_f0;
              iVar11 = *piVar5;
              *(int *)(iVar11 + 0x150) = (int)uVar32;
              *(undefined4 *)(iVar11 + 0x154) = uVar33;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x158) = fVar14;
              *(float *)(iVar11 + 0x15c) = fVar17;
              *(float *)(iVar11 + 0x160) = fVar16;
            }
            else {
              *(int *)(iVar11 + 0x164) = (int)uVar34;
              *(undefined4 *)(iVar11 + 0x168) = uVar35;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x16c) = fStack_ec;
              *(float *)(iVar11 + 0x170) = fStack_e8;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x174) = fStack_f4;
              *(float *)(iVar11 + 0x178) = fStack_f0;
              iVar11 = *piVar5;
              *(int *)(iVar11 + 0x17c) = (int)uVar32;
              *(undefined4 *)(iVar11 + 0x180) = uVar33;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x184) = fVar14;
              *(float *)(iVar11 + 0x188) = fVar17;
              *(float *)(iVar11 + 0x18c) = fVar16;
            }
            goto LAB_0051a2d0;
          }
          *(float *)(iVar11 + 0x198) = fStack_108;
          *(float *)(iVar11 + 0x19c) = fStack_104 + *(float *)(iVar11 + 0x130) * -0.5f;
          *(float *)(iVar11 + 0x1a0) = fStack_108;
LAB_005194b4:
          *(float *)(iVar11 + 0x1a4) = fStack_104 + *(float *)(iVar11 + 0x130) * 0.5f;
          *(undefined4 *)(iVar11 + 400) = *(undefined4 *)(iVar11 + 0x198);
          *(undefined4 *)(iVar11 + 0x194) = *(undefined4 *)(iVar11 + 0x19c);
          iVar11 = *piVar5;
          *(undefined4 *)(iVar11 + 0x1a8) = *(undefined4 *)(iVar11 + 0x1a0);
          *(undefined4 *)(iVar11 + 0x1ac) = *(undefined4 *)(iVar11 + 0x1a4);
        }
        else {
          fVar16 = c_00 - fStack_108;
          fVar17 = fVar26 - fStack_104;
          fVar14 = fVar16 * fVar16 + fVar17 * fVar17;
          if ((ABS(fVar14) < (1.0000000656873453e-05f))) {
            *(float *)(iVar11 + 0x198) = fStack_108;
            *(float *)(iVar11 + 0x19c) = fStack_104 + *(float *)(iVar11 + 0x130) * -0.5f;
            *(float *)(iVar11 + 0x1a0) = fStack_108;
            goto LAB_005194b4;
          }
          fVar14 = audio_uart_float_sqrt_4397a8(fVar14);
          fVar16 = fVar16 * (1.0f / fVar14);
          fVar17 = fVar17 * (1.0f / fVar14);
          fVar19 = *(float *)(iVar11 + 0x130) * 0.5f * fVar17;
          fVar28 = fStack_108 - fVar19;
          fVar27 = *(float *)(iVar11 + 0x134) * 0.5f * fVar16;
          fVar29 = fVar27 + fStack_104;
          uVar34 = CONCAT44(g2c_float_to_bits(fVar29),g2c_float_to_bits(fVar28));
          *(float *)(iVar11 + 400) = fVar28;
          *(float *)(iVar11 + 0x194) = fVar29;
          iVar11 = *piVar5;
          fVar22 = c_00 - fVar19;
          fVar23 = fVar27 + fVar26;
          *(float *)(iVar11 + 0x198) = fVar22;
          *(float *)(iVar11 + 0x19c) = fVar23;
          iVar11 = *piVar5;
          fVar24 = fVar19 + c_00;
          fVar25 = fVar26 - fVar27;
          *(float *)(iVar11 + 0x1a0) = fVar24;
          *(float *)(iVar11 + 0x1a4) = fVar25;
          iVar11 = *piVar5;
          fVar19 = fVar19 + fStack_108;
          fVar27 = fStack_104 - fVar27;
          uVar32 = CONCAT44(g2c_float_to_bits(fVar27),g2c_float_to_bits(fVar19));
          *(float *)(iVar11 + 0x1a8) = fVar19;
          *(float *)(iVar11 + 0x1ac) = fVar27;
          iVar11 = *piVar5;
          if (*(int *)(iVar11 + 0x110) == 0) {
            uVar6 = audio_uart_nema_stencil_restore_5226b2(*(uint *)(iVar11 + 0x8c));
            g2c_nema_vg_emit_verts_516b34(fVar28,fVar29,fVar22,fVar23,fVar24,fVar25,fVar19,fVar27);
          }
          else {
            bVar13 = -1 < (int)((uint)*(byte *)(iVar11 + 0x7d) << 0x1b);
            uVar6 = audio_uart_nema_stencil_save_52266e((uint)bVar13,0,(uint)bVar13,0);
            iVar11 = *piVar5;
            if (0.0f < *(float *)(iVar11 + 0x184)) {
              g2c_nema_vg_emit_verts_516b34
                        (*(float *)(iVar11 + 0x164),*(float *)(iVar11 + 0x168),
                         *(float *)(iVar11 + 0x16c),*(float *)(iVar11 + 0x170),
                         *(float *)(iVar11 + 0x174),*(float *)(iVar11 + 0x178),
                         *(float *)(iVar11 + 0x17c),*(float *)(iVar11 + 0x180));
              iVar11 = *piVar5;
              if ((ABS(*(float *)(iVar11 + 0x188) * fVar17 -
                                   *(float *)(iVar11 + 0x18c) * fVar16) < (0.05000000447034836f))) {
                uVar34 = *(undefined8 *)(iVar11 + 0x16c);
                uVar32 = *(undefined8 *)(iVar11 + 0x174);
              }
              else {
                g2c_nema_vg_emit_verts_516b34
                          (*(float *)(iVar11 + 0x16c),*(float *)(iVar11 + 0x170),fVar28,fVar29,
                           *(float *)(iVar11 + 0x174),*(float *)(iVar11 + 0x178),fVar19,fVar27);
              }
            }
            iVar11 = *piVar5;
            if ((0.0f < *(float *)(iVar11 + 0x158)) && (*(int *)(iVar11 + 0x128) == 1)) {
              if ((ABS(*(float *)(iVar11 + 0x15c) * fVar17 -
                                   *(float *)(iVar11 + 0x160) * fVar16) < (0.05000000447034836f))) {
                uVar34 = *(undefined8 *)(iVar11 + 0x140);
                uVar32 = *(undefined8 *)(iVar11 + 0x148);
              }
              else {
                g2c_nema_vg_emit_verts_516b34
                          (*(float *)(iVar11 + 0x140),*(float *)(iVar11 + 0x144),(float)g2c_bits_to_float((uint)(uVar34)),
                           (float)g2c_bits_to_float((uint)(((ulonglong)uVar34 >> 0x20))),*(float *)(iVar11 + 0x148),
                           *(float *)(iVar11 + 0x14c),(float)g2c_bits_to_float((uint)(uVar32)),
                           (float)g2c_bits_to_float((uint)(((ulonglong)uVar32 >> 0x20))));
              }
            }
            iVar11 = *piVar5;
            *(int *)(iVar11 + 0x128) = *(int *)(iVar11 + 0x128) + 1;
            uVar35 = (undefined4)((ulonglong)uVar34 >> 0x20);
            uVar33 = (undefined4)((ulonglong)uVar32 >> 0x20);
            if (*(float *)(iVar11 + 0x158) == 0.0f) {
              *(int *)(iVar11 + 0x138) = (int)uVar34;
              *(undefined4 *)(iVar11 + 0x13c) = uVar35;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x140) = fVar22;
              *(float *)(iVar11 + 0x144) = fVar23;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x148) = fVar24;
              *(float *)(iVar11 + 0x14c) = fVar25;
              iVar11 = *piVar5;
              *(int *)(iVar11 + 0x150) = (int)uVar32;
              *(undefined4 *)(iVar11 + 0x154) = uVar33;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x158) = fVar14;
              *(float *)(iVar11 + 0x15c) = fVar16;
              *(float *)(iVar11 + 0x160) = fVar17;
            }
            else {
              *(int *)(iVar11 + 0x164) = (int)uVar34;
              *(undefined4 *)(iVar11 + 0x168) = uVar35;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x16c) = fVar22;
              *(float *)(iVar11 + 0x170) = fVar23;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x174) = fVar24;
              *(float *)(iVar11 + 0x178) = fVar25;
              iVar11 = *piVar5;
              *(int *)(iVar11 + 0x17c) = (int)uVar32;
              *(undefined4 *)(iVar11 + 0x180) = uVar33;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x184) = fVar14;
              *(float *)(iVar11 + 0x188) = fVar16;
              *(float *)(iVar11 + 0x18c) = fVar17;
            }
          }
LAB_0051a2d0:
          audio_uart_nema_stencil_restore_5226b2(uVar6);
        }
        fVar16 = fStack_120 - c_00;
        fVar17 = fStack_11c - fVar26;
        fVar14 = fVar16 * fVar16 + fVar17 * fVar17;
        if ((ABS(fVar14) < (1.0000000656873453e-05f))) {
          iVar11 = *piVar5;
          *(float *)(iVar11 + 0x198) = c_00;
          *(float *)(iVar11 + 0x19c) = fVar26 + *(float *)(iVar11 + 0x130) * -0.5f;
          *(float *)(iVar11 + 0x1a0) = c_00;
          *(float *)(iVar11 + 0x1a4) = fVar26 + *(float *)(iVar11 + 0x130) * 0.5f;
          *(undefined4 *)(iVar11 + 400) = *(undefined4 *)(iVar11 + 0x198);
          *(undefined4 *)(iVar11 + 0x194) = *(undefined4 *)(iVar11 + 0x19c);
          iVar11 = *piVar5;
          *(undefined4 *)(iVar11 + 0x1a8) = *(undefined4 *)(iVar11 + 0x1a0);
          *(undefined4 *)(iVar11 + 0x1ac) = *(undefined4 *)(iVar11 + 0x1a4);
        }
        else {
          fVar14 = audio_uart_float_sqrt_4397a8(fVar14);
          iVar11 = *piVar5;
          fVar16 = fVar16 * (1.0f / fVar14);
          fVar17 = fVar17 * (1.0f / fVar14);
          fVar19 = *(float *)(iVar11 + 0x130) * 0.5f * fVar17;
          fVar28 = c_00 - fVar19;
          fVar27 = *(float *)(iVar11 + 0x134) * 0.5f * fVar16;
          fVar29 = fVar27 + fVar26;
          uVar34 = CONCAT44(g2c_float_to_bits(fVar29),g2c_float_to_bits(fVar28));
          *(float *)(iVar11 + 400) = fVar28;
          *(float *)(iVar11 + 0x194) = fVar29;
          iVar11 = *piVar5;
          fVar22 = fStack_120 - fVar19;
          fVar23 = fVar27 + fStack_11c;
          *(float *)(iVar11 + 0x198) = fVar22;
          *(float *)(iVar11 + 0x19c) = fVar23;
          iVar11 = *piVar5;
          fVar24 = fVar19 + fStack_120;
          fVar25 = fStack_11c - fVar27;
          *(float *)(iVar11 + 0x1a0) = fVar24;
          *(float *)(iVar11 + 0x1a4) = fVar25;
          iVar11 = *piVar5;
          fVar19 = fVar19 + c_00;
          fVar26 = fVar26 - fVar27;
          uVar32 = CONCAT44(g2c_float_to_bits(fVar26),g2c_float_to_bits(fVar19));
          *(float *)(iVar11 + 0x1a8) = fVar19;
          *(float *)(iVar11 + 0x1ac) = fVar26;
          iVar11 = *piVar5;
          if (*(int *)(iVar11 + 0x110) == 0) {
            uVar6 = audio_uart_nema_stencil_restore_5226b2(*(uint *)(iVar11 + 0x8c));
            g2c_nema_vg_emit_verts_516b34(fVar28,fVar29,fVar22,fVar23,fVar24,fVar25,fVar19,fVar26);
          }
          else {
            bVar13 = -1 < (int)((uint)*(byte *)(iVar11 + 0x7d) << 0x1b);
            uVar6 = audio_uart_nema_stencil_save_52266e((uint)bVar13,0,(uint)bVar13,0);
            iVar11 = *piVar5;
            if (0.0f < *(float *)(iVar11 + 0x184)) {
              g2c_nema_vg_emit_verts_516b34
                        (*(float *)(iVar11 + 0x164),*(float *)(iVar11 + 0x168),
                         *(float *)(iVar11 + 0x16c),*(float *)(iVar11 + 0x170),
                         *(float *)(iVar11 + 0x174),*(float *)(iVar11 + 0x178),
                         *(float *)(iVar11 + 0x17c),*(float *)(iVar11 + 0x180));
              iVar11 = *piVar5;
              if ((ABS(*(float *)(iVar11 + 0x188) * fVar17 -
                                   *(float *)(iVar11 + 0x18c) * fVar16) < (0.05000000447034836f))
                 ) {
                uVar34 = *(undefined8 *)(iVar11 + 0x16c);
                uVar32 = *(undefined8 *)(iVar11 + 0x174);
              }
              else {
                g2c_nema_vg_emit_verts_516b34
                          (*(float *)(iVar11 + 0x16c),*(float *)(iVar11 + 0x170),fVar28,fVar29,
                           *(float *)(iVar11 + 0x174),*(float *)(iVar11 + 0x178),fVar19,fVar26);
              }
            }
            iVar11 = *piVar5;
            if ((0.0f < *(float *)(iVar11 + 0x158)) && (*(int *)(iVar11 + 0x128) == 1)) {
              if ((ABS(*(float *)(iVar11 + 0x15c) * fVar17 -
                                   *(float *)(iVar11 + 0x160) * fVar16) < (0.05000000447034836f))
                 ) {
                uVar34 = *(undefined8 *)(iVar11 + 0x140);
                uVar32 = *(undefined8 *)(iVar11 + 0x148);
              }
              else {
                g2c_nema_vg_emit_verts_516b34
                          (*(float *)(iVar11 + 0x140),*(float *)(iVar11 + 0x144),(float)g2c_bits_to_float((uint)(uVar34)),
                           (float)g2c_bits_to_float((uint)(((ulonglong)uVar34 >> 0x20))),*(float *)(iVar11 + 0x148),
                           *(float *)(iVar11 + 0x14c),(float)g2c_bits_to_float((uint)(uVar32)),
                           (float)g2c_bits_to_float((uint)(((ulonglong)uVar32 >> 0x20))));
              }
            }
            iVar11 = *piVar5;
            *(int *)(iVar11 + 0x128) = *(int *)(iVar11 + 0x128) + 1;
            uVar35 = (undefined4)((ulonglong)uVar34 >> 0x20);
            uVar33 = (undefined4)((ulonglong)uVar32 >> 0x20);
            if (*(float *)(iVar11 + 0x158) == 0.0f) {
              *(int *)(iVar11 + 0x138) = (int)uVar34;
              *(undefined4 *)(iVar11 + 0x13c) = uVar35;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x140) = fVar22;
              *(float *)(iVar11 + 0x144) = fVar23;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x148) = fVar24;
              *(float *)(iVar11 + 0x14c) = fVar25;
              iVar11 = *piVar5;
              *(int *)(iVar11 + 0x150) = (int)uVar32;
              *(undefined4 *)(iVar11 + 0x154) = uVar33;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x158) = fVar14;
              *(float *)(iVar11 + 0x15c) = fVar16;
              *(float *)(iVar11 + 0x160) = fVar17;
            }
            else {
              *(int *)(iVar11 + 0x164) = (int)uVar34;
              *(undefined4 *)(iVar11 + 0x168) = uVar35;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x16c) = fVar22;
              *(float *)(iVar11 + 0x170) = fVar23;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x174) = fVar24;
              *(float *)(iVar11 + 0x178) = fVar25;
              iVar11 = *piVar5;
              *(int *)(iVar11 + 0x17c) = (int)uVar32;
              *(undefined4 *)(iVar11 + 0x180) = uVar33;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x184) = fVar14;
              *(float *)(iVar11 + 0x188) = fVar16;
              *(float *)(iVar11 + 0x18c) = fVar17;
            }
          }
          audio_uart_nema_stencil_restore_5226b2(uVar6);
        }
      }
      else {
        uVar6 = g2c_nema_vg_path_bounds_5639e8(fStack_108,fStack_104,c_00,fVar26);
        if ((uVar6 != 0) ||
           (uVar6 = g2c_nema_vg_path_bounds_5639e8(c_00,fVar26,fStack_120,fStack_11c), uVar6 != 0))
        {
          iVar10 = *piVar5;
          *(undefined4 *)(iVar10 + 0x114) = 0;
          *(undefined4 *)(iVar10 + 0x118) = 0;
          audio_uart_nema_vg_set_error_51565c(uVar6);
          return uVar6;
        }
      }
      iVar11 = *piVar5;
      if (*(int *)(iVar11 + 700) != 0) {
        iVar7 = *(int *)(iVar11 + 700) + -1;
        *(int *)(iVar11 + 700) = iVar7;
        iVar11 = iVar11 + iVar7 * 0x18;
        fStack_108 = *(float *)(iVar11 + 0x1cc);
        fStack_104 = *(float *)(iVar11 + 0x1d0);
        fStack_10c = *(float *)(iVar11 + 0x1d4);
        fStack_110 = *(float *)(iVar11 + 0x1d8);
        fStack_120 = *(float *)(iVar11 + 0x1dc);
        fStack_11c = *(float *)(iVar11 + 0x1e0);
      }
    }
    else {
      if (fVar29 <= fVar27 * 0.5f) goto LAB_00519504;
LAB_00519384:
      if (*(int *)(iVar11 + 700) < 10) {
        *(float *)(iVar11 + *(int *)(iVar11 + 700) * 0x18 + 0x1cc) = c_00;
        *(float *)(iVar11 + *(int *)(iVar11 + 700) * 0x18 + 0x1d0) = fVar26;
        *(float *)(iVar11 + *(int *)(iVar11 + 700) * 0x18 + 0x1d4) = fVar17;
        *(float *)(iVar11 + *(int *)(iVar11 + 700) * 0x18 + 0x1d8) = fVar19;
        *(float *)(iVar11 + *(int *)(iVar11 + 700) * 0x18 + 0x1dc) = fStack_120;
        *(float *)(iVar11 + *(int *)(iVar11 + 700) * 0x18 + 0x1e0) = fStack_11c;
        *(int *)(iVar11 + 700) = *(int *)(iVar11 + 700) + 1;
      }
      iVar10 = iVar10 + 1;
      fStack_120 = c_00;
      fStack_11c = fVar26;
      fStack_110 = fVar16;
      fStack_10c = fVar14;
    }
    if (iVar10 == 0) {
      return 0;
    }
  } while( true );
}
#undef fStack_120
#undef fStack_11c
#undef fStack_110
#undef fStack_10c
#undef fStack_108
#undef fStack_104
#undef fStack_fc
#undef fStack_f8
#undef fStack_f4
#undef fStack_f0
#undef fStack_ec
#undef fStack_e8
#undef fStack_e4
#undef fStack_e0
#undef fStack_dc
#undef fStack_d8
#undef fStack_d4
#undef fStack_d0
#undef fStack_cc
#undef fStack_c8
#undef fStack_c4
#undef fStack_c0
#undef fStack_bc
#undef fStack_b8
#undef fStack_b4
#undef fStack_b0
#undef fStack_ac
#undef fStack_a8
#undef fStack_a4
#undef fStack_a0
#undef fStack_9c
#undef fStack_98
#undef fStack_94
#undef fStack_90
#undef fStack_8c
#undef fStack_88
#undef fStack_84
#undef fStack_80
#undef fStack_7c
#undef uStack_78
#undef uStack_74
#undef uStack_70


  

/* ---- lifted 0x51a660 ---- */

void g2c_nema_vg_quad_to_51a660(float a,float b,float c,float d,float e,float f,float *out)

{
  float fVar1;
  
  fVar1 = *out;
  *out = (fVar1 * c * a - out[1] * d * b) + e;
  out[1] = fVar1 * c * b + out[1] * d * a + f;
  return;
}

  

/* ---- lifted 0x51a694 ---- */

uint g2c_nema_vg_cubic_to_51a694(float a,float b,float c,float d,float e,float f,uint g,int h,int i)

{
  uint error;
  int iVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  undefined1 auStack_78 [12];
  float fStack_6c;
  float fStack_68;
  float fStack_64;
  float fStack_60;
  float fStack_5c;
  float fStack_58;
  float fStack_54;
  float fStack_50;
  
  fVar6 = a * (0.01745329238474369f);
  fVar5 = b * (0.01745329238474369f) - fVar6;
  fVar2 = audio_uart_float_tangent_563f40(fVar5 * 0.25f);
  fVar2 = fVar2 * (1.3333333730697632f);
  fVar3 = audio_uart_float_trig_mode1_50968c(fVar5);
  fStack_60 = audio_uart_float_trig_mode0_509690(fVar5);
  fStack_6c = 1.0f;
  fStack_5c = 1.0f;
  fStack_54 = fVar3 + fVar2 * fStack_60;
  fStack_50 = fStack_60 - fVar2 * fVar3;
  fStack_68 = 0.0f;
  fVar7 = (*(float *)(h + 0x24) / (180.0f)) * (3.1415927410125732f);
  fStack_64 = fVar3;
  fStack_58 = fVar2;
  fVar2 = audio_uart_float_trig_mode1_50968c(fVar6);
  fVar3 = audio_uart_float_trig_mode0_509690(fVar6);
  fVar5 = audio_uart_float_trig_mode1_50968c(fVar7);
  fVar6 = audio_uart_float_trig_mode0_509690(fVar7);
  if (i << 0x1f < 0) {
    fStack_6c = *(float *)(h + 0xc);
    fStack_68 = *(float *)(h + 0x10);
  }
  else {
    fVar7 = (fVar3 + fVar2 * g2c_bits_to_float((uint)((0x0u)))) * f;
    fVar4 = (fVar2 - fVar3 * g2c_bits_to_float((uint)((0x0u)))) * e;
    fStack_68 = fVar4 * fVar6 + fVar7 * fVar5 + d;
    fStack_6c = (fVar4 * fVar5 - fVar7 * fVar6) + c;
  }
  fVar7 = (fVar3 + fStack_58 * fVar2) * f;
  fVar4 = (fVar2 - fStack_58 * fVar3) * e;
  fStack_58 = fVar4 * fVar6 + fVar7 * fVar5 + d;
  fStack_5c = (fVar4 * fVar5 - fVar7 * fVar6) + c;
  fVar7 = (fStack_54 * fVar3 + fStack_50 * fVar2) * f;
  fVar4 = (fStack_54 * fVar2 - fStack_50 * fVar3) * e;
  fStack_50 = fVar4 * fVar6 + fVar7 * fVar5 + d;
  fStack_54 = (fVar4 * fVar5 - fVar7 * fVar6) + c;
  if (i << 0x1e < 0) {
    fStack_64 = *(float *)(h + 0x14);
    fStack_60 = *(float *)(h + 0x18);
  }
  else {
    fVar7 = (fStack_64 * fVar3 + fStack_60 * fVar2) * f;
    fVar2 = (fStack_64 * fVar2 - fStack_60 * fVar3) * e;
    fStack_60 = fVar2 * fVar6 + fVar7 * fVar5 + d;
    fStack_64 = (fVar2 * fVar5 - fVar7 * fVar6) + c;
  }
  error = g2c_nema_vg_tess_516cf8((int)auStack_78);
  if (error != 0) {
    iVar1 = *(((int *)&audio_uart_nema_vg_context_cell));
    *(undefined4 *)(iVar1 + 0x114) = 0;
    *(undefined4 *)(iVar1 + 0x118) = 0;
    audio_uart_nema_vg_set_error_51565c(error);
    return error;
  }
  return 0;
}

  

/* ---- lifted 0x51a8ec ---- */


uint g2c_nema_vg_arc_to_51a8ec(uint a,int b)

{
  /* Evidence (wave11): the s1 left by cubic_to_51a694 (bl at 0x51b016/0x51b096) is dead. The next
   * loop head redefines s1 with ite mi vmovmi/vmovpl (0x51b03c/0x51b0bc), and loop exit returns. */
  byte bVar1;
  int *piVar2;
  undefined4 *puVar3;
  uint error;
  byte bVar4;
  int iVar5;
  uint uVar6;
  bool bVar7;
  float fVar8;
  float fVar9;
  float fVar10;
  float fVar11;
  float fVar12;
  float fVar13;
  float fVar14;
  float fVar15;
  float fVar17;
  undefined8 uVar16;
  undefined4 uVar18;
  undefined8 uVar19;
  undefined4 uVar20;
  float fVar21;
  float fVar22;
  float fVar23;
  float fVar24;
  float fVar25;
  float fVar26;
  float fVar27;
  float fVar28;
  float fVar29;
  float fVar30;
  float fVar31;
  /* Stock frame of 0x51a8ec as one block: locals keep the entry-SP offsets Ghidra named them by
   * (X_Stack_NN at g2c_frame_51a8ec[0x80-0xNN]) so &local passed to callees spans its stock neighbours. */
  unsigned char g2c_frame_51a8ec[0x80] __attribute__((aligned(8)));
  typedef float __attribute__((may_alias)) g2c_fa_float;
#define fStack_7c (*(g2c_fa_float *)(void *)&g2c_frame_51a8ec[0x80-0x7c])
#define fStack_78 (*(g2c_fa_float *)(void *)&g2c_frame_51a8ec[0x80-0x78])
#define fStack_74 (*(g2c_fa_float *)(void *)&g2c_frame_51a8ec[0x80-0x74])
#define fStack_70 (*(g2c_fa_float *)(void *)&g2c_frame_51a8ec[0x80-0x70])
#define fStack_6c (*(g2c_fa_float *)(void *)&g2c_frame_51a8ec[0x80-0x6c])
#define fStack_68 (*(g2c_fa_float *)(void *)&g2c_frame_51a8ec[0x80-0x68])
#define fStack_64 (*(g2c_fa_float *)(void *)&g2c_frame_51a8ec[0x80-0x64])
#define fStack_60 (*(g2c_fa_float *)(void *)&g2c_frame_51a8ec[0x80-0x60])
  
  piVar2 = (((int *)&audio_uart_nema_vg_context_cell));
  /* Evidence (wave11): the entry value of s17 (d8 high half) is dead in stock. It is written by
   * vabspl at 0x51a91c on the path that bpl 0x51adb6 takes, and vlive.py from 0x51a8f6 reports
   * s16/s17 "none". So it starts at 0.0f, which is never observed. */
  fVar17 = 0.0f;
  fVar15 = ABS(*(float *)(b + 0x1c));
  bVar7 = (1.0000000656873453e-05f) <= fVar15;
  if (bVar7) {
    fVar17 = ABS(*(float *)(b + 0x20));
  }
  if (bVar7 && (bVar7 && (1.0000000656873453e-05f) <= fVar17)) {
    fVar28 = *(float *)(b + 0x24) * (0.01745329238474369f);
    fVar8 = *(float *)(b + 0x34);
    fVar21 = *(float *)(b + 0x38);
    fVar22 = *(float *)(b + 0x2c);
    fVar9 = *(float *)(b + 0x30);
    bVar4 = *(byte *)(b + 3);
    fVar26 = audio_uart_float_trig_mode1_50968c(fVar28);
    fVar28 = audio_uart_float_trig_mode0_509690(fVar28);
    fVar14 = fVar8 * fVar26 + fVar21 * fVar28;
    fVar24 = fVar22 * fVar26 + fVar9 * fVar28;
    fVar10 = fVar14 / fVar15;
    fVar8 = fVar21 * fVar26 - fVar8 * fVar28;
    fVar12 = fVar24 / fVar15;
    fVar31 = fVar9 * fVar26 - fVar22 * fVar28;
    fVar11 = fVar8 / fVar17;
    fVar13 = fVar31 / fVar17;
    fVar27 = fVar10 - fVar12;
    fVar29 = fVar11 - fVar13;
    fVar22 = fVar10 + fVar12;
    fVar21 = fVar27 * fVar27 + fVar29 * fVar29;
    bVar1 = bVar4 >> 6;
    fVar9 = fVar11 + fVar13;
    bVar4 = bVar4 >> 5 & 1;
    if (fVar21 == 0.0f) {
      iVar5 = *piVar2;
      *(undefined4 *)(iVar5 + 0x114) = 0;
      *(undefined4 *)(iVar5 + 0x118) = 0;
      audio_uart_nema_vg_set_error_51565c(0x100);
      return 0x100;
    }
    fVar30 = 1.0f / fVar21 + -0.25f;
    if ((fVar30 < 0.0f)) {
      fVar21 = audio_uart_float_sqrt_4397a8(fVar21 * 0.25f);
      fVar17 = fVar17 * fVar21;
      fVar15 = fVar15 * fVar21;
      fVar10 = fVar14 / fVar15;
      fVar11 = fVar8 / fVar17;
      fVar12 = fVar24 / fVar15;
      fVar22 = fVar10 + fVar12;
      fVar13 = fVar31 / fVar17;
      fVar9 = fVar11 + fVar13;
      fVar27 = fVar10 - fVar12;
      fVar29 = fVar11 - fVar13;
      fVar30 = g2c_bits_to_float((uint)((0x0u)));
    }
    fVar14 = fVar17;
    fStack_7c = fVar15;
    fVar24 = audio_uart_float_sqrt_4397a8(fVar30);
    fVar23 = fVar22 * 0.5f + fVar24 * fVar29;
    fVar25 = fVar9 * 0.5f - fVar24 * fVar27;
    fVar31 = audio_uart_float_two_input_angle_50969c(fVar11 - fVar25,fVar10 - fVar23);
    fVar21 = audio_uart_float_two_input_angle_50969c(fVar13 - fVar25,fVar12 - fVar23);
    fVar8 = (57.295780181884766f);
    fVar31 = fVar31 * (57.295780181884766f);
    fVar21 = fVar21 * (57.295780181884766f);
    fVar30 = fVar21 - fVar31;
    if ((fVar30 < 0.0f)) {
      fVar30 = fVar30 + (360.0f);
    }
    if (((!(fVar30 < (180.0f))) || (bVar4 == (bVar1 & 1))) &&
       ((fVar30 < (180.0f) || (bVar4 != (bVar1 & 1))))) {
      fVar23 = fVar22 * 0.5f - fVar24 * fVar29;
      fVar25 = fVar9 * 0.5f + fVar24 * fVar27;
      fVar31 = audio_uart_float_two_input_angle_50969c(fVar11 - fVar25,fVar10 - fVar23);
      fVar21 = audio_uart_float_two_input_angle_50969c(fVar13 - fVar25,fVar12 - fVar23);
      fVar31 = fVar31 * fVar8;
      fVar21 = fVar21 * fVar8;
    }
    fVar9 = fStack_7c;
    fVar22 = (-90.0f);
    fVar8 = (90.0f);
    fVar10 = fVar23 * fVar15 * fVar26 - fVar25 * fVar17 * fVar28;
    fVar15 = fVar23 * fVar15 * fVar28 + fVar25 * fVar17 * fVar26;
    fVar17 = fVar31;
    if ((bVar1 & 1) == 0) {
      fVar17 = fVar21;
      fVar21 = fVar31;
    }
    if ((fVar21 < fVar17)) {
      fVar21 = fVar21 + (360.0f);
    }
    bVar7 = true;
    bVar4 = 1;
    fVar26 = fVar21;
    if ((bVar1 & 1) == 0) {
      while ((fVar17 < fVar21)) {
        fVar28 = fVar21 + fVar22;
        iVar5 = (uint)(fVar17 < fVar28) << 0x1f;
        if (iVar5 < 0) {
          fVar26 = fVar28;
        }
        if (-1 < iVar5) {
          fVar26 = fVar17;
        }
        if (!(fVar17 < fVar28)) {
          bVar4 = bVar4 + 2;
        }
        if (!bVar7) {
          *(bool *)(*piVar2 + 0x1c0) = bVar7;
          *(undefined1 *)(*piVar2 + 0x2eb) = 1;
        }
        uVar6 = g2c_nema_vg_cubic_to_51a694
                          (fVar21,fVar26,fVar10,fVar15,fVar9,fVar14,a,b,(uint)bVar4);
        if (uVar6 != 0) goto LAB_0051b0dc;
        bVar7 = false;
        bVar4 = 0;
        fVar21 = fVar28;
      }
    }
    else {
      while ((fVar17 < fVar21)) {
        fVar28 = fVar17 + fVar8;
        iVar5 = (uint)(fVar28 < fVar21) << 0x1f;
        if (iVar5 < 0) {
          fVar26 = fVar28;
        }
        if (-1 < iVar5) {
          fVar26 = fVar21;
        }
        if (!(fVar28 < fVar21)) {
          bVar4 = bVar4 + 2;
        }
        if (!bVar7) {
          *(bool *)(*piVar2 + 0x1c0) = bVar7;
          *(undefined1 *)(*piVar2 + 0x2eb) = 1;
        }
        uVar6 = g2c_nema_vg_cubic_to_51a694
                          (fVar17,fVar26,fVar10,fVar15,fVar9,fVar14,a,b,(uint)bVar4);
        if (uVar6 != 0) {
LAB_0051b0dc:
          iVar5 = *piVar2;
          *(undefined4 *)(iVar5 + 0x114) = 0;
          *(undefined4 *)(iVar5 + 0x118) = 0;
          audio_uart_nema_vg_set_error_51565c(uVar6);
          return uVar6;
        }
        bVar7 = false;
        bVar4 = 0;
        fVar17 = fVar28;
      }
    }
    *(undefined1 *)(*piVar2 + 0x1c0) = 1;
    *(undefined1 *)(*piVar2 + 0x2eb) = 0;
    return 0;
  }
  iVar5 = *(((int *)&audio_uart_nema_vg_context_cell));
  if (*(char *)(iVar5 + 0x7c) != '\0') {
    uVar19 = *(undefined8 *)(b + 0xc);
    uVar16 = *(undefined8 *)(b + 0x14);
    uVar6 = 0;
    if (*(int *)(iVar5 + 0x88) != 0) {
      if (*(int *)(iVar5 + 0x114) == 0) {
        uVar6 = 0x7800000;
      }
      else {
        uVar6 = 0x4000000;
      }
    }
    uVar6 = uVar6 & *(uint *)(iVar5 + 0x8c);
    if (*(char *)(*(((int *)audio_uart_nema_context_cell)) + 8) == '\x01') {
      uVar6 = uVar6 | *(uint *)(*(((int *)audio_uart_nema_context_cell)) + 0xc) & 0xc0000000;
    }
    puVar3 = (undefined4 *)audio_uart_nema_cl_get_space_514aec(5);
    if (puVar3 == (undefined4 *)0x0) {
      return 0;
    }
    *puVar3 = 800;
    puVar3[1] = (int)uVar19;
    puVar3[2] = 0x324;
    puVar3[3] = (int)((ulonglong)uVar19 >> 0x20);
    puVar3[4] = 0x330;
    puVar3[5] = (int)uVar16;
    puVar3[6] = 0x334;
    puVar3[7] = (int)((ulonglong)uVar16 >> 0x20);
    puVar3[8] = (0xff000100u);
    uVar6 = uVar6 | 0xb;
LAB_0051ada8:
    puVar3[9] = uVar6;
    return 0;
  }
  fVar28 = *(float *)(b + 0xc);
  fVar17 = *(float *)(b + 0x10);
  fVar15 = *(float *)(b + 0x14);
  fVar26 = *(float *)(b + 0x18);
  if (*(int *)(iVar5 + 0x110) == 0) {
    uVar6 = 0;
    if (*(int *)(iVar5 + 0x88) != 0) {
      uVar6 = 0x7800000;
    }
    uVar6 = uVar6 & *(uint *)(iVar5 + 0x8c);
    if (*(char *)(*(((int *)audio_uart_nema_context_cell)) + 8) == '\x01') {
      uVar6 = uVar6 | *(uint *)(*(((int *)audio_uart_nema_context_cell)) + 0xc) & 0xc0000000;
    }
    puVar3 = (undefined4 *)audio_uart_nema_cl_get_space_514aec(5);
    if (puVar3 == (undefined4 *)0x0) {
      return 0;
    }
    *puVar3 = 800;
    puVar3[2] = 0x324;
    puVar3[4] = 0x330;
    uVar18 = (0xff000100u);
    puVar3[1] = g2c_float_to_bits(fVar28);
    puVar3[3] = g2c_float_to_bits(fVar17);
    puVar3[5] = g2c_float_to_bits(fVar15);
    puVar3[6] = 0x334;
    puVar3[7] = g2c_float_to_bits(fVar26);
    puVar3[8] = uVar18;
    uVar6 = uVar6 | 10;
    goto LAB_0051ada8;
  }
  fVar21 = fVar15 - fVar28;
  fVar22 = fVar26 - fVar17;
  fVar8 = fVar21 * fVar21 + fVar22 * fVar22;
  if ((ABS(fVar8) < (1.0000000656873453e-05f))) {
    *(float *)(iVar5 + 0x198) = fVar28;
    *(float *)(iVar5 + 0x19c) = fVar17 + *(float *)(iVar5 + 0x130) * -0.5f;
    *(float *)(iVar5 + 0x1a0) = fVar28;
    *(float *)(iVar5 + 0x1a4) = fVar17 + *(float *)(iVar5 + 0x130) * 0.5f;
    *(undefined4 *)(iVar5 + 400) = *(undefined4 *)(iVar5 + 0x198);
    *(undefined4 *)(iVar5 + 0x194) = *(undefined4 *)(iVar5 + 0x19c);
    iVar5 = *piVar2;
    *(undefined4 *)(iVar5 + 0x1a8) = *(undefined4 *)(iVar5 + 0x1a0);
    *(undefined4 *)(iVar5 + 0x1ac) = *(undefined4 *)(iVar5 + 0x1a4);
    return 0;
  }
  fVar8 = audio_uart_float_sqrt_4397a8(fVar8);
  fVar21 = fVar21 * (1.0f / fVar8);
  fVar22 = fVar22 * (1.0f / fVar8);
  fVar9 = *(float *)(iVar5 + 0x130) * 0.5f * fVar22;
  fVar11 = fVar28 - fVar9;
  fVar10 = *(float *)(iVar5 + 0x134) * 0.5f * fVar21;
  fVar12 = fVar10 + fVar17;
  uVar19 = CONCAT44(g2c_float_to_bits(fVar12),g2c_float_to_bits(fVar11));
  *(float *)(iVar5 + 400) = fVar11;
  *(float *)(iVar5 + 0x194) = fVar12;
  iVar5 = *piVar2;
  fVar13 = fVar15 - fVar9;
  fVar14 = fVar10 + fVar26;
  *(float *)(iVar5 + 0x198) = fVar13;
  *(float *)(iVar5 + 0x19c) = fVar14;
  iVar5 = *piVar2;
  fVar15 = fVar9 + fVar15;
  fVar26 = fVar26 - fVar10;
  *(float *)(iVar5 + 0x1a0) = fVar15;
  *(float *)(iVar5 + 0x1a4) = fVar26;
  iVar5 = *piVar2;
  fVar9 = fVar9 + fVar28;
  fVar17 = fVar17 - fVar10;
  uVar16 = CONCAT44(g2c_float_to_bits(fVar17),g2c_float_to_bits(fVar9));
  *(float *)(iVar5 + 0x1a8) = fVar9;
  *(float *)(iVar5 + 0x1ac) = fVar17;
  iVar5 = *piVar2;
  if (*(int *)(iVar5 + 0x110) == 0) {
    uVar6 = audio_uart_nema_stencil_restore_5226b2(*(uint *)(iVar5 + 0x8c));
    g2c_nema_vg_emit_verts_516b34(fVar11,fVar12,fVar13,fVar14,fVar15,fVar26,fVar9,fVar17);
  }
  else {
    bVar7 = -1 < (int)((uint)*(byte *)(iVar5 + 0x7d) << 0x1b);
    uVar6 = audio_uart_nema_stencil_save_52266e((uint)bVar7,0,(uint)bVar7,0);
    iVar5 = *piVar2;
    if (0.0f < *(float *)(iVar5 + 0x184)) {
      fStack_64 = *(float *)(iVar5 + 0x164);
      fStack_60 = *(float *)(iVar5 + 0x168);
      fStack_6c = *(float *)(iVar5 + 0x16c);
      fStack_68 = *(float *)(iVar5 + 0x170);
      fStack_74 = *(float *)(iVar5 + 0x174);
      fStack_70 = *(float *)(iVar5 + 0x178);
      fStack_7c = *(float *)(iVar5 + 0x17c);
      fStack_78 = *(float *)(iVar5 + 0x180);
      g2c_nema_vg_emit_verts_516b34
                (fStack_64,fStack_60,fStack_6c,fStack_68,fStack_74,fStack_70,fStack_7c,fStack_78);
      iVar5 = *piVar2;
      if ((ABS(*(float *)(iVar5 + 0x188) * fVar22 - *(float *)(iVar5 + 0x18c) * fVar21)
                      < (0.05000000447034836f))) {
        uVar19 = *(undefined8 *)(iVar5 + 0x16c);
        uVar16 = *(undefined8 *)(iVar5 + 0x174);
      }
      else {
        fStack_64 = *(float *)(iVar5 + 0x16c);
        fStack_60 = *(float *)(iVar5 + 0x170);
        fStack_74 = *(float *)(iVar5 + 0x174);
        fStack_70 = *(float *)(iVar5 + 0x178);
        fStack_7c = fVar9;
        fStack_78 = fVar17;
        fStack_6c = fVar11;
        fStack_68 = fVar12;
        error = g2c_nema_vg_stroke_join_5179d0
                          (&fStack_64,(uint *)&fStack_6c,&fStack_74,(uint *)&fStack_7c,0);
        if (error != 0) goto LAB_0051acca;
      }
    }
    iVar5 = *piVar2;
    if ((0.0f < *(float *)(iVar5 + 0x158)) && (*(int *)(iVar5 + 0x128) == 1)) {
      if ((ABS(*(float *)(iVar5 + 0x15c) * fVar22 - *(float *)(iVar5 + 0x160) * fVar21)
                      < (0.05000000447034836f))) {
        uVar19 = *(undefined8 *)(iVar5 + 0x140);
        uVar16 = *(undefined8 *)(iVar5 + 0x148);
      }
      else {
        fStack_64 = *(float *)(iVar5 + 0x140);
        fStack_60 = *(float *)(iVar5 + 0x144);
        fStack_6c = (float)g2c_bits_to_float((uint)(uVar19));
        fStack_68 = (float)g2c_bits_to_float((uint)(((ulonglong)uVar19 >> 0x20)));
        fStack_74 = *(float *)(iVar5 + 0x148);
        fStack_70 = *(float *)(iVar5 + 0x14c);
        fStack_7c = (float)g2c_bits_to_float((uint)(uVar16));
        fStack_78 = (float)g2c_bits_to_float((uint)(((ulonglong)uVar16 >> 0x20)));
        error = g2c_nema_vg_stroke_join_5179d0
                          (&fStack_64,(uint *)&fStack_6c,&fStack_74,(uint *)&fStack_7c,0);
        if (error != 0) {
LAB_0051acca:
          iVar5 = *piVar2;
          *(undefined4 *)(iVar5 + 0x114) = 0;
          *(undefined4 *)(iVar5 + 0x118) = 0;
          audio_uart_nema_vg_set_error_51565c(error);
          return 0;
        }
      }
    }
    iVar5 = *piVar2;
    *(int *)(iVar5 + 0x128) = *(int *)(iVar5 + 0x128) + 1;
    uVar20 = (undefined4)((ulonglong)uVar19 >> 0x20);
    uVar18 = (undefined4)((ulonglong)uVar16 >> 0x20);
    if (*(float *)(iVar5 + 0x158) == 0.0f) {
      *(int *)(iVar5 + 0x138) = (int)uVar19;
      *(undefined4 *)(iVar5 + 0x13c) = uVar20;
      iVar5 = *piVar2;
      *(float *)(iVar5 + 0x140) = fVar13;
      *(float *)(iVar5 + 0x144) = fVar14;
      iVar5 = *piVar2;
      *(float *)(iVar5 + 0x148) = fVar15;
      *(float *)(iVar5 + 0x14c) = fVar26;
      iVar5 = *piVar2;
      *(int *)(iVar5 + 0x150) = (int)uVar16;
      *(undefined4 *)(iVar5 + 0x154) = uVar18;
      iVar5 = *piVar2;
      *(float *)(iVar5 + 0x158) = fVar8;
      *(float *)(iVar5 + 0x15c) = fVar21;
      *(float *)(iVar5 + 0x160) = fVar22;
    }
    else {
      *(int *)(iVar5 + 0x164) = (int)uVar19;
      *(undefined4 *)(iVar5 + 0x168) = uVar20;
      iVar5 = *piVar2;
      *(float *)(iVar5 + 0x16c) = fVar13;
      *(float *)(iVar5 + 0x170) = fVar14;
      iVar5 = *piVar2;
      *(float *)(iVar5 + 0x174) = fVar15;
      *(float *)(iVar5 + 0x178) = fVar26;
      iVar5 = *piVar2;
      *(int *)(iVar5 + 0x17c) = (int)uVar16;
      *(undefined4 *)(iVar5 + 0x180) = uVar18;
      iVar5 = *piVar2;
      *(float *)(iVar5 + 0x184) = fVar8;
      *(float *)(iVar5 + 0x188) = fVar21;
      *(float *)(iVar5 + 0x18c) = fVar22;
    }
  }
  audio_uart_nema_stencil_restore_5226b2(uVar6);
  return 0;
}
#undef fStack_7c
#undef fStack_78
#undef fStack_74
#undef fStack_70
#undef fStack_6c
#undef fStack_68
#undef fStack_64
#undef fStack_60


  

/* ---- lifted 0x51b140 ---- */


/* Evidence: stock FUN_0051b140 @ 0x51b140; ambient FPSCR scratch unused after
 * VFP compares recovered as g2c_fpscr_eq/is_eq (decomp used FPSCR masks). */
void g2c_nema_vg_bezier_subdiv_51b140(float a,float b,float c,int d)

{
  int *piVar1;
  uint uVar2;
  float *pfVar3;
  int iVar4;
  uint uVar5;
  byte bVar6;
  bool bVar7;
  float fVar8;
  float fVar9;
  float fVar10;
  float fVar11;
  float fVar12;
  float fVar13;
  float fVar14;
  float fVar15;
  float fVar16;
  float afStack_1d4 [3];
  uint uStack_1c8;
  float fStack_1c4;
  float fStack_1c0;
  float afStack_1bc [97];
  
  piVar1 = (((int *)&audio_uart_nema_vg_context_cell));
  iVar4 = *(((int *)&audio_uart_nema_vg_context_cell));
  fVar8 = *(float *)(iVar4 + 0x198);
  fVar13 = *(float *)(iVar4 + 400);
  /* stock 0x51b158 vcmp; itttt eq; vcmpeq 0x51b16a; bne.w 0x51b4fe (EQ ordered; wave19) */
  uVar5 = 0; /* Z-only stand-in dropped (wave19): compare moved into the test below */
  bVar6 = 0;
  if ((byte)(fVar13 == fVar8) != 0) {
    c = *(float *)(iVar4 + 0x194);
    uVar5 = 0; /* Z-only stand-in dropped (wave19): compare moved into the test below */
    bVar6 = (byte)(c == *(float *)(iVar4 + 0x19c));
  }
  if (bVar6 != 0) {
    fVar14 = *(float *)(iVar4 + 0x1a0);
    fVar16 = *(float *)(iVar4 + 0x1a8);
    uVar2 = uVar5 & 0xfffffff;
    /* stock 0x51b17e vcmp; itttt eq; vcmpeq 0x51b190; bne.w 0x51b4fe (EQ ordered; wave19) */
    uVar5 = uVar2; /* Z-only stand-in dropped (wave19): compare moved into the test below */
    bVar6 = 0;
    if ((byte)(fVar14 == fVar16) != 0) {
      fVar16 = *(float *)(iVar4 + 0x1a4);
      uVar5 = uVar2; /* Z-only stand-in dropped (wave19): compare moved into the test below */
      bVar6 = (byte)(fVar16 == *(float *)(iVar4 + 0x1ac));
    }
    if (bVar6 != 0) {
      fVar9 = *(float *)(iVar4 + 0x2d8);
      fVar8 = (fVar13 - fVar14) / fVar9;
      fVar14 = (fVar13 + fVar14) * 0.5f;
      fVar13 = (c - fVar16) / fVar9;
      fVar9 = fVar9 * 0.5f;
      fVar16 = (c + fVar16) * 0.5f;
      if (d == 1) {
        uVar2 = g2c_nema_vg_f2u_522f1c(fVar9);
        iVar4 = (int)uVar2 / 2;
        fVar10 = (float)VectorSignedToFloat(iVar4,(byte)(uVar5 >> 0x16) & 3);
        fVar10 = (180.0f) / fVar10;
        fVar11 = audio_uart_nema_cos_524130(fVar10);
        fVar10 = audio_uart_nema_sin_52405c(fVar10);
        fStack_1c4 = fVar14 - fVar8 * fVar9;
        fStack_1c0 = fVar16 - fVar13 * fVar9;
        uVar5 = iVar4 - 1;
        if (1 < iVar4) {
          pfVar3 = afStack_1d4 + 6;
          for (uVar2 = uVar5 & 3; uVar2 != 0; uVar2 = uVar2 - 1) {
            *pfVar3 = fVar14 + fVar9 * fVar8;
            pfVar3[1] = fVar16 + fVar9 * fVar13;
            fVar12 = fVar10 * fVar8;
            fVar8 = fVar11 * fVar8 - fVar10 * fVar13;
            pfVar3 = pfVar3 + 2;
            fVar13 = fVar12 + fVar11 * fVar13;
          }
          for (uVar2 = uVar5 >> 2; uStack_1c8 = uVar5, uVar2 != 0; uVar2 = uVar2 - 1) {
            *pfVar3 = fVar14 + fVar9 * fVar8;
            pfVar3[1] = fVar16 + fVar9 * fVar13;
            fVar12 = fVar11 * fVar8 - fVar10 * fVar13;
            pfVar3[2] = fVar14 + fVar9 * fVar12;
            fVar13 = fVar10 * fVar8 + fVar11 * fVar13;
            fVar15 = fVar10 * fVar12 + fVar11 * fVar13;
            fVar8 = fVar11 * fVar12 - fVar10 * fVar13;
            pfVar3[4] = fVar14 + fVar9 * fVar8;
            pfVar3[3] = fVar16 + fVar9 * fVar13;
            fVar12 = fVar10 * fVar8 + fVar11 * fVar15;
            fVar8 = fVar11 * fVar8 - fVar10 * fVar15;
            pfVar3[5] = fVar16 + fVar9 * fVar15;
            pfVar3[6] = fVar14 + fVar9 * fVar8;
            pfVar3[7] = fVar16 + fVar9 * fVar12;
            fVar13 = fVar10 * fVar8 + fVar11 * fVar12;
            fVar8 = fVar11 * fVar8 - fVar10 * fVar12;
            pfVar3 = pfVar3 + 8;
          }
        }
        uVar2 = audio_uart_nema_stencil_save_52266e
                          (0,-(uint)((*(byte *)(*piVar1 + 0x7d) & 0x10) == 0) >> 0x1f,0,0);
        g2c_nema_vg_path_transform_523a34(afStack_1d4 + 4,uVar5,2);
        bVar7 = -1 < (int)((uint)*(byte *)(*piVar1 + 0x7d) << 0x1b);
        audio_uart_nema_stencil_save_52266e(0,(uint)bVar7,(uint)bVar7,0);
      }
      else {
        uVar2 = g2c_nema_vg_f2u_522f1c(fVar9);
        iVar4 = (int)uVar2 / 2;
        fVar10 = (float)VectorSignedToFloat(iVar4,(byte)(uVar5 >> 0x16) & 3);
        fVar10 = (180.0f) / fVar10;
        fVar11 = audio_uart_nema_cos_524130(fVar10);
        fVar10 = audio_uart_nema_sin_52405c(fVar10);
        fVar10 = -fVar10;
        fStack_1c4 = fVar14 - fVar8 * fVar9;
        fStack_1c0 = fVar16 - fVar13 * fVar9;
        uVar5 = iVar4 - 1;
        if (1 < iVar4) {
          pfVar3 = afStack_1d4 + 6;
          for (uVar2 = uVar5 & 3; uVar2 != 0; uVar2 = uVar2 - 1) {
            *pfVar3 = fVar14 + fVar9 * fVar8;
            pfVar3[1] = fVar16 + fVar9 * fVar13;
            fVar12 = fVar10 * fVar8;
            fVar8 = fVar11 * fVar8 - fVar10 * fVar13;
            pfVar3 = pfVar3 + 2;
            fVar13 = fVar12 + fVar11 * fVar13;
          }
          for (uVar2 = uVar5 >> 2; uStack_1c8 = uVar5, uVar2 != 0; uVar2 = uVar2 - 1) {
            *pfVar3 = fVar14 + fVar9 * fVar8;
            pfVar3[1] = fVar16 + fVar9 * fVar13;
            fVar12 = fVar11 * fVar8 - fVar10 * fVar13;
            pfVar3[2] = fVar14 + fVar9 * fVar12;
            fVar13 = fVar10 * fVar8 + fVar11 * fVar13;
            fVar15 = fVar10 * fVar12 + fVar11 * fVar13;
            fVar8 = fVar11 * fVar12 - fVar10 * fVar13;
            pfVar3[4] = fVar14 + fVar9 * fVar8;
            pfVar3[3] = fVar16 + fVar9 * fVar13;
            fVar12 = fVar10 * fVar8 + fVar11 * fVar15;
            fVar8 = fVar11 * fVar8 - fVar10 * fVar15;
            pfVar3[5] = fVar16 + fVar9 * fVar15;
            pfVar3[6] = fVar14 + fVar9 * fVar8;
            pfVar3[7] = fVar16 + fVar9 * fVar12;
            fVar13 = fVar10 * fVar8 + fVar11 * fVar12;
            fVar8 = fVar11 * fVar8 - fVar10 * fVar12;
            pfVar3 = pfVar3 + 8;
          }
        }
        uVar2 = audio_uart_nema_stencil_save_52266e
                          (0,-(uint)((*(byte *)(*piVar1 + 0x7d) & 0x10) == 0) >> 0x1f,0,0);
        g2c_nema_vg_path_transform_523a34(afStack_1d4 + 4,uVar5,2);
        bVar7 = -1 < (int)((uint)*(byte *)(*piVar1 + 0x7d) << 0x1b);
        audio_uart_nema_stencil_save_52266e(0,(uint)bVar7,(uint)bVar7,0);
      }
      goto LAB_0051b8ac;
    }
  }
  fVar13 = *(float *)(iVar4 + 0x2d8);
  if (d == 1) {
    fVar16 = (*(float *)(iVar4 + 0x1a0) - fVar8) / fVar13;
    fVar9 = (*(float *)(iVar4 + 0x1a0) + fVar8) * 0.5f;
    fVar11 = fVar13 * 0.5f;
    fVar13 = (*(float *)(iVar4 + 0x1a4) - *(float *)(iVar4 + 0x19c)) / fVar13;
    fVar10 = (*(float *)(iVar4 + 0x1a4) + *(float *)(iVar4 + 0x19c)) * 0.5f;
    uVar2 = g2c_nema_vg_f2u_522f1c(fVar11);
    iVar4 = (int)uVar2 / 2;
    fVar8 = (float)VectorSignedToFloat(iVar4,(byte)(uVar5 >> 0x16) & 3);
    fVar8 = (180.0f) / fVar8;
    fVar14 = audio_uart_nema_cos_524130(fVar8);
    fVar8 = audio_uart_nema_sin_52405c(fVar8);
    fStack_1c4 = fVar9 - fVar16 * fVar11;
    fStack_1c0 = fVar10 - fVar13 * fVar11;
    uVar5 = iVar4 - 1;
    if (1 < iVar4) {
      pfVar3 = afStack_1d4 + 6;
      for (uVar2 = uVar5 & 3; uVar2 != 0; uVar2 = uVar2 - 1) {
        *pfVar3 = fVar9 + fVar11 * fVar16;
        pfVar3[1] = fVar10 + fVar11 * fVar13;
        fVar12 = fVar8 * fVar16;
        fVar16 = fVar14 * fVar16 - fVar8 * fVar13;
        pfVar3 = pfVar3 + 2;
        fVar13 = fVar12 + fVar14 * fVar13;
      }
      for (uVar2 = uVar5 >> 2; uStack_1c8 = uVar5, uVar2 != 0; uVar2 = uVar2 - 1) {
        *pfVar3 = fVar9 + fVar11 * fVar16;
        pfVar3[1] = fVar10 + fVar11 * fVar13;
        fVar12 = fVar14 * fVar16 - fVar8 * fVar13;
        pfVar3[2] = fVar9 + fVar11 * fVar12;
        fVar16 = fVar8 * fVar16 + fVar14 * fVar13;
        fVar15 = fVar8 * fVar12 + fVar14 * fVar16;
        fVar13 = fVar14 * fVar12 - fVar8 * fVar16;
        pfVar3[4] = fVar9 + fVar11 * fVar13;
        pfVar3[3] = fVar10 + fVar11 * fVar16;
        fVar12 = fVar8 * fVar13 + fVar14 * fVar15;
        fVar16 = fVar14 * fVar13 - fVar8 * fVar15;
        pfVar3[5] = fVar10 + fVar11 * fVar15;
        pfVar3[6] = fVar9 + fVar11 * fVar16;
        pfVar3[7] = fVar10 + fVar11 * fVar12;
        fVar13 = fVar8 * fVar16 + fVar14 * fVar12;
        fVar16 = fVar14 * fVar16 - fVar8 * fVar12;
        pfVar3 = pfVar3 + 8;
      }
    }
    uVar2 = audio_uart_nema_stencil_save_52266e
                      (0,-(uint)((*(byte *)(*piVar1 + 0x7d) & 0x10) == 0) >> 0x1f,0,0);
    g2c_nema_vg_path_transform_523a34(afStack_1d4 + 4,uVar5,2);
    bVar7 = -1 < (int)((uint)*(byte *)(*piVar1 + 0x7d) << 0x1b);
    audio_uart_nema_stencil_save_52266e(0,(uint)bVar7,(uint)bVar7,0);
  }
  else {
    fVar8 = (*(float *)(iVar4 + 0x150) - *(float *)(iVar4 + 0x138)) / fVar13;
    fVar9 = (*(float *)(iVar4 + 0x150) + *(float *)(iVar4 + 0x138)) * 0.5f;
    fVar11 = fVar13 * 0.5f;
    fVar13 = (*(float *)(iVar4 + 0x154) - *(float *)(iVar4 + 0x13c)) / fVar13;
    fVar10 = (*(float *)(iVar4 + 0x154) + *(float *)(iVar4 + 0x13c)) * 0.5f;
    uVar2 = g2c_nema_vg_f2u_522f1c(fVar11);
    iVar4 = (int)uVar2 / 2;
    fVar16 = (float)VectorSignedToFloat(iVar4,(byte)(uVar5 >> 0x16) & 3);
    fVar16 = (180.0f) / fVar16;
    fVar14 = audio_uart_nema_cos_524130(fVar16);
    fVar16 = audio_uart_nema_sin_52405c(fVar16);
    fVar16 = -fVar16;
    fStack_1c4 = fVar9 - fVar8 * fVar11;
    fStack_1c0 = fVar10 - fVar13 * fVar11;
    uVar5 = iVar4 - 1;
    if (1 < iVar4) {
      pfVar3 = afStack_1d4 + 6;
      for (uVar2 = uVar5 & 3; uVar2 != 0; uVar2 = uVar2 - 1) {
        *pfVar3 = fVar9 + fVar11 * fVar8;
        pfVar3[1] = fVar10 + fVar11 * fVar13;
        fVar12 = fVar16 * fVar8;
        fVar8 = fVar14 * fVar8 - fVar16 * fVar13;
        pfVar3 = pfVar3 + 2;
        fVar13 = fVar12 + fVar14 * fVar13;
      }
      for (uVar2 = uVar5 >> 2; uStack_1c8 = uVar5, uVar2 != 0; uVar2 = uVar2 - 1) {
        *pfVar3 = fVar9 + fVar11 * fVar8;
        pfVar3[1] = fVar10 + fVar11 * fVar13;
        fVar12 = fVar14 * fVar8 - fVar16 * fVar13;
        pfVar3[2] = fVar9 + fVar11 * fVar12;
        fVar13 = fVar16 * fVar8 + fVar14 * fVar13;
        fVar15 = fVar16 * fVar12 + fVar14 * fVar13;
        fVar8 = fVar14 * fVar12 - fVar16 * fVar13;
        pfVar3[4] = fVar9 + fVar11 * fVar8;
        pfVar3[3] = fVar10 + fVar11 * fVar13;
        fVar12 = fVar16 * fVar8 + fVar14 * fVar15;
        fVar8 = fVar14 * fVar8 - fVar16 * fVar15;
        pfVar3[5] = fVar10 + fVar11 * fVar15;
        pfVar3[6] = fVar9 + fVar11 * fVar8;
        pfVar3[7] = fVar10 + fVar11 * fVar12;
        fVar13 = fVar16 * fVar8 + fVar14 * fVar12;
        fVar8 = fVar14 * fVar8 - fVar16 * fVar12;
        pfVar3 = pfVar3 + 8;
      }
    }
    uVar2 = audio_uart_nema_stencil_save_52266e
                      (0,-(uint)((*(byte *)(*piVar1 + 0x7d) & 0x10) == 0) >> 0x1f,0,0);
    g2c_nema_vg_path_transform_523a34(afStack_1d4 + 4,uVar5,2);
    bVar7 = -1 < (int)((uint)*(byte *)(*piVar1 + 0x7d) << 0x1b);
    audio_uart_nema_stencil_save_52266e(0,(uint)bVar7,(uint)bVar7,0);
  }
LAB_0051b8ac:
  g2c_nema_raster_triangle_f_522a24
            (fStack_1c4,fStack_1c0,afStack_1d4[iVar4 * 2],afStack_1d4[iVar4 * 2 + 1],
             afStack_1d4[iVar4 * 2 + 2],afStack_1d4[iVar4 * 2 + 3]);
  audio_uart_nema_stencil_restore_5226b2(uVar2);
  return;
}

  

/* ---- lifted 0x51b8f0 ---- */


/* Evidence: stock FUN_0051b8f0 @ 0x51b8f0; ambient FPSCR scratch unused after
 * VFP compares recovered as g2c_fpscr_eq/is_eq. */
uint g2c_nema_vg_arc_seg_51b8f0(float a,float b,float c,float d,float e)

{
  char cVar1;
  undefined8 uVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  int *piVar5;
  uint uVar6;
  float *pfVar7;
  int iVar8;
  uint uVar9;
  byte bVar10;
  bool bVar11;
  float fVar12;
  float fVar13;
  float fVar14;
  float fVar15;
  float fVar16;
  float fVar17;
  float fVar18;
  float fVar19;
  float fVar20;
  float afStack_1f4 [3];
  uint uStack_1e8;
  float fStack_1e4;
  float fStack_1e0;
  float afStack_1dc [97];
  
  piVar5 = (((int *)&audio_uart_nema_vg_context_cell));
  iVar8 = *(((int *)&audio_uart_nema_vg_context_cell));
  bVar11 = *(int *)(iVar8 + 0x110) == 0;
  cVar1 = '\0';
  if (!bVar11) {
    cVar1 = *(char *)(iVar8 + 0x2e0);
  }
  if (bVar11 || cVar1 == '\0') {
    return 0;
  }
  if (cVar1 != '\x02') {
    if (cVar1 != '\x01') {
      return 0x800000;
    }
    fVar12 = *(float *)(iVar8 + 400);
    fVar15 = *(float *)(iVar8 + 0x198);
    /* stock 0x51b91e vcmp; itttt eq; vcmpeq 0x51b930; bne 0x51b9e8 (EQ ordered; wave19) */
    uVar9 = 0; /* Z-only stand-in dropped (wave19): compare moved into the test below */
    bVar10 = 0;
    if ((byte)(fVar12 == fVar15) != 0) {
      fVar15 = *(float *)(iVar8 + 0x194);
      uVar9 = 0; /* Z-only stand-in dropped (wave19): compare moved into the test below */
      bVar10 = (byte)(fVar15 == *(float *)(iVar8 + 0x19c));
    }
    if (bVar10 != 0) {
      fVar16 = *(float *)(iVar8 + 0x1a0);
      fVar17 = *(float *)(iVar8 + 0x1a8);
      uVar6 = uVar9 & 0xfffffff;
      /* stock 0x51b942 vcmp; itttt eq; vcmpeq 0x51b954; bne 0x51b9e8 (EQ ordered; wave19) */
      uVar9 = uVar6; /* Z-only stand-in dropped (wave19): compare moved into the test below */
      bVar10 = 0;
      if ((byte)(fVar16 == fVar17) != 0) {
        fVar17 = *(float *)(iVar8 + 0x1a4);
        uVar9 = uVar6; /* Z-only stand-in dropped (wave19): compare moved into the test below */
        bVar10 = (byte)(fVar17 == *(float *)(iVar8 + 0x1ac));
      }
      if (bVar10 != 0) {
        fVar20 = *(float *)(iVar8 + 0x2d8);
        fVar18 = (fVar12 - fVar16) / fVar20;
        fVar16 = (fVar12 + fVar16) * 0.5f;
        fVar13 = fVar20 * 0.5f;
        fVar20 = (fVar15 - fVar17) / fVar20;
        fVar17 = (fVar15 + fVar17) * 0.5f;
        uVar6 = g2c_nema_vg_f2u_522f1c(fVar13);
        iVar8 = (int)uVar6 / 2;
        fVar15 = (float)VectorSignedToFloat(iVar8,(byte)(uVar9 >> 0x16) & 3);
        fVar15 = (180.0f) / fVar15;
        fVar12 = audio_uart_nema_cos_524130(fVar15);
        fVar15 = audio_uart_nema_sin_52405c(fVar15);
        fVar15 = -fVar15;
        fStack_1e4 = fVar16 - fVar18 * fVar13;
        fStack_1e0 = fVar17 - fVar20 * fVar13;
        uVar9 = iVar8 - 1;
        if (1 < iVar8) {
          pfVar7 = afStack_1f4 + 6;
          for (uVar6 = uVar9 & 3; uVar6 != 0; uVar6 = uVar6 - 1) {
            *pfVar7 = fVar16 + fVar13 * fVar18;
            pfVar7[1] = fVar17 + fVar13 * fVar20;
            fVar14 = fVar15 * fVar18;
            fVar18 = fVar12 * fVar18 - fVar15 * fVar20;
            pfVar7 = pfVar7 + 2;
            fVar20 = fVar14 + fVar12 * fVar20;
          }
          for (uVar6 = uVar9 >> 2; uStack_1e8 = uVar9, uVar6 != 0; uVar6 = uVar6 - 1) {
            *pfVar7 = fVar16 + fVar13 * fVar18;
            pfVar7[1] = fVar17 + fVar13 * fVar20;
            fVar14 = fVar12 * fVar18 - fVar15 * fVar20;
            pfVar7[2] = fVar16 + fVar13 * fVar14;
            fVar20 = fVar15 * fVar18 + fVar12 * fVar20;
            fVar19 = fVar15 * fVar14 + fVar12 * fVar20;
            fVar18 = fVar12 * fVar14 - fVar15 * fVar20;
            pfVar7[4] = fVar16 + fVar13 * fVar18;
            pfVar7[3] = fVar17 + fVar13 * fVar20;
            fVar14 = fVar15 * fVar18 + fVar12 * fVar19;
            fVar18 = fVar12 * fVar18 - fVar15 * fVar19;
            pfVar7[5] = fVar17 + fVar13 * fVar19;
            pfVar7[6] = fVar16 + fVar13 * fVar18;
            pfVar7[7] = fVar17 + fVar13 * fVar14;
            fVar20 = fVar15 * fVar18 + fVar12 * fVar14;
            fVar18 = fVar12 * fVar18 - fVar15 * fVar14;
            pfVar7 = pfVar7 + 8;
          }
        }
        uVar6 = audio_uart_nema_stencil_save_52266e
                          (0,-(uint)((*(byte *)(*piVar5 + 0x7d) & 0x10) == 0) >> 0x1f,0,0);
        g2c_nema_vg_path_transform_523a34(afStack_1f4 + 4,uVar9,2);
        bVar11 = -1 < (int)((uint)*(byte *)(*piVar5 + 0x7d) << 0x1b);
        audio_uart_nema_stencil_save_52266e(0,(uint)bVar11,(uint)bVar11,0);
        g2c_nema_raster_triangle_f_522a24
                  (fStack_1e4,fStack_1e0,afStack_1f4[iVar8 * 2],afStack_1f4[iVar8 * 2 + 1],
                   afStack_1f4[iVar8 * 2 + 2],afStack_1f4[iVar8 * 2 + 3]);
        goto LAB_0051b9d8;
      }
    }
    fVar12 = *(float *)(iVar8 + 0x2d8);
    fVar15 = (*(float *)(iVar8 + 0x150) - *(float *)(iVar8 + 0x138)) / fVar12;
    fVar18 = (*(float *)(iVar8 + 0x150) + *(float *)(iVar8 + 0x138)) * 0.5f;
    fVar13 = fVar12 * 0.5f;
    fVar12 = (*(float *)(iVar8 + 0x154) - *(float *)(iVar8 + 0x13c)) / fVar12;
    fVar20 = (*(float *)(iVar8 + 0x154) + *(float *)(iVar8 + 0x13c)) * 0.5f;
    uVar6 = g2c_nema_vg_f2u_522f1c(fVar13);
    iVar8 = (int)uVar6 / 2;
    fVar17 = (float)VectorSignedToFloat(iVar8,(byte)(uVar9 >> 0x16) & 3);
    fVar17 = (180.0f) / fVar17;
    fVar16 = audio_uart_nema_cos_524130(fVar17);
    fVar17 = audio_uart_nema_sin_52405c(fVar17);
    fVar17 = -fVar17;
    fStack_1e4 = fVar18 - fVar15 * fVar13;
    fStack_1e0 = fVar20 - fVar12 * fVar13;
    uVar9 = iVar8 - 1;
    if (1 < iVar8) {
      pfVar7 = afStack_1f4 + 6;
      for (uVar6 = uVar9 & 3; uVar6 != 0; uVar6 = uVar6 - 1) {
        *pfVar7 = fVar18 + fVar13 * fVar15;
        pfVar7[1] = fVar20 + fVar13 * fVar12;
        fVar14 = fVar17 * fVar15;
        fVar15 = fVar16 * fVar15 - fVar17 * fVar12;
        pfVar7 = pfVar7 + 2;
        fVar12 = fVar14 + fVar16 * fVar12;
      }
      for (uVar6 = uVar9 >> 2; uStack_1e8 = uVar9, uVar6 != 0; uVar6 = uVar6 - 1) {
        *pfVar7 = fVar18 + fVar13 * fVar15;
        pfVar7[1] = fVar20 + fVar13 * fVar12;
        fVar14 = fVar16 * fVar15 - fVar17 * fVar12;
        pfVar7[2] = fVar18 + fVar13 * fVar14;
        fVar12 = fVar17 * fVar15 + fVar16 * fVar12;
        fVar19 = fVar17 * fVar14 + fVar16 * fVar12;
        fVar15 = fVar16 * fVar14 - fVar17 * fVar12;
        pfVar7[4] = fVar18 + fVar13 * fVar15;
        pfVar7[3] = fVar20 + fVar13 * fVar12;
        fVar14 = fVar17 * fVar15 + fVar16 * fVar19;
        fVar15 = fVar16 * fVar15 - fVar17 * fVar19;
        pfVar7[5] = fVar20 + fVar13 * fVar19;
        pfVar7[6] = fVar18 + fVar13 * fVar15;
        pfVar7[7] = fVar20 + fVar13 * fVar14;
        fVar12 = fVar17 * fVar15 + fVar16 * fVar14;
        fVar15 = fVar16 * fVar15 - fVar17 * fVar14;
        pfVar7 = pfVar7 + 8;
      }
    }
    uVar6 = audio_uart_nema_stencil_save_52266e
                      (0,-(uint)((*(byte *)(*piVar5 + 0x7d) & 0x10) == 0) >> 0x1f,0,0);
    g2c_nema_vg_path_transform_523a34(afStack_1f4 + 4,uVar9,2);
    bVar11 = -1 < (int)((uint)*(byte *)(*piVar5 + 0x7d) << 0x1b);
    audio_uart_nema_stencil_save_52266e(0,(uint)bVar11,(uint)bVar11,0);
    g2c_nema_raster_triangle_f_522a24
              (fStack_1e4,fStack_1e0,afStack_1f4[iVar8 * 2],afStack_1f4[iVar8 * 2 + 1],
               afStack_1f4[iVar8 * 2 + 2],afStack_1f4[iVar8 * 2 + 3]);
    goto LAB_0051b9d8;
  }
  fVar12 = *(float *)(iVar8 + 400);
  fVar15 = *(float *)(iVar8 + 0x198);
  bVar11 = fVar12 == fVar15;
  if (bVar11) {
    fVar15 = *(float *)(iVar8 + 0x194);
    c = *(float *)(iVar8 + 0x19c);
  }
  if (bVar11 && (bVar11 && fVar15 == c)) {
    fVar16 = *(float *)(iVar8 + 0x1a0);
    fVar17 = *(float *)(iVar8 + 0x1a8);
    bVar11 = fVar16 == fVar17;
    if (bVar11) {
      fVar17 = *(float *)(iVar8 + 0x1a4);
      e = *(float *)(iVar8 + 0x1ac);
    }
    if (bVar11 && (bVar11 && fVar17 == e)) {
      fVar18 = *(float *)(iVar8 + 300) * -0.5f;
      bVar11 = -1 < (int)((uint)*(byte *)(iVar8 + 0x7d) << 0x1b);
      uVar6 = audio_uart_nema_stencil_save_52266e((uint)bVar11,0,(uint)bVar11,(uint)bVar11);
      g2c_nema_vg_emit_verts_516b34
                (fVar18 + fVar12,fVar15,fVar12,fVar15,fVar16,fVar17,fVar18 + fVar16,fVar17);
      goto LAB_0051b9d8;
    }
  }
  fVar15 = 0.5f;
  fVar16 = *(float *)(iVar8 + 300) * 0.5f;
  bVar11 = *(float *)(iVar8 + 0x140) <= *(float *)(iVar8 + 0x138);
  uVar2 = *(undefined8 *)(iVar8 + 0x138);
  uVar3 = *(undefined8 *)(iVar8 + 0x150);
  fVar12 = *(float *)(iVar8 + 0x150);
  uVar4 = *(undefined8 *)(iVar8 + 0x138);
  fVar17 = *(float *)(iVar8 + 0x154);
  if (!bVar11) {
    fVar15 = *(float *)(iVar8 + 0x148);
  }
  fVar13 = (float)g2c_bits_to_float((uint)(uVar4));
  fVar19 = fVar12 - fVar13;
  fVar14 = (float)g2c_bits_to_float((uint)(((ulonglong)uVar4 >> 0x20)));
  fVar20 = fVar17 - fVar14;
  fVar18 = g2c_nema_vg_sqrt_524218(fVar19 * fVar19 + fVar20 * fVar20);
  fVar20 = -(fVar20 / fVar18);
  if (bVar11 || (bVar11 || fVar15 <= fVar12)) {
    if (0.0f < fVar20) goto LAB_0051ba64;
LAB_0051baa6:
    fVar12 = fVar12 - fVar16 * fVar20;
    fVar15 = fVar16 * (fVar19 / fVar18);
    fVar13 = fVar13 - fVar16 * fVar20;
    fVar17 = fVar17 - fVar15;
    fVar15 = fVar14 - fVar15;
  }
  else {
    if (0.0f < fVar20) goto LAB_0051baa6;
LAB_0051ba64:
    fVar12 = fVar16 * fVar20 + fVar12;
    fVar15 = fVar16 * (fVar19 / fVar18);
    fVar13 = fVar16 * fVar20 + fVar13;
    fVar17 = fVar15 + fVar17;
    fVar15 = fVar15 + fVar14;
  }
  bVar11 = -1 < (int)((uint)*(byte *)(*piVar5 + 0x7d) << 0x1b);
  uVar6 = audio_uart_nema_stencil_save_52266e(0,(uint)bVar11,(uint)bVar11,(uint)bVar11);
  g2c_nema_vg_emit_verts_516b34
            ((float)g2c_bits_to_float((uint)(uVar2)),(float)g2c_bits_to_float((uint)(((ulonglong)uVar2 >> 0x20))),(float)g2c_bits_to_float((uint)(uVar3)),
             (float)g2c_bits_to_float((uint)(((ulonglong)uVar3 >> 0x20))),fVar12,fVar17,fVar13,fVar15);
  if ((int)((uint)*(byte *)(*piVar5 + 0x7d) << 0x1b) < 0) {
    return 0;
  }
LAB_0051b9d8:
  audio_uart_nema_stencil_restore_5226b2(uVar6);
  return 0;
}

  

/* ---- lifted 0x51bf7c ---- */


/* Evidence: stock FUN_0051bf7c @ 0x51bf7c; outer ambient FPSCR decl removed
 * (dead); live FPSCR scratch remains where NAN/Z flags still thread. */
uint g2c_nema_vg_arc_seg2_51bf7c(float a,float b,float c,float d,float e)

{
  char cVar1;
  undefined8 uVar2;
  undefined8 uVar3;
  int *piVar4;
  uint uVar5;
  float *pfVar6;
  int iVar7;
  uint uVar8;
  byte bVar9;
  bool bVar10;
  bool bVar11;
  float fVar12;
  float fVar13;
  float fVar14;
  float fVar15;
  float fVar16;
  float fVar17;
  float fVar18;
  float fVar19;
  float fVar20;
  float afStack_1f4 [3];
  uint uStack_1e8;
  float fStack_1e4;
  float fStack_1e0;
  float afStack_1dc [97];
  
  piVar4 = (((int *)&audio_uart_nema_vg_context_cell));
  iVar7 = *(((int *)&audio_uart_nema_vg_context_cell));
  bVar11 = *(int *)(iVar7 + 0x110) == 0;
  cVar1 = '\0';
  if (!bVar11) {
    cVar1 = *(char *)(iVar7 + 0x2e1);
  }
  if (bVar11 || cVar1 == '\0') {
    return 0;
  }
  if (cVar1 != '\x02') {
    if (cVar1 != '\x01') {
      return 0x800000;
    }
    fVar18 = *(float *)(iVar7 + 0x198);
    fVar17 = *(float *)(iVar7 + 400);
    /* stock 0x51bfaa vcmp; ittt eq; vcmpeq 0x51bfbc; bne 0x51c06e (EQ ordered; wave19) */
    uVar8 = 0; /* Z-only stand-in dropped (wave19): compare moved into the test below */
    fVar12 = *(float *)(iVar7 + 0x19c);
    bVar9 = 0;
    if ((byte)(fVar17 == fVar18) != 0) {
      d = *(float *)(iVar7 + 0x194);
      uVar8 = 0; /* Z-only stand-in dropped (wave19): compare moved into the test below */
      bVar9 = (byte)(d == fVar12);
    }
    if (bVar9 != 0) {
      fVar14 = *(float *)(iVar7 + 0x1a0);
      fVar15 = *(float *)(iVar7 + 0x1a8);
      uVar5 = uVar8 & 0xfffffff;
      /* stock 0x51bfce vcmp; itttt eq; vcmpeq 0x51bfe0; bne 0x51c06e (EQ ordered; wave19) */
      uVar8 = uVar5; /* Z-only stand-in dropped (wave19): compare moved into the test below */
      bVar9 = 0;
      if ((byte)(fVar14 == fVar15) != 0) {
        fVar15 = *(float *)(iVar7 + 0x1a4);
        uVar8 = uVar5; /* Z-only stand-in dropped (wave19): compare moved into the test below */
        bVar9 = (byte)(fVar15 == *(float *)(iVar7 + 0x1ac));
      }
      if (bVar9 != 0) {
        fVar18 = *(float *)(iVar7 + 0x2d8);
        fVar12 = (fVar17 - fVar14) / fVar18;
        fVar14 = (fVar17 + fVar14) * 0.5f;
        fVar20 = fVar18 * 0.5f;
        fVar18 = (d - fVar15) / fVar18;
        fVar13 = (d + fVar15) * 0.5f;
        uVar5 = g2c_nema_vg_f2u_522f1c(fVar20);
        iVar7 = (int)uVar5 / 2;
        fVar17 = (float)VectorSignedToFloat(iVar7,(byte)(uVar8 >> 0x16) & 3);
        fVar17 = (180.0f) / fVar17;
        fVar15 = audio_uart_nema_cos_524130(fVar17);
        fVar17 = audio_uart_nema_sin_52405c(fVar17);
        fStack_1e4 = fVar14 - fVar12 * fVar20;
        fStack_1e0 = fVar13 - fVar18 * fVar20;
        uVar8 = iVar7 - 1;
        if (1 < iVar7) {
          pfVar6 = afStack_1f4 + 6;
          for (uVar5 = uVar8 & 3; uVar5 != 0; uVar5 = uVar5 - 1) {
            *pfVar6 = fVar14 + fVar20 * fVar12;
            pfVar6[1] = fVar13 + fVar20 * fVar18;
            fVar19 = fVar17 * fVar12;
            fVar12 = fVar15 * fVar12 - fVar17 * fVar18;
            pfVar6 = pfVar6 + 2;
            fVar18 = fVar19 + fVar15 * fVar18;
          }
          for (uVar5 = uVar8 >> 2; uStack_1e8 = uVar8, uVar5 != 0; uVar5 = uVar5 - 1) {
            *pfVar6 = fVar14 + fVar20 * fVar12;
            pfVar6[1] = fVar13 + fVar20 * fVar18;
            fVar19 = fVar15 * fVar12 - fVar17 * fVar18;
            pfVar6[2] = fVar14 + fVar20 * fVar19;
            fVar18 = fVar17 * fVar12 + fVar15 * fVar18;
            fVar16 = fVar17 * fVar19 + fVar15 * fVar18;
            fVar12 = fVar15 * fVar19 - fVar17 * fVar18;
            pfVar6[4] = fVar14 + fVar20 * fVar12;
            pfVar6[3] = fVar13 + fVar20 * fVar18;
            fVar19 = fVar17 * fVar12 + fVar15 * fVar16;
            fVar12 = fVar15 * fVar12 - fVar17 * fVar16;
            pfVar6[5] = fVar13 + fVar20 * fVar16;
            pfVar6[6] = fVar14 + fVar20 * fVar12;
            pfVar6[7] = fVar13 + fVar20 * fVar19;
            fVar18 = fVar17 * fVar12 + fVar15 * fVar19;
            fVar12 = fVar15 * fVar12 - fVar17 * fVar19;
            pfVar6 = pfVar6 + 8;
          }
        }
        uVar5 = audio_uart_nema_stencil_save_52266e
                          (0,-(uint)((*(byte *)(*piVar4 + 0x7d) & 0x10) == 0) >> 0x1f,0,0);
        g2c_nema_vg_path_transform_523a34(afStack_1f4 + 4,uVar8,2);
        bVar11 = -1 < (int)((uint)*(byte *)(*piVar4 + 0x7d) << 0x1b);
        audio_uart_nema_stencil_save_52266e(0,(uint)bVar11,(uint)bVar11,0);
        g2c_nema_raster_triangle_f_522a24
                  (fStack_1e4,fStack_1e0,afStack_1f4[iVar7 * 2],afStack_1f4[iVar7 * 2 + 1],
                   afStack_1f4[iVar7 * 2 + 2],afStack_1f4[iVar7 * 2 + 3]);
        goto LAB_0051c05e;
      }
    }
    fVar15 = *(float *)(iVar7 + 0x2d8);
    fVar14 = (*(float *)(iVar7 + 0x1a0) + fVar18) * 0.5f;
    fVar20 = fVar15 * 0.5f;
    fVar17 = (*(float *)(iVar7 + 0x1a4) - fVar12) / fVar15;
    fVar13 = (*(float *)(iVar7 + 0x1a4) + fVar12) * 0.5f;
    fVar15 = (*(float *)(iVar7 + 0x1a0) - fVar18) / fVar15;
    uVar5 = g2c_nema_vg_f2u_522f1c(fVar20);
    iVar7 = (int)uVar5 / 2;
    fVar12 = (float)VectorSignedToFloat(iVar7,(byte)(uVar8 >> 0x16) & 3);
    fVar12 = (180.0f) / fVar12;
    fVar18 = audio_uart_nema_cos_524130(fVar12);
    fVar12 = audio_uart_nema_sin_52405c(fVar12);
    fStack_1e4 = fVar14 - fVar15 * fVar20;
    fStack_1e0 = fVar13 - fVar17 * fVar20;
    uVar8 = iVar7 - 1;
    if (1 < iVar7) {
      pfVar6 = afStack_1f4 + 6;
      for (uVar5 = uVar8 & 3; uVar5 != 0; uVar5 = uVar5 - 1) {
        *pfVar6 = fVar14 + fVar20 * fVar15;
        pfVar6[1] = fVar13 + fVar20 * fVar17;
        fVar19 = fVar12 * fVar15;
        fVar15 = fVar18 * fVar15 - fVar12 * fVar17;
        pfVar6 = pfVar6 + 2;
        fVar17 = fVar19 + fVar18 * fVar17;
      }
      for (uVar5 = uVar8 >> 2; uStack_1e8 = uVar8, uVar5 != 0; uVar5 = uVar5 - 1) {
        *pfVar6 = fVar14 + fVar20 * fVar15;
        pfVar6[1] = fVar13 + fVar20 * fVar17;
        fVar19 = fVar18 * fVar15 - fVar12 * fVar17;
        pfVar6[2] = fVar14 + fVar20 * fVar19;
        fVar15 = fVar12 * fVar15 + fVar18 * fVar17;
        fVar16 = fVar12 * fVar19 + fVar18 * fVar15;
        fVar17 = fVar18 * fVar19 - fVar12 * fVar15;
        pfVar6[4] = fVar14 + fVar20 * fVar17;
        pfVar6[3] = fVar13 + fVar20 * fVar15;
        fVar19 = fVar12 * fVar17 + fVar18 * fVar16;
        fVar15 = fVar18 * fVar17 - fVar12 * fVar16;
        pfVar6[5] = fVar13 + fVar20 * fVar16;
        pfVar6[6] = fVar14 + fVar20 * fVar15;
        pfVar6[7] = fVar13 + fVar20 * fVar19;
        fVar17 = fVar12 * fVar15 + fVar18 * fVar19;
        fVar15 = fVar18 * fVar15 - fVar12 * fVar19;
        pfVar6 = pfVar6 + 8;
      }
    }
    uVar5 = audio_uart_nema_stencil_save_52266e
                      (0,-(uint)((*(byte *)(*piVar4 + 0x7d) & 0x10) == 0) >> 0x1f,0,0);
    g2c_nema_vg_path_transform_523a34(afStack_1f4 + 4,uVar8,2);
    bVar11 = -1 < (int)((uint)*(byte *)(*piVar4 + 0x7d) << 0x1b);
    audio_uart_nema_stencil_save_52266e(0,(uint)bVar11,(uint)bVar11,0);
    g2c_nema_raster_triangle_f_522a24
              (fStack_1e4,fStack_1e0,afStack_1f4[iVar7 * 2],afStack_1f4[iVar7 * 2 + 1],
               afStack_1f4[iVar7 * 2 + 2],afStack_1f4[iVar7 * 2 + 3]);
    goto LAB_0051c05e;
  }
  fVar18 = *(float *)(iVar7 + 0x198);
  fVar12 = *(float *)(iVar7 + 400);
  bVar11 = fVar12 == fVar18;
  fVar17 = *(float *)(iVar7 + 0x19c);
  if (bVar11) {
    b = *(float *)(iVar7 + 0x194);
  }
  if (bVar11 && (bVar11 && b == fVar17)) {
    fVar14 = *(float *)(iVar7 + 0x1a0);
    fVar15 = *(float *)(iVar7 + 0x1a8);
    bVar11 = fVar14 == fVar15;
    if (bVar11) {
      fVar15 = *(float *)(iVar7 + 0x1a4);
      e = *(float *)(iVar7 + 0x1ac);
    }
    if (bVar11 && (bVar11 && fVar15 == e)) {
      fVar18 = *(float *)(iVar7 + 300) * 0.5f;
      uVar8 = (uint)(-1 < (int)((uint)*(byte *)(iVar7 + 0x7d) << 0x1b));
      uVar5 = audio_uart_nema_stencil_save_52266e(uVar8,uVar8,uVar8,0);
      g2c_nema_vg_emit_verts_516b34(fVar12,b,fVar18 + fVar12,b,fVar18 + fVar14,fVar15,fVar14,fVar15)
      ;
      goto LAB_0051c05e;
    }
  }
  /* stock 0x51c080 vcmp s0,s25; itttt ge; vldrge [0x1a8]; vcmpge 0x51c0a2 s0,[0x1a0]; movge r5,#1;
     0x51c0d0 cmp r5,#0; beq 0x51c11a. r5 = both ordered >= (wave18; replaces the LT/unordered pair). */
  bVar11 = (fVar12 >= fVar18);
  uVar2 = *(undefined8 *)(iVar7 + 0x198);
  uVar3 = *(undefined8 *)(iVar7 + 0x1a0);
  fVar14 = *(float *)(iVar7 + 300) * 0.5f;
  fVar12 = *(float *)(iVar7 + 0x1a0);
  fVar15 = *(float *)(iVar7 + 0x1a4);
  if (bVar11) {
    bVar11 = (*(float *)(iVar7 + 0x1a8) >= fVar12);
  }
  fVar19 = fVar12 - fVar18;
  fVar20 = fVar15 - fVar17;
  fVar13 = g2c_nema_vg_sqrt_524218(fVar19 * fVar19 + fVar20 * fVar20);
  fVar20 = -(fVar20 / fVar13);
  if (bVar11) {
    if (0.0f < fVar20) goto LAB_0051c120;
LAB_0051c0de:
    fVar12 = fVar14 * fVar20 + fVar12;
    fVar13 = fVar14 * (fVar19 / fVar13);
    fVar18 = fVar14 * fVar20 + fVar18;
    fVar15 = fVar13 + fVar15;
    fVar13 = fVar13 + fVar17;
  }
  else {
    if (0.0f < fVar20) goto LAB_0051c0de;
LAB_0051c120:
    fVar12 = fVar12 - fVar14 * fVar20;
    fVar13 = fVar14 * (fVar19 / fVar13);
    fVar18 = fVar18 - fVar14 * fVar20;
    fVar15 = fVar15 - fVar13;
    fVar13 = fVar17 - fVar13;
  }
  bVar11 = -1 < (int)((uint)*(byte *)(*piVar4 + 0x7d) << 0x1b);
  uVar5 = audio_uart_nema_stencil_save_52266e(0,(uint)bVar11,(uint)bVar11,(uint)bVar11);
  g2c_nema_vg_emit_verts_516b34
            ((float)g2c_bits_to_float((uint)(uVar2)),(float)g2c_bits_to_float((uint)(((ulonglong)uVar2 >> 0x20))),(float)g2c_bits_to_float((uint)(uVar3)),
             (float)g2c_bits_to_float((uint)(((ulonglong)uVar3 >> 0x20))),fVar12,fVar15,fVar18,fVar13);
  if ((int)((uint)*(byte *)(*piVar4 + 0x7d) << 0x1b) < 0) {
    return 0;
  }
LAB_0051c05e:
  audio_uart_nema_stencil_restore_5226b2(uVar5);
  return 0;
}

  

/* ---- lifted 0x51c5ec ---- */


uint g2c_nema_vg_arc_seg3_51c5ec(float a,float b,float c,float d,float e)

{
  char cVar1;
  undefined8 uVar2;
  byte bVar3;
  undefined8 uVar4;
  int *piVar5;
  uint uVar6;
  float *pfVar7;
  uint uVar8;
  int iVar9;
  byte bVar10;
  bool bVar11;
  bool bVar12;
  /* Evidence (wave10, stock 2.2.6.10 0x51c5ec..): every FPSCR read here is
   * vcmp.f32 + vmrs APSR_nzcv (0x51c61a, 0x51c62c, 0x51c640, 0x51c652,
   * 0x51c6fe, 0x51c710, 0x51c804/0x51c80a/0x51c84c). NZCV is fully rewritten by each
   * vcmp, so flag tests are the float compares themselves. RMode is RN:
   * FPSCR is set once to 0x02040000 at 0x5e428c, and the only other vmsr
   * writers (0x4d42e0/0x4d42ec, 0x59d2ea/0x59d2f6) restore it after clearing
   * the exception bits. */
  float fVar13;
  float fVar14;
  float fVar15;
  float fVar16;
  float fVar17;
  float fVar18;
  float fVar19;
  float fVar20;
  float fVar21;
  float fVar22;
  float afStack_1f4 [4];
  float fStack_1e4;
  float fStack_1e0;
  float afStack_1dc [97];
  
  piVar5 = (((int *)&audio_uart_nema_vg_context_cell));
  iVar9 = *(((int *)&audio_uart_nema_vg_context_cell));
  bVar12 = *(int *)(iVar9 + 0x110) != 0;
  cVar1 = '\0';
  if (bVar12) {
    cVar1 = *(char *)(iVar9 + 0x2e0);
  }
  if (bVar12 && cVar1 != '\0') {
    if (cVar1 == '\x02') {
      fVar13 = *(float *)(iVar9 + 400);
      fVar16 = *(float *)(iVar9 + 0x198);
      bVar10 = 0;
      if (fVar13 == fVar16) {
        fVar16 = *(float *)(iVar9 + 0x194);
        bVar10 = (byte)(fVar16 == *(float *)(iVar9 + 0x19c));
      }
      if (bVar10 != 0) {
        fVar17 = *(float *)(iVar9 + 0x1a0);
        fVar18 = *(float *)(iVar9 + 0x1a8);
        bVar10 = 0;
        if (fVar17 == fVar18) {
          fVar18 = *(float *)(iVar9 + 0x1a4);
          bVar10 = (byte)(fVar18 == *(float *)(iVar9 + 0x1ac));
        }
        if (bVar10 != 0) {
          fVar20 = *(float *)(iVar9 + 300) * -0.5f;
          bVar12 = -1 < (int)((uint)*(byte *)(iVar9 + 0x7d) << 0x1b);
          uVar6 = audio_uart_nema_stencil_save_52266e((uint)bVar12,0,(uint)bVar12,(uint)bVar12);
          g2c_nema_vg_emit_verts_516b34
                    (fVar20 + fVar13,fVar16,fVar13,fVar16,fVar17,fVar18,fVar20 + fVar17,fVar18);
          goto LAB_0051c6d8;
        }
      }
      fStack_1e0 = *(float *)(iVar9 + 0x138);
      afStack_1dc[0] = *(float *)(iVar9 + 0x13c);
      afStack_1f4[3] = *(float *)(iVar9 + 0x150);
      fStack_1e4 = *(float *)(iVar9 + 0x154);
      fVar18 = *(float *)(iVar9 + 300) * 0.5f;
      fVar16 = *(float *)(iVar9 + 0x150);
      uVar2 = *(undefined8 *)(iVar9 + 0x138);
      fVar13 = *(float *)(iVar9 + 0x154);
      bVar10 = 0;
      if (*(float *)(iVar9 + 0x138) < *(float *)(iVar9 + 0x140)) {
        bVar10 = (byte)(fVar16 < *(float *)(iVar9 + 0x148));
      }
      fVar14 = (float)g2c_bits_to_float((uint)(uVar2));
      fVar21 = fVar16 - fVar14;
      fVar22 = (float)g2c_bits_to_float((uint)(((ulonglong)uVar2 >> 0x20)));
      fVar20 = fVar13 - fVar22;
      fVar17 = g2c_nema_vg_sqrt_524218(fVar21 * fVar21 + fVar20 * fVar20);
      fVar20 = -(fVar20 / fVar17);
      if (bVar10 == 0) {
        /* 0x51c84c vmrs; bhi 0x51c810: C&&!Z, true for f>0 or unordered. */
        if (!(fVar20 <= 0.0f)) goto LAB_0051c810;
LAB_0051c852:
        fVar16 = fVar16 - fVar18 * fVar20;
        fVar17 = fVar18 * (fVar21 / fVar17);
        fVar14 = fVar14 - fVar18 * fVar20;
        fVar13 = fVar13 - fVar17;
        fVar17 = fVar22 - fVar17;
      }
      else {
        /* 0x51c80a vmrs; bgt 0x51c852 */
        if (fVar20 > 0.0f)
        goto LAB_0051c852;
LAB_0051c810:
        fVar16 = fVar18 * fVar20 + fVar16;
        fVar17 = fVar18 * (fVar21 / fVar17);
        fVar14 = fVar18 * fVar20 + fVar14;
        fVar13 = fVar17 + fVar13;
        fVar17 = fVar17 + fVar22;
      }
      bVar12 = -1 < (int)((uint)*(byte *)(*piVar5 + 0x7d) << 0x1b);
      uVar6 = audio_uart_nema_stencil_save_52266e(0,(uint)bVar12,(uint)bVar12,(uint)bVar12);
      g2c_nema_vg_emit_verts_516b34
                (fStack_1e0,afStack_1dc[0],afStack_1f4[3],fStack_1e4,fVar16,fVar13,fVar14,fVar17);
      /* Evidence: s1/s2/s4 (b/c/e) are dead after this call: stock reloads
       * them with vldreq [ctx,#0x194/#0x19c/#0x1ac] at 0x51c708/0x51c70c/0x51c732
       * before any read on every path from 0x51c6dc. */
      if ((int)((uint)*(byte *)(*piVar5 + 0x7d) << 0x1b) < 0) goto LAB_0051c6dc;
    }
    else {
      if (cVar1 != '\x01') goto LAB_0051cd0a;
      fVar13 = *(float *)(iVar9 + 400);
      fVar16 = *(float *)(iVar9 + 0x198);
      bVar10 = 0;
      if (fVar13 == fVar16) {
        fVar16 = *(float *)(iVar9 + 0x194);
        bVar10 = (byte)(fVar16 == *(float *)(iVar9 + 0x19c));
      }
      if (bVar10 != 0) {
        fVar17 = *(float *)(iVar9 + 0x1a0);
        fVar18 = *(float *)(iVar9 + 0x1a8);
        bVar10 = 0;
        if (fVar17 == fVar18) {
          fVar18 = *(float *)(iVar9 + 0x1a4);
          bVar10 = (byte)(fVar18 == *(float *)(iVar9 + 0x1ac));
        }
        if (bVar10 != 0) {
          fVar14 = *(float *)(iVar9 + 0x2d8);
          fVar20 = (fVar13 - fVar17) / fVar14;
          fVar17 = (fVar13 + fVar17) * 0.5f;
          fVar21 = fVar14 * 0.5f;
          fVar14 = (fVar16 - fVar18) / fVar14;
          fVar22 = (fVar16 + fVar18) * 0.5f;
          uVar6 = g2c_nema_vg_f2u_522f1c(fVar21);
          iVar9 = (int)uVar6 / 2;
          fVar16 = (float)VectorSignedToFloat(iVar9,G2C_FPSCR_RMODE_RN);
          fVar16 = (180.0f) / fVar16;
          fVar13 = audio_uart_nema_cos_524130(fVar16);
          fVar18 = audio_uart_nema_sin_52405c(fVar16);
          fVar18 = -fVar18;
          fStack_1e4 = fVar17 - fVar20 * fVar21;
          fStack_1e0 = fVar22 - fVar14 * fVar21;
          fVar16 = (float)(iVar9 - 1);
          if (1 < iVar9) {
            pfVar7 = afStack_1f4 + 6;
            for (uVar6 = (uint)g2c_float_to_bits(fVar16) & 3; uVar6 != 0; uVar6 = uVar6 - 1) {
              *pfVar7 = fVar17 + fVar21 * fVar20;
              pfVar7[1] = fVar22 + fVar21 * fVar14;
              fVar15 = fVar18 * fVar20;
              fVar20 = fVar13 * fVar20 - fVar18 * fVar14;
              pfVar7 = pfVar7 + 2;
              fVar14 = fVar15 + fVar13 * fVar14;
            }
            for (uVar6 = (uint)g2c_float_to_bits(fVar16) >> 2; afStack_1f4[3] = fVar16, uVar6 != 0; uVar6 = uVar6 - 1)
            {
              *pfVar7 = fVar17 + fVar21 * fVar20;
              pfVar7[1] = fVar22 + fVar21 * fVar14;
              fVar15 = fVar13 * fVar20 - fVar18 * fVar14;
              pfVar7[2] = fVar17 + fVar21 * fVar15;
              fVar14 = fVar18 * fVar20 + fVar13 * fVar14;
              fVar19 = fVar18 * fVar15 + fVar13 * fVar14;
              fVar20 = fVar13 * fVar15 - fVar18 * fVar14;
              pfVar7[4] = fVar17 + fVar21 * fVar20;
              pfVar7[3] = fVar22 + fVar21 * fVar14;
              fVar15 = fVar18 * fVar20 + fVar13 * fVar19;
              fVar20 = fVar13 * fVar20 - fVar18 * fVar19;
              pfVar7[5] = fVar22 + fVar21 * fVar19;
              pfVar7[6] = fVar17 + fVar21 * fVar20;
              pfVar7[7] = fVar22 + fVar21 * fVar15;
              fVar14 = fVar18 * fVar20 + fVar13 * fVar15;
              fVar20 = fVar13 * fVar20 - fVar18 * fVar15;
              pfVar7 = pfVar7 + 8;
            }
          }
          uVar6 = audio_uart_nema_stencil_save_52266e
                            (0,-(uint)((*(byte *)(*piVar5 + 0x7d) & 0x10) == 0) >> 0x1f,0,0);
          g2c_nema_vg_path_transform_523a34(afStack_1f4 + 4,(int)g2c_float_to_bits(fVar16),2);
          bVar12 = -1 < (int)((uint)*(byte *)(*piVar5 + 0x7d) << 0x1b);
          audio_uart_nema_stencil_save_52266e(0,(uint)bVar12,(uint)bVar12,0);
          g2c_nema_raster_triangle_f_522a24
                    (fStack_1e4,fStack_1e0,afStack_1f4[iVar9 * 2],afStack_1f4[iVar9 * 2 + 1],
                     afStack_1f4[iVar9 * 2 + 2],afStack_1f4[iVar9 * 2 + 3]);
          goto LAB_0051c6d8;
        }
      }
      fVar13 = *(float *)(iVar9 + 0x2d8);
      fVar16 = (*(float *)(iVar9 + 0x150) - *(float *)(iVar9 + 0x138)) / fVar13;
      fVar14 = (*(float *)(iVar9 + 0x150) + *(float *)(iVar9 + 0x138)) * 0.5f;
      fVar21 = fVar13 * 0.5f;
      fVar13 = (*(float *)(iVar9 + 0x154) - *(float *)(iVar9 + 0x13c)) / fVar13;
      fVar22 = (*(float *)(iVar9 + 0x154) + *(float *)(iVar9 + 0x13c)) * 0.5f;
      uVar6 = g2c_nema_vg_f2u_522f1c(fVar21);
      iVar9 = (int)uVar6 / 2;
      fVar18 = (float)VectorSignedToFloat(iVar9,G2C_FPSCR_RMODE_RN);
      fVar18 = (180.0f) / fVar18;
      fVar17 = audio_uart_nema_cos_524130(fVar18);
      fVar20 = audio_uart_nema_sin_52405c(fVar18);
      fVar20 = -fVar20;
      fStack_1e4 = fVar14 - fVar16 * fVar21;
      fStack_1e0 = fVar22 - fVar13 * fVar21;
      fVar18 = (float)(iVar9 - 1);
      if (1 < iVar9) {
        pfVar7 = afStack_1f4 + 6;
        for (uVar6 = (uint)g2c_float_to_bits(fVar18) & 3; uVar6 != 0; uVar6 = uVar6 - 1) {
          *pfVar7 = fVar14 + fVar21 * fVar16;
          pfVar7[1] = fVar22 + fVar21 * fVar13;
          fVar15 = fVar20 * fVar16;
          fVar16 = fVar17 * fVar16 - fVar20 * fVar13;
          pfVar7 = pfVar7 + 2;
          fVar13 = fVar15 + fVar17 * fVar13;
        }
        for (uVar6 = (uint)g2c_float_to_bits(fVar18) >> 2; afStack_1f4[3] = fVar18, uVar6 != 0; uVar6 = uVar6 - 1) {
          *pfVar7 = fVar14 + fVar21 * fVar16;
          pfVar7[1] = fVar22 + fVar21 * fVar13;
          fVar15 = fVar17 * fVar16 - fVar20 * fVar13;
          pfVar7[2] = fVar14 + fVar21 * fVar15;
          fVar13 = fVar20 * fVar16 + fVar17 * fVar13;
          fVar19 = fVar20 * fVar15 + fVar17 * fVar13;
          fVar16 = fVar17 * fVar15 - fVar20 * fVar13;
          pfVar7[4] = fVar14 + fVar21 * fVar16;
          pfVar7[3] = fVar22 + fVar21 * fVar13;
          fVar15 = fVar20 * fVar16 + fVar17 * fVar19;
          fVar16 = fVar17 * fVar16 - fVar20 * fVar19;
          pfVar7[5] = fVar22 + fVar21 * fVar19;
          pfVar7[6] = fVar14 + fVar21 * fVar16;
          pfVar7[7] = fVar22 + fVar21 * fVar15;
          fVar13 = fVar20 * fVar16 + fVar17 * fVar15;
          fVar16 = fVar17 * fVar16 - fVar20 * fVar15;
          pfVar7 = pfVar7 + 8;
        }
      }
      uVar6 = audio_uart_nema_stencil_save_52266e
                        (0,-(uint)((*(byte *)(*piVar5 + 0x7d) & 0x10) == 0) >> 0x1f,0,0);
      g2c_nema_vg_path_transform_523a34(afStack_1f4 + 4,(int)g2c_float_to_bits(fVar18),2);
      bVar12 = -1 < (int)((uint)*(byte *)(*piVar5 + 0x7d) << 0x1b);
      audio_uart_nema_stencil_save_52266e(0,(uint)bVar12,(uint)bVar12,0);
      g2c_nema_raster_triangle_f_522a24
                (fStack_1e4,fStack_1e0,afStack_1f4[iVar9 * 2],afStack_1f4[iVar9 * 2 + 1],
                 afStack_1f4[iVar9 * 2 + 2],afStack_1f4[iVar9 * 2 + 3]);
    }
LAB_0051c6d8:
    audio_uart_nema_stencil_restore_5226b2(uVar6);
  }
LAB_0051c6dc:
  iVar9 = *piVar5;
  bVar12 = *(int *)(iVar9 + 0x110) == 0;
  cVar1 = '\0';
  if (!bVar12) {
    cVar1 = *(char *)(iVar9 + 0x2e1);
  }
  if (bVar12 || cVar1 == '\0') {
    return 0;
  }
  if (cVar1 != '\x02') {
    if (cVar1 != '\x01') {
LAB_0051cd0a:
      *(undefined4 *)(iVar9 + 0x114) = 0;
      *(undefined4 *)(iVar9 + 0x118) = 0;
      audio_uart_nema_vg_set_error_51565c(0x800000);
      return 0x800000;
    }
    fVar16 = *(float *)(iVar9 + 0x198);
    fVar13 = *(float *)(iVar9 + 400);
    /* stock 0x51c61a vcmp; itttt eq; vcmpeq 0x51c62c; bne.w 0x51c788 (EQ ordered; wave19) */
    uVar6 = 0; /* Z-only stand-in dropped (wave19): compare moved into the test below */
    bVar10 = 0;
    if ((byte)(fVar13 == fVar16) != 0) {
      c = *(float *)(iVar9 + 0x194);
      uVar6 = 0; /* Z-only stand-in dropped (wave19): compare moved into the test below */
      bVar10 = (byte)(c == *(float *)(iVar9 + 0x19c));
    }
    if (bVar10 != 0) {
      fVar17 = *(float *)(iVar9 + 0x1a0);
      fVar18 = *(float *)(iVar9 + 0x1a8);
      uVar8 = uVar6 & 0xfffffff;
      /* stock 0x51c640 vcmp; itttt eq; vcmpeq 0x51c652; bne.w 0x51c788 (EQ ordered; wave19) */
      uVar6 = uVar8; /* Z-only stand-in dropped (wave19): compare moved into the test below */
      bVar10 = 0;
      if ((byte)(fVar17 == fVar18) != 0) {
        fVar18 = *(float *)(iVar9 + 0x1a4);
        uVar6 = uVar8; /* Z-only stand-in dropped (wave19): compare moved into the test below */
        bVar10 = (byte)(fVar18 == *(float *)(iVar9 + 0x1ac));
      }
      if (bVar10 != 0) {
        fVar20 = *(float *)(iVar9 + 0x2d8);
        fVar16 = (fVar13 - fVar17) / fVar20;
        fVar14 = (fVar13 + fVar17) * 0.5f;
        fVar21 = fVar20 * 0.5f;
        fVar20 = (c - fVar18) / fVar20;
        fVar22 = (c + fVar18) * 0.5f;
        uVar8 = g2c_nema_vg_f2u_522f1c(fVar21);
        iVar9 = (int)uVar8 / 2;
        fVar13 = (float)VectorSignedToFloat(iVar9,(byte)(uVar6 >> 0x16) & 3);
        fVar13 = (180.0f) / fVar13;
        fVar18 = audio_uart_nema_cos_524130(fVar13);
        fVar17 = audio_uart_nema_sin_52405c(fVar13);
        fStack_1e4 = fVar14 - fVar16 * fVar21;
        fStack_1e0 = fVar22 - fVar20 * fVar21;
        fVar13 = (float)(iVar9 - 1);
        if (1 < iVar9) {
          pfVar7 = afStack_1f4 + 6;
          for (uVar6 = (uint)g2c_float_to_bits(fVar13) & 3; uVar6 != 0; uVar6 = uVar6 - 1) {
            *pfVar7 = fVar14 + fVar21 * fVar16;
            pfVar7[1] = fVar22 + fVar21 * fVar20;
            fVar15 = fVar17 * fVar16;
            fVar16 = fVar18 * fVar16 - fVar17 * fVar20;
            pfVar7 = pfVar7 + 2;
            fVar20 = fVar15 + fVar18 * fVar20;
          }
          for (uVar6 = (uint)g2c_float_to_bits(fVar13) >> 2; afStack_1f4[3] = fVar13, uVar6 != 0; uVar6 = uVar6 - 1) {
            *pfVar7 = fVar14 + fVar21 * fVar16;
            pfVar7[1] = fVar22 + fVar21 * fVar20;
            fVar15 = fVar18 * fVar16 - fVar17 * fVar20;
            pfVar7[2] = fVar14 + fVar21 * fVar15;
            fVar20 = fVar17 * fVar16 + fVar18 * fVar20;
            fVar19 = fVar17 * fVar15 + fVar18 * fVar20;
            fVar16 = fVar18 * fVar15 - fVar17 * fVar20;
            pfVar7[4] = fVar14 + fVar21 * fVar16;
            pfVar7[3] = fVar22 + fVar21 * fVar20;
            fVar15 = fVar17 * fVar16 + fVar18 * fVar19;
            fVar16 = fVar18 * fVar16 - fVar17 * fVar19;
            pfVar7[5] = fVar22 + fVar21 * fVar19;
            pfVar7[6] = fVar14 + fVar21 * fVar16;
            pfVar7[7] = fVar22 + fVar21 * fVar15;
            fVar20 = fVar17 * fVar16 + fVar18 * fVar15;
            fVar16 = fVar18 * fVar16 - fVar17 * fVar15;
            pfVar7 = pfVar7 + 8;
          }
        }
        uVar6 = audio_uart_nema_stencil_save_52266e
                          (0,-(uint)((*(byte *)(*piVar5 + 0x7d) & 0x10) == 0) >> 0x1f,0,0);
        g2c_nema_vg_path_transform_523a34(afStack_1f4 + 4,(int)g2c_float_to_bits(fVar13),2);
        bVar12 = -1 < (int)((uint)*(byte *)(*piVar5 + 0x7d) << 0x1b);
        audio_uart_nema_stencil_save_52266e(0,(uint)bVar12,(uint)bVar12,0);
        g2c_nema_raster_triangle_f_522a24
                  (fStack_1e4,fStack_1e0,afStack_1f4[iVar9 * 2],afStack_1f4[iVar9 * 2 + 1],
                   afStack_1f4[iVar9 * 2 + 2],afStack_1f4[iVar9 * 2 + 3]);
        goto LAB_0051cd56;
      }
    }
    fVar18 = *(float *)(iVar9 + 0x2d8);
    fVar13 = (*(float *)(iVar9 + 0x1a0) - fVar16) / fVar18;
    fVar14 = (*(float *)(iVar9 + 0x1a0) + fVar16) * 0.5f;
    fVar21 = fVar18 * 0.5f;
    fVar18 = (*(float *)(iVar9 + 0x1a4) - *(float *)(iVar9 + 0x19c)) / fVar18;
    fVar22 = (*(float *)(iVar9 + 0x1a4) + *(float *)(iVar9 + 0x19c)) * 0.5f;
    uVar8 = g2c_nema_vg_f2u_522f1c(fVar21);
    iVar9 = (int)uVar8 / 2;
    fVar16 = (float)VectorSignedToFloat(iVar9,(byte)(uVar6 >> 0x16) & 3);
    fVar16 = (180.0f) / fVar16;
    fVar17 = audio_uart_nema_cos_524130(fVar16);
    fVar20 = audio_uart_nema_sin_52405c(fVar16);
    fStack_1e4 = fVar14 - fVar13 * fVar21;
    fStack_1e0 = fVar22 - fVar18 * fVar21;
    fVar16 = (float)(iVar9 - 1);
    if (1 < iVar9) {
      pfVar7 = afStack_1f4 + 6;
      for (uVar6 = (uint)g2c_float_to_bits(fVar16) & 3; uVar6 != 0; uVar6 = uVar6 - 1) {
        *pfVar7 = fVar14 + fVar21 * fVar13;
        pfVar7[1] = fVar22 + fVar21 * fVar18;
        fVar15 = fVar20 * fVar13;
        fVar13 = fVar17 * fVar13 - fVar20 * fVar18;
        pfVar7 = pfVar7 + 2;
        fVar18 = fVar15 + fVar17 * fVar18;
      }
      for (uVar6 = (uint)g2c_float_to_bits(fVar16) >> 2; afStack_1f4[3] = fVar16, uVar6 != 0; uVar6 = uVar6 - 1) {
        *pfVar7 = fVar14 + fVar21 * fVar13;
        pfVar7[1] = fVar22 + fVar21 * fVar18;
        fVar15 = fVar17 * fVar13 - fVar20 * fVar18;
        pfVar7[2] = fVar14 + fVar21 * fVar15;
        fVar18 = fVar20 * fVar13 + fVar17 * fVar18;
        fVar19 = fVar20 * fVar15 + fVar17 * fVar18;
        fVar13 = fVar17 * fVar15 - fVar20 * fVar18;
        pfVar7[4] = fVar14 + fVar21 * fVar13;
        pfVar7[3] = fVar22 + fVar21 * fVar18;
        fVar15 = fVar20 * fVar13 + fVar17 * fVar19;
        fVar13 = fVar17 * fVar13 - fVar20 * fVar19;
        pfVar7[5] = fVar22 + fVar21 * fVar19;
        pfVar7[6] = fVar14 + fVar21 * fVar13;
        pfVar7[7] = fVar22 + fVar21 * fVar15;
        fVar18 = fVar20 * fVar13 + fVar17 * fVar15;
        fVar13 = fVar17 * fVar13 - fVar20 * fVar15;
        pfVar7 = pfVar7 + 8;
      }
    }
    uVar6 = audio_uart_nema_stencil_save_52266e
                      (0,-(uint)((*(byte *)(*piVar5 + 0x7d) & 0x10) == 0) >> 0x1f,0,0);
    g2c_nema_vg_path_transform_523a34(afStack_1f4 + 4,(int)g2c_float_to_bits(fVar16),2);
    bVar12 = -1 < (int)((uint)*(byte *)(*piVar5 + 0x7d) << 0x1b);
    audio_uart_nema_stencil_save_52266e(0,(uint)bVar12,(uint)bVar12,0);
    g2c_nema_raster_triangle_f_522a24
              (fStack_1e4,fStack_1e0,afStack_1f4[iVar9 * 2],afStack_1f4[iVar9 * 2 + 1],
               afStack_1f4[iVar9 * 2 + 2],afStack_1f4[iVar9 * 2 + 3]);
    goto LAB_0051cd56;
  }
  fVar13 = *(float *)(iVar9 + 0x198);
  fVar16 = *(float *)(iVar9 + 400);
  bVar12 = fVar16 == fVar13;
  if (bVar12) {
    b = *(float *)(iVar9 + 0x194);
    c = *(float *)(iVar9 + 0x19c);
  }
  if (bVar12 && (bVar12 && b == c)) {
    fVar17 = *(float *)(iVar9 + 0x1a0);
    fVar18 = *(float *)(iVar9 + 0x1a8);
    bVar12 = fVar17 == fVar18;
    if (bVar12) {
      fVar18 = *(float *)(iVar9 + 0x1a4);
      e = *(float *)(iVar9 + 0x1ac);
    }
    if (bVar12 && (bVar12 && fVar18 == e)) {
      fVar13 = *(float *)(iVar9 + 300) * 0.5f;
      afStack_1f4[3] = fVar13 + fVar16;
      uVar6 = (uint)(-1 < (int)((uint)*(byte *)(iVar9 + 0x7d) << 0x1b));
      fStack_1e4 = b;
      fStack_1e0 = fVar16;
      afStack_1dc[0] = b;
      uVar6 = audio_uart_nema_stencil_save_52266e(uVar6,uVar6,uVar6,0);
      g2c_nema_vg_emit_verts_516b34
                (fStack_1e0,afStack_1dc[0],afStack_1f4[3],fStack_1e4,fVar13 + fVar17,fVar18,fVar17,
                 fVar18);
      goto LAB_0051cd56;
    }
  }
  /* stock 0x51cd78 vcmp s0,s24; itttt ge; vldrge [0x1a8]; vcmpge 0x51cd9e s0,[0x1a0]; movge r5,#1;
     0x51cdcc cmp r5,#0; beq 0x51ce16. r5 = both ordered >= (wave18). */
  bVar12 = (fVar16 >= fVar13);
  uVar2 = *(undefined8 *)(iVar9 + 0x198);
  uVar4 = *(undefined8 *)(iVar9 + 0x1a0);
  fVar17 = *(float *)(iVar9 + 300) * 0.5f;
  fVar16 = *(float *)(iVar9 + 0x1a0);
  fVar20 = *(float *)(iVar9 + 0x19c);
  fVar18 = *(float *)(iVar9 + 0x1a4);
  if (bVar12) {
    bVar12 = (*(float *)(iVar9 + 0x1a8) >= fVar16);
  }
  fVar21 = fVar16 - fVar13;
  fVar22 = fVar18 - fVar20;
  fVar14 = g2c_nema_vg_sqrt_524218(fVar21 * fVar21 + fVar22 * fVar22);
  fVar22 = -(fVar22 / fVar14);
  if (bVar12) {
    if (0.0f < fVar22) goto LAB_0051ce1c;
LAB_0051cdda:
    fVar16 = fVar17 * fVar22 + fVar16;
    fVar14 = fVar17 * (fVar21 / fVar14);
    fVar13 = fVar17 * fVar22 + fVar13;
    fVar18 = fVar14 + fVar18;
    fVar14 = fVar14 + fVar20;
  }
  else {
    if (0.0f < fVar22) goto LAB_0051cdda;
LAB_0051ce1c:
    fVar16 = fVar16 - fVar17 * fVar22;
    fVar14 = fVar17 * (fVar21 / fVar14);
    fVar13 = fVar13 - fVar17 * fVar22;
    fVar18 = fVar18 - fVar14;
    fVar14 = fVar20 - fVar14;
  }
  bVar12 = -1 < (int)((uint)*(byte *)(*piVar5 + 0x7d) << 0x1b);
  uVar6 = audio_uart_nema_stencil_save_52266e(0,(uint)bVar12,(uint)bVar12,(uint)bVar12);
  g2c_nema_vg_emit_verts_516b34
            ((float)g2c_bits_to_float((uint)(uVar2)),(float)g2c_bits_to_float((uint)(((ulonglong)uVar2 >> 0x20))),(float)g2c_bits_to_float((uint)(uVar4)),
             (float)g2c_bits_to_float((uint)(((ulonglong)uVar4 >> 0x20))),fVar16,fVar18,fVar13,fVar14);
  if ((int)((uint)*(byte *)(*piVar5 + 0x7d) << 0x1b) < 0) {
    return 0;
  }
LAB_0051cd56:
  audio_uart_nema_stencil_restore_5226b2(uVar6);
  return 0;
}

  

/* ---- lifted 0x51d2e0 ---- */


uint g2c_nema_vg_draw_fill_51d2e0(uint *a)

{
  /* sp+0 float slot: 0x522f50 out0 (stock 0x51e706/0x51e926 mov r0,sp; read back 0x51e7b0/0x51e94c vldr s0,[sp]). */
  float fStack_2d0 = 0.0f;
  char cVar1;
  undefined8 uVar2;
  int *piVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  float *pfVar10;
  uint uVar11;
  uint uVar12;
  uint uVar13;
  uint uVar14;
  byte bVar15;
  byte bVar16;
  bool bVar17;
  bool bVar18;
  float a_00;
  float a_01;
  float fVar19;
  float fVar20;
  float fVar21;
  float fVar22;
  float fVar23;
  float b;
  float b_00;
  float fVar24;
  float *pfVar25;
  float c;
  float c_00;
  float fVar26;
  float fVar27;
  float d;
  float d_00;
  float fVar28;
  float fVar29;
  float fVar30;
  float fVar31;
  float e;
  float e_00;
  float fVar32;
  float fVar33;
  float fVar34;
  float fVar35;
  float fVar36;
  undefined8 uVar37;
  undefined4 uVar38;
  undefined8 uVar39;
  undefined4 uVar40;
  float fVar41;
  float fVar42;
  float g;
  /* Stock frame of 0x51d2e0 as one block: locals keep the entry-SP offsets Ghidra named them by
   * (X_Stack_NN at g2c_frame_51d2e0[0x2d0-0xNN]) so &local passed to callees spans its stock neighbours. */
  unsigned char g2c_frame_51d2e0[0x2d0] __attribute__((aligned(8)));
  typedef float *__attribute__((may_alias)) g2c_fa_float_p;
#define pfStack_2cc (*(g2c_fa_float_p *)(void *)&g2c_frame_51d2e0[0x2d0-0x2cc])
  typedef float __attribute__((may_alias)) g2c_fa_float;
#define fStack_2c8 (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x2c8])
#define pfStack_2c4 (*(g2c_fa_float_p *)(void *)&g2c_frame_51d2e0[0x2d0-0x2c4])
#define fStack_2c0 (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x2c0])
#define fStack_2bc (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x2bc])
#define fStack_2b8 (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x2b8])
#define fStack_2b4 (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x2b4])
#define fStack_2b0 (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x2b0])
#define fStack_2ac (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x2ac])
#define fStack_2a8 (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x2a8])
#define fStack_2a4 (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x2a4])
#define fStack_2a0 (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x2a0])
#define fStack_29c (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x29c])
#define fStack_298 (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x298])
#define fStack_294 (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x294])
#define fStack_290 (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x290])
#define fStack_28c (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x28c])
#define fStack_288 (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x288])
#define fStack_284 (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x284])
#define fStack_280 (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x280])
#define fStack_27c (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x27c])
#define fStack_278 (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x278])
#define fStack_274 (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x274])
#define fStack_270 (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x270])
#define fStack_26c (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x26c])
#define fStack_268 (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x268])
#define fStack_264 (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x264])
#define fStack_260 (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x260])
#define fStack_25c (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x25c])
#define fStack_258 (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x258])
#define fStack_254 (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x254])
#define fStack_250 (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x250])
#define fStack_24c (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x24c])
#define fStack_248 (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x248])
  typedef undefined4 __attribute__((may_alias)) g2c_fa_undefined4;
#define uStack_244 (*(g2c_fa_undefined4 *)(void *)&g2c_frame_51d2e0[0x2d0-0x244])
#define uStack_240 (*(g2c_fa_undefined4 *)(void *)&g2c_frame_51d2e0[0x2d0-0x240])
#define uStack_23c (*(g2c_fa_undefined4 *)(void *)&g2c_frame_51d2e0[0x2d0-0x23c])
#define uStack_238 (*(g2c_fa_undefined4 *)(void *)&g2c_frame_51d2e0[0x2d0-0x238])
#define fStack_22c (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x22c])
#define fStack_228 (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x228])
#define fStack_224 (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x224])
#define fStack_220 (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x220])
#define fStack_21c (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x21c])
#define fStack_218 (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x218])
#define fStack_214 (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x214])
#define fStack_210 (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x210])
#define afStack_200 (((g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x200]))
#define fStack_1f0 (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x1f0])
#define fStack_1ec (*(g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x1ec])
#define afStack_1e8 (((g2c_fa_float *)(void *)&g2c_frame_51d2e0[0x2d0-0x1e8]))
  
  audio_uart_lv_memzero_48949c((uint)&uStack_238,0x48);
  piVar3 = (((int *)&audio_uart_nema_vg_context_cell));
  uVar12 = 0;
  ((byte *)&(uStack_238))[0] = 1;
  ((byte *)&(uStack_238))[2] = '\x01';
  ((byte *)&(uStack_238))[1] = '\x01';
  pfStack_2cc = (g2c_nvg_zero_pair_1);
LAB_0051d332:
  do {
    if (*a <= uVar12) {
      uVar12 = 0;
      iVar5 = -(uint)(((byte *)&(uStack_238))[1] == '\0');
      iVar6 = -(iVar5 >> 0x1f);
      if ((int)((uint)*(byte *)(*piVar3 + 0x7d) << 0x1b) < 0) {
        uVar12 = audio_uart_nema_stencil_save_52266e(0,0,0,0);
      }
      if (iVar5 < 0) {
        iVar7 = *piVar3;
        /* Evidence (wave12): stock 0x51e14c vcmp [+0x158],#0; ittt gt; vcmpgt [+0x184],#0;
         * ble.w 0x51e59c. Skip unless both values are > 0 (ordered). */
        if (!(*(float *)(iVar7 + 0x158) > 0.0f) || !(*(float *)(iVar7 + 0x184) > 0.0f))
          goto LAB_0051e59c;
        if (*(int *)(iVar7 + 0x110) == 0) goto LAB_0051e59c;
        cVar1 = *(char *)(iVar7 + 0x2e2);
        uVar4 = 0;
        fVar27 = (float)g2c_bits_to_float((uint)(*(undefined8 *)(iVar7 + 0x150)));
        fVar19 = (float)g2c_bits_to_float((uint)(((ulonglong)*(undefined8 *)(iVar7 + 0x150) >> 0x20)));
        fVar31 = (float)g2c_bits_to_float((uint)(*(undefined8 *)(iVar7 + 0x174)));
        pfVar25 = (float *)((ulonglong)*(undefined8 *)(iVar7 + 0x174) >> 0x20);
        fVar41 = (float)g2c_bits_to_float((uint)(*(undefined8 *)(iVar7 + 0x138)));
        fVar42 = (float)g2c_bits_to_float((uint)(((ulonglong)*(undefined8 *)(iVar7 + 0x138) >> 0x20)));
        fVar22 = (float)g2c_bits_to_float((uint)(*(undefined8 *)(iVar7 + 0x16c)));
        fVar21 = (float)g2c_bits_to_float((uint)(((ulonglong)*(undefined8 *)(iVar7 + 0x16c) >> 0x20)));
        if ((cVar1 == '\0') || (*(int *)(iVar7 + 0x118) != 0)) {
          if (-1 < (int)((uint)*(byte *)(iVar7 + 0x7d) << 0x1b)) {
            uVar4 = audio_uart_nema_stencil_save_52266e(1,0,1,0);
          }
          g2c_nema_vg_emit_verts_516b34
                    (fVar22,fVar21,fVar41,fVar42,fVar31,g2c_ptr_as_float(pfVar25),fVar27,fVar19);
LAB_0051e58c:
          if (-1 < (int)((uint)*(byte *)(*piVar3 + 0x7d) << 0x1b)) {
            audio_uart_nema_stencil_restore_5226b2(uVar4);
          }
          goto LAB_0051e59c;
        }
        if (cVar1 == '\x02') {
          fStack_2c8 = *(g2c_nvg_zero_pair_0);
          pfStack_2c4 = ((float *)g2c_float_as_ptr(g2c_nvg_zero_pair_0[1])) /* stock vldmia lit pair; vstmia sp (value copy) */;
          iVar7 = g2c_nema_vg_cubic_approx_522f50
                            (fVar22,fVar21,fVar31,g2c_ptr_as_float(pfVar25),fVar41,fVar42,fVar27,fVar19,
                             &fStack_2c8,(float *)&pfStack_2c4);
          if (iVar7 != 0) {
            iVar7 = *piVar3;
            fVar22 = audio_uart_float_sqrt_4397a8
                               (*(float *)(iVar7 + 0xec) * *(float *)(iVar7 + 0xec) +
                                *(float *)(iVar7 + 0xf0) * *(float *)(iVar7 + 0xf0));
            fVar21 = audio_uart_float_sqrt_4397a8
                               (*(float *)(iVar7 + 0xf8) * *(float *)(iVar7 + 0xf8) +
                                *(float *)(iVar7 + 0xfc) * *(float *)(iVar7 + 0xfc));
            /* Evidence (wave12): stock 0x51e222 vcmp |s16|,(2.000000238418579f); itt lt; vcmplt |s0|,(2.000000238418579f); then the ge path
             * (r6=1) calls 0x522622(1). The flag is set unless both are < (2.000000238418579f) (lt includes unordered). */
            bVar15 = (byte)(!(!(ABS(fVar22) >= (2.000000238418579f)) && !(ABS(fVar21) >= (2.000000238418579f))));
            bVar16 = 1;
            if (bVar15 == bVar16) {
              g2c_nema_vg_set_flag_522622(1);
            }
            fVar22 = *(float *)(*piVar3 + 0x2d8) * 0.5f;
            if ((int)((uint)*(byte *)(*piVar3 + 0x7d) << 0x1b) < 0) {
              g2c_nema_vg_move_to_522fb4(fStack_2c8,g2c_ptr_as_float(pfStack_2c4),fVar22);
            }
            else {
              g2c_nema_vg_line_to_523284(fStack_2c8,g2c_ptr_as_float(pfStack_2c4),fVar22);
            }
            if (bVar15 == bVar16) {
              g2c_nema_vg_set_flag_522622(0);
            }
          }
          goto LAB_0051e59c;
        }
        if (cVar1 == '\x01') {
          if (*(char *)(iVar7 + 0x2e4) == '\0') {
            if (*(int *)(iVar7 + 0x128) == 1) {
              fStack_28c = *(float *)(iVar7 + 0x138);
              fStack_288 = *(float *)(iVar7 + 0x13c);
              fStack_284 = *(float *)(iVar7 + 0x140);
              fStack_280 = *(float *)(iVar7 + 0x144);
              fStack_27c = *(float *)(iVar7 + 0x148);
              fStack_278 = *(float *)(iVar7 + 0x14c);
              fStack_274 = *(float *)(iVar7 + 0x150);
              fStack_270 = *(float *)(iVar7 + 0x154);
              fStack_26c = *(float *)(iVar7 + 0x158);
              fStack_268 = *(float *)(iVar7 + 0x15c);
              fStack_264 = *(float *)(iVar7 + 0x160);
              fStack_2b8 = *(float *)(iVar7 + 400);
              fStack_2b4 = *(float *)(iVar7 + 0x194);
              fStack_2b0 = *(float *)(iVar7 + 0x198);
              fStack_2ac = *(float *)(iVar7 + 0x19c);
              fStack_2a8 = *(float *)(iVar7 + 0x1a0);
              fStack_2a4 = *(float *)(iVar7 + 0x1a4);
              fStack_2a0 = *(float *)(iVar7 + 0x1a8);
              fStack_29c = *(float *)(iVar7 + 0x1ac);
              fStack_298 = *(float *)(iVar7 + 0x1b0);
              fStack_294 = *(float *)(iVar7 + 0x1b4);
              fStack_290 = *(float *)(iVar7 + 0x1b8);
            }
            else {
              fStack_2b8 = *(float *)(iVar7 + 0x138);
              fStack_2b4 = *(float *)(iVar7 + 0x13c);
              fStack_2b0 = *(float *)(iVar7 + 0x140);
              fStack_2ac = *(float *)(iVar7 + 0x144);
              fStack_2a8 = *(float *)(iVar7 + 0x148);
              fStack_2a4 = *(float *)(iVar7 + 0x14c);
              fStack_2a0 = *(float *)(iVar7 + 0x150);
              fStack_29c = *(float *)(iVar7 + 0x154);
              fStack_298 = *(float *)(iVar7 + 0x158);
              fStack_294 = *(float *)(iVar7 + 0x15c);
              fStack_290 = *(float *)(iVar7 + 0x160);
              fStack_28c = *(float *)(iVar7 + 0x164);
              fStack_288 = *(float *)(iVar7 + 0x168);
              fStack_284 = *(float *)(iVar7 + 0x16c);
              fStack_280 = *(float *)(iVar7 + 0x170);
              fStack_27c = *(float *)(iVar7 + 0x174);
              fStack_278 = *(float *)(iVar7 + 0x178);
              fStack_274 = *(float *)(iVar7 + 0x17c);
              fStack_270 = *(float *)(iVar7 + 0x180);
              fStack_26c = *(float *)(iVar7 + 0x184);
              fStack_268 = *(float *)(iVar7 + 0x188);
              fStack_264 = *(float *)(iVar7 + 0x18c);
            }
          }
          else {
            fStack_28c = *(float *)(iVar7 + 0x334);
            fStack_288 = *(float *)(iVar7 + 0x338);
            fStack_284 = *(float *)(iVar7 + 0x33c);
            fStack_280 = *(float *)(iVar7 + 0x340);
            fStack_27c = *(float *)(iVar7 + 0x344);
            fStack_278 = *(float *)(iVar7 + 0x348);
            fStack_274 = *(float *)(iVar7 + 0x34c);
            fStack_270 = *(float *)(iVar7 + 0x350);
            fStack_26c = *(float *)(iVar7 + 0x354);
            fStack_268 = *(float *)(iVar7 + 0x358);
            fStack_264 = *(float *)(iVar7 + 0x35c);
            fStack_2b8 = *(float *)(iVar7 + 0x308);
            fStack_2b4 = *(float *)(iVar7 + 0x30c);
            fStack_2b0 = *(float *)(iVar7 + 0x310);
            fStack_2ac = *(float *)(iVar7 + 0x314);
            fStack_2a8 = *(float *)(iVar7 + 0x318);
            fStack_2a4 = *(float *)(iVar7 + 0x31c);
            fStack_2a0 = *(float *)(iVar7 + 800);
            fStack_29c = *(float *)(iVar7 + 0x324);
            fStack_298 = *(float *)(iVar7 + 0x328);
            fStack_294 = *(float *)(iVar7 + 0x32c);
            fStack_290 = *(float *)(iVar7 + 0x330);
          }
          iVar7 = g2c_nema_vg_near_5177a4(&fStack_2b8,&fStack_28c);
          if ((((iVar7 != 1) ||
               (iVar7 = g2c_nema_vg_near_5177a4(&fStack_2b0,&fStack_284), iVar7 != 1)) ||
              (iVar7 = g2c_nema_vg_near_5177a4(&fStack_2a8,&fStack_27c), iVar7 != 1)) ||
             (iVar7 = g2c_nema_vg_near_5177a4(&fStack_2a0,&fStack_274), iVar7 != 1)) {
            iVar7 = g2c_nema_vg_near2_51785c(&fStack_2b8,&fStack_284);
            if ((iVar7 != 0) ||
               (iVar7 = g2c_nema_vg_near2_51785c(&fStack_28c,&fStack_2b8), iVar7 != 0))
            goto LAB_0051e3a0;
            iVar7 = g2c_nema_vg_near2_51785c(&fStack_2b8,&fStack_27c);
            fVar24 = fStack_27c;
            fVar29 = fStack_278;
            fVar30 = fStack_2a0;
            fVar34 = fStack_29c;
            fVar33 = fStack_2ac;
            fVar36 = fStack_2b0;
            fVar35 = fStack_288;
            fVar32 = fStack_28c;
            fVar23 = fStack_2b8;
            fVar26 = fStack_2b4;
            fVar20 = fStack_284;
            fVar28 = fStack_280;
            if ((iVar7 == 0) &&
               (iVar7 = g2c_nema_vg_near2_51785c(&fStack_28c,&fStack_2a0), fVar24 = fStack_27c,
               fVar29 = fStack_278, fVar30 = fStack_2a0, fVar34 = fStack_29c, fVar33 = fStack_2ac,
               fVar36 = fStack_2b0, fVar35 = fStack_288, fVar32 = fStack_28c, fVar23 = fStack_2b8,
               fVar26 = fStack_2b4, fVar20 = fStack_284, fVar28 = fStack_280, iVar7 == 0)) {
              if (fStack_280 <= fStack_2b4) {
                if (fStack_280 > fStack_278) goto LAB_0051e3a0;
              }
              else if (fStack_280 <= fStack_278) {
LAB_0051e3a0:
                fVar24 = fStack_284;
                fVar29 = fStack_280;
                fVar30 = fStack_2b8;
                fVar34 = fStack_2b4;
                fVar33 = fStack_2a4;
                fVar36 = fStack_2a8;
                fVar35 = fStack_270;
                fVar32 = fStack_274;
                fVar23 = fStack_2a0;
                fVar26 = fStack_29c;
                fVar20 = fStack_27c;
                fVar28 = fStack_278;
              }
            }
            fStack_2c0 = *pfStack_2cc;
            fStack_2bc = pfStack_2cc[1];
            fStack_2c8 = *(g2c_nvg_zero_pair_2);
            pfStack_2c4 = ((float *)g2c_float_as_ptr(g2c_nvg_zero_pair_2[1])) /* stock vldmia lit pair; vstmia sp (value copy) */;
            iVar7 = g2c_nema_vg_cubic_approx_522f50
                              (fVar20,fVar28,fVar24,fVar29,fVar23,fVar26,fVar30,fVar34,&fStack_2c0,
                               &fStack_2bc);
            iVar8 = g2c_nema_vg_cubic_approx_522f50
                              (fVar32,fVar35,fVar20,fVar28,fVar23,fVar26,fVar36,fVar33,&fStack_2c8,
                               (float *)&pfStack_2c4);
            fVar24 = g2c_nema_vg_sqrt_524218
                               ((fStack_2c8 - fStack_2c0) * (fStack_2c8 - fStack_2c0) +
                                (g2c_ptr_as_float(pfStack_2c4) - fStack_2bc) *
                                (g2c_ptr_as_float(pfStack_2c4) - fStack_2bc));
            iVar9 = *piVar3;
            if ((*(float *)(iVar9 + 0x2dc) * *(float *)(iVar9 + 0x2d8) < fVar24) ||
               (iVar8 == 0 || iVar7 == 0)) {
              fVar20 = fVar41;
              fVar28 = fVar42;
              fVar23 = fVar27;
              fVar26 = fVar19;
              if (-1 < (int)((uint)*(byte *)(iVar9 + 0x7d) << 0x1b)) {
                uVar4 = audio_uart_nema_stencil_save_52266e(1,0,1,0);
              }
            }
            else {
              fVar22 = fStack_2c0;
              fVar21 = fStack_2bc;
              fVar31 = fStack_2c8;
              pfVar25 = pfStack_2c4;
              if (-1 < (int)((uint)*(byte *)(iVar9 + 0x7d) << 0x1b)) {
                uVar4 = audio_uart_nema_stencil_save_52266e(0,1,1,0);
                fVar22 = fStack_2c0;
                fVar21 = fStack_2bc;
                fVar31 = fStack_2c8;
                pfVar25 = pfStack_2c4;
              }
            }
            g2c_nema_vg_emit_verts_516b34
                      (fVar22,fVar21,fVar20,fVar28,fVar31,g2c_ptr_as_float(pfVar25),fVar23,fVar26);
            goto LAB_0051e58c;
          }
          goto LAB_0051e59c;
        }
LAB_0051e51e:
        *(undefined4 *)(iVar7 + 0x114) = 0;
        *(undefined4 *)(iVar7 + 0x118) = 0;
        audio_uart_nema_vg_set_error_51565c(0x1000000);
        iVar5 = *piVar3;
        *(undefined4 *)(iVar5 + 0x114) = 0;
        *(undefined4 *)(iVar5 + 0x118) = 0;
LAB_0051e538:
        audio_uart_nema_vg_set_error_51565c(0x1000000);
        return 0x1000000;
      }
LAB_0051e59c:
      iVar7 = *piVar3;
      fVar22 = *(float *)(iVar7 + 0x184);
      /* stock 0x51e5a2 vcmp.f32 s0,#0.0; vmrs; ble.n 0x51e610 (body runs on GT). */
      if (fVar22 > 0.0f) {
        if (-1 < (int)((uint)*(byte *)(iVar7 + 0x7d) << 0x1b)) {
          if (iVar6 == 0) {
            uVar12 = -(uint)(*(char *)(iVar7 + 0x1bf) == '\0') >> 0x1f;
          }
          else {
            uVar12 = 0;
          }
          uVar12 = audio_uart_nema_stencil_save_52266e(1,uVar12,1,0);
        }
        iVar7 = *piVar3;
        g2c_nema_vg_emit_verts_516b34
                  (*(float *)(iVar7 + 0x164),*(float *)(iVar7 + 0x168),*(float *)(iVar7 + 0x16c),
                   *(float *)(iVar7 + 0x170),*(float *)(iVar7 + 0x174),*(float *)(iVar7 + 0x178),
                   *(float *)(iVar7 + 0x17c),*(float *)(iVar7 + 0x180));
        iVar7 = *piVar3;
        *(undefined4 *)(iVar7 + 0x184) = 0;
        if (-1 < (int)((uint)*(byte *)(iVar7 + 0x7d) << 0x1b)) {
          audio_uart_nema_stencil_restore_5226b2(uVar12);
        }
      }
      iVar7 = *piVar3;
      fVar22 = *(float *)(iVar7 + 0x158);
      /* stock 0x51e616 vcmp.f32 s0,#0.0; vmrs; ble.n 0x51e6b0 (body runs on GT). */
      if (fVar22 > 0.0f) {
        if (-1 < (int)((uint)*(byte *)(iVar7 + 0x7d) << 0x1b)) {
          if (iVar6 == 0) {
            if (*(int *)(iVar7 + 0x128) == 1) {
              if (*(char *)(iVar7 + 0x1bf) == '\0') {
                uVar11 = 1;
                uVar12 = 1;
              }
              else {
                uVar11 = -(uint)(*(char *)(iVar7 + 0x2e0) == '\0') >> 0x1f;
                uVar12 = -(uint)(*(char *)(iVar7 + 0x2e1) == '\0') >> 0x1f;
              }
            }
            else {
              uVar11 = -(uint)(*(char *)(iVar7 + 0x1bf) == '\0') >> 0x1f;
              uVar12 = 0;
            }
          }
          else {
            uVar11 = 0;
            uVar12 = 0;
          }
          uVar12 = audio_uart_nema_stencil_save_52266e(1,uVar12,1,uVar11);
        }
        iVar7 = *piVar3;
        g2c_nema_vg_emit_verts_516b34
                  (*(float *)(iVar7 + 0x138),*(float *)(iVar7 + 0x13c),*(float *)(iVar7 + 0x140),
                   *(float *)(iVar7 + 0x144),*(float *)(iVar7 + 0x148),*(float *)(iVar7 + 0x14c),
                   *(float *)(iVar7 + 0x150),*(float *)(iVar7 + 0x154));
        iVar7 = *piVar3;
        *(undefined4 *)(iVar7 + 0x158) = 0;
        if (-1 < (int)((uint)*(byte *)(iVar7 + 0x7d) << 0x1b)) {
          audio_uart_nema_stencil_restore_5226b2(uVar12);
        }
      }
      iVar7 = *piVar3;
      if (*(int *)(iVar7 + 0x128) == 2) {
        if (*(int *)(iVar7 + 0x110) != 0) {
          cVar1 = *(char *)(iVar7 + 0x2e2);
          uVar11 = 0;
          fVar21 = (float)g2c_bits_to_float((uint)(*(undefined8 *)(iVar7 + 0x17c)));
          fVar31 = (float)g2c_bits_to_float((uint)(((ulonglong)*(undefined8 *)(iVar7 + 0x17c) >> 0x20)));
          fVar27 = (float)g2c_bits_to_float((uint)(*(undefined8 *)(iVar7 + 0x148)));
          pfVar10 = (float *)((ulonglong)*(undefined8 *)(iVar7 + 0x148) >> 0x20);
          fVar19 = (float)g2c_bits_to_float((uint)(*(undefined8 *)(iVar7 + 0x164)));
          fVar41 = (float)g2c_bits_to_float((uint)(((ulonglong)*(undefined8 *)(iVar7 + 0x164) >> 0x20)));
          fVar22 = (float)g2c_bits_to_float((uint)(*(undefined8 *)(iVar7 + 0x140)));
          pfVar25 = (float *)((ulonglong)*(undefined8 *)(iVar7 + 0x140) >> 0x20);
          if ((cVar1 == '\0') || (*(int *)(iVar7 + 0x118) != 0)) {
            if (-1 < (int)((uint)*(byte *)(iVar7 + 0x7d) << 0x1b)) {
              uVar11 = audio_uart_nema_stencil_save_52266e(1,0,1,0);
            }
            g2c_nema_vg_emit_verts_516b34
                      (fVar22,g2c_ptr_as_float(pfVar25),fVar19,fVar41,fVar27,g2c_ptr_as_float(pfVar10),fVar21,fVar31);
LAB_0051ea72:
            if (-1 < (int)((uint)*(byte *)(*piVar3 + 0x7d) << 0x1b)) {
              audio_uart_nema_stencil_restore_5226b2(uVar11);
            }
          }
          else if (cVar1 == '\x02') {
            fStack_2d0 = *(g2c_nvg_zero_pair_0); /* stock 0x51e702..0x51e70c */
            pfStack_2cc = ((float *)g2c_float_as_ptr(g2c_nvg_zero_pair_0[1])) /* stock vldmia lit pair; vstmia sp (value copy) */;
            iVar7 = g2c_nema_vg_cubic_approx_522f50
                              (fVar22,g2c_ptr_as_float(pfVar25),fVar27,g2c_ptr_as_float(pfVar10),fVar19,fVar41,fVar21,
                               fVar31,&fStack_2d0,(float *)&pfStack_2cc);
            if (iVar7 != 0) {
              iVar7 = *piVar3;
              fVar22 = audio_uart_float_sqrt_4397a8
                                 (*(float *)(iVar7 + 0xec) * *(float *)(iVar7 + 0xec) +
                                  *(float *)(iVar7 + 0xf0) * *(float *)(iVar7 + 0xf0));
              fVar21 = audio_uart_float_sqrt_4397a8
                                 (*(float *)(iVar7 + 0xf8) * *(float *)(iVar7 + 0xf8) +
                                  *(float *)(iVar7 + 0xfc) * *(float *)(iVar7 + 0xfc));
              /* stock 0x51e776 vcmp; itt lt; vcmplt 0x51e784; iteee lt; blge 0x522622:
                 GE (ordered >=) on either |v| against 2.0000002f. */
              bVar15 = (byte)(ABS(fVar22) >= 2.0000002f || ABS(fVar21) >= 2.0000002f); /* = stock r6 (movge r6,#1 / movlt #0) */
              bVar16 = 1;
              if (bVar15 == bVar16) {
                g2c_nema_vg_set_flag_522622(1);
              }
              fVar22 = *(float *)(*piVar3 + 0x2d8) * 0.5f;
              if ((int)((uint)*(byte *)(*piVar3 + 0x7d) << 0x1b) < 0) {
                g2c_nema_vg_move_to_522fb4(fStack_2d0,g2c_ptr_as_float(pfStack_2cc),fVar22); /* 0x51e7b0 */
              }
              else {
                g2c_nema_vg_line_to_523284(fStack_2d0,g2c_ptr_as_float(pfStack_2cc),fVar22); /* 0x51e7b0 */
              }
              if (bVar15 == bVar16) { /* stock 0x51e7c8 cmp r6,#0; beq skip; set_flag(0) (wave18: previously tested a stale bVar15) */
                g2c_nema_vg_set_flag_522622(0);
              }
            }
          }
          else {
            if (cVar1 != '\x01') goto LAB_0051e51e;
            if (*(char *)(iVar7 + 0x2e4) == '\0') {
              fStack_294 = *(float *)(iVar7 + 0x164);
              fStack_290 = *(float *)(iVar7 + 0x168);
              fStack_28c = *(float *)(iVar7 + 0x16c);
              fStack_288 = *(float *)(iVar7 + 0x170);
              fStack_284 = *(float *)(iVar7 + 0x174);
              fStack_280 = *(float *)(iVar7 + 0x178);
              fStack_27c = *(float *)(iVar7 + 0x17c);
              fStack_278 = *(float *)(iVar7 + 0x180);
              fStack_274 = *(float *)(iVar7 + 0x184);
              fStack_270 = *(float *)(iVar7 + 0x188);
              fStack_26c = *(float *)(iVar7 + 0x18c);
              fStack_2c0 = *(float *)(iVar7 + 400);
              fStack_2bc = *(float *)(iVar7 + 0x194);
              fStack_2b8 = *(float *)(iVar7 + 0x198);
              fStack_2b4 = *(float *)(iVar7 + 0x19c);
              fStack_2b0 = *(float *)(iVar7 + 0x1a0);
              fStack_2ac = *(float *)(iVar7 + 0x1a4);
              fStack_2a8 = *(float *)(iVar7 + 0x1a8);
              fStack_2a4 = *(float *)(iVar7 + 0x1ac);
              fStack_2a0 = *(float *)(iVar7 + 0x1b0);
              fStack_29c = *(float *)(iVar7 + 0x1b4);
              fStack_298 = *(float *)(iVar7 + 0x1b8);
            }
            else {
              fStack_294 = *(float *)(iVar7 + 0x334);
              fStack_290 = *(float *)(iVar7 + 0x338);
              fStack_28c = *(float *)(iVar7 + 0x33c);
              fStack_288 = *(float *)(iVar7 + 0x340);
              fStack_284 = *(float *)(iVar7 + 0x344);
              fStack_280 = *(float *)(iVar7 + 0x348);
              fStack_27c = *(float *)(iVar7 + 0x34c);
              fStack_278 = *(float *)(iVar7 + 0x350);
              fStack_274 = *(float *)(iVar7 + 0x354);
              fStack_270 = *(float *)(iVar7 + 0x358);
              fStack_26c = *(float *)(iVar7 + 0x35c);
              fStack_2c0 = *(float *)(iVar7 + 0x308);
              fStack_2bc = *(float *)(iVar7 + 0x30c);
              fStack_2b8 = *(float *)(iVar7 + 0x310);
              fStack_2b4 = *(float *)(iVar7 + 0x314);
              fStack_2b0 = *(float *)(iVar7 + 0x318);
              fStack_2ac = *(float *)(iVar7 + 0x31c);
              fStack_2a8 = *(float *)(iVar7 + 800);
              fStack_2a4 = *(float *)(iVar7 + 0x324);
              fStack_2a0 = *(float *)(iVar7 + 0x328);
              fStack_29c = *(float *)(iVar7 + 0x32c);
              fStack_298 = *(float *)(iVar7 + 0x330);
            }
            iVar7 = g2c_nema_vg_near_5177a4(&fStack_2c0,&fStack_294);
            if ((((iVar7 != 1) ||
                 (iVar7 = g2c_nema_vg_near_5177a4(&fStack_2b8,&fStack_28c), iVar7 != 1)) ||
                (iVar7 = g2c_nema_vg_near_5177a4(&fStack_2b0,&fStack_284), iVar7 != 1)) ||
               (iVar7 = g2c_nema_vg_near_5177a4(&fStack_2a8,&fStack_27c), iVar7 != 1)) {
              iVar7 = g2c_nema_vg_near2_51785c(&fStack_2c0,&fStack_28c);
              if ((iVar7 != 0) ||
                 (iVar7 = g2c_nema_vg_near2_51785c(&fStack_294,&fStack_2c0), iVar7 != 0))
              goto LAB_0051e8c4;
              iVar7 = g2c_nema_vg_near2_51785c(&fStack_2c0,&fStack_284);
              fVar20 = fStack_284;
              fVar28 = fStack_280;
              fVar23 = fStack_2a8;
              fVar26 = fStack_2a4;
              fVar34 = fStack_2b4;
              fVar33 = fStack_2b8;
              fVar36 = fStack_290;
              fVar35 = fStack_294;
              fVar29 = fStack_2c0;
              fVar30 = fStack_2bc;
              fVar42 = fStack_28c;
              fVar24 = fStack_288;
              if ((iVar7 == 0) &&
                 (iVar7 = g2c_nema_vg_near2_51785c(&fStack_294,&fStack_2a8), fVar20 = fStack_284,
                 fVar28 = fStack_280, fVar23 = fStack_2a8, fVar26 = fStack_2a4, fVar34 = fStack_2b4,
                 fVar33 = fStack_2b8, fVar36 = fStack_290, fVar35 = fStack_294, fVar29 = fStack_2c0,
                 fVar30 = fStack_2bc, fVar42 = fStack_28c, fVar24 = fStack_288, iVar7 == 0)) {
                /* stock 0x51e8a8 vcmp [sp+20],[sp+72]; 0x51e8b4 vcmp [sp+80],[sp+72];
                   bpl.w 0x51e9c6 -> bmi.w 0x51e8c4 ; else bmi.w 0x51e9ce. */
                if (!(fStack_2bc < fStack_288)) {
                  if (fStack_280 < fStack_288) goto LAB_0051e8c4;
                }
                else if (!(fStack_280 < fStack_288)) {
LAB_0051e8c4:
                  fVar20 = fStack_28c;
                  fVar28 = fStack_288;
                  fVar23 = fStack_2c0;
                  fVar26 = fStack_2bc;
                  fVar34 = fStack_2ac;
                  fVar33 = fStack_2b0;
                  fVar36 = fStack_278;
                  fVar35 = fStack_27c;
                  fVar29 = fStack_2a8;
                  fVar30 = fStack_2a4;
                  fVar42 = fStack_284;
                  fVar24 = fStack_280;
                }
              }
              fStack_2c8 = *pfStack_2cc;
              pfStack_2c4 = ((float *)g2c_float_as_ptr((pfStack_2cc)[1]));
              fStack_2d0 = *(g2c_nvg_zero_pair_2); /* stock 0x51e900..0x51e906 */
              pfStack_2cc = ((float *)g2c_float_as_ptr(g2c_nvg_zero_pair_2[1])) /* stock vldmia lit pair; vstmia sp (value copy) */;
              iVar7 = g2c_nema_vg_cubic_approx_522f50
                                (fVar42,fVar24,fVar20,fVar28,fVar29,fVar30,fVar23,fVar26,&fStack_2c8
                                 ,(float *)&pfStack_2c4);
              iVar8 = g2c_nema_vg_cubic_approx_522f50
                                (fVar35,fVar36,fVar42,fVar24,fVar29,fVar30,fVar33,fVar34,
                                 &fStack_2d0,(float *)&pfStack_2cc);
              fVar20 = g2c_nema_vg_sqrt_524218
                                 ((fStack_2d0 - fStack_2c8) * (fStack_2d0 - fStack_2c8) + /* 0x51e94c vldr s0,[sp] */
                                  (g2c_ptr_as_float(pfStack_2cc) - g2c_ptr_as_float(pfStack_2c4)) *
                                  (g2c_ptr_as_float(pfStack_2cc) - g2c_ptr_as_float(pfStack_2c4)));
              iVar9 = *piVar3;
              if ((*(float *)(iVar9 + 0x2dc) * *(float *)(iVar9 + 0x2d8) < fVar20) ||
                 (iVar8 == 0 || iVar7 == 0)) {
                fVar42 = fVar19;
                fVar24 = fVar41;
                fVar32 = fVar27;
                fVar29 = fVar21;
                fVar30 = fVar31;
                if (-1 < (int)((uint)*(byte *)(iVar9 + 0x7d) << 0x1b)) {
                  uVar11 = audio_uart_nema_stencil_save_52266e(1,0,1,0);
                }
              }
              else {
                fVar22 = fStack_2c8;
                pfVar25 = pfStack_2c4;
                fVar32 = fStack_2d0; /* stock 0x51e9a8 mov r0,sp; 0x51e9b4 vldmia r0,{s4-s5} */
                pfVar10 = pfStack_2cc;
                if (-1 < (int)((uint)*(byte *)(iVar9 + 0x7d) << 0x1b)) {
                  uVar11 = audio_uart_nema_stencil_save_52266e(0,1,1,0);
                  fVar22 = fStack_2c8;
                  pfVar25 = pfStack_2c4;
                  pfVar10 = pfStack_2cc;
                }
              }
              g2c_nema_vg_emit_verts_516b34
                        (fVar22,g2c_ptr_as_float(pfVar25),fVar42,fVar24,fVar32,g2c_ptr_as_float(pfVar10),fVar29,fVar30);
              goto LAB_0051ea72;
            }
          }
        }
      }
      audio_uart_nema_stencil_restore_5226b2(uVar12);
      iVar7 = *piVar3;
      *(undefined4 *)(iVar7 + 0x128) = 0;
      if (iVar5 < 0) {
        return 0;
      }
      bVar18 = *(int *)(iVar7 + 0x110) != 0;
      cVar1 = '\0';
      if (bVar18) {
        cVar1 = *(char *)(iVar7 + 0x2e0);
      }
      /* Evidence (wave11): s1/s2/s4 here are dead in stock (.waves/w11/vlive.py; checked from 0x51ea88, 0x51eb72 and after bl 0x516b34 at 0x51ed3a). */
      if (!bVar18 || cVar1 == '\0') goto LAB_0051eb76;
      if (cVar1 == '\x02') {
        fVar21 = *(float *)(iVar7 + 400);
        fVar22 = *(float *)(iVar7 + 0x198);
        /* stock 0x51eab4/0x51eac6 (bne.w 0x51ec22) vcmp; itttt eq; vcmpeq; bne.w. */
        bVar15 = 0;
        if (fVar21 == fVar22) {
          fVar22 = *(float *)(iVar7 + 0x194);
          bVar15 = (fVar22 == *(float *)(iVar7 + 0x19c));
        }
        if (bVar15 != 0) {
          fVar27 = *(float *)(iVar7 + 0x1a0);
          fVar31 = *(float *)(iVar7 + 0x1a8);
          /* stock 0x51eada/0x51eaec (bne.w 0x51ec22) vcmp; itttt eq; vcmpeq; bne.w. */
          bVar15 = 0;
          if (fVar27 == fVar31) {
            fVar31 = *(float *)(iVar7 + 0x1a4);
            bVar15 = (fVar31 == *(float *)(iVar7 + 0x1ac));
          }
          if (bVar15 != 0) {
            fVar19 = *(float *)(iVar7 + 300) * -0.5f;
            bVar18 = -1 < (int)((uint)*(byte *)(iVar7 + 0x7d) << 0x1b);
            uVar11 = audio_uart_nema_stencil_save_52266e((uint)bVar18,0,(uint)bVar18,(uint)bVar18);
            g2c_nema_vg_emit_verts_516b34
                      (fVar19 + fVar21,fVar22,fVar21,fVar22,fVar27,fVar31,fVar19 + fVar27,fVar31);
            goto LAB_0051eb72;
          }
        }
        fStack_2c8 = *(float *)(iVar7 + 0x138);
        pfStack_2c4 = *(float **)(iVar7 + 0x13c);
        fVar22 = *(float *)(iVar7 + 0x150);
        pfStack_2cc = *(float **)(iVar7 + 0x154);
        fVar27 = *(float *)(iVar7 + 300) * 0.5f;
        fVar21 = *(float *)(iVar7 + 0x150);
        uVar39 = *(undefined8 *)(iVar7 + 0x138);
        fVar31 = *(float *)(iVar7 + 0x154);
        bVar15 = 0;
        if (*(float *)(iVar7 + 0x138) < *(float *)(iVar7 + 0x140)) {
          /* stock 0x51ec52 vcmp; itttt mi; vcmpmi 0x51ec6c; movmi r5,#1. */
          bVar15 = (fVar21 < *(float *)(iVar7 + 0x148));
        }
        if (bVar15 != 0) {
          iVar6 = 1;
        }
        fVar42 = (float)g2c_bits_to_float((uint)(uVar39));
        fVar24 = fVar21 - fVar42;
        fVar20 = (float)g2c_bits_to_float((uint)(((ulonglong)uVar39 >> 0x20)));
        fVar41 = fVar31 - fVar20;
        fVar19 = g2c_nema_vg_sqrt_524218(fVar24 * fVar24 + fVar41 * fVar41);
        fVar41 = -(fVar41 / fVar19);
        /* stock 0x51ec9c vcmp.f32 s0,#0.0; r5==0: 0x51ece4 bhi.n 0x51eca8; else 0x51eca6 bgt.n 0x51ecea. */
        if (iVar6 == 0) {
          if (!(fVar41 <= 0.0f)) goto LAB_0051eca8;
LAB_0051ecea:
          fVar21 = fVar21 - fVar27 * fVar41;
          fVar19 = fVar27 * (fVar24 / fVar19);
          fVar42 = fVar42 - fVar27 * fVar41;
          fVar31 = fVar31 - fVar19;
          fVar19 = fVar20 - fVar19;
        }
        else {
          if (fVar41 > 0.0f)
          goto LAB_0051ecea;
LAB_0051eca8:
          fVar21 = fVar27 * fVar41 + fVar21;
          fVar19 = fVar27 * (fVar24 / fVar19);
          fVar42 = fVar27 * fVar41 + fVar42;
          fVar31 = fVar19 + fVar31;
          fVar19 = fVar19 + fVar20;
        }
        bVar18 = -1 < (int)((uint)*(byte *)(*piVar3 + 0x7d) << 0x1b);
        uVar11 = audio_uart_nema_stencil_save_52266e(0,(uint)bVar18,(uint)bVar18,(uint)bVar18);
        g2c_nema_vg_emit_verts_516b34
                  (fStack_2c8,g2c_ptr_as_float(pfStack_2c4),fVar22,g2c_ptr_as_float(pfStack_2cc),fVar21,fVar31,fVar42,
                   fVar19);
      /* Evidence (wave11): s1/s2/s4 here are dead in stock (.waves/w11/vlive.py; checked from 0x51ea88, 0x51eb72 and after bl 0x516b34 at 0x51ed3a). */
        if ((int)((uint)*(byte *)(*piVar3 + 0x7d) << 0x1b) < 0) goto LAB_0051eb76;
      }
      else {
        if (cVar1 != '\x01') goto LAB_0051f756;
        fVar21 = *(float *)(iVar7 + 400);
        fVar22 = *(float *)(iVar7 + 0x198);
        /* stock 0x51ed5a/0x51ed6c (bne.w 0x51ef96) vcmp; itttt eq; vcmpeq; bne.w. */
        bVar15 = 0;
        if (fVar21 == fVar22) {
          fVar22 = *(float *)(iVar7 + 0x194);
          bVar15 = (fVar22 == *(float *)(iVar7 + 0x19c));
        }
        if (bVar15 == 0) {
LAB_0051ef96:
          fVar21 = *(float *)(iVar7 + 0x2d8);
          fVar22 = (*(float *)(iVar7 + 0x150) - *(float *)(iVar7 + 0x138)) / fVar21;
          fVar19 = (*(float *)(iVar7 + 0x150) + *(float *)(iVar7 + 0x138)) * 0.5f;
          fVar42 = fVar21 * 0.5f;
          fVar21 = (*(float *)(iVar7 + 0x154) - *(float *)(iVar7 + 0x13c)) / fVar21;
          fVar41 = (*(float *)(iVar7 + 0x154) + *(float *)(iVar7 + 0x13c)) * 0.5f;
          uVar12 = g2c_nema_vg_f2u_522f1c(fVar42);
          iVar5 = (int)uVar12 / 2;
          fVar31 = (float)VectorSignedToFloat(iVar5,0 /* rounding arg ignored (line 37) */);
          fVar31 = (180.0f) / fVar31;
          fVar27 = audio_uart_nema_cos_524130(fVar31);
          fVar31 = audio_uart_nema_sin_52405c(fVar31);
          fVar31 = -fVar31;
          fStack_1f0 = fVar19 - fVar22 * fVar42;
          fStack_1ec = fVar41 - fVar21 * fVar42;
          uVar12 = iVar5 - 1;
          if (uVar12 != 0 && 0 < iVar5) {
            pfVar25 = afStack_200 + 6;
            for (uVar11 = uVar12 & 3; uVar11 != 0; uVar11 = uVar11 - 1) {
              *pfVar25 = fVar19 + fVar42 * fVar22;
              pfVar25[1] = fVar41 + fVar42 * fVar21;
              fVar20 = fVar31 * fVar22;
              fVar22 = fVar27 * fVar22 - fVar31 * fVar21;
              pfVar25 = pfVar25 + 2;
              fVar21 = fVar20 + fVar27 * fVar21;
            }
            for (uVar11 = uVar12 >> 2; uVar11 != 0; uVar11 = uVar11 - 1) {
              *pfVar25 = fVar19 + fVar42 * fVar22;
              pfVar25[1] = fVar41 + fVar42 * fVar21;
              fVar20 = fVar27 * fVar22 - fVar31 * fVar21;
              pfVar25[2] = fVar19 + fVar42 * fVar20;
              fVar21 = fVar31 * fVar22 + fVar27 * fVar21;
              fVar24 = fVar31 * fVar20 + fVar27 * fVar21;
              fVar22 = fVar27 * fVar20 - fVar31 * fVar21;
              pfVar25[4] = fVar19 + fVar42 * fVar22;
              pfVar25[3] = fVar41 + fVar42 * fVar21;
              fVar20 = fVar31 * fVar22 + fVar27 * fVar24;
              fVar22 = fVar27 * fVar22 - fVar31 * fVar24;
              pfVar25[5] = fVar41 + fVar42 * fVar24;
              pfVar25[6] = fVar19 + fVar42 * fVar22;
              pfVar25[7] = fVar41 + fVar42 * fVar20;
              fVar21 = fVar31 * fVar22 + fVar27 * fVar20;
              fVar22 = fVar27 * fVar22 - fVar31 * fVar20;
              pfVar25 = pfVar25 + 8;
            }
          }
          uVar11 = audio_uart_nema_stencil_save_52266e
                             (0,-(uint)((*(byte *)(*piVar3 + 0x7d) & 0x10) == 0) >> 0x1f,0,0);
          g2c_nema_vg_path_transform_523a34(afStack_200 + 4,uVar12,2);
          bVar18 = -1 < (int)((uint)*(byte *)(*piVar3 + 0x7d) << 0x1b);
          audio_uart_nema_stencil_save_52266e(0,(uint)bVar18,(uint)bVar18,0);
          g2c_nema_raster_triangle_f_522a24
                    (fStack_1f0,fStack_1ec,afStack_200[iVar5 * 2],afStack_200[iVar5 * 2 + 1],
                     afStack_200[iVar5 * 2 + 2],afStack_200[iVar5 * 2 + 3]);
        }
        else {
          fVar27 = *(float *)(iVar7 + 0x1a0);
          fVar31 = *(float *)(iVar7 + 0x1a8);
          /* stock 0x51ed80/0x51ed92 (bne.w 0x51ef96) vcmp; itttt eq; vcmpeq; bne.w. */
          bVar15 = 0;
          if (fVar27 == fVar31) {
            fVar31 = *(float *)(iVar7 + 0x1a4);
            bVar15 = (fVar31 == *(float *)(iVar7 + 0x1ac));
          }
          if (bVar15 == 0) goto LAB_0051ef96;
          fVar41 = *(float *)(iVar7 + 0x2d8);
          fVar19 = (fVar21 - fVar27) / fVar41;
          fVar27 = (fVar21 + fVar27) * 0.5f;
          fVar42 = fVar41 * 0.5f;
          fVar41 = (fVar22 - fVar31) / fVar41;
          fVar31 = (fVar22 + fVar31) * 0.5f;
          uVar12 = g2c_nema_vg_f2u_522f1c(fVar42);
          iVar5 = (int)uVar12 / 2;
          fVar22 = (float)VectorSignedToFloat(iVar5,0 /* rounding arg ignored (line 37) */);
          fVar22 = (180.0f) / fVar22;
          fVar21 = audio_uart_nema_cos_524130(fVar22);
          fVar22 = audio_uart_nema_sin_52405c(fVar22);
          fVar22 = -fVar22;
          fStack_1f0 = fVar27 - fVar19 * fVar42;
          fStack_1ec = fVar31 - fVar41 * fVar42;
          uVar12 = iVar5 - 1;
          if (uVar12 != 0 && 0 < iVar5) {
            pfVar25 = afStack_200 + 6;
            for (uVar11 = uVar12 & 3; uVar11 != 0; uVar11 = uVar11 - 1) {
              *pfVar25 = fVar27 + fVar42 * fVar19;
              pfVar25[1] = fVar31 + fVar42 * fVar41;
              fVar20 = fVar22 * fVar19;
              fVar19 = fVar21 * fVar19 - fVar22 * fVar41;
              pfVar25 = pfVar25 + 2;
              fVar41 = fVar20 + fVar21 * fVar41;
            }
            for (uVar11 = uVar12 >> 2; uVar11 != 0; uVar11 = uVar11 - 1) {
              *pfVar25 = fVar27 + fVar42 * fVar19;
              pfVar25[1] = fVar31 + fVar42 * fVar41;
              fVar20 = fVar21 * fVar19 - fVar22 * fVar41;
              pfVar25[2] = fVar27 + fVar42 * fVar20;
              fVar41 = fVar22 * fVar19 + fVar21 * fVar41;
              fVar24 = fVar22 * fVar20 + fVar21 * fVar41;
              fVar19 = fVar21 * fVar20 - fVar22 * fVar41;
              pfVar25[4] = fVar27 + fVar42 * fVar19;
              pfVar25[3] = fVar31 + fVar42 * fVar41;
              fVar20 = fVar22 * fVar19 + fVar21 * fVar24;
              fVar19 = fVar21 * fVar19 - fVar22 * fVar24;
              pfVar25[5] = fVar31 + fVar42 * fVar24;
              pfVar25[6] = fVar27 + fVar42 * fVar19;
              pfVar25[7] = fVar31 + fVar42 * fVar20;
              fVar41 = fVar22 * fVar19 + fVar21 * fVar20;
              fVar19 = fVar21 * fVar19 - fVar22 * fVar20;
              pfVar25 = pfVar25 + 8;
            }
          }
          uVar11 = audio_uart_nema_stencil_save_52266e
                             (0,-(uint)((*(byte *)(*piVar3 + 0x7d) & 0x10) == 0) >> 0x1f,0,0);
          g2c_nema_vg_path_transform_523a34(afStack_200 + 4,uVar12,2);
          bVar18 = -1 < (int)((uint)*(byte *)(*piVar3 + 0x7d) << 0x1b);
          audio_uart_nema_stencil_save_52266e(0,(uint)bVar18,(uint)bVar18,0);
          g2c_nema_raster_triangle_f_522a24
                    (fStack_1f0,fStack_1ec,afStack_200[iVar5 * 2],afStack_200[iVar5 * 2 + 1],
                     afStack_200[iVar5 * 2 + 2],afStack_200[iVar5 * 2 + 3]);
        }
      }
LAB_0051eb72:
      audio_uart_nema_stencil_restore_5226b2(uVar11);
      /* Evidence (wave11): s1/s2/s4 here are dead in stock (.waves/w11/vlive.py; checked from 0x51ea88, 0x51eb72 and after bl 0x516b34 at 0x51ed3a). */
LAB_0051eb76:
      iVar7 = *piVar3;
      bVar18 = *(int *)(iVar7 + 0x110) == 0;
      cVar1 = '\0';
      if (!bVar18) {
        cVar1 = *(char *)(iVar7 + 0x2e1);
      }
      if (bVar18 || cVar1 == '\0') {
        return 0;
      }
      if (cVar1 == '\x02') {
        fVar27 = *(float *)(iVar7 + 0x198);
        fVar31 = *(float *)(iVar7 + 400);
        bVar18 = fVar31 == fVar27;
        if (bVar18) {
          pfVar25 = *(float **)(iVar7 + 0x194);
          fVar22 = *(float *)(iVar7 + 0x19c);
        }
        if (bVar18 && (bVar18 && g2c_ptr_as_float(pfVar25) == fVar22)) {
          fVar19 = *(float *)(iVar7 + 0x1a0);
          fVar22 = *(float *)(iVar7 + 0x1a8);
          bVar18 = fVar19 == fVar22;
          if (bVar18) {
            fVar22 = *(float *)(iVar7 + 0x1a4);
            fVar21 = *(float *)(iVar7 + 0x1ac);
          }
          if (bVar18 && (bVar18 && fVar22 == fVar21)) {
            fVar27 = *(float *)(iVar7 + 300) * 0.5f;
            fVar21 = fVar27 + fVar31;
            uVar12 = (uint)(-1 < (int)((uint)*(byte *)(iVar7 + 0x7d) << 0x1b));
            pfStack_2cc = pfVar25;
            fStack_2c8 = fVar31;
            pfStack_2c4 = pfVar25;
            uVar4 = audio_uart_nema_stencil_save_52266e(uVar12,uVar12,uVar12,0);
            g2c_nema_vg_emit_verts_516b34
                      (fStack_2c8,g2c_ptr_as_float(pfStack_2c4),fVar21,g2c_ptr_as_float(pfStack_2cc),fVar27 + fVar19,
                       fVar22,fVar19,fVar22);
            goto LAB_0051f1ce;
          }
        }
        /* stock 0x51f1f4 vcmp s0,s24; itttt ge; vcmpge 0x51f21a [+0x1a8],s26; movge r5,#1:
           r5 = both ordered >=.  (wave17: replaces the decompiler's lt/unordered pair.) */
        bVar18 = (fVar31 >= fVar27);
        uVar39 = *(undefined8 *)(iVar7 + 0x198);
        uVar37 = *(undefined8 *)(iVar7 + 0x1a0);
        fVar31 = *(float *)(iVar7 + 300) * 0.5f;
        fVar22 = *(float *)(iVar7 + 0x1a0);
        fVar19 = *(float *)(iVar7 + 0x19c);
        fVar21 = *(float *)(iVar7 + 0x1a4);
        if (bVar18) {
          bVar18 = (*(float *)(iVar7 + 0x1a8) >= fVar22);
        }
        fVar20 = fVar22 - fVar27;
        fVar42 = fVar21 - fVar19;
        fVar41 = g2c_nema_vg_sqrt_524218(fVar20 * fVar20 + fVar42 * fVar42);
        fVar42 = -(fVar42 / fVar41);
        /* stock 0x51f24a vcmp s0,#0.0; r5!=0: bgt.n 0x51f298; r5==0: 0x51f292 bhi.n 0x51f256. */
        if (bVar18) {
          if (fVar42 > 0.0f) goto LAB_0051f298;
LAB_0051f256:
          fVar22 = fVar31 * fVar42 + fVar22;
          fVar41 = fVar31 * (fVar20 / fVar41);
          fVar27 = fVar31 * fVar42 + fVar27;
          fVar21 = fVar41 + fVar21;
          fVar41 = fVar41 + fVar19;
        }
        else {
          if (!(fVar42 <= 0.0f)) goto LAB_0051f256;
LAB_0051f298:
          fVar22 = fVar22 - fVar31 * fVar42;
          fVar41 = fVar31 * (fVar20 / fVar41);
          fVar27 = fVar27 - fVar31 * fVar42;
          fVar21 = fVar21 - fVar41;
          fVar41 = fVar19 - fVar41;
        }
        bVar18 = -1 < (int)((uint)*(byte *)(*piVar3 + 0x7d) << 0x1b);
        uVar4 = audio_uart_nema_stencil_save_52266e(0,(uint)bVar18,(uint)bVar18,(uint)bVar18);
        g2c_nema_vg_emit_verts_516b34
                  ((float)g2c_bits_to_float((uint)(uVar39)),(float)g2c_bits_to_float((uint)(((ulonglong)uVar39 >> 0x20))),(float)g2c_bits_to_float((uint)(uVar37)),
                   (float)g2c_bits_to_float((uint)(((ulonglong)uVar37 >> 0x20))),fVar22,fVar21,fVar27,fVar41);
        if ((int)((uint)*(byte *)(*piVar3 + 0x7d) << 0x1b) < 0) {
          return 0;
        }
LAB_0051f1ce:
        audio_uart_nema_stencil_restore_5226b2(uVar4);
        return 0;
      }
      if (cVar1 == '\x01') {
        fVar21 = *(float *)(iVar7 + 0x198);
        fVar31 = *(float *)(iVar7 + 400);
        /* stock 0x51f30e vcmp; itttt eq; vcmpeq 0x51f320; bne.w 0x51f552. */
        bVar15 = 0;
        if (fVar31 == fVar21) {
          fVar22 = *(float *)(iVar7 + 0x194);
          bVar15 = (fVar22 == *(float *)(iVar7 + 0x19c));
        }
        if (bVar15 != 0) {
          fVar19 = *(float *)(iVar7 + 0x1a0);
          fVar27 = *(float *)(iVar7 + 0x1a8);
          /* stock 0x51f334 vcmp; itttt eq; vcmpeq 0x51f346; bne.w 0x51f552. */
          bVar15 = 0;
          if (fVar19 == fVar27) {
            fVar27 = *(float *)(iVar7 + 0x1a4);
            bVar15 = (fVar27 == *(float *)(iVar7 + 0x1ac));
          }
          if (bVar15 != 0) {
            fVar41 = *(float *)(iVar7 + 0x2d8);
            fVar21 = (fVar31 - fVar19) / fVar41;
            fVar19 = (fVar31 + fVar19) * 0.5f;
            fVar42 = fVar41 * 0.5f;
            fVar41 = (fVar22 - fVar27) / fVar41;
            fVar27 = (fVar22 + fVar27) * 0.5f;
            uVar4 = g2c_nema_vg_f2u_522f1c(fVar42);
            iVar5 = (int)uVar4 / 2;
            fVar22 = (float)VectorSignedToFloat(iVar5,0 /* rounding arg ignored (line 37) */);
            fVar22 = (180.0f) / fVar22;
            fVar31 = audio_uart_nema_cos_524130(fVar22);
            fVar22 = audio_uart_nema_sin_52405c(fVar22);
            fStack_1f0 = fVar19 - fVar21 * fVar42;
            fStack_1ec = fVar27 - fVar41 * fVar42;
            uVar12 = iVar5 - 1;
            if (uVar12 != 0 && 0 < iVar5) {
              pfVar25 = afStack_200 + 6;
              for (uVar4 = uVar12 & 3; uVar4 != 0; uVar4 = uVar4 - 1) {
                *pfVar25 = fVar19 + fVar42 * fVar21;
                pfVar25[1] = fVar27 + fVar42 * fVar41;
                fVar20 = fVar22 * fVar21;
                fVar21 = fVar31 * fVar21 - fVar22 * fVar41;
                pfVar25 = pfVar25 + 2;
                fVar41 = fVar20 + fVar31 * fVar41;
              }
              for (uVar4 = uVar12 >> 2; uVar4 != 0; uVar4 = uVar4 - 1) {
                *pfVar25 = fVar19 + fVar42 * fVar21;
                pfVar25[1] = fVar27 + fVar42 * fVar41;
                fVar20 = fVar31 * fVar21 - fVar22 * fVar41;
                pfVar25[2] = fVar19 + fVar42 * fVar20;
                fVar41 = fVar22 * fVar21 + fVar31 * fVar41;
                fVar24 = fVar22 * fVar20 + fVar31 * fVar41;
                fVar21 = fVar31 * fVar20 - fVar22 * fVar41;
                pfVar25[4] = fVar19 + fVar42 * fVar21;
                pfVar25[3] = fVar27 + fVar42 * fVar41;
                fVar20 = fVar22 * fVar21 + fVar31 * fVar24;
                fVar21 = fVar31 * fVar21 - fVar22 * fVar24;
                pfVar25[5] = fVar27 + fVar42 * fVar24;
                pfVar25[6] = fVar19 + fVar42 * fVar21;
                pfVar25[7] = fVar27 + fVar42 * fVar20;
                fVar41 = fVar22 * fVar21 + fVar31 * fVar20;
                fVar21 = fVar31 * fVar21 - fVar22 * fVar20;
                pfVar25 = pfVar25 + 8;
              }
            }
            uVar4 = audio_uart_nema_stencil_save_52266e
                              (0,-(uint)((*(byte *)(*piVar3 + 0x7d) & 0x10) == 0) >> 0x1f,0,0);
            g2c_nema_vg_path_transform_523a34(afStack_200 + 4,uVar12,2);
            bVar18 = -1 < (int)((uint)*(byte *)(*piVar3 + 0x7d) << 0x1b);
            audio_uart_nema_stencil_save_52266e(0,(uint)bVar18,(uint)bVar18,0);
            g2c_nema_raster_triangle_f_522a24
                      (fStack_1f0,fStack_1ec,afStack_200[iVar5 * 2],afStack_200[iVar5 * 2 + 1],
                       afStack_200[iVar5 * 2 + 2],afStack_200[iVar5 * 2 + 3]);
            goto LAB_0051f1ce;
          }
        }
        fVar31 = *(float *)(iVar7 + 0x2d8);
        fVar22 = (*(float *)(iVar7 + 0x1a0) - fVar21) / fVar31;
        fVar19 = (*(float *)(iVar7 + 0x1a0) + fVar21) * 0.5f;
        fVar42 = fVar31 * 0.5f;
        fVar31 = (*(float *)(iVar7 + 0x1a4) - *(float *)(iVar7 + 0x19c)) / fVar31;
        fVar41 = (*(float *)(iVar7 + 0x1a4) + *(float *)(iVar7 + 0x19c)) * 0.5f;
        uVar4 = g2c_nema_vg_f2u_522f1c(fVar42);
        iVar5 = (int)uVar4 / 2;
        fVar21 = (float)VectorSignedToFloat(iVar5,0 /* rounding arg ignored (line 37) */);
        fVar21 = (180.0f) / fVar21;
        fVar27 = audio_uart_nema_cos_524130(fVar21);
        fVar21 = audio_uart_nema_sin_52405c(fVar21);
        fStack_1f0 = fVar19 - fVar22 * fVar42;
        fStack_1ec = fVar41 - fVar31 * fVar42;
        uVar12 = iVar5 - 1;
        if (uVar12 != 0 && 0 < iVar5) {
          pfVar25 = afStack_200 + 6;
          for (uVar4 = uVar12 & 3; uVar4 != 0; uVar4 = uVar4 - 1) {
            *pfVar25 = fVar19 + fVar42 * fVar22;
            pfVar25[1] = fVar41 + fVar42 * fVar31;
            fVar20 = fVar21 * fVar22;
            fVar22 = fVar27 * fVar22 - fVar21 * fVar31;
            pfVar25 = pfVar25 + 2;
            fVar31 = fVar20 + fVar27 * fVar31;
          }
          for (uVar4 = uVar12 >> 2; uVar4 != 0; uVar4 = uVar4 - 1) {
            *pfVar25 = fVar19 + fVar42 * fVar22;
            pfVar25[1] = fVar41 + fVar42 * fVar31;
            fVar20 = fVar27 * fVar22 - fVar21 * fVar31;
            pfVar25[2] = fVar19 + fVar42 * fVar20;
            fVar31 = fVar21 * fVar22 + fVar27 * fVar31;
            fVar24 = fVar21 * fVar20 + fVar27 * fVar31;
            fVar22 = fVar27 * fVar20 - fVar21 * fVar31;
            pfVar25[4] = fVar19 + fVar42 * fVar22;
            pfVar25[3] = fVar41 + fVar42 * fVar31;
            fVar20 = fVar21 * fVar22 + fVar27 * fVar24;
            fVar22 = fVar27 * fVar22 - fVar21 * fVar24;
            pfVar25[5] = fVar41 + fVar42 * fVar24;
            pfVar25[6] = fVar19 + fVar42 * fVar22;
            pfVar25[7] = fVar41 + fVar42 * fVar20;
            fVar31 = fVar21 * fVar22 + fVar27 * fVar20;
            fVar22 = fVar27 * fVar22 - fVar21 * fVar20;
            pfVar25 = pfVar25 + 8;
          }
        }
        uVar4 = audio_uart_nema_stencil_save_52266e
                          (0,-(uint)((*(byte *)(*piVar3 + 0x7d) & 0x10) == 0) >> 0x1f,0,0);
        g2c_nema_vg_path_transform_523a34(afStack_200 + 4,uVar12,2);
        bVar18 = -1 < (int)((uint)*(byte *)(*piVar3 + 0x7d) << 0x1b);
        audio_uart_nema_stencil_save_52266e(0,(uint)bVar18,(uint)bVar18,0);
        g2c_nema_raster_triangle_f_522a24
                  (fStack_1f0,fStack_1ec,afStack_200[iVar5 * 2],afStack_200[iVar5 * 2 + 1],
                   afStack_200[iVar5 * 2 + 2],afStack_200[iVar5 * 2 + 3]);
        goto LAB_0051f1ce;
      }
LAB_0051f756:
      *(undefined4 *)(iVar7 + 0x114) = 0;
      *(undefined4 *)(iVar7 + 0x118) = 0;
      audio_uart_nema_vg_set_error_51565c(0x800000);
      iVar5 = *piVar3;
      *(undefined4 *)(iVar5 + 0x114) = 0;
      *(undefined4 *)(iVar5 + 0x118) = 0;
      audio_uart_nema_vg_set_error_51565c(0x800000);
      return 0x800000;
    }
    uVar11 = (uint)*(byte *)(a[2] + uVar12);
    uVar12 = uVar12 + 1;
    uVar4 = g2c_nema_vg_path_cmd_5156b8(a,uVar11,(float *)&uStack_238);
    fVar27 = fStack_220;
    fVar31 = fStack_224;
    fVar21 = fStack_228;
    fVar22 = fStack_22c;
    uVar13 = uVar11 & 0x6f;
    if (uVar4 != 0) goto LAB_0051e0fc;
    if ((((byte *)&(uStack_238))[2] != '\0') || ((int)(uVar11 << 0x18) < 0)) {
      uVar13 = 0;
      if ((int)((uint)*(byte *)(*piVar3 + 0x7d) << 0x1b) < 0) {
        uVar13 = audio_uart_nema_stencil_save_52266e(0,0,0,0);
      }
      iVar5 = *piVar3;
      /* Evidence (wave12): stock 0x51d380 vcmp [+0x184],#0 / bls 0x51d400 (hi includes unordered). */
      uVar4 = 0;
      if (!(*(float *)(iVar5 + 0x184) <= 0.0f)) {
        if (-1 < (int)((uint)*(byte *)(iVar5 + 0x7d) << 0x1b)) {
          uVar13 = audio_uart_nema_stencil_save_52266e
                             (1,-(uint)(*(char *)(iVar5 + 0x1bf) == '\0') >> 0x1f,1,0);
        }
        iVar5 = *piVar3;
        fStack_2b0 = *(float *)(iVar5 + 0x164);
        fStack_2ac = *(float *)(iVar5 + 0x168);
        fStack_2b8 = *(float *)(iVar5 + 0x16c);
        fStack_2b4 = *(float *)(iVar5 + 0x170);
        fStack_2c0 = *(float *)(iVar5 + 0x174);
        fStack_2bc = *(float *)(iVar5 + 0x178);
        fStack_2c8 = *(float *)(iVar5 + 0x17c);
        pfStack_2c4 = *(float **)(iVar5 + 0x180);
        g2c_nema_vg_emit_verts_516b34
                  (fStack_2b0,fStack_2ac,fStack_2b8,fStack_2b4,fStack_2c0,fStack_2bc,fStack_2c8,
                   g2c_ptr_as_float(pfStack_2c4));
        iVar5 = *piVar3;
        *(undefined4 *)(iVar5 + 0x184) = 0;
        if (-1 < (int)((uint)*(byte *)(iVar5 + 0x7d) << 0x1b)) {
          audio_uart_nema_stencil_restore_5226b2(uVar13);
        }
      }
      iVar5 = *piVar3;
      /* stock 0x51d402 vcmp [+0x158],#0 / bls 0x51d486; lsls r6,#24 / bmi 0x51d486 */
      if (!(*(float *)(iVar5 + 0x158) <= 0.0f) && (-1 < (int)(uVar11 << 0x18))) {
        if (-1 < (int)((uint)*(byte *)(iVar5 + 0x7d) << 0x1b)) {
          if (*(int *)(iVar5 + 0x128) == 1) {
            if (*(char *)(iVar5 + 0x1bf) == '\0') {
              uVar11 = 1;
              uVar4 = 1;
            }
            else {
              uVar11 = -(uint)(*(char *)(iVar5 + 0x2e0) == '\0') >> 0x1f;
              uVar4 = -(uint)(*(char *)(iVar5 + 0x2e1) == '\0') >> 0x1f;
            }
          }
          else {
            uVar11 = -(uint)(*(char *)(iVar5 + 0x1bf) == '\0') >> 0x1f;
            uVar4 = 0;
          }
          uVar13 = audio_uart_nema_stencil_save_52266e(1,uVar4,1,uVar11);
        }
        iVar5 = *piVar3;
        fStack_2b0 = *(float *)(iVar5 + 0x138);
        fStack_2ac = *(float *)(iVar5 + 0x13c);
        fStack_2b8 = *(float *)(iVar5 + 0x140);
        fStack_2b4 = *(float *)(iVar5 + 0x144);
        fStack_2c0 = *(float *)(iVar5 + 0x148);
        fStack_2bc = *(float *)(iVar5 + 0x14c);
        fStack_2c8 = *(float *)(iVar5 + 0x150);
        pfStack_2c4 = *(float **)(iVar5 + 0x154);
        g2c_nema_vg_emit_verts_516b34
                  (fStack_2b0,fStack_2ac,fStack_2b8,fStack_2b4,fStack_2c0,fStack_2bc,fStack_2c8,
                   g2c_ptr_as_float(pfStack_2c4));
        iVar5 = *piVar3;
        *(undefined4 *)(iVar5 + 0x158) = 0;
        if (-1 < (int)((uint)*(byte *)(iVar5 + 0x7d) << 0x1b)) {
          audio_uart_nema_stencil_restore_5226b2(uVar13);
        }
      }
      iVar5 = *piVar3;
      if (*(int *)(iVar5 + 0x128) == 2) {
        fStack_2b0 = *(float *)(iVar5 + 0x140);
        fStack_2ac = *(float *)(iVar5 + 0x144);
        fStack_2b8 = *(float *)(iVar5 + 0x164);
        fStack_2b4 = *(float *)(iVar5 + 0x168);
        fStack_2c0 = *(float *)(iVar5 + 0x148);
        fStack_2bc = *(float *)(iVar5 + 0x14c);
        fStack_2c8 = *(float *)(iVar5 + 0x17c);
        pfStack_2c4 = *(float **)(iVar5 + 0x180);
        uVar4 = g2c_nema_vg_stroke_join_5179d0
                          (&fStack_2b0,(uint *)&fStack_2b8,&fStack_2c0,(uint *)&fStack_2c8,0);
        if (uVar4 != 0) {
          iVar5 = *piVar3;
          *(undefined4 *)(iVar5 + 0x114) = 0;
          *(undefined4 *)(iVar5 + 0x118) = 0;
          audio_uart_nema_vg_set_error_51565c(uVar4);
          goto LAB_0051e0fc;
        }
      }
      audio_uart_nema_stencil_restore_5226b2(uVar13);
      *(undefined4 *)(*piVar3 + 0x128) = 0;
      if ((((byte *)&(uStack_238))[1] != '\0' && uVar12 != 1) &&
         ((uVar4 = g2c_nema_vg_arc_seg_51b8f0(a_00,b,c,d,e), uVar4 != 0 ||
          (uVar4 = g2c_nema_vg_arc_seg2_51bf7c(a_01,b_00,c_00,d_00,e_00), uVar4 != 0)))) {
        iVar5 = *piVar3;
        *(undefined4 *)(iVar5 + 0x114) = 0;
        *(undefined4 *)(iVar5 + 0x118) = 0;
        audio_uart_nema_vg_set_error_51565c(uVar4);
        goto LAB_0051e0fc;
      }
      goto LAB_0051d332;
    }
    if (uVar13 == 6 || uVar13 == 8) {
      g2c_nema_vg_stroke_path_517e18
                (fStack_22c,fStack_228,fStack_21c,fStack_218,fStack_214,fStack_210,fStack_224,
                 fStack_220);
    }
    else if ((uVar13 == 5) || (uVar13 == 7)) {
      g2c_nema_vg_fill_path_519290
                (fStack_22c,fStack_228,fStack_21c,fStack_218,fStack_224,fStack_220);
    }
    else if ((uVar11 & 0xf) == 9) {
      uVar4 = g2c_nema_vg_arc_to_51a8ec((uint)a,(int)&uStack_238);
      if (uVar4 != 0) {
LAB_0051e0fc:
        iVar5 = *piVar3;
        *(undefined4 *)(iVar5 + 0x114) = 0;
        *(undefined4 *)(iVar5 + 0x118) = 0;
        audio_uart_nema_vg_set_error_51565c(uVar4);
        return uVar4;
      }
    }
    else if (uVar13 != 10 && uVar13 != 0xb) {
      fVar42 = fStack_224 - fStack_22c;
      fVar41 = fStack_220 - fStack_228;
      fVar19 = fVar42 * fVar42 + fVar41 * fVar41;
      if ((1.0000000656873453e-05f) <= ABS(fVar19)) {
        fVar19 = audio_uart_float_sqrt_4397a8(fVar19);
        iVar5 = *piVar3;
        fVar42 = fVar42 * (1.0f / fVar19);
        fVar41 = fVar41 * (1.0f / fVar19);
        fVar20 = *(float *)(iVar5 + 0x130) * 0.5f * fVar41;
        fVar28 = fVar22 - fVar20;
        fVar24 = *(float *)(iVar5 + 0x134) * 0.5f * fVar42;
        fVar29 = fVar24 + fVar21;
        uVar39 = CONCAT44(g2c_float_to_bits(fVar29),g2c_float_to_bits(fVar28));
        fStack_2b8 = fVar31 - fVar20;
        fStack_2b4 = fVar24 + fVar27;
        fStack_2c0 = fVar20 + fVar31;
        fStack_2bc = fVar27 - fVar24;
        *(float *)(iVar5 + 400) = fVar28;
        *(float *)(iVar5 + 0x194) = fVar29;
        fVar20 = fVar20 + fVar22;
        iVar5 = *piVar3;
        fVar21 = fVar21 - fVar24;
        uVar37 = CONCAT44(g2c_float_to_bits(fVar21),g2c_float_to_bits(fVar20));
        *(float *)(iVar5 + 0x198) = fStack_2b8;
        *(float *)(iVar5 + 0x19c) = fStack_2b4;
        iVar5 = *piVar3;
        *(float *)(iVar5 + 0x1a0) = fStack_2c0;
        *(float *)(iVar5 + 0x1a4) = fStack_2bc;
        iVar5 = *piVar3;
        *(float *)(iVar5 + 0x1a8) = fVar20;
        *(float *)(iVar5 + 0x1ac) = fVar21;
        iVar5 = *piVar3;
        if (*(int *)(iVar5 + 0x110) == 0) {
          uVar11 = audio_uart_nema_stencil_restore_5226b2(*(uint *)(iVar5 + 0x8c));
          g2c_nema_vg_emit_verts_516b34
                    (fVar28,fVar29,fStack_2b8,fStack_2b4,fStack_2c0,fStack_2bc,fVar20,fVar21);
        }
        else {
          bVar18 = -1 < (int)((uint)*(byte *)(iVar5 + 0x7d) << 0x1b);
          uVar11 = audio_uart_nema_stencil_save_52266e((uint)bVar18,0,(uint)bVar18,0);
          iVar5 = *piVar3;
          /* stock 0x51d6c0 vcmp [+0x184],#0 / bls 0x51d794 */
          uVar4 = 0;
          if (!(*(float *)(iVar5 + 0x184) <= 0.0f)) {
            g2c_nema_vg_emit_verts_516b34
                      (*(float *)(iVar5 + 0x164),*(float *)(iVar5 + 0x168),*(float *)(iVar5 + 0x16c)
                       ,*(float *)(iVar5 + 0x170),*(float *)(iVar5 + 0x174),
                       *(float *)(iVar5 + 0x178),*(float *)(iVar5 + 0x17c),*(float *)(iVar5 + 0x180)
                      );
            iVar5 = *piVar3;
            if (ABS(*(float *)(iVar5 + 0x188) * fVar41 - *(float *)(iVar5 + 0x18c) * fVar42) <
                (0.05000000447034836f)) {
              uVar39 = *(undefined8 *)(iVar5 + 0x16c);
              uVar37 = *(undefined8 *)(iVar5 + 0x174);
              goto LAB_0051d794;
            }
            uVar2 = *(undefined8 *)(iVar5 + 0x16c);
            fStack_298 = fVar28;
            fStack_294 = fVar29;
            if (*(int *)(iVar5 + 0x110) == 0) goto LAB_0051d794;
            cVar1 = *(char *)(iVar5 + 0x2e2);
            uVar13 = 0;
            pfVar25 = (float *)((ulonglong)*(undefined8 *)(iVar5 + 0x174) >> 0x20);
            fVar31 = (float)g2c_bits_to_float((uint)(((ulonglong)uVar2 >> 0x20)));
            fVar27 = (float)g2c_bits_to_float((uint)(*(undefined8 *)(iVar5 + 0x174)));
            fVar22 = (float)g2c_bits_to_float((uint)(uVar2));
            if ((cVar1 == '\0') || (*(int *)(iVar5 + 0x118) != 0)) {
              if (-1 < (int)((uint)*(byte *)(iVar5 + 0x7d) << 0x1b)) {
                uVar13 = audio_uart_nema_stencil_save_52266e(1,0,1,0);
              }
              g2c_nema_vg_emit_verts_516b34
                        (fVar22,fVar31,fStack_298,fStack_294,fVar27,g2c_ptr_as_float(pfVar25),fVar20,fVar21);
              bVar15 = *(byte *)(*piVar3 + 0x7d);
joined_r0x0051d790:
              if (-1 < (int)((uint)bVar15 << 0x1b)) {
                audio_uart_nema_stencil_restore_5226b2(uVar13);
              }
              goto LAB_0051d794;
            }
            if (cVar1 == '\x02') {
              fStack_2c8 = *(g2c_nvg_zero_pair_0);
              pfStack_2c4 = ((float *)g2c_float_as_ptr(g2c_nvg_zero_pair_0[1])) /* stock vldmia lit pair; vstmia sp (value copy) */;
              iVar5 = g2c_nema_vg_cubic_approx_522f50
                                (fVar22,fVar31,fVar27,g2c_ptr_as_float(pfVar25),fVar28,fVar29,fVar20,fVar21,
                                 &fStack_2c8,(float *)&pfStack_2c4);
              if (iVar5 != 0) {
                iVar5 = *piVar3;
                fVar22 = audio_uart_float_sqrt_4397a8
                                   (*(float *)(iVar5 + 0xec) * *(float *)(iVar5 + 0xec) +
                                    *(float *)(iVar5 + 0xf0) * *(float *)(iVar5 + 0xf0));
                fVar21 = audio_uart_float_sqrt_4397a8
                                   (*(float *)(iVar5 + 0xf8) * *(float *)(iVar5 + 0xf8) +
                                    *(float *)(iVar5 + 0xfc) * *(float *)(iVar5 + 0xfc));
                /* Evidence (wave12): stock 0x51d85c vcmp |s20|,(2.000000238418579f); itt lt; vcmplt |s0|,(2.000000238418579f); iteee lt;
                 * blge 0x522622(1). */
                bVar15 = (byte)(!(!(ABS(fVar22) >= (2.000000238418579f)) && !(ABS(fVar21) >= (2.000000238418579f))));
                bVar16 = 1;
                if (bVar15 == bVar16) {
                  g2c_nema_vg_set_flag_522622(1);
                }
                fVar22 = *(float *)(*piVar3 + 0x2d8) * 0.5f;
                if ((int)((uint)*(byte *)(*piVar3 + 0x7d) << 0x1b) < 0) {
                  g2c_nema_vg_move_to_522fb4(fStack_2c8,g2c_ptr_as_float(pfStack_2c4),fVar22);
                }
                else {
                  g2c_nema_vg_line_to_523284(fStack_2c8,g2c_ptr_as_float(pfStack_2c4),fVar22);
                }
                if (bVar15 == bVar16) {
                  g2c_nema_vg_set_flag_522622(0);
                }
              }
              goto LAB_0051d794;
            }
            if (cVar1 == '\x01') {
              if (*(char *)(iVar5 + 0x2e4) == '\0') {
                fVar24 = *(float *)(iVar5 + 0x158);
                /* stock 0x51d8ec vcmp [+0x158],#0 / ble 0x51d920 (le includes unordered) */
                if (!(fVar24 > 0.0f) ||
                   (*(int *)(iVar5 + 0x128) != 1)) {
                  fStack_264 = *(float *)(iVar5 + 0x164);
                  fStack_260 = *(float *)(iVar5 + 0x168);
                  fStack_25c = *(float *)(iVar5 + 0x16c);
                  fStack_258 = *(float *)(iVar5 + 0x170);
                  fStack_254 = *(float *)(iVar5 + 0x174);
                  fStack_250 = *(float *)(iVar5 + 0x178);
                  pfVar10 = (float *)(iVar5 + 400);
                  fStack_24c = *(float *)(iVar5 + 0x17c);
                  fStack_248 = *(float *)(iVar5 + 0x180);
                  uStack_244 = *(undefined4 *)(iVar5 + 0x184);
                  uStack_240 = *(undefined4 *)(iVar5 + 0x188);
                  uStack_23c = *(undefined4 *)(iVar5 + 0x18c);
                }
                else {
                  fStack_264 = *(float *)(iVar5 + 0x138);
                  fStack_260 = *(float *)(iVar5 + 0x13c);
                  fStack_25c = *(float *)(iVar5 + 0x140);
                  fStack_258 = *(float *)(iVar5 + 0x144);
                  fStack_254 = *(float *)(iVar5 + 0x148);
                  fStack_250 = *(float *)(iVar5 + 0x14c);
                  pfVar10 = (float *)(iVar5 + 400);
                  fStack_24c = *(float *)(iVar5 + 0x150);
                  fStack_248 = *(float *)(iVar5 + 0x154);
                  uStack_244 = *(undefined4 *)(iVar5 + 0x158);
                  uStack_240 = *(undefined4 *)(iVar5 + 0x15c);
                  uStack_23c = *(undefined4 *)(iVar5 + 0x160);
                }
              }
              else {
                fStack_264 = *(float *)(iVar5 + 0x334);
                fStack_260 = *(float *)(iVar5 + 0x338);
                fStack_25c = *(float *)(iVar5 + 0x33c);
                fStack_258 = *(float *)(iVar5 + 0x340);
                fStack_254 = *(float *)(iVar5 + 0x344);
                fStack_250 = *(float *)(iVar5 + 0x348);
                pfVar10 = (float *)(iVar5 + 0x308);
                fStack_24c = *(float *)(iVar5 + 0x34c);
                fStack_248 = *(float *)(iVar5 + 0x350);
                uStack_244 = *(undefined4 *)(iVar5 + 0x354);
                uStack_240 = *(undefined4 *)(iVar5 + 0x358);
                uStack_23c = *(undefined4 *)(iVar5 + 0x35c);
              }
              fStack_290 = *pfVar10;
              fStack_28c = pfVar10[1];
              fStack_288 = pfVar10[2];
              fStack_284 = pfVar10[3];
              fStack_280 = pfVar10[4];
              fStack_27c = pfVar10[5];
              fStack_278 = pfVar10[6];
              fStack_274 = pfVar10[7];
              fStack_270 = pfVar10[8];
              fStack_26c = pfVar10[9];
              fStack_268 = pfVar10[10];
              iVar5 = g2c_nema_vg_near_5177a4(&fStack_290,&fStack_264);
              if ((((iVar5 != 1) ||
                   (iVar5 = g2c_nema_vg_near_5177a4(&fStack_288,&fStack_25c), iVar5 != 1)) ||
                  (iVar5 = g2c_nema_vg_near_5177a4(&fStack_280,&fStack_254), iVar5 != 1)) ||
                 (iVar5 = g2c_nema_vg_near_5177a4(&fStack_278,&fStack_24c), iVar5 != 1)) {
                iVar5 = g2c_nema_vg_near2_51785c(&fStack_290,&fStack_25c);
                if ((iVar5 != 0) ||
                   (iVar5 = g2c_nema_vg_near2_51785c(&fStack_264,&fStack_290), iVar5 != 0))
                goto LAB_0051d9ae;
                iVar5 = g2c_nema_vg_near2_51785c(&fStack_290,&fStack_254);
                if ((iVar5 == 0) &&
                   (iVar5 = g2c_nema_vg_near2_51785c(&fStack_264,&fStack_278), iVar5 == 0)) {
                  /* stock 0x51dafa vcmp [sp+68],[sp+120]; 0x51db06 vcmp [sp+128],[sp+120];
                     blt.n 0x51db14 -> bpl.w 0x51d9ae else 0x51daba; GE path: bpl.n 0x51daba.
                     (wave17: the decompiler's NaN-only first test replaced by the stock LT test.) */
                  if (!(fStack_28c >= fStack_258)) {
                    if (fStack_250 < fStack_258) goto LAB_0051daba;
                  }
                  else if (!(fStack_250 < fStack_258)) goto LAB_0051daba;
LAB_0051d9ae:
                  fStack_29c = fStack_24c;
                  fStack_2a0 = fStack_248;
                  fStack_2a4 = fStack_280;
                  fStack_2a8 = fStack_27c;
                  fVar28 = fStack_25c;
                  fVar23 = fStack_258;
                  fVar26 = fStack_290;
                  fVar33 = fStack_28c;
                  fVar30 = fStack_278;
                  fVar34 = fStack_274;
                  fVar24 = fStack_254;
                  fVar29 = fStack_250;
                }
                else {
LAB_0051daba:
                  fStack_2a0 = fStack_260;
                  fStack_29c = fStack_264;
                  fStack_2a4 = fStack_288;
                  fStack_2a8 = fStack_284;
                  fVar28 = fStack_254;
                  fVar23 = fStack_250;
                  fVar26 = fStack_278;
                  fVar33 = fStack_274;
                  fVar30 = fStack_290;
                  fVar34 = fStack_28c;
                  fVar24 = fStack_25c;
                  fVar29 = fStack_258;
                }
                fStack_2b0 = *pfStack_2cc;
                fStack_2ac = pfStack_2cc[1];
                fStack_2c8 = *(g2c_nvg_zero_pair_2);
                pfStack_2c4 = ((float *)g2c_float_as_ptr(g2c_nvg_zero_pair_2[1])) /* stock vldmia lit pair; vstmia sp (value copy) */;
                iVar5 = g2c_nema_vg_cubic_approx_522f50
                                  (fVar24,fVar29,fVar28,fVar23,fVar30,fVar34,fVar26,fVar33,
                                   &fStack_2b0,&fStack_2ac);
                iVar6 = g2c_nema_vg_cubic_approx_522f50
                                  (fStack_29c,fStack_2a0,fVar24,fVar29,fVar30,fVar34,fStack_2a4,
                                   fStack_2a8,&fStack_2c8,(float *)&pfStack_2c4);
                fVar28 = g2c_nema_vg_sqrt_524218
                                   ((fStack_2c8 - fStack_2b0) * (fStack_2c8 - fStack_2b0) +
                                    (g2c_ptr_as_float(pfStack_2c4) - fStack_2ac) *
                                    (g2c_ptr_as_float(pfStack_2c4) - fStack_2ac));
                iVar7 = *piVar3;
                fVar23 = *(float *)(iVar7 + 0x2dc) * *(float *)(iVar7 + 0x2d8);
                /* stock 0x51da6a vcmp.f32 s2,s0; vmrs; blt.n 0x51da78 (GE continues). */
                if (((fVar23 >= fVar28) && (iVar6 != 0)) &&
                   (iVar5 != 0)) {
                  fVar22 = fStack_2b0;
                  fVar31 = fStack_2ac;
                  fVar27 = fStack_2c8;
                  pfVar25 = pfStack_2c4;
                  if (-1 < (int)((uint)*(byte *)(iVar7 + 0x7d) << 0x1b)) {
                    uVar13 = audio_uart_nema_stencil_save_52266e(0,1,1,0);
                    fVar22 = fStack_2b0;
                    fVar31 = fStack_2ac;
                    fVar27 = fStack_2c8;
                    pfVar25 = pfStack_2c4;
                  }
                }
                else {
                  fVar24 = fStack_298;
                  fVar29 = fStack_294;
                  fVar30 = fVar20;
                  fVar34 = fVar21;
                  if (-1 < (int)((uint)*(byte *)(iVar7 + 0x7d) << 0x1b)) {
                    uVar13 = audio_uart_nema_stencil_save_52266e(1,0,1,0);
                    fVar24 = fStack_298;
                    fVar29 = fStack_294;
                  }
                }
                g2c_nema_vg_emit_verts_516b34
                          (fVar22,fVar31,fVar24,fVar29,fVar27,g2c_ptr_as_float(pfVar25),fVar30,fVar34);
                bVar15 = *(byte *)(*piVar3 + 0x7d);
                goto joined_r0x0051d790;
              }
              goto LAB_0051d794;
            }
LAB_0051d8c6:
            *(undefined4 *)(iVar5 + 0x114) = 0;
            *(undefined4 *)(iVar5 + 0x118) = 0;
            audio_uart_nema_vg_set_error_51565c(0x1000000);
            iVar5 = *piVar3;
            *(undefined4 *)(iVar5 + 0x114) = 0;
            *(undefined4 *)(iVar5 + 0x118) = 0;
            goto LAB_0051e538;
          }
LAB_0051d794:
          iVar5 = *piVar3;
          /* stock 0x51d79a vcmp.f32 s0,#0.0; vmrs; bls.w 0x51dc00 (body runs on HI). */
          if (!(*(float *)(iVar5 + 0x158) <= 0.0f) && (*(int *)(iVar5 + 0x128) == 1)) {
            uVar13 = uVar4;
            if ((0.05000000447034836f) <=
                ABS(*(float *)(iVar5 + 0x15c) * fVar41 - *(float *)(iVar5 + 0x160) * fVar42)) {
              uVar2 = *(undefined8 *)(iVar5 + 0x140);
              fVar31 = (float)g2c_bits_to_float((uint)(uVar39));
              fVar27 = (float)g2c_bits_to_float((uint)(((ulonglong)uVar39 >> 0x20)));
              fVar22 = (float)g2c_bits_to_float((uint)(uVar37));
              fVar21 = (float)g2c_bits_to_float((uint)(((ulonglong)uVar37 >> 0x20)));
              if (*(int *)(iVar5 + 0x110) != 0) {
                cVar1 = *(char *)(iVar5 + 0x2e2);
                uVar14 = 0;
                pfVar25 = (float *)((ulonglong)*(undefined8 *)(iVar5 + 0x148) >> 0x20);
                fVar24 = (float)g2c_bits_to_float((uint)(((ulonglong)uVar2 >> 0x20)));
                fVar28 = (float)g2c_bits_to_float((uint)(*(undefined8 *)(iVar5 + 0x148)));
                fVar20 = (float)g2c_bits_to_float((uint)(uVar2));
                if ((cVar1 == '\0') || (*(int *)(iVar5 + 0x118) != 0)) {
                  if (-1 < (int)((uint)*(byte *)(iVar5 + 0x7d) << 0x1b)) {
                    uVar14 = audio_uart_nema_stencil_save_52266e(1,0,1,0);
                  }
                  g2c_nema_vg_emit_verts_516b34
                            (fVar20,fVar24,fVar31,fVar27,fVar28,g2c_ptr_as_float(pfVar25),fVar22,fVar21);
                  bVar15 = *(byte *)(*piVar3 + 0x7d);
joined_r0x0051dbfc:
                  uVar13 = uVar4;
                  if (-1 < (int)((uint)bVar15 << 0x1b)) {
                    audio_uart_nema_stencil_restore_5226b2(uVar14);
                    uVar13 = uVar4;
                  }
                }
                else if (cVar1 == '\x02') {
                  fStack_2c8 = *(g2c_nvg_zero_pair_0);
                  pfStack_2c4 = ((float *)g2c_float_as_ptr(g2c_nvg_zero_pair_0[1])) /* stock vldmia lit pair; vstmia sp (value copy) */;
                  iVar5 = g2c_nema_vg_cubic_approx_522f50
                                    (fVar20,fVar24,fVar28,g2c_ptr_as_float(pfVar25),fVar31,fVar27,fVar22,fVar21
                                     ,&fStack_2c8,(float *)&pfStack_2c4);
                  uVar13 = uVar4;
                  if (iVar5 != 0) {
                    iVar5 = *piVar3;
                    fVar22 = audio_uart_float_sqrt_4397a8
                                       (*(float *)(iVar5 + 0xec) * *(float *)(iVar5 + 0xec) +
                                        *(float *)(iVar5 + 0xf0) * *(float *)(iVar5 + 0xf0));
                    fVar21 = audio_uart_float_sqrt_4397a8
                                       (*(float *)(iVar5 + 0xf8) * *(float *)(iVar5 + 0xf8) +
                                        *(float *)(iVar5 + 0xfc) * *(float *)(iVar5 + 0xfc));
                    /* stock 0x51dcd8 vcmp; ittt lt; vcmplt 0x51dcea; iteee lt; blge 0x522622. */
                    bVar15 = (byte)(ABS(fVar22) >= 2.0000002f || ABS(fVar21) >= 2.0000002f); /* = stock r5 (movge r5,#1 / movlt #0) */
                    bVar16 = 1;
                    if (bVar15 == bVar16) {
                      g2c_nema_vg_set_flag_522622(1);
                    }
                    fVar22 = *(float *)(*piVar3 + 0x2d8) * 0.5f;
                    if ((int)((uint)*(byte *)(*piVar3 + 0x7d) << 0x1b) < 0) {
                      g2c_nema_vg_move_to_522fb4(fStack_2c8,g2c_ptr_as_float(pfStack_2c4),fVar22);
                    }
                    else {
                      g2c_nema_vg_line_to_523284(fStack_2c8,g2c_ptr_as_float(pfStack_2c4),fVar22);
                    }
                    if (bVar15 == bVar16) { /* stock 0x51dd34 cmp r5,#0; beq skip; set_flag(0) (wave18: previously tested a stale bVar15) */
                      g2c_nema_vg_set_flag_522622(0);
                    }
                  }
                }
                else {
                  if (cVar1 != '\x01') goto LAB_0051d8c6;
                  if (*(char *)(iVar5 + 0x2e4) == '\0') {
                    fStack_274 = *(float *)(iVar5 + 0x138);
                    fStack_270 = *(float *)(iVar5 + 0x13c);
                    fStack_26c = *(float *)(iVar5 + 0x140);
                    fStack_268 = *(float *)(iVar5 + 0x144);
                    fStack_264 = *(float *)(iVar5 + 0x148);
                    fStack_260 = *(float *)(iVar5 + 0x14c);
                    pfVar10 = (float *)(iVar5 + 400);
                    fStack_25c = *(float *)(iVar5 + 0x150);
                    fStack_258 = *(float *)(iVar5 + 0x154);
                    fStack_254 = *(float *)(iVar5 + 0x158);
                    fStack_250 = *(float *)(iVar5 + 0x15c);
                    fStack_24c = *(float *)(iVar5 + 0x160);
                  }
                  else {
                    fStack_274 = *(float *)(iVar5 + 0x334);
                    fStack_270 = *(float *)(iVar5 + 0x338);
                    fStack_26c = *(float *)(iVar5 + 0x33c);
                    fStack_268 = *(float *)(iVar5 + 0x340);
                    fStack_264 = *(float *)(iVar5 + 0x344);
                    fStack_260 = *(float *)(iVar5 + 0x348);
                    pfVar10 = (float *)(iVar5 + 0x308);
                    fStack_25c = *(float *)(iVar5 + 0x34c);
                    fStack_258 = *(float *)(iVar5 + 0x350);
                    fStack_254 = *(float *)(iVar5 + 0x354);
                    fStack_250 = *(float *)(iVar5 + 0x358);
                    fStack_24c = *(float *)(iVar5 + 0x35c);
                  }
                  fStack_2a0 = *pfVar10;
                  fStack_29c = pfVar10[1];
                  fStack_298 = pfVar10[2];
                  fStack_294 = pfVar10[3];
                  fStack_290 = pfVar10[4];
                  fStack_28c = pfVar10[5];
                  fStack_288 = pfVar10[6];
                  fStack_284 = pfVar10[7];
                  fStack_280 = pfVar10[8];
                  fStack_27c = pfVar10[9];
                  fStack_278 = pfVar10[10];
                  iVar5 = g2c_nema_vg_near_5177a4(&fStack_2a0,&fStack_274);
                  if ((((iVar5 != 1) ||
                       (iVar5 = g2c_nema_vg_near_5177a4(&fStack_298,&fStack_26c), iVar5 != 1)) ||
                      (iVar5 = g2c_nema_vg_near_5177a4(&fStack_290,&fStack_264), iVar5 != 1)) ||
                     (iVar5 = g2c_nema_vg_near_5177a4(&fStack_288,&fStack_25c), uVar13 = uVar4,
                     iVar5 != 1)) {
                    iVar5 = g2c_nema_vg_near2_51785c(&fStack_2a0,&fStack_26c);
                    if ((iVar5 != 0) ||
                       (iVar5 = g2c_nema_vg_near2_51785c(&fStack_274,&fStack_2a0), iVar5 != 0))
                    goto LAB_0051ddda;
                    iVar5 = g2c_nema_vg_near2_51785c(&fStack_2a0,&fStack_264);
                    if ((iVar5 == 0) &&
                       (iVar5 = g2c_nema_vg_near2_51785c(&fStack_274,&fStack_288), iVar5 == 0)) {
                      /* stock 0x51df2e vcmp [sp+52],[sp+104]; 0x51df3a vcmp [sp+112],[sp+104];
                         blt.n 0x51df48 -> bpl.w 0x51ddda else 0x51deec; GE path: bpl.n 0x51deec.
                         (wave17: the decompiler's NaN-only first test replaced by the stock LT test.) */
                      if (!(fStack_29c >= fStack_268)) {
                        if (fStack_260 < fStack_268) goto LAB_0051deec;
                      }
                      else if (!(fStack_260 < fStack_268)) goto LAB_0051deec;
LAB_0051ddda:
                      fStack_2a4 = fStack_25c;
                      fStack_2a8 = fStack_258;
                      fVar23 = fStack_26c;
                      fVar26 = fStack_268;
                      fVar33 = fStack_2a0;
                      fVar35 = fStack_29c;
                      fVar32 = fStack_28c;
                      g = fStack_290;
                      fVar34 = fStack_288;
                      fVar36 = fStack_284;
                      fVar29 = fStack_264;
                      fVar30 = fStack_260;
                    }
                    else {
LAB_0051deec:
                      fStack_2a8 = fStack_270;
                      fStack_2a4 = fStack_274;
                      fVar23 = fStack_264;
                      fVar26 = fStack_260;
                      fVar33 = fStack_288;
                      fVar35 = fStack_284;
                      fVar32 = fStack_294;
                      g = fStack_298;
                      fVar34 = fStack_2a0;
                      fVar36 = fStack_29c;
                      fVar29 = fStack_26c;
                      fVar30 = fStack_268;
                    }
                    fStack_2b0 = *pfStack_2cc;
                    fStack_2ac = pfStack_2cc[1];
                    fStack_2c8 = *(g2c_nvg_zero_pair_2);
                    pfStack_2c4 = ((float *)g2c_float_as_ptr(g2c_nvg_zero_pair_2[1])) /* stock vldmia lit pair; vstmia sp (value copy) */;
                    iVar5 = g2c_nema_vg_cubic_approx_522f50
                                      (fVar29,fVar30,fVar23,fVar26,fVar34,fVar36,fVar33,fVar35,
                                       &fStack_2b0,&fStack_2ac);
                    iVar6 = g2c_nema_vg_cubic_approx_522f50
                                      (fStack_2a4,fStack_2a8,fVar29,fVar30,fVar34,fVar36,g,fVar32,
                                       &fStack_2c8,(float *)&pfStack_2c4);
                    fVar23 = g2c_nema_vg_sqrt_524218
                                       ((fStack_2c8 - fStack_2b0) * (fStack_2c8 - fStack_2b0) +
                                        (g2c_ptr_as_float(pfStack_2c4) - fStack_2ac) *
                                        (g2c_ptr_as_float(pfStack_2c4) - fStack_2ac));
                    iVar7 = *piVar3;
                    fVar26 = *(float *)(iVar7 + 0x2dc) * *(float *)(iVar7 + 0x2d8);
                    /* stock 0x51de96 vcmp.f32 s2,s0; vmrs; blt.n 0x51dea4 (GE continues). */
                    if (((fVar26 >= fVar23) && (iVar6 != 0)) &&
                       (iVar5 != 0)) {
                      fVar20 = fStack_2b0;
                      fVar24 = fStack_2ac;
                      fVar28 = fStack_2c8;
                      pfVar25 = pfStack_2c4;
                      if (-1 < (int)((uint)*(byte *)(iVar7 + 0x7d) << 0x1b)) {
                        uVar14 = audio_uart_nema_stencil_save_52266e(0,1,1,0);
                        fVar20 = fStack_2b0;
                        fVar24 = fStack_2ac;
                        fVar28 = fStack_2c8;
                        pfVar25 = pfStack_2c4;
                      }
                    }
                    else {
                      fVar29 = fVar31;
                      fVar30 = fVar27;
                      fVar34 = fVar22;
                      fVar36 = fVar21;
                      if (-1 < (int)((uint)*(byte *)(iVar7 + 0x7d) << 0x1b)) {
                        uVar14 = audio_uart_nema_stencil_save_52266e(1,0,1,0);
                      }
                    }
                    g2c_nema_vg_emit_verts_516b34
                              (fVar20,fVar24,fVar29,fVar30,fVar28,g2c_ptr_as_float(pfVar25),fVar34,fVar36);
                    bVar15 = *(byte *)(*piVar3 + 0x7d);
                    goto joined_r0x0051dbfc;
                  }
                }
              }
            }
            else {
              uVar39 = *(undefined8 *)(iVar5 + 0x140);
              uVar37 = *(undefined8 *)(iVar5 + 0x148);
            }
          }
          iVar5 = *piVar3;
          /* stock 0x51dc06 vcmp [+0x158],#0 / beq.w 0x51dfc4 */
          *(int *)(iVar5 + 0x128) = *(int *)(iVar5 + 0x128) + 1;
          uVar40 = (undefined4)((ulonglong)uVar39 >> 0x20);
          uVar38 = (undefined4)((ulonglong)uVar37 >> 0x20);
          if (*(float *)(iVar5 + 0x158) != 0.0f) {
            *(int *)(iVar5 + 0x164) = (int)uVar39;
            *(undefined4 *)(iVar5 + 0x168) = uVar40;
            iVar5 = *piVar3;
            *(float *)(iVar5 + 0x16c) = fStack_2b8;
            *(float *)(iVar5 + 0x170) = fStack_2b4;
            iVar5 = *piVar3;
            *(float *)(iVar5 + 0x174) = fStack_2c0;
            *(float *)(iVar5 + 0x178) = fStack_2bc;
            iVar5 = *piVar3;
            *(int *)(iVar5 + 0x17c) = (int)uVar37;
            *(undefined4 *)(iVar5 + 0x180) = uVar38;
            iVar5 = *piVar3;
            *(float *)(iVar5 + 0x184) = fVar19;
            *(float *)(iVar5 + 0x188) = fVar42;
            *(float *)(iVar5 + 0x18c) = fVar41;
          }
          else {
            *(int *)(iVar5 + 0x138) = (int)uVar39;
            *(undefined4 *)(iVar5 + 0x13c) = uVar40;
            iVar5 = *piVar3;
            *(float *)(iVar5 + 0x140) = fStack_2b8;
            *(float *)(iVar5 + 0x144) = fStack_2b4;
            iVar5 = *piVar3;
            *(float *)(iVar5 + 0x148) = fStack_2c0;
            *(float *)(iVar5 + 0x14c) = fStack_2bc;
            iVar5 = *piVar3;
            *(int *)(iVar5 + 0x150) = (int)uVar37;
            *(undefined4 *)(iVar5 + 0x154) = uVar38;
            iVar5 = *piVar3;
            *(float *)(iVar5 + 0x158) = fVar19;
            *(float *)(iVar5 + 0x15c) = fVar42;
            *(float *)(iVar5 + 0x160) = fVar41;
          }
        }
        audio_uart_nema_stencil_restore_5226b2(uVar11);
      }
      else {
        iVar5 = *piVar3;
        *(float *)(iVar5 + 0x198) = fStack_22c;
        *(float *)(iVar5 + 0x19c) = fStack_228 + *(float *)(iVar5 + 0x130) * -0.5f;
        *(float *)(iVar5 + 0x1a0) = fStack_22c;
        *(float *)(iVar5 + 0x1a4) = fStack_228 + *(float *)(iVar5 + 0x130) * 0.5f;
        *(undefined4 *)(iVar5 + 400) = *(undefined4 *)(iVar5 + 0x198);
        *(undefined4 *)(iVar5 + 0x194) = *(undefined4 *)(iVar5 + 0x19c);
        iVar5 = *piVar3;
        *(undefined4 *)(iVar5 + 0x1a8) = *(undefined4 *)(iVar5 + 0x1a0);
        *(undefined4 *)(iVar5 + 0x1ac) = *(undefined4 *)(iVar5 + 0x1a4);
      }
    }
  } while( true );
}
#undef pfStack_2cc
#undef fStack_2c8
#undef pfStack_2c4
#undef fStack_2c0
#undef fStack_2bc
#undef fStack_2b8
#undef fStack_2b4
#undef fStack_2b0
#undef fStack_2ac
#undef fStack_2a8
#undef fStack_2a4
#undef fStack_2a0
#undef fStack_29c
#undef fStack_298
#undef fStack_294
#undef fStack_290
#undef fStack_28c
#undef fStack_288
#undef fStack_284
#undef fStack_280
#undef fStack_27c
#undef fStack_278
#undef fStack_274
#undef fStack_270
#undef fStack_26c
#undef fStack_268
#undef fStack_264
#undef fStack_260
#undef fStack_25c
#undef fStack_258
#undef fStack_254
#undef fStack_250
#undef fStack_24c
#undef fStack_248
#undef uStack_244
#undef uStack_240
#undef uStack_23c
#undef uStack_238
#undef fStack_22c
#undef fStack_228
#undef fStack_224
#undef fStack_220
#undef fStack_21c
#undef fStack_218
#undef fStack_214
#undef fStack_210
#undef afStack_200
#undef fStack_1f0
#undef fStack_1ec
#undef afStack_1e8


  

/* ---- lifted 0x51f798 ---- */


uint g2c_nema_vg_draw_stroke_51f798(uint *a)

{
  /* Evidence (wave11): every s0-s4 value left after a call in this function is dead in stock.
   * .waves/w11/vlive.py reports "none" after each bl at 0x51f8a0/8c8/a60/aa2/ad6/ba4/bb6/ca0/df8/
   * e24/e56/e5c/f9a/ffb4 and at 0x51fa72. So the callee-leftover copies are removed. */
  char cVar1;
  byte bVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  undefined8 uVar5;
  int *piVar6;
  uint uVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  float *pfVar12;
  undefined4 uVar13;
  uint uVar14;
  undefined4 uVar15;
  uint uVar16;
  uint cmd;
  undefined4 uVar17;
  undefined4 uVar18;
  undefined4 uVar19;
  bool bVar20;
  float fVar21;
  float fVar22;
  float fVar23;
  float fVar24;
  float fVar25;
  float d;
  float fVar26;
  float g;
  float h;
  float fVar27;
  float e;
  float fVar28;
  float f;
  float a_00;
  float b;
  float fVar29;
  float h_00;
  float g_00;
  float b_00;
  float a_01;
  /* Stock frame of 0x51f798 as one block: locals keep the entry-SP offsets Ghidra named them by
   * (X_Stack_NN at g2c_frame_51f798[0x118-0xNN]) so &local passed to callees spans its stock neighbours. */
  unsigned char g2c_frame_51f798[0x118] __attribute__((aligned(8)));
  typedef float __attribute__((may_alias)) g2c_fa_float;
#define fStack_118 (*(g2c_fa_float *)(void *)&g2c_frame_51f798[0x118-0x118])
#define fStack_114 (*(g2c_fa_float *)(void *)&g2c_frame_51f798[0x118-0x114])
#define fStack_110 (*(g2c_fa_float *)(void *)&g2c_frame_51f798[0x118-0x110])
#define fStack_10c (*(g2c_fa_float *)(void *)&g2c_frame_51f798[0x118-0x10c])
#define fStack_108 (*(g2c_fa_float *)(void *)&g2c_frame_51f798[0x118-0x108])
#define fStack_104 (*(g2c_fa_float *)(void *)&g2c_frame_51f798[0x118-0x104])
#define fStack_100 (*(g2c_fa_float *)(void *)&g2c_frame_51f798[0x118-0x100])
#define fStack_fc (*(g2c_fa_float *)(void *)&g2c_frame_51f798[0x118-0xfc])
#define fStack_f8 (*(g2c_fa_float *)(void *)&g2c_frame_51f798[0x118-0xf8])
#define fStack_f4 (*(g2c_fa_float *)(void *)&g2c_frame_51f798[0x118-0xf4])
#define fStack_f0 (*(g2c_fa_float *)(void *)&g2c_frame_51f798[0x118-0xf0])
#define fStack_ec (*(g2c_fa_float *)(void *)&g2c_frame_51f798[0x118-0xec])
#define fStack_e8 (*(g2c_fa_float *)(void *)&g2c_frame_51f798[0x118-0xe8])
#define fStack_e4 (*(g2c_fa_float *)(void *)&g2c_frame_51f798[0x118-0xe4])
#define fStack_e0 (*(g2c_fa_float *)(void *)&g2c_frame_51f798[0x118-0xe0])
#define fStack_dc (*(g2c_fa_float *)(void *)&g2c_frame_51f798[0x118-0xdc])
#define fStack_d8 (*(g2c_fa_float *)(void *)&g2c_frame_51f798[0x118-0xd8])
#define fStack_d4 (*(g2c_fa_float *)(void *)&g2c_frame_51f798[0x118-0xd4])
#define fStack_d0 (*(g2c_fa_float *)(void *)&g2c_frame_51f798[0x118-0xd0])
#define fStack_cc (*(g2c_fa_float *)(void *)&g2c_frame_51f798[0x118-0xcc])
#define fStack_c8 (*(g2c_fa_float *)(void *)&g2c_frame_51f798[0x118-0xc8])
#define fStack_c4 (*(g2c_fa_float *)(void *)&g2c_frame_51f798[0x118-0xc4])
#define fStack_c0 (*(g2c_fa_float *)(void *)&g2c_frame_51f798[0x118-0xc0])
  typedef undefined4 __attribute__((may_alias)) g2c_fa_undefined4;
#define uStack_bc (*(g2c_fa_undefined4 *)(void *)&g2c_frame_51f798[0x118-0xbc])
#define uStack_b8 (*(g2c_fa_undefined4 *)(void *)&g2c_frame_51f798[0x118-0xb8])
#define uStack_b4 (*(g2c_fa_undefined4 *)(void *)&g2c_frame_51f798[0x118-0xb4])
  typedef undefined1 __attribute__((may_alias)) g2c_fa_undefined1;
#define uStack_b0 (*(g2c_fa_undefined1 *)(void *)&g2c_frame_51f798[0x118-0xb0])
  typedef char __attribute__((may_alias)) g2c_fa_char;
#define cStack_af (*(g2c_fa_char *)(void *)&g2c_frame_51f798[0x118-0xaf])
#define cStack_ae (*(g2c_fa_char *)(void *)&g2c_frame_51f798[0x118-0xae])
#define fStack_a4 (*(g2c_fa_float *)(void *)&g2c_frame_51f798[0x118-0xa4])
#define fStack_a0 (*(g2c_fa_float *)(void *)&g2c_frame_51f798[0x118-0xa0])
#define fStack_9c (*(g2c_fa_float *)(void *)&g2c_frame_51f798[0x118-0x9c])
#define fStack_98 (*(g2c_fa_float *)(void *)&g2c_frame_51f798[0x118-0x98])
#define fStack_94 (*(g2c_fa_float *)(void *)&g2c_frame_51f798[0x118-0x94])
#define fStack_90 (*(g2c_fa_float *)(void *)&g2c_frame_51f798[0x118-0x90])
#define fStack_8c (*(g2c_fa_float *)(void *)&g2c_frame_51f798[0x118-0x8c])
#define fStack_88 (*(g2c_fa_float *)(void *)&g2c_frame_51f798[0x118-0x88])
  
  piVar6 = (((int *)&audio_uart_nema_vg_context_cell));
  iVar10 = *(((int *)&audio_uart_nema_vg_context_cell));
  audio_uart_lv_memzero_48949c((uint)&uStack_b0,0x48);
  uStack_b0 = 1;
  cStack_ae = '\x01';
  cStack_af = '\x01';
  uVar16 = 0;
  g2c_nema_vg_path_clear_56395c();
LAB_0051f7ee:
  do {
    do {
      do {
        while( true ) {
          if (*a <= uVar16) {
            return 0;
          }
          bVar2 = *(byte *)(a[2] + uVar16);
          cmd = (uint)bVar2;
          uVar16 = uVar16 + 1;
          uVar7 = g2c_nema_vg_path_cmd_5156b8(a,cmd,(float *)&uStack_b0);
          uVar14 = cmd & 0x6f;
          if (uVar7 != 0) goto LAB_0051f812;
          if (uVar16 == *a) {
            *(undefined1 *)(*piVar6 + 0x1c1) = 1;
          }
          else {
            *(bool *)(*piVar6 + 0x1c1) = *(char *)(a[2] + uVar16) == '\x01';
          }
          *(byte *)(iVar10 + 0x2e9) = (byte)(-(uint)(cStack_af == '\0') >> 0x1f);
          if ((cStack_ae == '\0') && (-1 < (int)(cmd << 0x18))) break;
          iVar11 = *piVar6;
          if (*(char *)(iVar11 + 0x2e7) != '\0') {
            *(undefined4 *)(iVar11 + 0x2f8) = 0;
            *(undefined4 *)(iVar11 + 0x304) = *(undefined4 *)(iVar11 + 0x300);
          }
          *(undefined1 *)(iVar10 + 0x2e8) = 0;
          *(undefined4 *)(iVar10 + 0x2fc) = 0;
          *(undefined1 *)(iVar10 + 0x2e5) = 1;
        }
        if ((uVar14 == 6) || (uVar14 == 8)) {
          *(undefined1 *)(iVar10 + 0x2ea) = 1;
          g2c_nema_vg_stroke_path_517e18
                    (fStack_a4,fStack_a0,fStack_94,fStack_90,fStack_8c,fStack_88,fStack_9c,fStack_98
                    );
        }
        else if ((uVar14 == 5) || (uVar14 == 7)) {
          *(undefined1 *)(iVar10 + 0x2ea) = 1;
          g2c_nema_vg_fill_path_519290(fStack_a4,fStack_a0,fStack_94,fStack_90,fStack_9c,fStack_98);
        }
        else {
          if ((cmd & 0xf) == 9) {
            *(undefined1 *)(iVar10 + 0x2ea) = 1;
            uVar7 = g2c_nema_vg_arc_to_51a8ec((uint)a,(int)&uStack_b0);
          }
          else {
            if (uVar14 == 10 || uVar14 == 0xb) goto LAB_0051fa72;
            *(undefined1 *)(iVar10 + 0x2ea) = 0;
            uVar7 = g2c_nema_vg_path_bounds_5639e8(fStack_a4,fStack_a0,fStack_9c,fStack_98);
          }
          if (uVar7 != 0) {
LAB_0051f812:
            iVar10 = *piVar6;
            *(undefined4 *)(iVar10 + 0x114) = 0;
            *(undefined4 *)(iVar10 + 0x118) = 0;
            audio_uart_nema_vg_set_error_51565c(uVar7);
            return uVar7;
          }
        }
LAB_0051fa72:
        iVar11 = *piVar6;
        if ((*(char *)(iVar11 + 0x1c1) != '\0') &&
           ((((bVar2 & 0x6f) != 0 && (*(int *)(iVar11 + 0x2f8) != 0)) ||
            (*(char *)(iVar11 + 0x1c2) != '\0')))) {
          bVar20 = *(int *)(iVar11 + 0x110) != 0;
          cVar1 = '\0';
          if (bVar20) {
            cVar1 = *(char *)(iVar11 + 0x2e1);
          }
          if (bVar20 && cVar1 != '\0') {
            if (cVar1 == '\x02') {
              fVar29 = *(float *)(iVar11 + 0x198);
              fVar21 = *(float *)(iVar11 + 400);
              bVar20 = fVar21 != fVar29;
              if (!bVar20) {
                fVar23 = *(float *)(iVar11 + 0x194);
                fVar24 = *(float *)(iVar11 + 0x19c);
              }
              if (bVar20 || (bVar20 || fVar23 != fVar24)) {
LAB_0051f93c:
                fStack_118 = *(float *)(iVar11 + 0x198);
                fStack_114 = *(float *)(iVar11 + 0x19c);
                bVar20 = fVar29 <= fVar21;
                uVar3 = *(undefined8 *)(iVar11 + 0x1a0);
                fVar26 = *(float *)(iVar11 + 300) * 0.5f;
                fVar24 = *(float *)(iVar11 + 0x1a0);
                fVar25 = *(float *)(iVar11 + 0x19c);
                fVar23 = *(float *)(iVar11 + 0x1a4);
                if (bVar20) {
                  fVar21 = *(float *)(iVar11 + 0x1a8);
                }
                fVar27 = fVar24 - fVar29;
                fVar28 = fVar23 - fVar25;
                fVar22 = g2c_nema_vg_sqrt_524218(fVar27 * fVar27 + fVar28 * fVar28);
                fVar28 = -(fVar28 / fVar22);
                if (!bVar20 || (!bVar20 || fVar21 < fVar24)) {
                  if (0.0f < fVar28) goto LAB_0051f9c0;
LAB_0051fc4c:
                  fVar24 = fVar24 - fVar26 * fVar28;
                  fVar21 = fVar26 * (fVar27 / fVar22);
                  fVar29 = fVar29 - fVar26 * fVar28;
                  fVar23 = fVar23 - fVar21;
                  fVar21 = fVar25 - fVar21;
                }
                else {
                  if (0.0f < fVar28) goto LAB_0051fc4c;
LAB_0051f9c0:
                  fVar24 = fVar26 * fVar28 + fVar24;
                  fVar21 = fVar26 * (fVar27 / fVar22);
                  fVar29 = fVar26 * fVar28 + fVar29;
                  fVar23 = fVar21 + fVar23;
                  fVar21 = fVar21 + fVar25;
                }
                bVar20 = -1 < (int)((uint)*(byte *)(*piVar6 + 0x7d) << 0x1b);
                uVar7 = audio_uart_nema_stencil_save_52266e
                                  (0,(uint)bVar20,(uint)bVar20,(uint)bVar20);
                g2c_nema_vg_emit_verts_516b34
                          (fStack_118,fStack_114,(float)g2c_bits_to_float((uint)(uVar3)),(float)g2c_bits_to_float((uint)(((ulonglong)uVar3 >> 0x20))),
                           fVar24,fVar23,fVar29,fVar21);
                if ((int)((uint)*(byte *)(*piVar6 + 0x7d) << 0x1b) < 0) goto LAB_0051fcb0;
              }
              else {
                fVar25 = *(float *)(iVar11 + 0x1a0);
                fVar24 = *(float *)(iVar11 + 0x1a8);
                bVar20 = fVar25 == fVar24;
                if (bVar20) {
                  fVar24 = *(float *)(iVar11 + 0x1a4);
                  fVar26 = *(float *)(iVar11 + 0x1ac);
                }
                if (!bVar20 || (!bVar20 || fVar24 != fVar26)) goto LAB_0051f93c;
                fVar26 = *(float *)(iVar11 + 300) * 0.5f;
                uVar7 = (uint)(-1 < (int)((uint)*(byte *)(iVar11 + 0x7d) << 0x1b));
                uVar7 = audio_uart_nema_stencil_save_52266e(uVar7,uVar7,uVar7,0);
                g2c_nema_vg_emit_verts_516b34
                          (fVar21,fVar23,fVar26 + fVar21,fVar23,fVar26 + fVar25,fVar24,fVar25,fVar24
                          );
              }
              audio_uart_nema_stencil_restore_5226b2(uVar7);
            }
            else {
              if (cVar1 != '\x01') goto LAB_0051fe02;
              g2c_nema_vg_bezier_subdiv_51b140(fVar29,fVar23,fVar24,1);
            }
          }
        }
LAB_0051fcb0:
        iVar11 = *piVar6;
      } while (*(char *)(iVar11 + 0x1c1) == '\0');
      if ((((bVar2 & 0x6f) != 0) || (*(char *)(iVar11 + 0x1c2) != '\0')) ||
         (*(char *)(iVar10 + 0x2e5) == '\0')) {
        uVar13 = *(undefined4 *)(iVar10 + 0x364);
        uVar15 = *(undefined4 *)(iVar10 + 0x368);
        uVar17 = *(undefined4 *)(iVar10 + 0x36c);
        uVar18 = *(undefined4 *)(iVar10 + 0x370);
        uVar19 = *(undefined4 *)(iVar10 + 0x374);
        *(undefined4 *)(iVar11 + 0x164) = *(undefined4 *)(iVar10 + 0x360);
        *(undefined4 *)(iVar11 + 0x168) = uVar13;
        *(undefined4 *)(iVar11 + 0x16c) = uVar15;
        *(undefined4 *)(iVar11 + 0x170) = uVar17;
        *(undefined4 *)(iVar11 + 0x174) = uVar18;
        *(undefined4 *)(iVar11 + 0x178) = uVar19;
        uVar13 = *(undefined4 *)(iVar10 + 0x37c);
        uVar15 = *(undefined4 *)(iVar10 + 0x380);
        uVar17 = *(undefined4 *)(iVar10 + 900);
        uVar18 = *(undefined4 *)(iVar10 + 0x388);
        *(undefined4 *)(iVar11 + 0x17c) = *(undefined4 *)(iVar10 + 0x378);
        *(undefined4 *)(iVar11 + 0x180) = uVar13;
        *(undefined4 *)(iVar11 + 0x184) = uVar15;
        *(undefined4 *)(iVar11 + 0x188) = uVar17;
        *(undefined4 *)(iVar11 + 0x18c) = uVar18;
        iVar11 = *piVar6;
        uVar13 = *(undefined4 *)(iVar10 + 0x364);
        uVar15 = *(undefined4 *)(iVar10 + 0x368);
        uVar17 = *(undefined4 *)(iVar10 + 0x36c);
        uVar18 = *(undefined4 *)(iVar10 + 0x370);
        uVar19 = *(undefined4 *)(iVar10 + 0x374);
        *(undefined4 *)(iVar11 + 400) = *(undefined4 *)(iVar10 + 0x360);
        *(undefined4 *)(iVar11 + 0x194) = uVar13;
        *(undefined4 *)(iVar11 + 0x198) = uVar15;
        *(undefined4 *)(iVar11 + 0x19c) = uVar17;
        *(undefined4 *)(iVar11 + 0x1a0) = uVar18;
        *(undefined4 *)(iVar11 + 0x1a4) = uVar19;
        uVar13 = *(undefined4 *)(iVar10 + 0x37c);
        uVar15 = *(undefined4 *)(iVar10 + 0x380);
        uVar17 = *(undefined4 *)(iVar10 + 900);
        uVar18 = *(undefined4 *)(iVar10 + 0x388);
        *(undefined4 *)(iVar11 + 0x1a8) = *(undefined4 *)(iVar10 + 0x378);
        *(undefined4 *)(iVar11 + 0x1ac) = uVar13;
        *(undefined4 *)(iVar11 + 0x1b0) = uVar15;
        *(undefined4 *)(iVar11 + 0x1b4) = uVar17;
        *(undefined4 *)(iVar11 + 0x1b8) = uVar18;
        iVar11 = *piVar6;
        uVar13 = *(undefined4 *)(iVar10 + 0x364);
        uVar15 = *(undefined4 *)(iVar10 + 0x368);
        uVar17 = *(undefined4 *)(iVar10 + 0x36c);
        uVar18 = *(undefined4 *)(iVar10 + 0x370);
        uVar19 = *(undefined4 *)(iVar10 + 0x374);
        *(undefined4 *)(iVar11 + 0x138) = *(undefined4 *)(iVar10 + 0x360);
        *(undefined4 *)(iVar11 + 0x13c) = uVar13;
        *(undefined4 *)(iVar11 + 0x140) = uVar15;
        *(undefined4 *)(iVar11 + 0x144) = uVar17;
        *(undefined4 *)(iVar11 + 0x148) = uVar18;
        *(undefined4 *)(iVar11 + 0x14c) = uVar19;
        uVar13 = *(undefined4 *)(iVar10 + 0x37c);
        uVar15 = *(undefined4 *)(iVar10 + 0x380);
        uVar17 = *(undefined4 *)(iVar10 + 900);
        uVar18 = *(undefined4 *)(iVar10 + 0x388);
        *(undefined4 *)(iVar11 + 0x150) = *(undefined4 *)(iVar10 + 0x378);
        *(undefined4 *)(iVar11 + 0x154) = uVar13;
        *(undefined4 *)(iVar11 + 0x158) = uVar15;
        *(undefined4 *)(iVar11 + 0x15c) = uVar17;
        *(undefined4 *)(iVar11 + 0x160) = uVar18;
        iVar11 = *piVar6;
        bVar20 = *(int *)(iVar11 + 0x110) != 0;
        cVar1 = '\0';
        if (bVar20) {
          cVar1 = *(char *)(iVar11 + 0x2e0);
        }
        if (bVar20 && cVar1 != '\0') {
          if (cVar1 == '\x02') {
            fVar24 = *(float *)(iVar11 + 400);
            if (fVar24 == *(float *)(iVar11 + 0x198)) {
              fVar26 = *(float *)(iVar11 + 0x194);
              fVar23 = *(float *)(iVar11 + 0x19c);
              bVar20 = fVar26 != fVar23;
              if (!bVar20) {
                fVar23 = *(float *)(iVar11 + 0x1a0);
                fVar21 = *(float *)(iVar11 + 0x1a8);
              }
              if ((bVar20 || (bVar20 || fVar23 != fVar21)) ||
                 (fVar21 = *(float *)(iVar11 + 0x1a4), fVar21 != *(float *)(iVar11 + 0x1ac)))
              goto LAB_0051fd40;
              fVar29 = *(float *)(iVar11 + 300) * -0.5f;
              fStack_110 = fVar29 + fVar24;
              bVar20 = -1 < (int)((uint)*(byte *)(iVar11 + 0x7d) << 0x1b);
              fStack_118 = fVar24;
              fStack_114 = fVar26;
              fStack_10c = fVar26;
              uVar7 = audio_uart_nema_stencil_save_52266e((uint)bVar20,0,(uint)bVar20,(uint)bVar20);
              g2c_nema_vg_emit_verts_516b34
                        (fStack_110,fStack_10c,fStack_118,fStack_114,fVar23,fVar21,fVar29 + fVar23,
                         fVar21);
            }
            else {
LAB_0051fd40:
              fVar26 = *(float *)(iVar11 + 300) * 0.5f;
              bVar20 = false;
              uVar3 = *(undefined8 *)(iVar11 + 0x138);
              uVar4 = *(undefined8 *)(iVar11 + 0x150);
              fVar24 = *(float *)(iVar11 + 0x150);
              uVar5 = *(undefined8 *)(iVar11 + 0x138);
              fVar23 = *(float *)(iVar11 + 0x154);
              if ((*(float *)(iVar11 + 0x138) < *(float *)(iVar11 + 0x140)) &&
                 (fVar24 < *(float *)(iVar11 + 0x148))) {
                bVar20 = true;
              }
              fVar25 = (float)g2c_bits_to_float((uint)(uVar5));
              fVar28 = fVar24 - fVar25;
              fVar22 = (float)g2c_bits_to_float((uint)(((ulonglong)uVar5 >> 0x20)));
              fVar29 = fVar23 - fVar22;
              fVar21 = g2c_nema_vg_sqrt_524218(fVar28 * fVar28 + fVar29 * fVar29);
              fVar29 = -(fVar29 / fVar21);
              if (bVar20) {
                if (0.0f < fVar29) goto LAB_0051ff44;
LAB_0051fdb8:
                fVar24 = fVar26 * fVar29 + fVar24;
                fVar21 = fVar26 * (fVar28 / fVar21);
                fVar25 = fVar26 * fVar29 + fVar25;
                fVar23 = fVar21 + fVar23;
                fVar21 = fVar21 + fVar22;
              }
              else {
                if (0.0f < fVar29) goto LAB_0051fdb8;
LAB_0051ff44:
                fVar24 = fVar24 - fVar26 * fVar29;
                fVar21 = fVar26 * (fVar28 / fVar21);
                fVar25 = fVar25 - fVar26 * fVar29;
                fVar23 = fVar23 - fVar21;
                fVar21 = fVar22 - fVar21;
              }
              bVar20 = -1 < (int)((uint)*(byte *)(*piVar6 + 0x7d) << 0x1b);
              uVar7 = audio_uart_nema_stencil_save_52266e(0,(uint)bVar20,(uint)bVar20,(uint)bVar20);
              g2c_nema_vg_emit_verts_516b34
                        ((float)g2c_bits_to_float((uint)(uVar3)),(float)g2c_bits_to_float((uint)(((ulonglong)uVar3 >> 0x20))),(float)g2c_bits_to_float((uint)(uVar4)),
                         (float)g2c_bits_to_float((uint)(((ulonglong)uVar4 >> 0x20))),fVar24,fVar23,fVar25,fVar21);
              if ((int)((uint)*(byte *)(*piVar6 + 0x7d) << 0x1b) < 0) goto LAB_0051faf0;
            }
            audio_uart_nema_stencil_restore_5226b2(uVar7);
          }
          else {
            if (cVar1 != '\x01') {
LAB_0051fe02:
              *(undefined4 *)(iVar11 + 0x114) = 0;
              *(undefined4 *)(iVar11 + 0x118) = 0;
              audio_uart_nema_vg_set_error_51565c(0x800000);
              return 0x800000;
            }
            g2c_nema_vg_bezier_subdiv_51b140(fVar29,fVar23,fVar24,0);
          }
        }
      }
LAB_0051faf0:
    } while (((*(char *)(*piVar6 + 0x1c1) == '\0') || (((bVar2 & 0x6f) != 0 && (uVar14 != 10)))) ||
            ((*(char *)(iVar10 + 0x2e5) == '\0' && (*(int *)(iVar10 + 0x2f8) != 0))));
    uVar3 = *(undefined8 *)(iVar10 + 0x310);
    uVar4 = *(undefined8 *)(iVar10 + 0x318);
    *(undefined4 *)(iVar10 + 0x334) = *(undefined4 *)(iVar10 + 0x308);
    *(undefined4 *)(iVar10 + 0x338) = *(undefined4 *)(iVar10 + 0x30c);
    *(undefined4 *)(iVar10 + 0x33c) = *(undefined4 *)(iVar10 + 0x310);
    *(undefined4 *)(iVar10 + 0x340) = *(undefined4 *)(iVar10 + 0x314);
    *(undefined4 *)(iVar10 + 0x344) = *(undefined4 *)(iVar10 + 0x318);
    *(undefined4 *)(iVar10 + 0x348) = *(undefined4 *)(iVar10 + 0x31c);
    *(undefined4 *)(iVar10 + 0x34c) = *(undefined4 *)(iVar10 + 800);
    *(undefined4 *)(iVar10 + 0x350) = *(undefined4 *)(iVar10 + 0x324);
    *(undefined4 *)(iVar10 + 0x354) = *(undefined4 *)(iVar10 + 0x328);
    *(undefined4 *)(iVar10 + 0x358) = *(undefined4 *)(iVar10 + 0x32c);
    *(undefined4 *)(iVar10 + 0x35c) = *(undefined4 *)(iVar10 + 0x330);
    *(undefined4 *)(iVar10 + 0x308) = *(undefined4 *)(iVar10 + 0x360);
    *(undefined4 *)(iVar10 + 0x30c) = *(undefined4 *)(iVar10 + 0x364);
    *(undefined4 *)(iVar10 + 0x310) = *(undefined4 *)(iVar10 + 0x368);
    *(undefined4 *)(iVar10 + 0x314) = *(undefined4 *)(iVar10 + 0x36c);
    *(undefined4 *)(iVar10 + 0x318) = *(undefined4 *)(iVar10 + 0x370);
    *(undefined4 *)(iVar10 + 0x31c) = *(undefined4 *)(iVar10 + 0x374);
    *(undefined4 *)(iVar10 + 800) = *(undefined4 *)(iVar10 + 0x378);
    *(undefined4 *)(iVar10 + 0x324) = *(undefined4 *)(iVar10 + 0x37c);
    *(undefined4 *)(iVar10 + 0x328) = *(undefined4 *)(iVar10 + 0x380);
    *(undefined4 *)(iVar10 + 0x32c) = *(undefined4 *)(iVar10 + 900);
    *(undefined4 *)(iVar10 + 0x330) = *(undefined4 *)(iVar10 + 0x388);
    iVar11 = *piVar6;
  } while (*(int *)(iVar11 + 0x110) == 0);
  cVar1 = *(char *)(iVar11 + 0x2e2);
  uVar7 = 0;
  fVar28 = (float)g2c_bits_to_float((uint)(((ulonglong)*(undefined8 *)(iVar10 + 0x378) >> 0x20)));
  fVar25 = (float)g2c_bits_to_float((uint)(((ulonglong)uVar4 >> 0x20)));
  fVar21 = (float)g2c_bits_to_float((uint)(((ulonglong)*(undefined8 *)(iVar10 + 0x360) >> 0x20)));
  fVar23 = (float)g2c_bits_to_float((uint)(((ulonglong)uVar3 >> 0x20)));
  fVar22 = (float)g2c_bits_to_float((uint)(*(undefined8 *)(iVar10 + 0x378)));
  fVar29 = (float)g2c_bits_to_float((uint)(uVar4));
  fVar26 = (float)g2c_bits_to_float((uint)(*(undefined8 *)(iVar10 + 0x360)));
  fVar24 = (float)g2c_bits_to_float((uint)(uVar3));
  if ((cVar1 == '\0') || (*(int *)(iVar11 + 0x118) != 0)) {
    if (-1 < (int)((uint)*(byte *)(iVar11 + 0x7d) << 0x1b)) {
      uVar7 = audio_uart_nema_stencil_save_52266e(1,0,1,0);
    }
    g2c_nema_vg_emit_verts_516b34(fVar24,fVar23,fVar26,fVar21,fVar29,fVar25,fVar22,fVar28);
  }
  else {
    if (cVar1 == '\x02') {
      fStack_118 = g2c_bits_to_float((uint)((0x0u)));
      fStack_114 = g2c_bits_to_float((uint)((0x0u)));
      iVar11 = g2c_nema_vg_cubic_approx_522f50
                         (fVar24,fVar23,fVar29,fVar25,fVar26,fVar21,fVar22,fVar28,&fStack_118,
                          &fStack_114);
      if (iVar11 != 0) {
        iVar11 = *piVar6;
        fVar24 = audio_uart_float_sqrt_4397a8
                           (*(float *)(iVar11 + 0xec) * *(float *)(iVar11 + 0xec) +
                            *(float *)(iVar11 + 0xf0) * *(float *)(iVar11 + 0xf0));
        fVar23 = audio_uart_float_sqrt_4397a8
                           (*(float *)(iVar11 + 0xf8) * *(float *)(iVar11 + 0xf8) +
                            *(float *)(iVar11 + 0xfc) * *(float *)(iVar11 + 0xfc));
        fVar24 = ABS(fVar24);
        /* stock 0x51fefc vcmp |s16|,K; ittt lt; vcmplt 0x51ff0e |s0|,K; iteee lt; movlt r4,#0 / movge r4,#1
           (0x51ff18); reset test 0x51ffe4 cmp r4,#0. LT includes unordered, so r4 = either ordered >= (wave18). */
        bVar20 = (ABS(fVar23) >= (2.000000238418579f) || fVar24 >= (2.000000238418579f));
        if (bVar20) {
          g2c_nema_vg_set_flag_522622(1);
        }
        fVar24 = *(float *)(*piVar6 + 0x2d8) * 0.5f;
        if ((int)((uint)*(byte *)(*piVar6 + 0x7d) << 0x1b) < 0) {
          g2c_nema_vg_move_to_522fb4(fStack_118,fStack_114,fVar24);
        }
        else {
          g2c_nema_vg_line_to_523284(fStack_118,fStack_114,fVar24);
        }
        if (bVar20) {
          g2c_nema_vg_set_flag_522622(0);
        }
      }
      goto LAB_0051f7ee;
    }
    if (cVar1 != '\x01') {
      *(undefined4 *)(iVar11 + 0x114) = 0;
      *(undefined4 *)(iVar11 + 0x118) = 0;
      audio_uart_nema_vg_set_error_51565c(0x1000000);
      return 0x1000000;
    }
    if (*(char *)(iVar11 + 0x2e4) == '\0') {
      if ((*(float *)(iVar11 + 0x158) <= 0.0f) || (*(int *)(iVar11 + 0x128) != 1)) {
        fStack_dc = *(float *)(iVar11 + 0x164);
        fStack_d8 = *(float *)(iVar11 + 0x168);
        fStack_d4 = *(float *)(iVar11 + 0x16c);
        fStack_d0 = *(float *)(iVar11 + 0x170);
        fStack_cc = *(float *)(iVar11 + 0x174);
        fStack_c8 = *(float *)(iVar11 + 0x178);
        pfVar12 = (float *)(iVar11 + 400);
        fStack_c4 = *(float *)(iVar11 + 0x17c);
        fStack_c0 = *(float *)(iVar11 + 0x180);
        uStack_bc = *(undefined4 *)(iVar11 + 0x184);
        uStack_b8 = *(undefined4 *)(iVar11 + 0x188);
        uStack_b4 = *(undefined4 *)(iVar11 + 0x18c);
      }
      else {
        fStack_dc = *(float *)(iVar11 + 0x138);
        fStack_d8 = *(float *)(iVar11 + 0x13c);
        fStack_d4 = *(float *)(iVar11 + 0x140);
        fStack_d0 = *(float *)(iVar11 + 0x144);
        fStack_cc = *(float *)(iVar11 + 0x148);
        fStack_c8 = *(float *)(iVar11 + 0x14c);
        pfVar12 = (float *)(iVar11 + 400);
        fStack_c4 = *(float *)(iVar11 + 0x150);
        fStack_c0 = *(float *)(iVar11 + 0x154);
        uStack_bc = *(undefined4 *)(iVar11 + 0x158);
        uStack_b8 = *(undefined4 *)(iVar11 + 0x15c);
        uStack_b4 = *(undefined4 *)(iVar11 + 0x160);
      }
    }
    else {
      fStack_dc = *(float *)(iVar11 + 0x334);
      fStack_d8 = *(float *)(iVar11 + 0x338);
      fStack_d4 = *(float *)(iVar11 + 0x33c);
      fStack_d0 = *(float *)(iVar11 + 0x340);
      fStack_cc = *(float *)(iVar11 + 0x344);
      fStack_c8 = *(float *)(iVar11 + 0x348);
      pfVar12 = (float *)(iVar11 + 0x308);
      fStack_c4 = *(float *)(iVar11 + 0x34c);
      fStack_c0 = *(float *)(iVar11 + 0x350);
      uStack_bc = *(undefined4 *)(iVar11 + 0x354);
      uStack_b8 = *(undefined4 *)(iVar11 + 0x358);
      uStack_b4 = *(undefined4 *)(iVar11 + 0x35c);
    }
    fStack_108 = *pfVar12;
    fStack_104 = pfVar12[1];
    fStack_100 = pfVar12[2];
    fStack_fc = pfVar12[3];
    fStack_f8 = pfVar12[4];
    fStack_f4 = pfVar12[5];
    fStack_f0 = pfVar12[6];
    fStack_ec = pfVar12[7];
    fStack_e8 = pfVar12[8];
    fStack_e4 = pfVar12[9];
    fStack_e0 = pfVar12[10];
    iVar11 = g2c_nema_vg_near_5177a4(&fStack_108,&fStack_dc);
    if ((((iVar11 == 1) && (iVar11 = g2c_nema_vg_near_5177a4(&fStack_100,&fStack_d4), iVar11 == 1))
        && (iVar11 = g2c_nema_vg_near_5177a4(&fStack_f8,&fStack_cc), iVar11 == 1)) &&
       (iVar11 = g2c_nema_vg_near_5177a4(&fStack_f0,&fStack_c4), iVar11 == 1)) goto LAB_0051f7ee;
    iVar11 = g2c_nema_vg_near2_51785c(&fStack_108,&fStack_d4);
    if ((iVar11 != 0) || (iVar11 = g2c_nema_vg_near2_51785c(&fStack_dc,&fStack_108), iVar11 != 0))
    goto LAB_005200d8;
    iVar11 = g2c_nema_vg_near2_51785c(&fStack_108,&fStack_cc);
    fVar27 = fStack_cc;
    d = fStack_c8;
    g = fStack_f0;
    h = fStack_ec;
    h_00 = fStack_fc;
    g_00 = fStack_100;
    b_00 = fStack_d8;
    a_01 = fStack_dc;
    e = fStack_108;
    f = fStack_104;
    a_00 = fStack_d4;
    b = fStack_d0;
    if ((iVar11 == 0) &&
       (iVar11 = g2c_nema_vg_near2_51785c(&fStack_dc,&fStack_f0), fVar27 = fStack_cc, d = fStack_c8,
       g = fStack_f0, h = fStack_ec, h_00 = fStack_fc, g_00 = fStack_100, b_00 = fStack_d8,
       a_01 = fStack_dc, e = fStack_108, f = fStack_104, a_00 = fStack_d4, b = fStack_d0,
       iVar11 == 0)) {
      iVar11 = (uint)(fStack_c8 < fStack_d0) << 0x1f;
      if (fStack_104 < fStack_d0) {
        if (-1 < iVar11) goto LAB_005200d8;
      }
      else if (iVar11 < 0) {
LAB_005200d8:
        fVar27 = fStack_d4;
        d = fStack_d0;
        g = fStack_108;
        h = fStack_104;
        h_00 = fStack_f4;
        g_00 = fStack_f8;
        b_00 = fStack_c0;
        a_01 = fStack_c4;
        e = fStack_f0;
        f = fStack_ec;
        a_00 = fStack_cc;
        b = fStack_c8;
      }
    }
    fStack_110 = g2c_bits_to_float((uint)((0x0u)));
    fStack_10c = g2c_bits_to_float((uint)((0x0u)));
    fStack_118 = g2c_bits_to_float((uint)((0x0u)));
    fStack_114 = g2c_bits_to_float((uint)((0x0u)));
    iVar11 = g2c_nema_vg_cubic_approx_522f50(a_00,b,fVar27,d,e,f,g,h,&fStack_110,&fStack_10c);
    iVar8 = g2c_nema_vg_cubic_approx_522f50(a_01,b_00,a_00,b,e,f,g_00,h_00,&fStack_118,&fStack_114);
    fVar27 = g2c_nema_vg_sqrt_524218
                       ((fStack_118 - fStack_110) * (fStack_118 - fStack_110) +
                        (fStack_114 - fStack_10c) * (fStack_114 - fStack_10c));
    iVar9 = *piVar6;
    if ((*(float *)(iVar9 + 0x2dc) * *(float *)(iVar9 + 0x2d8) < fVar27) ||
       (iVar8 == 0 || iVar11 == 0)) {
      if (-1 < (int)((uint)*(byte *)(iVar9 + 0x7d) << 0x1b)) {
        uVar7 = audio_uart_nema_stencil_save_52266e(1,0,1,0);
      }
    }
    else {
      fVar24 = fStack_110;
      fVar23 = fStack_10c;
      fVar26 = a_00;
      fVar21 = b;
      fVar29 = fStack_118;
      fVar25 = fStack_114;
      fVar22 = e;
      fVar28 = f;
      if (-1 < (int)((uint)*(byte *)(iVar9 + 0x7d) << 0x1b)) {
        uVar7 = audio_uart_nema_stencil_save_52266e(0,1,1,0);
        fVar24 = fStack_110;
        fVar23 = fStack_10c;
        fVar29 = fStack_118;
        fVar25 = fStack_114;
      }
    }
    g2c_nema_vg_emit_verts_516b34(fVar24,fVar23,fVar26,fVar21,fVar29,fVar25,fVar22,fVar28);
  }
  if (-1 < (int)((uint)*(byte *)(*piVar6 + 0x7d) << 0x1b)) {
    audio_uart_nema_stencil_restore_5226b2(uVar7);
  }
  goto LAB_0051f7ee;
}
#undef fStack_118
#undef fStack_114
#undef fStack_110
#undef fStack_10c
#undef fStack_108
#undef fStack_104
#undef fStack_100
#undef fStack_fc
#undef fStack_f8
#undef fStack_f4
#undef fStack_f0
#undef fStack_ec
#undef fStack_e8
#undef fStack_e4
#undef fStack_e0
#undef fStack_dc
#undef fStack_d8
#undef fStack_d4
#undef fStack_d0
#undef fStack_cc
#undef fStack_c8
#undef fStack_c4
#undef fStack_c0
#undef uStack_bc
#undef uStack_b8
#undef uStack_b4
#undef uStack_b0
#undef cStack_af
#undef cStack_ae
#undef fStack_a4
#undef fStack_a0
#undef fStack_9c
#undef fStack_98
#undef fStack_94
#undef fStack_90
#undef fStack_8c
#undef fStack_88


  

/* ---- lifted 0x5202ec ---- */


uint audio_uart_ambiq_vector_shape_draw_5202ec(uint *path,int paint)

{
  /* Evidence (wave17): stock prologue 0x5202ec push 9 regs, 0x5202f0 sub sp,#4,
   * 0x5202f4 vpush d8-d15, 0x5202f8 sub sp,#104 -> sp = entry-0xd0, so the decompiler's
   * stack0xffffff30 is sp+0 of a 104-byte frame. Its pair-indexed (i*8) uses run into
   * afStack_c4 (= sp+0xc), so both now share one frame array (before, 3 scalars were indexed out of bounds). */
  uint g2c_sp_frame_5202ec[26] = {0};
  char cVar1;
  char cVar2;
  uint *puVar3;
  uint *puVar4;
  int *piVar5;
  undefined1 uVar6;
  uint uVar7;
  uint uVar8;
  undefined4 *puVar9;
  undefined4 *puVar10;
  float *pfVar11;
  uint uVar12;
  int iVar13;
  undefined4 uVar14;
  int iVar15;
  uint uVar16;
  float *pfVar17;
  float *pfVar18;
  int iVar19;
  float *pfVar20;
  byte bVar21;
  bool bVar22;
  byte bVar23;
  bool bVar24;
  /* Evidence (wave10): FPSCR scratch was declared here but never read; removed. */
  float fVar25;
  float fVar26;
  uint uVar27;
  uint uVar28;
  uint uVar29;
  float fVar30;
  float fVar31;
  float fVar32;
  float fVar33;
  float fVar34;
  float fVar35;
  float fVar36;
  float fVar37;
  float fVar38;
  float fVar39;
  float fVar40;
  float d;
  float f;
  float h;
  float *const afStack_c4 = (float *)&g2c_sp_frame_5202ec[3]; /* sp+0xc */
  /* Stock frame of 0x5202ec as one block: locals keep the entry-SP offsets Ghidra named them by
   * (X_Stack_NN at g2c_frame_5202ec[0xb0-0xNN]) so &local passed to callees spans its stock neighbours. */
  unsigned char g2c_frame_5202ec[0xb0] __attribute__((aligned(8)));
  typedef uint __attribute__((may_alias)) g2c_fa_uint;
#define uStack_b0 (*(g2c_fa_uint *)(void *)&g2c_frame_5202ec[0xb0-0xb0])
#define uStack_ac (*(g2c_fa_uint *)(void *)&g2c_frame_5202ec[0xb0-0xac])
  typedef float __attribute__((may_alias)) g2c_fa_float;
#define fStack_a8 (*(g2c_fa_float *)(void *)&g2c_frame_5202ec[0xb0-0xa8])
  typedef int __attribute__((may_alias)) g2c_fa_int;
#define iStack_a4 (*(g2c_fa_int *)(void *)&g2c_frame_5202ec[0xb0-0xa4])
#define fStack_a0 (*(g2c_fa_float *)(void *)&g2c_frame_5202ec[0xb0-0xa0])
  typedef undefined4 __attribute__((may_alias)) g2c_fa_undefined4;
#define uStack_9c (*(g2c_fa_undefined4 *)(void *)&g2c_frame_5202ec[0xb0-0x9c])
#define uStack_98 (*(g2c_fa_uint *)(void *)&g2c_frame_5202ec[0xb0-0x98])
#define uStack_94 (*(g2c_fa_undefined4 *)(void *)&g2c_frame_5202ec[0xb0-0x94])
#define uStack_90 (*(g2c_fa_undefined4 *)(void *)&g2c_frame_5202ec[0xb0-0x90])
#define uStack_8c (*(g2c_fa_undefined4 *)(void *)&g2c_frame_5202ec[0xb0-0x8c])
#define uStack_88 (*(g2c_fa_undefined4 *)(void *)&g2c_frame_5202ec[0xb0-0x88])
#define uStack_84 (*(g2c_fa_undefined4 *)(void *)&g2c_frame_5202ec[0xb0-0x84])
#define uStack_80 (*(g2c_fa_undefined4 *)(void *)&g2c_frame_5202ec[0xb0-0x80])
#define uStack_7c (*(g2c_fa_undefined4 *)(void *)&g2c_frame_5202ec[0xb0-0x7c])
#define uStack_78 (*(g2c_fa_uint *)(void *)&g2c_frame_5202ec[0xb0-0x78])
#define uStack_74 (*(g2c_fa_undefined4 *)(void *)&g2c_frame_5202ec[0xb0-0x74])
#define uStack_70 (*(g2c_fa_undefined4 *)(void *)&g2c_frame_5202ec[0xb0-0x70])
#define uStack_6c (*(g2c_fa_undefined4 *)(void *)&g2c_frame_5202ec[0xb0-0x6c])
  
  puVar9 = (undefined4 *)((byte *)&g2c_sp_frame_5202ec[0]);
  uVar16 = 0;
  uVar7 = audio_uart_nema_cl_get_bound_5144fa();
  piVar5 = (((int *)audio_uart_nema_context_cell));
  puVar4 = (((int *)&audio_uart_nema_vg_framebuffer_context_cell_20074f08));
  puVar3 = (((int *)&audio_uart_nema_vg_context_cell));
  if (uVar7 == 0) {
    uVar16 = 0x40;
  }
  if ((path == (uint *)0x0 || paint == 0) || (uVar7 = *(((int *)&audio_uart_nema_vg_context_cell)), uVar7 == 0)) {
    uVar16 = uVar16 | 1;
  }
  if (path[1] != 0) {
    uVar7 = *path;
  }
  if (path[1] == 0 || uVar7 == 0) {
    uVar16 = uVar16 | 0x10;
  }
  fVar25 = (float)g2c_bits_to_float((uint)(path[0x14]));
  bVar24 = 0.0f <= fVar25;
  if (bVar24) {
    fVar25 = (float)g2c_bits_to_float((uint)(path[0x15]));
  }
  if (!bVar24 || (!bVar24 || fVar25 < 0.0f)) {
    uVar16 = uVar16 | 0x400;
  }
  /* Evidence (wave10): stock 0x520352 vcmp s1,s0 + bge, 0x520364 vcmp + bmi,
   * 0x520372 vcmp + bge, 0x520380 vcmp + bpl. The FPSCR flag tests are these
   * compares (N==V is ge: false when unordered). uVar7 holds only NZCV
   * scratch, and later code masks it with 0xfffffff before it tests flags. */
  uVar7 = 0;
  if (((float)g2c_bits_to_float((uint)(path[6])) >= (32767.001953125f)) || ((float)g2c_bits_to_float((uint)(path[4])) < (-32768.0f)) ||
      ((float)g2c_bits_to_float((uint)(path[7])) >= (32767.001953125f)) || ((float)g2c_bits_to_float((uint)(path[5])) < (-32768.0f))) {
    uVar16 = uVar16 | 0x4000;
  }
  if ((*(char *)(*(((int *)&audio_uart_nema_vg_context_cell)) + 0x7c) == '\0') &&
     (fVar25 = *(float *)(*(((int *)&audio_uart_nema_vg_context_cell)) + 0x2d8),
     uVar7 = uVar7 & 0xfffffff | (uint)(fVar25 == 0.0f) << 0x1e | (uint)(0.0f <= fVar25) << 0x1d,
     bVar21 = (byte)(uVar7 >> 0x18), !(bool)(bVar21 >> 5 & 1) || (bool)(bVar21 >> 6))) {
    uVar16 = uVar16 | 0x200000;
  }
  uVar7 = uVar7 & 0xfffffff;
  if (*(float *)(paint + 0xd0) < 0.0f) {
    uVar16 = uVar16 | 0x400000;
  }
  uVar8 = *(((int *)&audio_uart_nema_vg_framebuffer_context_cell_20074f08));
  uVar12 = *(uint *)(uVar8 + 0x10);
  iVar15 = *(int *)(*(((int *)audio_uart_nema_context_cell)) + 0x3c);
  bVar24 = SBORROW4(uVar12,iVar15);
  iVar13 = uVar12 - iVar15;
  if (iVar15 <= (int)uVar12) {
    uVar8 = *(uint *)(uVar8 + 0x14);
    iVar13 = *(int *)(*(((int *)audio_uart_nema_context_cell)) + 0x40);
    bVar24 = SBORROW4(uVar8,iVar13);
    iVar13 = uVar8 - iVar13;
  }
  if ((iVar13 < 0 != bVar24) || ((uVar12 & 3) != 0 || (uVar8 & 3) != 0)) {
    uVar16 = uVar16 | 0x2000000;
  }
  audio_uart_nema_vg_set_error_51565c(uVar16);
  uVar8 = *puVar3;
  if (uVar16 != 0) {
    *(undefined4 *)(uVar8 + 0x114) = 0;
    *(undefined4 *)(uVar8 + 0x118) = 0;
    goto LAB_00520d64;
  }
  uVar16 = *(int *)(uVar8 + 0x84) << 1;
  if ((int)uVar16 < 0) {
    uVar12 = (uint)*(byte *)(paint + 0xd5);
    bVar24 = uVar12 == 0;
    if (bVar24) {
      uVar12 = *(uint *)(*piVar5 + 0xfc);
      uVar16 = *(uint *)(paint + 0xd8);
    }
    if (bVar24 && uVar12 == uVar16) {
      return 0;
    }
  }
  bVar21 = (byte)path[0x21];
  bVar23 = *(byte *)(uVar8 + 0x90);
  *(byte *)(uVar8 + 0x1bc) = bVar23 & 1 | bVar21 & 1;
  *(undefined1 *)(*puVar3 + 0x1be) = *(undefined1 *)(*puVar3 + 0x1bc);
  if ((bVar23 & 1) == 0) {
    if ((bVar21 & 1) == 0) {
      audio_uart_nema_matrix_identity_561810(*puVar3 + 0xec);
    }
    else {
      audio_uart_nema_matrix_copy_561830(*puVar3 + 0xec,(uint)(path + 0x18));
    }
  }
  else {
    audio_uart_nema_matrix_copy_561830(*puVar3 + 0xec,*puVar3 + 0xa4);
    if ((bVar21 & 1) != 0) {
      g2c_nema_vg_mat_mul_5619f2((float *)(*puVar3 + 0xec),(float *)(path + 0x18));
    }
  }
  if (*(char *)(*puVar3 + 0x7e) != '\0') {
    *(undefined1 *)(*puVar3 + 0x1bc) = 0;
  }
  uVar16 = *(uint *)(paint + 0xd8);
  uVar8 = *puVar3;
  *(uint *)(uVar8 + 0x124) = uVar16;
  fVar25 = *(float *)(paint + 0xd0);
  uVar7 = uVar7 & 0xfffffff;
  if (fVar25 < 1.0f) {
    uVar7 = uVar7 | (uint)(fVar25 == 0.0f) << 0x1e | (uint)(0.0f <= fVar25) << 0x1d;
    bVar21 = (byte)(uVar7 >> 0x18);
    if (!(bool)(bVar21 >> 5 & 1) || (bool)(bVar21 >> 6)) {
      audio_uart_nema_vg_set_error_51565c(0x400000);
      return 0x400000;
    }
    fVar31 = (float)VectorSignedToFloat(uVar16 >> 0x18,(byte)(uVar7 >> 0x16) & 3);
    *(uint *)(uVar8 + 0x124) = uVar16 & 0xffffff | (int)(fVar31 * fVar25 + 0.5f) << 0x18;
  }
  uVar16 = *(int *)(uVar8 + 0x84) << 5;
  if ((int)uVar16 < 0) {
    uVar12 = *(uint *)(uVar8 + 0x124);
    uVar16 = uVar12 >> 0x18;
    bVar21 = (byte)(uVar12 >> 0x18);
    *(uint *)(uVar8 + 0x124) =
         ((uint)((ulonglong)(uint)((int)(short)(ushort)bVar21 * (int)(short)((ushort)uVar12 & 0xff))
                 * (ulonglong)(0x80808081u) >> 0x20) & 0x7fff) >> 7 |
         (((uint)((ulonglong)
                  (uint)((int)(short)(ushort)bVar21 * (int)(short)(ushort)(byte)(uVar12 >> 8)) *
                  (ulonglong)(0x80808081u) >> 0x20) & 0x7fff) >> 7) << 8 |
         (((uint)((ulonglong)
                  (uint)((int)(short)(ushort)bVar21 * (int)(short)(ushort)(byte)(uVar12 >> 0x10)) *
                  (ulonglong)(0x80808081u) >> 0x20) & 0x7fff) >> 7) << 0x10 | uVar16 << 0x18;
  }
  cVar1 = *(char *)(uVar8 + 0x7c);
  fVar25 = *(float *)(uVar8 + 0x2d8);
  *(float *)(uVar8 + 300) = fVar25;
  *(float *)(uVar8 + 0x130) = fVar25;
  *(float *)(uVar8 + 0x134) = fVar25;
  fVar31 = fVar25;
  fVar26 = fVar25;
  if (cVar1 == '\0') {
    cVar2 = *(char *)(uVar8 + 0x1bc);
    if (cVar2 == '\0') {
      uVar16 = (uint)*(byte *)(uVar8 + 0x1be);
    }
    if (cVar2 != '\0' || uVar16 != 0) {
      if ((int)((uint)*(byte *)(uVar8 + 0x90) << 0x1e) < 0) {
        if (cVar2 != '\0') {
          fVar36 = audio_uart_float_sqrt_4397a8
                             (*(float *)(uVar8 + 0xec) * *(float *)(uVar8 + 0xec) +
                              *(float *)(uVar8 + 0xf0) * *(float *)(uVar8 + 0xf0));
          fVar32 = audio_uart_float_sqrt_4397a8
                             (*(float *)(uVar8 + 0xf8) * *(float *)(uVar8 + 0xf8) +
                              *(float *)(uVar8 + 0xfc) * *(float *)(uVar8 + 0xfc));
          *(float *)(uVar8 + 0x130) = fVar25 * (1.0f / ABS(fVar36));
          *(float *)(uVar8 + 0x134) = (1.0f / ABS(fVar32)) * fVar25;
        }
      }
      else {
        fVar31 = audio_uart_float_sqrt_4397a8
                           (*(float *)(uVar8 + 0xec) * *(float *)(uVar8 + 0xec) +
                            *(float *)(uVar8 + 0xf0) * *(float *)(uVar8 + 0xf0));
        fVar26 = audio_uart_float_sqrt_4397a8
                           (*(float *)(uVar8 + 0xf8) * *(float *)(uVar8 + 0xf8) +
                            *(float *)(uVar8 + 0xfc) * *(float *)(uVar8 + 0xfc));
        fVar31 = fVar25 * ABS(fVar31);
        fVar26 = fVar25 * ABS(fVar26);
        uVar7 = uVar7 & 0xfffffff;
        fVar25 = fVar26;
        if (fVar26 < fVar31) {
          fVar25 = fVar31;
        }
      }
    }
    uVar16 = uVar7 & 0xfffffff;
    fVar36 = ABS(fVar31);
    if (ABS(fVar26) <= ABS(fVar31)) {
      fVar36 = ABS(fVar26);
    }
    fVar32 = fVar31 - fVar26;
    if (fVar32 < 0.0f) {
      fVar32 = fVar26 - fVar31;
    }
    /* stock 0x520676 vcmp s0(min*1e-5),s1(|diff|); blt 0x520714 => GE path; 0x520684 vcmp s17,#1.0; bpl 0x520714
       => taken when ordered <. NZCV word dropped: only bits 0..27 (RMode) are read later (wave19). */
    uVar7 = uVar16;
    if ((fVar36 * (9.999999747378752e-06f) >= fVar32) && fVar31 < 1.0f) {
      uVar12 = *(uint *)(uVar8 + 0x124);
      fVar25 = (float)VectorUnsignedToFloat(uVar12 & 0xff,(byte)(uVar16 >> 0x16) & 3);
      uVar27 = VectorFloatToUnsigned(fVar25 * fVar31,3);
      fVar25 = (float)VectorUnsignedToFloat((uVar12 & 0xffff) >> 8,(byte)(uVar16 >> 0x16) & 3);
      uVar28 = VectorFloatToUnsigned(fVar25 * fVar31,3);
      fVar25 = (float)VectorUnsignedToFloat((uVar12 & 0xffffff) >> 0x10,(byte)(uVar16 >> 0x16) & 3);
      uVar29 = VectorFloatToUnsigned(fVar25 * fVar31,3);
      fVar25 = (float)VectorUnsignedToFloat(uVar12 >> 0x18,(byte)(uVar16 >> 0x16) & 3);
      iVar13 = VectorFloatToUnsigned(fVar25 * fVar31,3);
      fVar25 = 1.0f;
      fVar31 = 1.0f;
      *(uint *)(uVar8 + 0x124) =
           uVar27 & 0xff | (uVar28 & 0xff) << 8 | (uVar29 & 0xff) << 0x10 | iVar13 << 0x18;
      fVar26 = 1.0f;
    }
  }
  if ((*(char *)(uVar8 + 0x1bc) == '\0') && (*(char *)(uVar8 + 0x1be) != '\0')) {
    *(float *)(uVar8 + 300) = fVar25;
    *(float *)(uVar8 + 0x130) = fVar31;
    *(float *)(uVar8 + 0x134) = fVar26;
  }
  if (cVar1 == '\0') {
    /* stock 0x520736 vcmp s17,K(lit 0x520758); itt lt; vcmplt 0x520740 s18,K; blt 0x52075c.
       LT includes unordered => !(x >= K) (wave19). */
    uVar7 = uVar7 & 0xfffffff;
    bVar21 = !(fVar31 >= (1.0000001192092896f));
    if (bVar21) {
      bVar21 = !(fVar26 >= (1.0000001192092896f));
    }
    if (bVar21) goto LAB_0052075c;
    *(undefined4 *)(uVar8 + 0x110) = 1;
  }
  else {
LAB_0052075c:
    *(undefined4 *)(uVar8 + 0x110) = 0;
    *(undefined4 *)(uVar8 + 0x130) = 0x3f800000;
    *(undefined4 *)(uVar8 + 0x134) = 0x3f800000;
    *(undefined4 *)(uVar8 + 300) = 0x3f800000;
  }
  if (*(char *)(uVar8 + 0x2e0) == '\0') {
    *(byte *)(uVar8 + 0x1bf) = (byte)~(byte)(-(uint)(*(char *)(uVar8 + 0x2e1) == '\0') >> 0x18) >> 7
    ;
  }
  else {
    *(undefined1 *)(uVar8 + 0x1bf) = 1;
  }
  uVar16 = *puVar3;
  cVar1 = *(char *)(uVar16 + 0x7c);
  uVar8 = *(uint *)(uVar16 + 0x84);
  *(undefined4 *)(uVar16 + 0x114) = 0;
  bVar24 = cVar1 == '\0';
  if (bVar24) {
    cVar1 = *(char *)(paint + 0xd5);
  }
  if (bVar24 && cVar1 == '\0') {
    if (*(int *)(uVar16 + 0x110) != 0 && uVar8 != 1) {
      uVar12 = uVar8 & 0xffff;
      bVar24 = uVar12 != 0x501;
      if (!bVar24) {
        uVar12 = *(uint *)(uVar16 + 0x124) & 0xff000000;
      }
      if (bVar24 || uVar12 != 0xff000000) goto LAB_005207e4;
    }
    if (*(char *)(uVar16 + 0xa0) != '\x01') {
      *(undefined4 *)(uVar16 + 0x114) = 1;
    }
  }
LAB_005207e4:
  uVar12 = *(uint *)(uVar16 + 0x110);
  fVar25 = *(float *)(uVar16 + 300) * 0.5f;
  bVar24 = uVar12 == 1;
  if (bVar24) {
    uVar12 = (uint)*(byte *)(uVar16 + 0x1bf);
  }
  if (bVar24 && uVar12 == 1) {
    fVar25 = *(float *)(uVar16 + 300) + 1.0f + fVar25;
  }
  fVar26 = 4.0f;
  fVar31 = 1.0f;
  *(undefined4 *)(uVar16 + 0x1c4) = 0;
  *(undefined4 *)(uVar16 + 0x1c8) = 0;
  if (*(char *)(uVar16 + 0x1bc) != '\0') {
    fVar30 = audio_uart_float_sqrt_4397a8
                       (*(float *)(uVar16 + 0xec) * *(float *)(uVar16 + 0xec) +
                        *(float *)(uVar16 + 0xf0) * *(float *)(uVar16 + 0xf0));
    fVar26 = 4.0f;
    fVar32 = audio_uart_float_sqrt_4397a8
                       (*(float *)(uVar16 + 0xf8) * *(float *)(uVar16 + 0xf8) +
                        *(float *)(uVar16 + 0xfc) * *(float *)(uVar16 + 0xfc));
    fVar36 = (0.0010000001639127731f);
    fVar30 = ABS(fVar30);
    fVar32 = ABS(fVar32);
    *(float *)(uVar16 + 0x1c4) = fVar30;
    *(float *)(uVar16 + 0x1c8) = fVar32;
    /* stock 0x52086a vcmp |s21|,0.001f (lit 0x520bd8); itt ge; vdivge s20 = 4/s0. The decompile had dropped
       the compare (only !NAN remained); wave19 restores it from stock. */
    if (fVar30 >= fVar36) {
      fVar26 = 4.0f / fVar30;
    }
    /* stock 0x520884 vcmp s1,s2; itt ge; vdivge s19 = 4/s1 (wave19). */
    uVar7 = uVar7 & 0xfffffff;
    if (fVar32 >= fVar36) {
      fVar31 = 4.0f / fVar32;
    }
  }
  uVar12 = *puVar4;
  fVar26 = fVar26 + fVar25;
  fVar35 = (float)g2c_bits_to_float((uint)(path[4])) - fVar26;
  *(float *)(uVar12 + 0x1c) = fVar35;
  fVar31 = fVar31 + fVar25;
  fVar32 = (float)g2c_bits_to_float((uint)(path[5])) - fVar31;
  *(float *)(uVar12 + 0x20) = fVar32;
  fVar30 = (float)g2c_bits_to_float((uint)(path[4])) + (float)g2c_bits_to_float((uint)(path[0x14])) + fVar26;
  *(float *)(uVar12 + 0x24) = fVar30;
  fVar33 = (float)g2c_bits_to_float((uint)(path[5])) - fVar31;
  *(float *)(uVar12 + 0x28) = fVar33;
  fVar34 = (float)g2c_bits_to_float((uint)(path[4])) + (float)g2c_bits_to_float((uint)(path[0x14])) + fVar26;
  *(float *)(uVar12 + 0x2c) = fVar34;
  fVar25 = (float)g2c_bits_to_float((uint)(path[5])) + (float)g2c_bits_to_float((uint)(path[0x15])) + fVar31;
  *(float *)(uVar12 + 0x30) = fVar25;
  fVar26 = (float)g2c_bits_to_float((uint)(path[4])) - fVar26;
  *(float *)(uVar12 + 0x34) = fVar26;
  fVar36 = (float)g2c_bits_to_float((uint)(path[5]));
  fVar31 = fVar36 + (float)g2c_bits_to_float((uint)(path[0x15])) + fVar31;
  *(float *)(uVar12 + 0x38) = fVar31;
  if (*(char *)(uVar16 + 0x1bc) != '\0') {
    *(float *)(uVar12 + 0x1c) =
         *(float *)(uVar16 + 0xec) * fVar35 + *(float *)(uVar16 + 0xf0) * fVar32 +
         *(float *)(uVar16 + 0xf4);
    *(float *)(uVar12 + 0x20) =
         *(float *)(uVar16 + 0xf8) * fVar35 + *(float *)(uVar16 + 0xfc) * fVar32 +
         *(float *)(uVar16 + 0x100);
    fVar36 = *(float *)(uVar16 + 0xf4);
    *(float *)(uVar12 + 0x24) =
         *(float *)(uVar16 + 0xec) * fVar30 + *(float *)(uVar16 + 0xf0) * fVar33 + fVar36;
    *(float *)(uVar12 + 0x28) =
         *(float *)(uVar16 + 0xf8) * fVar30 + *(float *)(uVar16 + 0xfc) * fVar33 +
         *(float *)(uVar16 + 0x100);
    *(float *)(uVar12 + 0x2c) =
         *(float *)(uVar16 + 0xec) * fVar34 + *(float *)(uVar16 + 0xf0) * fVar25 +
         *(float *)(uVar16 + 0xf4);
    *(float *)(uVar12 + 0x30) =
         *(float *)(uVar16 + 0xf8) * fVar34 + *(float *)(uVar16 + 0xfc) * fVar25 +
         *(float *)(uVar16 + 0x100);
    *(float *)(uVar12 + 0x34) =
         *(float *)(uVar16 + 0xec) * fVar26 + *(float *)(uVar16 + 0xf0) * fVar31 +
         *(float *)(uVar16 + 0xf4);
    *(float *)(uVar12 + 0x38) =
         *(float *)(uVar16 + 0xf8) * fVar26 + *(float *)(uVar16 + 0xfc) * fVar31 +
         *(float *)(uVar16 + 0x100);
  }
  fVar26 = *(float *)(uVar12 + 0x1c);
  uVar27 = uVar7 & 0xfffffff | (uint)(fVar26 == 0.0f) << 0x1e | (uint)(0.0f <= fVar26) << 0x1d;
  bVar21 = (byte)(uVar27 >> 0x18);
  bVar24 = (bool)(bVar21 >> 6);
  bVar22 = (bool)(bVar21 >> 5 & 1);
  if (!bVar22 || bVar24) {
    uVar27 = uVar7 & 0xfffffff | (uint)(*(float *)(uVar12 + 0x24) == 0.0f) << 0x1e |
             (uint)(0.0f <= *(float *)(uVar12 + 0x24)) << 0x1d;
    bVar21 = (byte)(uVar27 >> 0x18);
    bVar24 = (bool)(bVar21 >> 6);
    bVar22 = (bool)(bVar21 >> 5 & 1);
  }
  if (!bVar22 || bVar24) {
    uVar7 = uVar27 & 0xfffffff;
    uVar27 = uVar7 | (uint)(*(float *)(uVar12 + 0x2c) == 0.0f) << 0x1e |
             (uint)(0.0f <= *(float *)(uVar12 + 0x2c)) << 0x1d;
    bVar21 = (byte)(uVar27 >> 0x18);
    bVar24 = (bool)(bVar21 >> 6);
    bVar22 = (bool)(bVar21 >> 5 & 1);
    if (!bVar22 || bVar24) {
      uVar27 = uVar7 | (uint)(*(float *)(uVar12 + 0x34) == 0.0f) << 0x1e |
               (uint)(0.0f <= *(float *)(uVar12 + 0x34)) << 0x1d;
      bVar21 = (byte)(uVar27 >> 0x18);
      bVar24 = (bool)(bVar21 >> 6);
      bVar22 = (bool)(bVar21 >> 5 & 1);
    }
    if (!bVar22 || bVar24) {
      return 0;
    }
  }
  fVar32 = *(float *)(uVar12 + 0x20);
  uVar7 = uVar27 & 0xfffffff | (uint)(fVar32 == 0.0f) << 0x1e | (uint)(0.0f <= fVar32) << 0x1d;
  bVar21 = (byte)(uVar7 >> 0x18);
  bVar24 = (bool)(bVar21 >> 6);
  bVar22 = (bool)(bVar21 >> 5 & 1);
  if (!bVar22 || bVar24) {
    uVar7 = uVar27 & 0xfffffff | (uint)(*(float *)(uVar12 + 0x28) == 0.0f) << 0x1e |
            (uint)(0.0f <= *(float *)(uVar12 + 0x28)) << 0x1d;
    bVar21 = (byte)(uVar7 >> 0x18);
    bVar24 = (bool)(bVar21 >> 6);
    bVar22 = (bool)(bVar21 >> 5 & 1);
  }
  if (!bVar22 || bVar24) {
    uVar27 = uVar7 & 0xfffffff;
    uVar7 = uVar27 | (uint)(*(float *)(uVar12 + 0x30) == 0.0f) << 0x1e |
            (uint)(0.0f <= *(float *)(uVar12 + 0x30)) << 0x1d;
    bVar21 = (byte)(uVar7 >> 0x18);
    bVar24 = (bool)(bVar21 >> 6);
    bVar22 = (bool)(bVar21 >> 5 & 1);
    if (!bVar22 || bVar24) {
      uVar7 = uVar27 | (uint)(*(float *)(uVar12 + 0x38) == 0.0f) << 0x1e |
              (uint)(0.0f <= *(float *)(uVar12 + 0x38)) << 0x1d;
      bVar21 = (byte)(uVar7 >> 0x18);
      bVar24 = (bool)(bVar21 >> 6);
      bVar22 = (bool)(bVar21 >> 5 & 1);
    }
    if (!bVar22 || bVar24) {
      return 0;
    }
  }
  fVar30 = (float)VectorSignedToFloat(*(undefined4 *)(uVar12 + 0x10),(byte)(uVar7 >> 0x16) & 3);
  uVar27 = uVar7 & 0xfffffff | (uint)(fVar26 < fVar30) << 0x1f;
  /* stock 0x520a84..0x520ab6: vcmp/ittt ge/vcmpge chain vs vcvt [r1+0x10]; blt 0x520aba, bge.w 0x520d0a (return 0).
     GE is ordered >= (wave18; replaces NAN carrier). */
  bVar22 = (fVar26 >= fVar30); /* stock GE */
  if (bVar22) {
    uVar27 = uVar7 & 0xfffffff | (uint)(*(float *)(uVar12 + 0x24) < fVar30) << 0x1f;
    bVar22 = (*(float *)(uVar12 + 0x24) >= fVar30); /* stock GE */
  }
  if (bVar22) {
    fVar25 = *(float *)(uVar12 + 0x2c);
    uVar7 = uVar27 & 0xfffffff;
    uVar27 = uVar7 | (uint)(fVar25 < fVar30) << 0x1f;
    bVar22 = (fVar25 >= fVar30); /* stock GE */
    if (bVar22) {
      uVar27 = uVar7 | (uint)(*(float *)(uVar12 + 0x34) < fVar30) << 0x1f;
      bVar22 = (*(float *)(uVar12 + 0x34) >= fVar30); /* stock GE */
    }
    if (bVar22) {
      return 0;
    }
  }
  fVar30 = (float)VectorSignedToFloat(*(undefined4 *)(uVar12 + 0x14),(byte)(uVar27 >> 0x16) & 3);
  /* stock 0x520ac2 vcmp s1,[vcvt r1+0x14]; ittt ge; vcmpge 0x520ad0 [r1+0x28]; blt 0x520af8;
     0x520ade vcmp [r1+0x30]; ittt ge; vcmpge 0x520aec [r1+0x38]; bge.w 0x520d0a (return 0).
     GE is ordered >= (wave19). NZCV word dropped; uVar7 is only read masked & 0xfffffff below. */
  uVar7 = uVar27 & 0xfffffff;
  bVar21 = (fVar32 >= fVar30);
  if (bVar21) {
    bVar21 = (*(float *)(uVar12 + 0x28) >= fVar30);
  }
  if (bVar21) {
    fVar25 = *(float *)(uVar12 + 0x30);
    uVar27 = uVar7;
    bVar21 = (fVar25 >= fVar30);
    if (bVar21) {
      bVar21 = (*(float *)(uVar12 + 0x38) >= fVar30);
    }
    if (bVar21) {
      return 0;
    }
  }
  if (*(char *)(uVar16 + 0x7e) == '\0') {
    uVar27 = uVar7 & 0xfffffff | (uint)(fVar26 < (1535.0001220703125f)) << 0x1f;
    /* stock 0x520b00..0x520b6a: 8 vcmp vs 1535.0001f (lit 0x520c68), each pair it lt / vcmplt, bge 0x520bc0.
       LT includes unordered => each test is !(x >= K) (wave18; replaces NAN carrier). */
    bVar22 = !(fVar26 >= (1535.0001220703125f)); /* stock LT */
    if (bVar22) {
      uVar27 = uVar7 & 0xfffffff | (uint)(fVar32 < (1535.0001220703125f)) << 0x1f;
      bVar22 = !(fVar32 >= (1535.0001220703125f)); /* stock LT */
    }
    if (bVar22) {
      fVar30 = *(float *)(uVar12 + 0x24);
      uVar7 = uVar27 & 0xfffffff | (uint)(fVar30 < (1535.0001220703125f)) << 0x1f;
      bVar22 = !(fVar30 >= (1535.0001220703125f)); /* stock LT */
      if (bVar22) {
        fVar25 = *(float *)(uVar12 + 0x28);
        uVar7 = uVar27 & 0xfffffff | (uint)(fVar25 < (1535.0001220703125f)) << 0x1f;
        bVar22 = !(fVar25 >= (1535.0001220703125f)); /* stock LT */
      }
      if (bVar22) {
        fVar33 = *(float *)(uVar12 + 0x2c);
        uVar27 = uVar7 & 0xfffffff | (uint)(fVar33 < (1535.0001220703125f)) << 0x1f;
        bVar22 = !(fVar33 >= (1535.0001220703125f)); /* stock LT */
        if (bVar22) {
          fVar31 = *(float *)(uVar12 + 0x30);
          uVar27 = uVar7 & 0xfffffff | (uint)(fVar31 < (1535.0001220703125f)) << 0x1f;
          bVar22 = !(fVar31 >= (1535.0001220703125f)); /* stock LT */
        }
        if (bVar22) {
          fVar34 = *(float *)(uVar12 + 0x34);
          uVar28 = uVar27 & 0xfffffff | (uint)(fVar34 < (1535.0001220703125f)) << 0x1f;
          bVar22 = !(fVar34 >= (1535.0001220703125f)); /* stock LT */
          if (bVar22) {
            fVar36 = *(float *)(uVar12 + 0x38);
            uVar28 = uVar27 & 0xfffffff | (uint)(fVar36 < (1535.0001220703125f)) << 0x1f;
            bVar22 = !(fVar36 >= (1535.0001220703125f)); /* stock LT */
          }
          if ((((bVar22) &&
               ((-511.0f) <= fVar26 && ((-511.0f) <= fVar26 && (-511.0f) <= fVar32))) &&
              ((-511.0f) <= fVar30 && ((-511.0f) <= fVar30 && (-511.0f) <= fVar25))) &&
             ((-511.0f) <= fVar33 && ((-511.0f) <= fVar33 && (-511.0f) <= fVar31))) {
            uVar7 = uVar28 & 0xfffffff | (uint)(fVar34 < (-511.0f)) << 0x1f;
            bVar21 = -(char)((int)uVar7 >> 0x1f);
            if (bVar21 == 0) {
              uVar7 = uVar28 & 0xfffffff | (uint)(fVar36 < (-511.0f)) << 0x1f;
              bVar21 = (byte)(uVar7 >> 0x1f);
            }
            if (bVar21 == 0) goto LAB_00520bf4;
          }
        }
      }
    }
    if (-1 < (int)((uint)*(byte *)(uVar16 + 0x90) << 0x1d)) {
      audio_uart_nema_vg_set_error_51565c(0x4000);
      return 0x4000;
    }
    uVar16 = g2c_nema_vg_paint_apply_567230((uint)path,paint);
    if (uVar16 == 0) {
      return 0;
    }
LAB_00520c18:
    uVar7 = *puVar3;
    *(undefined4 *)(uVar7 + 0x114) = 0;
    *(undefined4 *)(uVar7 + 0x118) = 0;
    audio_uart_nema_vg_set_error_51565c(uVar16);
    return uVar16;
  }
LAB_00520bf4:
  if (*(int *)(uVar16 + 0x114) == 1) {
    if (((0x4000ffffu) & uVar8) == 0x501) {
      puVar9 = (undefined4 *)audio_uart_nema_cl_get_space_514aec(4);
      if (puVar9 == (undefined4 *)0x0) {
        uVar16 = 0x200;
        goto LAB_00520c18;
      }
      *puVar9 = 0x1d0;
      puVar9[1] = 1;
      uVar14 = (0x941fb414u);
      puVar9[2] = 0x11c;
      puVar9[3] = uVar14;
      puVar9[4] = 300;
      uVar14 = *(undefined4 *)(*puVar3 + 0x124);
      puVar9[6] = 0x118;
      puVar9[5] = uVar14;
      puVar9[7] = 0x90000000;
    }
    else {
      audio_uart_display_graphics_blend_513924(uVar8 | 0x1000000,0,0xffffffff,0xffffffff);
      display_driver_nema_select_522a16(*(uint *)(*puVar3 + 0x124));
    }
    g2c_nema_vg_paint_setup_516c82((uint *)(*puVar3 + 0xec));
    if (*(char *)(*puVar3 + 0x2e4) == '\0') {
      if (*(int *)(*puVar3 + 0x110) == 0) {
        uVar16 = g2c_nema_vg_tess_stroke_5171f8(path);
      }
      else {
        uVar16 = g2c_nema_vg_draw_fill_51d2e0(path);
      }
    }
    else {
      uVar16 = g2c_nema_vg_draw_stroke_51f798(path);
    }
    if (uVar16 != 0) {
      uVar7 = *puVar3;
      *(undefined4 *)(uVar7 + 0x114) = 0;
      *(undefined4 *)(uVar7 + 0x118) = 0;
      audio_uart_nema_vg_set_error_51565c(uVar16);
      goto LAB_00520c18;
    }
    goto LAB_00520ce6;
  }
  iVar13 = *piVar5;
  if (*(char *)(iVar13 + 8) == '\x01') {
    iVar13 = *(int *)(iVar13 + 0xc);
    if (iVar13 == 0x40000000) {
      audio_uart_nema_child_52262e(0);
      uVar6 = 3;
    }
    else {
      if (iVar13 != -0x40000000) goto LAB_00520d48;
      audio_uart_nema_child_52264e(0);
      uVar6 = 4;
    }
    *(undefined1 *)(*puVar3 + 0x7f) = uVar6;
  }
LAB_00520d48:
  uVar16 = *puVar4;
  if (*(int *)(uVar16 + 8) == 0) {
    audio_uart_nema_vg_set_error_51565c(2);
    uVar16 = 2;
  }
  else {
    uVar14 = 0x80808080;
    audio_uart_nema_bind_tex_4b1298
              (3,*(uint *)(uVar16 + 0xc),*(uint *)(uVar16 + 0x10),*(uint *)(uVar16 + 0x14),8,
               *(uint *)(uVar16 + 0x10),0);
    uStack_ac = *(uint *)(*puVar4 + 0x10);
    uStack_b0 = *(uint *)(*puVar4 + 0x14);
    uVar16 = uStack_ac + 3 >> 2;
    if (*(char *)(*puVar3 + 0x7c) == '\0') {
      uVar14 = 0;
    }
    puVar10 = (undefined4 *)audio_uart_nema_cl_get_space_514aec(8);
    if (puVar10 == (undefined4 *)0x0) {
      uVar16 = *puVar3;
      *(undefined4 *)(uVar16 + 0x114) = 0;
      *(undefined4 *)(uVar16 + 0x118) = 0;
      audio_uart_nema_vg_set_error_51565c(0x200);
      uVar16 = 0x200;
    }
    else {
      *puVar10 = 0x34;
      puVar10[1] = (uVar16 & 0x3fff) << 2 | 0x1000000;
      puVar10[2] = 0x38;
      puVar10[6] = 0x11c;
      puVar10[3] = uVar16 | uStack_b0 << 0x10;
      puVar10[5] = 1;
      puVar10[7] = (0x1c1f0015u);
      puVar10[10] = 0x110;
      puVar10[4] = 0x1d0;
      puVar10[8] = 300;
      puVar10[9] = uVar14;
      puVar10[0xb] = 0;
      puVar10[0xc] = 0x114;
      puVar10[0xe] = 0x118;
      puVar10[0xd] = uVar16 & 0xffff | uStack_b0 << 0x10;
      puVar10[0xf] = 0x90000000;
      uStack_98 = audio_uart_nema_stencil_restore_5226b2(0);
      memset((uint)&fStack_a8,0,0x10);
      uVar16 = *puVar4;
      fVar25 = *(float *)(uVar16 + 0x1c);
      fVar31 = *(float *)(uVar16 + 0x20);
      fVar26 = *(float *)(uVar16 + 0x24);
      afStack_c4[0] = *(float *)(uVar16 + 0x28);
      afStack_c4[1] = *(float *)(uVar16 + 0x2c);
      afStack_c4[2] = *(float *)(uVar16 + 0x30);
      afStack_c4[3] = *(float *)(uVar16 + 0x34);
      iVar13 = 0;
      uVar7 = uVar7 & 0xfffffff;
      afStack_c4[4] = *(float *)(uVar16 + 0x38);
      if (fVar26 < fVar25) {
LAB_00520ef2:
        pfVar11 = (float *)((byte *)&g2c_sp_frame_5202ec[2]);
        iVar13 = 1;
        uVar8 = uVar7;
      }
      else {
        fVar36 = ABS(fVar25);
        if (ABS(fVar26) <= ABS(fVar25)) {
          fVar36 = ABS(fVar26);
        }
        fVar32 = fVar25 - fVar26;
        if (fVar32 < 0.0f) {
          fVar32 = fVar26 - fVar25;
        }
        uVar8 = uVar7 | (uint)(fVar36 * (9.999999747378752e-06f) < fVar32) << 0x1f;
        pfVar11 = (float *)((byte *)&g2c_sp_frame_5202ec[0]);
        if ((/* stock 0x520ede vcmp.f32 s3, s0; blt 0x520ef6 => GE taken; 0x520ee8 vcmp; bpl 0x520ef6 at 0x520ef0 falls to 0x520ef2 (wave19, label-verified) */ (fVar36 * (9.999999747378752e-06f) >= fVar32)) &&
           (pfVar11 = (float *)((byte *)&g2c_sp_frame_5202ec[0]), uVar8 = uVar7, afStack_c4[0] < fVar31))
        goto LAB_00520ef2;
      }
      fVar36 = *pfVar11;
      uVar8 = uVar8 & 0xfffffff;
      if (afStack_c4[1] < fVar36) {
LAB_00520f5a:
        pfVar11 = afStack_c4 + 1;
        iVar13 = 2;
        uVar7 = uVar8;
      }
      else {
        fVar32 = fVar36;
        if (fVar36 < 0.0f) {
          fVar32 = -fVar36;
        }
        fVar30 = ABS(afStack_c4[1]);
        if (fVar32 < ABS(afStack_c4[1])) {
          fVar30 = fVar32;
        }
        fVar32 = fVar36 - afStack_c4[1];
        if (fVar32 < 0.0f) {
          fVar32 = afStack_c4[1] - fVar36;
        }
        uVar7 = uVar8 | (uint)(fVar30 * (9.999999747378752e-06f) < fVar32) << 0x1f;
        if ((/* stock 0x520f42 vcmp.f32 s2, s0; blt 0x520f5e => GE taken; 0x520f50 vcmp; bpl 0x520f5e at 0x520f58 falls to 0x520f5a (wave19, label-verified) */ (fVar30 * (9.999999747378752e-06f) >= fVar32)) &&
           (uVar7 = uVar8, *(float *)(uVar16 + 0x30) < pfVar11[1])) goto LAB_00520f5a;
      }
      fVar36 = *pfVar11;
      uVar7 = uVar7 & 0xfffffff;
      if (afStack_c4[3] < fVar36) {
LAB_00520fc2:
        iVar13 = 3;
        uVar8 = uVar7;
      }
      else {
        fVar32 = fVar36;
        if (fVar36 < 0.0f) {
          fVar32 = -fVar36;
        }
        if (ABS(afStack_c4[3]) <= fVar32) {
          fVar32 = ABS(afStack_c4[3]);
        }
        fVar30 = fVar36 - afStack_c4[3];
        if (fVar30 < 0.0f) {
          fVar30 = afStack_c4[3] - fVar36;
        }
        uVar8 = uVar7 | (uint)(fVar32 * (9.999999747378752e-06f) < fVar30) << 0x1f;
        if ((/* stock 0x520faa vcmp.f32 s0, s3; blt 0x520fc4 => GE taken; 0x520fb8 vcmp; bpl 0x520fc4 at 0x520fc0 falls to 0x520fc2 (wave19, label-verified) */ (fVar32 * (9.999999747378752e-06f) >= fVar30)) &&
           (uVar8 = uVar7, *(float *)(uVar16 + 0x38) < pfVar11[1])) goto LAB_00520fc2;
      }
      iVar19 = (iVar13 + 1U) - (iVar13 + 1U & 0xfffffffc);
      iVar15 = (iVar13 + 3U) - (iVar13 + 3U & 0xfffffffc);
      uVar8 = uVar8 & 0xfffffff;
      if (0.0f < (*(float *)(((byte *)&g2c_sp_frame_5202ec[0]) + iVar15 * 8) -
                *(float *)(((byte *)&g2c_sp_frame_5202ec[0]) + iVar13 * 8)) *
                (*(float *)(((byte *)&g2c_sp_frame_5202ec[1]) + iVar19 * 8) -
                *(float *)(((byte *)&g2c_sp_frame_5202ec[1]) + iVar13 * 8)) +
                (*(float *)(((byte *)&g2c_sp_frame_5202ec[0]) + iVar13 * 8) -
                *(float *)(((byte *)&g2c_sp_frame_5202ec[0]) + iVar19 * 8)) *
                (*(float *)(((byte *)&g2c_sp_frame_5202ec[1]) + iVar15 * 8) -
                *(float *)(((byte *)&g2c_sp_frame_5202ec[1]) + iVar13 * 8))) {
        fVar25 = *(float *)(uVar16 + 0x34);
        fVar31 = *(float *)(uVar16 + 0x38);
        fVar26 = *(float *)(uVar16 + 0x2c);
        afStack_c4[0] = *(float *)(uVar16 + 0x30);
        afStack_c4[1] = *(float *)(uVar16 + 0x24);
        afStack_c4[2] = *(float *)(uVar16 + 0x28);
        afStack_c4[3] = *(float *)(uVar16 + 0x1c);
        afStack_c4[4] = *(float *)(uVar16 + 0x20);
      }
      if (afStack_c4[0] < fVar31) {
LAB_005210f6:
        pfVar11 = (float *)((byte *)&g2c_sp_frame_5202ec[2]);
        fStack_a8 = 1.4013e-45f;
        uVar16 = uVar8;
      }
      else {
        fVar36 = ABS(fVar31);
        if (ABS(afStack_c4[0]) <= ABS(fVar31)) {
          fVar36 = ABS(afStack_c4[0]);
        }
        fVar32 = fVar31 - afStack_c4[0];
        if (fVar32 < 0.0f) {
          fVar32 = afStack_c4[0] - fVar31;
        }
        uVar16 = uVar8 | (uint)(fVar36 * (9.999999747378752e-06f) < fVar32) << 0x1f;
        pfVar11 = (float *)((byte *)&g2c_sp_frame_5202ec[0]);
        if ((/* stock 0x5210da vcmp.f32 s2, s0; blt 0x5210fc => GE taken; 0x5210ec vcmp; bpl 0x5210fc at 0x5210f4 falls to 0x5210f6 (wave19, label-verified) */ (fVar36 * (9.999999747378752e-06f) >= fVar32)) &&
           (pfVar11 = (float *)((byte *)&g2c_sp_frame_5202ec[0]), uVar16 = uVar8, fVar25 < fVar26))
        goto LAB_005210f6;
      }
      fVar36 = pfVar11[1];
      uVar16 = uVar16 & 0xfffffff;
      if (afStack_c4[2] < fVar36) {
LAB_0052115e:
        pfVar11 = afStack_c4 + 1;
        fStack_a8 = 2.8026e-45f;
        uVar7 = uVar16;
      }
      else {
        fVar32 = ABS(afStack_c4[2]);
        if (ABS(pfVar11[1]) < ABS(afStack_c4[2])) {
          fVar32 = ABS(pfVar11[1]);
        }
        fVar30 = fVar36 - afStack_c4[2];
        if (fVar30 < 0.0f) {
          fVar30 = afStack_c4[2] - fVar36;
        }
        uVar7 = uVar16 | (uint)(fVar32 * (9.999999747378752e-06f) < fVar30) << 0x1f;
        if ((/* stock 0x521142 vcmp.f32 s3, s0; blt 0x521164 => GE taken; 0x521154 vcmp; bpl 0x521164 at 0x52115c falls to 0x52115e (wave19, label-verified) */ (fVar32 * (9.999999747378752e-06f) >= fVar30)) &&
           (uVar7 = uVar16, *pfVar11 < afStack_c4[1])) goto LAB_0052115e;
      }
      fVar36 = pfVar11[1];
      uVar7 = uVar7 & 0xfffffff;
      if (afStack_c4[4] < fVar36) {
LAB_005211c6:
        pfVar11 = afStack_c4 + 3;
        fStack_a8 = 4.2039e-45f;
        uVar16 = uVar7;
      }
      else {
        fVar32 = ABS(pfVar11[1]);
        if (ABS(afStack_c4[4]) <= ABS(pfVar11[1])) {
          fVar32 = ABS(afStack_c4[4]);
        }
        fVar30 = fVar36 - afStack_c4[4];
        if (fVar30 < 0.0f) {
          fVar30 = afStack_c4[4] - fVar36;
        }
        uVar16 = uVar7 | (uint)(fVar32 * (9.999999747378752e-06f) < fVar30) << 0x1f;
        if ((/* stock 0x5211aa vcmp.f32 s0, s7; blt 0x5211cc => GE taken; 0x5211bc vcmp; bpl 0x5211cc at 0x5211c4 falls to 0x5211c6 (wave19, label-verified) */ (fVar32 * (9.999999747378752e-06f) >= fVar30)) &&
           (uVar16 = uVar7, *pfVar11 < afStack_c4[3])) goto LAB_005211c6;
      }
      uVar16 = uVar16 & 0xfffffff;
      if (afStack_c4[0] < fVar31) {
LAB_0052122a:
        pfVar18 = (float *)((byte *)&g2c_sp_frame_5202ec[2]);
        uStack_9c = 1;
        uVar7 = uVar16;
      }
      else {
        fVar36 = ABS(fVar31);
        if (ABS(afStack_c4[0]) <= ABS(fVar31)) {
          fVar36 = ABS(afStack_c4[0]);
        }
        fVar32 = fVar31 - afStack_c4[0];
        if (fVar32 < 0.0f) {
          fVar32 = afStack_c4[0] - fVar31;
        }
        uVar7 = uVar16 | (uint)(fVar36 * (9.999999747378752e-06f) < fVar32) << 0x1f;
        pfVar18 = (float *)((byte *)&g2c_sp_frame_5202ec[0]);
        if ((/* stock 0x52120e vcmp.f32 s6, s0; blt 0x521234 => GE taken; 0x521220 vcmp; bpl 0x521234 at 0x521228 falls to 0x52122a (wave19, label-verified) */ (fVar36 * (9.999999747378752e-06f) >= fVar32)) &&
           (pfVar18 = (float *)((byte *)&g2c_sp_frame_5202ec[0]), uVar7 = uVar16, fVar26 < fVar25))
        goto LAB_0052122a;
      }
      fVar36 = pfVar18[1];
      uVar7 = uVar7 & 0xfffffff;
      if (afStack_c4[2] < fVar36) {
LAB_00521292:
        pfVar18 = afStack_c4 + 1;
        uStack_9c = 2;
        uVar16 = uVar7;
      }
      else {
        fVar32 = ABS(afStack_c4[2]);
        if (ABS(pfVar18[1]) < ABS(afStack_c4[2])) {
          fVar32 = ABS(pfVar18[1]);
        }
        fVar30 = fVar36 - afStack_c4[2];
        if (fVar30 < 0.0f) {
          fVar30 = afStack_c4[2] - fVar36;
        }
        uVar16 = uVar7 | (uint)(fVar32 * (9.999999747378752e-06f) < fVar30) << 0x1f;
        if ((/* stock 0x521276 vcmp.f32 s6, s0; blt 0x52129c => GE taken; 0x521288 vcmp; bpl 0x52129c at 0x521290 falls to 0x521292 (wave19, label-verified) */ (fVar32 * (9.999999747378752e-06f) >= fVar30)) &&
           (uVar16 = uVar7, afStack_c4[1] < *pfVar18)) goto LAB_00521292;
      }
      fVar36 = pfVar18[1];
      uVar16 = uVar16 & 0xfffffff;
      if (afStack_c4[4] < fVar36) {
LAB_005212fa:
        pfVar18 = afStack_c4 + 3;
        uStack_9c = 3;
        uVar7 = uVar16;
      }
      else {
        fVar32 = ABS(pfVar18[1]);
        if (ABS(afStack_c4[4]) <= ABS(pfVar18[1])) {
          fVar32 = ABS(afStack_c4[4]);
        }
        fVar30 = fVar36 - afStack_c4[4];
        if (fVar30 < 0.0f) {
          fVar30 = afStack_c4[4] - fVar36;
        }
        uVar7 = uVar16 | (uint)(fVar32 * (9.999999747378752e-06f) < fVar30) << 0x1f;
        if ((/* stock 0x5212de vcmp.f32 s0, s7; blt 0x521304 => GE taken; 0x5212f0 vcmp; bpl 0x521304 at 0x5212f8 falls to 0x5212fa (wave19, label-verified) */ (fVar32 * (9.999999747378752e-06f) >= fVar30)) &&
           (uVar7 = uVar16, afStack_c4[3] < *pfVar18)) goto LAB_005212fa;
      }
      uVar7 = uVar7 & 0xfffffff;
      if (fVar31 < afStack_c4[0]) {
LAB_0052135e:
        pfVar20 = (float *)((byte *)&g2c_sp_frame_5202ec[2]);
        iStack_a4 = 1;
        uVar16 = uVar7;
      }
      else {
        fVar36 = ABS(fVar31);
        if (ABS(afStack_c4[0]) <= ABS(fVar31)) {
          fVar36 = ABS(afStack_c4[0]);
        }
        fVar32 = fVar31 - afStack_c4[0];
        if (fVar32 < 0.0f) {
          fVar32 = afStack_c4[0] - fVar31;
        }
        uVar16 = uVar7 | (uint)(fVar36 * (9.999999747378752e-06f) < fVar32) << 0x1f;
        pfVar20 = (float *)((byte *)&g2c_sp_frame_5202ec[0]);
        if ((/* stock 0x521342 vcmp.f32 s6, s0; blt 0x521368 => GE taken; 0x521354 vcmp; bpl 0x521368 at 0x52135c falls to 0x52135e (wave19, label-verified) */ (fVar36 * (9.999999747378752e-06f) >= fVar32)) &&
           (pfVar20 = (float *)((byte *)&g2c_sp_frame_5202ec[0]), uVar16 = uVar7, fVar25 < fVar26))
        goto LAB_0052135e;
      }
      fVar36 = pfVar20[1];
      uVar16 = uVar16 & 0xfffffff;
      if (fVar36 < afStack_c4[2]) {
LAB_005213c6:
        pfVar20 = afStack_c4 + 1;
        iStack_a4 = 2;
        uVar7 = uVar16;
      }
      else {
        fVar32 = ABS(afStack_c4[2]);
        if (ABS(pfVar20[1]) < ABS(afStack_c4[2])) {
          fVar32 = ABS(pfVar20[1]);
        }
        fVar30 = fVar36 - afStack_c4[2];
        if (fVar30 < 0.0f) {
          fVar30 = afStack_c4[2] - fVar36;
        }
        uVar7 = uVar16 | (uint)(fVar32 * (9.999999747378752e-06f) < fVar30) << 0x1f;
        if ((/* stock 0x5213aa vcmp.f32 s6, s0; blt 0x5213d0 => GE taken; 0x5213bc vcmp; bpl 0x5213d0 at 0x5213c4 falls to 0x5213c6 (wave19, label-verified) */ (fVar32 * (9.999999747378752e-06f) >= fVar30)) &&
           (uVar7 = uVar16, *pfVar20 < afStack_c4[1])) goto LAB_005213c6;
      }
      fVar36 = pfVar20[1];
      uVar7 = uVar7 & 0xfffffff;
      if (fVar36 < afStack_c4[4]) {
LAB_0052142e:
        pfVar20 = afStack_c4 + 3;
        iStack_a4 = 3;
        uVar16 = uVar7;
      }
      else {
        fVar32 = ABS(pfVar20[1]);
        if (ABS(afStack_c4[4]) <= ABS(pfVar20[1])) {
          fVar32 = ABS(afStack_c4[4]);
        }
        fVar30 = fVar36 - afStack_c4[4];
        if (fVar30 < 0.0f) {
          fVar30 = afStack_c4[4] - fVar36;
        }
        uVar16 = uVar7 | (uint)(fVar32 * (9.999999747378752e-06f) < fVar30) << 0x1f;
        if ((/* stock 0x521412 vcmp.f32 s0, s7; blt 0x521438 => GE taken; 0x521424 vcmp; bpl 0x521438 at 0x52142c falls to 0x52142e (wave19, label-verified) */ (fVar32 * (9.999999747378752e-06f) >= fVar30)) &&
           (uVar16 = uVar7, *pfVar20 < afStack_c4[3])) goto LAB_0052142e;
      }
      uVar16 = uVar16 & 0xfffffff;
      if (fVar31 < afStack_c4[0]) {
LAB_00521492:
        pfVar17 = (float *)((byte *)&g2c_sp_frame_5202ec[2]);
        fStack_a0 = 1.4013e-45f;
        uVar7 = uVar16;
      }
      else {
        fVar36 = ABS(fVar31);
        if (ABS(afStack_c4[0]) <= ABS(fVar31)) {
          fVar36 = ABS(afStack_c4[0]);
        }
        fVar32 = fVar31 - afStack_c4[0];
        if (fVar32 < 0.0f) {
          fVar32 = afStack_c4[0] - fVar31;
        }
        uVar7 = uVar16 | (uint)(fVar36 * (9.999999747378752e-06f) < fVar32) << 0x1f;
        pfVar17 = (float *)((byte *)&g2c_sp_frame_5202ec[0]);
        if ((/* stock 0x521476 vcmp.f32 s4, s0; blt 0x52149c => GE taken; 0x521488 vcmp; bpl 0x52149c at 0x521490 falls to 0x521492 (wave19, label-verified) */ (fVar36 * (9.999999747378752e-06f) >= fVar32)) &&
           (pfVar17 = (float *)((byte *)&g2c_sp_frame_5202ec[0]), uVar7 = uVar16, fVar26 < fVar25))
        goto LAB_00521492;
      }
      fVar25 = pfVar17[1];
      uVar7 = uVar7 & 0xfffffff;
      if (fVar25 < afStack_c4[2]) {
LAB_005214fa:
        pfVar17 = afStack_c4 + 1;
        fStack_a0 = 2.8026e-45f;
        uVar16 = uVar7;
      }
      else {
        fVar31 = ABS(afStack_c4[2]);
        if (ABS(pfVar17[1]) < ABS(afStack_c4[2])) {
          fVar31 = ABS(pfVar17[1]);
        }
        fVar26 = fVar25 - afStack_c4[2];
        if (fVar26 < 0.0f) {
          fVar26 = afStack_c4[2] - fVar25;
        }
        uVar16 = uVar7 | (uint)(fVar31 * (9.999999747378752e-06f) < fVar26) << 0x1f;
        if ((/* stock 0x5214de vcmp.f32 s2, s0; blt 0x521504 => GE taken; 0x5214f0 vcmp; bpl 0x521504 at 0x5214f8 falls to 0x5214fa (wave19, label-verified) */ (fVar31 * (9.999999747378752e-06f) >= fVar26)) &&
           (uVar16 = uVar7, afStack_c4[1] < *pfVar17)) goto LAB_005214fa;
      }
      fVar25 = pfVar17[1];
      uVar16 = uVar16 & 0xfffffff;
      if (fVar25 < afStack_c4[4]) {
LAB_00521562:
        pfVar17 = afStack_c4 + 3;
        fStack_a0 = 4.2039e-45f;
        uVar8 = uVar16;
      }
      else {
        fVar31 = ABS(pfVar17[1]);
        if (ABS(afStack_c4[4]) <= ABS(pfVar17[1])) {
          fVar31 = ABS(afStack_c4[4]);
        }
        fVar26 = fVar25 - afStack_c4[4];
        if (fVar26 < 0.0f) {
          fVar26 = afStack_c4[4] - fVar25;
        }
        /* stock 0x521546 vcmp s0(min*1e-5),s4; blt 0x52156c => GE path; 0x521558 vcmp; bpl 0x52156c falls to
           0x521562 (label-verified, wave19). NZCV word dropped: next read of uVar8 is masked & 0xfffffff. */
        uVar8 = uVar16;
        if ((fVar31 * (9.999999747378752e-06f) >= fVar26) && afStack_c4[3] < *pfVar17) goto LAB_00521562;
      }
      iVar13 = (int)g2c_float_to_bits(fStack_a8) + 1;
      if (pfVar11 == pfVar18) {
        fVar36 = pfVar11[1];
        fVar25 = *pfVar11;
        iVar13 = iVar13 - (iVar13 + ((uint)(iVar13 >> 1) >> 0x1e) & 0xfffffffc);
        fVar32 = *(float *)(((byte *)&g2c_sp_frame_5202ec[0]) + iVar13 * 8);
        fVar30 = *(float *)(((byte *)&g2c_sp_frame_5202ec[1]) + iVar13 * 8);
        iVar13 = (int)g2c_float_to_bits(fStack_a8) + 3;
        iVar13 = iVar13 - (iVar13 + ((uint)(iVar13 >> 1) >> 0x1e) & 0xfffffffc);
        fVar33 = *(float *)(((byte *)&g2c_sp_frame_5202ec[0]) + iVar13 * 8);
        fVar34 = *(float *)(((byte *)&g2c_sp_frame_5202ec[1]) + iVar13 * 8);
        fVar31 = fVar36;
        fVar26 = fVar25;
      }
      else {
        fVar25 = *pfVar11;
        fVar36 = pfVar11[1];
        iVar13 = iVar13 - (iVar13 + ((uint)(iVar13 >> 1) >> 0x1e) & 0xfffffffc);
        fVar32 = *(float *)(((byte *)&g2c_sp_frame_5202ec[0]) + iVar13 * 8);
        fVar30 = *(float *)(((byte *)&g2c_sp_frame_5202ec[1]) + iVar13 * 8);
        fVar26 = *pfVar18;
        iVar13 = (int)g2c_float_to_bits(fStack_a8) + 2;
        iVar13 = iVar13 - (iVar13 + ((uint)(iVar13 >> 1) >> 0x1e) & 0xfffffffc);
        fVar33 = *(float *)(((byte *)&g2c_sp_frame_5202ec[0]) + iVar13 * 8);
        fVar34 = *(float *)(((byte *)&g2c_sp_frame_5202ec[1]) + iVar13 * 8);
        fVar31 = pfVar18[1];
      }
      fVar37 = *pfVar20;
      iVar13 = iStack_a4 + 3;
      fVar40 = fVar37 + 4.0f;
      fVar35 = 1.0f;
      if (pfVar20 == pfVar17) {
        iVar15 = iStack_a4 + 1;
        d = pfVar20[1];
        iVar15 = iVar15 - (iVar15 + ((uint)(iVar15 >> 1) >> 0x1e) & 0xfffffffc);
        fStack_a8 = d;
        fVar38 = *(float *)(((byte *)&g2c_sp_frame_5202ec[0]) + iVar15 * 8);
      }
      else {
        iVar15 = iStack_a4 + 2;
        fStack_a8 = pfVar20[1];
        fVar37 = *pfVar17;
        iVar15 = iVar15 - (iVar15 + ((uint)(iVar15 >> 1) >> 0x1e) & 0xfffffffc);
        d = pfVar17[1];
        fVar38 = *(float *)(((byte *)&g2c_sp_frame_5202ec[0]) + iVar15 * 8);
      }
      f = *(float *)(((byte *)&g2c_sp_frame_5202ec[1]) + iVar15 * 8);
      iVar13 = iVar13 - (iVar13 + ((uint)(iVar13 >> 1) >> 0x1e) & 0xfffffffc);
      fVar39 = *(float *)(((byte *)&g2c_sp_frame_5202ec[0]) + iVar13 * 8);
      h = *(float *)(((byte *)&g2c_sp_frame_5202ec[1]) + iVar13 * 8);
      g2c_nema_vg_emit_verts_516b34
                ((fVar25 + 4.0f) * 0.25f,fVar36,(fVar32 + 4.0f) * 0.25f,fVar30,(fVar33 + -4.0f) * 0.25f,
                 fVar34,(fVar26 + -4.0f) * 0.25f,fVar31);
      g2c_nema_vg_emit_verts_516b34
                (fVar40 * 0.25f,fStack_a8,(fVar37 + -4.0f) * 0.25f,d,(fVar38 + -4.0f) * 0.25f,f,
                 (fVar39 + 4.0f) * 0.25f,h);
      audio_uart_nema_stencil_restore_5226b2(uStack_98);
      audio_uart_display_graphics_finish_4b1548();
      audio_uart_nema_child_514846(0x34,uStack_ac & 0xffff | 0x9000000);
      audio_uart_nema_child_514846(0x38,uStack_ac | uStack_b0 << 0x10);
      uVar16 = *puVar3;
      fVar31 = ((float)g2c_bits_to_float((uint)(path[4])) + (float)g2c_bits_to_float((uint)(path[6]))) * 0.5f + 0.5f;
      fVar25 = ((float)g2c_bits_to_float((uint)(path[5])) + (float)g2c_bits_to_float((uint)(path[7]))) * 0.5f + 0.5f;
      *(float *)(uVar16 + 0x2c4) = fVar25;
      *(int *)(uVar16 + 0x2cc) = (int)fVar25;
      *(float *)(uVar16 + 0x2c0) = fVar31;
      iVar13 = (int)fVar31;
      *(int *)(uVar16 + 0x2d0) = iVar13 << 0x10;
      *(int *)(uVar16 + 0x2c8) = iVar13;
      *(int *)(uVar16 + 0x2d4) = *(int *)(uVar16 + 0x2cc) << 0x10;
      g2c_nema_vg_paint_setup_516c82((uint *)(uVar16 + 0xec));
      uVar7 = *puVar3;
      uVar16 = *(uint *)(uVar7 + 0x110);
      fVar25 = *(float *)(uVar7 + 300) * 0.5f;
      bVar24 = uVar16 == 1;
      if (bVar24) {
        uVar16 = (uint)*(byte *)(uVar7 + 0x1bf);
      }
      if (bVar24 && uVar16 == 1) {
        fVar25 = *(float *)(uVar7 + 300) + 1.0f + fVar25;
      }
      fVar31 = 1.0f;
      /* stock 0x521864 vcmp [r1+0x1c4],0.001f; it ge; vdivge. Decompile had dropped the compare (wave19). */
      if (*(float *)(uVar7 + 0x1c4) >= (0.0010000001639127731f)) {
        fVar31 = 1.0f / *(float *)(uVar7 + 0x1c4);
      }
      fVar26 = *(float *)(uVar7 + 0x1c8);
      /* stock 0x52187a vcmp [r1+0x1c8],0.001f; itt ge; vdivge s16 (wave19). uVar12/uVar16 are reassigned
         before any later read (uVar12 = uVar8 & mask; uVar16 = call results). */
      if (fVar26 >= (0.0010000001639127731f)) {
        fVar35 = 1.0f / fVar26;
      }
      fVar31 = fVar31 + fVar25;
      fVar35 = fVar35 + fVar25;
      path[8] = (uint)g2c_float_to_bits(((float)g2c_bits_to_float((uint)(path[4])) - fVar31));
      path[9] = (uint)g2c_float_to_bits(((float)g2c_bits_to_float((uint)(path[5])) - fVar35));
      path[10] = (uint)g2c_float_to_bits(((float)g2c_bits_to_float((uint)(path[4])) + (float)g2c_bits_to_float((uint)(path[0x14])) + fVar31));
      path[0xb] = (uint)g2c_float_to_bits(((float)g2c_bits_to_float((uint)(path[5])) - fVar35));
      path[0xc] = (uint)g2c_float_to_bits(((float)g2c_bits_to_float((uint)(path[4])) + (float)g2c_bits_to_float((uint)(path[0x14])) + fVar31));
      path[0xd] = (uint)g2c_float_to_bits(((float)g2c_bits_to_float((uint)(path[5])) + (float)g2c_bits_to_float((uint)(path[0x15])) + fVar35));
      path[0xe] = (uint)g2c_float_to_bits(((float)g2c_bits_to_float((uint)(path[4])) - fVar31));
      path[0xf] = (uint)g2c_float_to_bits(((float)g2c_bits_to_float((uint)(path[5])) + (float)g2c_bits_to_float((uint)(path[0x15])) + fVar35));
      path[0x10] = (uint)g2c_float_to_bits(((float)g2c_bits_to_float((uint)(path[4])) - fVar31));
      path[0x11] = (uint)g2c_float_to_bits(((float)g2c_bits_to_float((uint)(path[5])) - fVar35));
      path[0x12] = (uint)g2c_float_to_bits(((float)g2c_bits_to_float((uint)(path[6])) + fVar31));
      path[0x13] = (uint)g2c_float_to_bits(((float)g2c_bits_to_float((uint)(path[7])) + fVar35));
      path[0x16] = (uint)g2c_float_to_bits(((float)g2c_bits_to_float((uint)(path[0x14])) + fVar31 * 2.0f));
      path[0x17] = (uint)g2c_float_to_bits(((float)g2c_bits_to_float((uint)(path[0x15])) + fVar35 * 2.0f));
      if (*(char *)(uVar7 + 0x1bc) != '\0') {
        pfVar11 = (float *)(uVar7 + 0xec);
        fVar25 = (float)g2c_bits_to_float((uint)(path[8]));
        path[8] = (uint)g2c_float_to_bits((*pfVar11 * fVar25 + *(float *)(uVar7 + 0xf0) * (float)g2c_bits_to_float((uint)(path[9])) +
                        *(float *)(uVar7 + 0xf4)));
        path[9] = (uint)g2c_float_to_bits((*(float *)(uVar7 + 0xf8) * fVar25 +
                         *(float *)(uVar7 + 0xfc) * (float)g2c_bits_to_float((uint)(path[9])) + *(float *)(uVar7 + 0x100)));
        fVar25 = (float)g2c_bits_to_float((uint)(path[10]));
        path[10] = (uint)g2c_float_to_bits((*pfVar11 * fVar25 + *(float *)(uVar7 + 0xf0) * (float)g2c_bits_to_float((uint)(path[0xb])) +
                         *(float *)(uVar7 + 0xf4)));
        path[0xb] = (uint)g2c_float_to_bits((*(float *)(uVar7 + 0xf8) * fVar25 +
                           *(float *)(uVar7 + 0xfc) * (float)g2c_bits_to_float((uint)(path[0xb])) + *(float *)(uVar7 + 0x100)));
        fVar25 = (float)g2c_bits_to_float((uint)(path[0xc]));
        path[0xc] = (uint)g2c_float_to_bits((*pfVar11 * fVar25 + *(float *)(uVar7 + 0xf0) * (float)g2c_bits_to_float((uint)(path[0xd])) +
                          *(float *)(uVar7 + 0xf4)));
        path[0xd] = (uint)g2c_float_to_bits((*(float *)(uVar7 + 0xf8) * fVar25 +
                           *(float *)(uVar7 + 0xfc) * (float)g2c_bits_to_float((uint)(path[0xd])) + *(float *)(uVar7 + 0x100)));
        fVar25 = (float)g2c_bits_to_float((uint)(path[0xe]));
        path[0xe] = (uint)g2c_float_to_bits((*pfVar11 * fVar25 + *(float *)(uVar7 + 0xf0) * (float)g2c_bits_to_float((uint)(path[0xf])) +
                          *(float *)(uVar7 + 0xf4)));
        fVar31 = (float)g2c_bits_to_float((uint)(path[10]));
        fVar36 = (float)g2c_bits_to_float((uint)(path[8]));
        fVar25 = *(float *)(uVar7 + 0xf8) * fVar25 + *(float *)(uVar7 + 0xfc) * (float)g2c_bits_to_float((uint)(path[0xf])) +
                 *(float *)(uVar7 + 0x100);
        path[0xf] = (uint)g2c_float_to_bits(fVar25);
        fVar26 = fVar36;
        if (fVar31 <= fVar36) {
          fVar26 = fVar31;
        }
        fVar30 = (float)g2c_bits_to_float((uint)(path[0xe]));
        fVar33 = (float)g2c_bits_to_float((uint)(path[0xc]));
        fVar32 = fVar33;
        if (fVar30 <= fVar33) {
          fVar32 = fVar30;
        }
        if (fVar32 <= fVar26) {
          fVar26 = fVar32;
        }
        fVar32 = (float)g2c_bits_to_float((uint)(path[0xb]));
        fVar35 = (float)g2c_bits_to_float((uint)(path[9]));
        fVar34 = fVar35;
        if (fVar32 <= fVar35) {
          fVar34 = fVar32;
        }
        fVar40 = (float)g2c_bits_to_float((uint)(path[0xd]));
        fVar37 = fVar40;
        if (fVar25 <= fVar40) {
          fVar37 = fVar25;
        }
        if (fVar37 <= fVar34) {
          fVar34 = fVar37;
        }
        if (fVar31 < fVar36) {
          fVar31 = fVar36;
        }
        if (fVar30 < fVar33) {
          fVar30 = fVar33;
        }
        if (fVar31 <= fVar30) {
          fVar31 = fVar30;
        }
        if (fVar32 < fVar35) {
          fVar32 = fVar35;
        }
        if (fVar25 < fVar40) {
          fVar25 = fVar40;
        }
        if (fVar25 < fVar32) {
          fVar25 = fVar32;
        }
        path[0x13] = (uint)g2c_float_to_bits(fVar25);
        path[0x10] = (uint)g2c_float_to_bits(fVar26);
        path[0x11] = (uint)g2c_float_to_bits(fVar34);
        path[0x12] = (uint)g2c_float_to_bits(fVar31);
        path[0x16] = (uint)g2c_float_to_bits((fVar31 - fVar26));
        path[0x17] = (uint)g2c_float_to_bits((fVar25 - fVar34));
        uVar12 = uVar8 & 0xfffffff;
      }
      bVar21 = *(byte *)(uVar7 + 0x7c);
      if (bVar21 == 0) {
        audio_uart_display_graphics_blend_513924((0x1000001u),3,0xffffffff,0xffffffff);
        display_driver_nema_select_522a16(0xffffffff);
        if (*(char *)(*puVar3 + 0x2e4) == '\0') {
          if (*(int *)(*puVar3 + 0x110) == 0) {
            uVar16 = g2c_nema_vg_tess_stroke_5171f8(path);
          }
          else {
            uVar16 = g2c_nema_vg_draw_fill_51d2e0(path);
          }
        }
        else {
          uVar16 = g2c_nema_vg_draw_stroke_51f798(path);
        }
        if (uVar16 == 0) {
          uVar16 = *(uint *)(*puVar4 + 0x10) & 0xffff | 0x8000000;
          goto LAB_00521c52;
        }
LAB_00521c36:
        uVar7 = *puVar3;
        *(undefined4 *)(uVar7 + 0x114) = 0;
        *(undefined4 *)(uVar7 + 0x118) = 0;
        audio_uart_nema_vg_set_error_51565c(uVar16);
      }
      else {
        if (bVar21 == 2) {
          audio_uart_nema_child_514846(0x11c,0xbc16);
          audio_uart_nema_child_514846(0x1e0,0xbc17);
          audio_uart_nema_rop_blend_mode_522956(0x10001);
          uVar16 = g2c_nema_vg_tess_fill_516e0c(path);
          if (uVar16 != 0) goto LAB_00521c36;
          uVar16 = *(uint *)(*puVar4 + 0x10) & 0xffff | 0x2f000000;
LAB_00521c52:
          audio_uart_nema_child_514846(0x34,uVar16);
          uVar16 = 0;
        }
        else {
          if (bVar21 < 2) {
            audio_uart_nema_child_514846(0x11c,0xbc16);
            audio_uart_nema_child_514846(0x1e0,0xbc17);
            audio_uart_nema_rop_blend_mode_522956(0x10001);
            uVar16 = g2c_nema_vg_tess_fill_516e0c(path);
            if (uVar16 != 0) goto LAB_00521c36;
            uVar16 = *(uint *)(*puVar4 + 0x10) & 0xffff | 0x2e000000;
            goto LAB_00521c52;
          }
          audio_uart_nema_vg_set_error_51565c(4);
          uVar16 = 4;
        }
        if (uVar16 == 0) {
          uVar16 = *puVar3;
          if (*(char *)(uVar16 + 0xa0) != '\x01') {
LAB_00521d5a:
            if (*(char *)(paint + 0xd5) != '\0') {
              g2c_nema_vg_path_reset_515148((int *)paint);
              uVar16 = g2c_nema_vg_path_alloc_51520c(paint);
              if (uVar16 != 0) {
                uVar7 = *puVar3;
                *(undefined4 *)(uVar7 + 0x114) = 0;
                *(undefined4 *)(uVar7 + 0x118) = 0;
                audio_uart_nema_vg_set_error_51565c(uVar16);
                goto LAB_00521c6a;
              }
            }
            if ((*(byte *)(*puVar3 + 0x7f) & 7) == 3) {
              audio_uart_nema_child_52262e(1);
            }
            else if ((*(byte *)(*puVar3 + 0x7f) & 7) == 4) {
              audio_uart_nema_child_52264e(1);
            }
            uVar16 = *(uint *)(*puVar3 + 0x84);
            cVar1 = *(char *)(paint + 0xd5);
            if (cVar1 == '\0') {
              if (((0x4000ffffu) & uVar16) == 0x501) {
                puVar9 = (undefined4 *)audio_uart_nema_cl_get_space_514aec(3);
                if (puVar9 == (undefined4 *)0x0) {
                  uVar16 = *puVar3;
                  *(undefined4 *)(uVar16 + 0x114) = 0;
                  *(undefined4 *)(uVar16 + 0x118) = 0;
                  audio_uart_nema_vg_set_error_51565c(0x200);
                  uVar16 = 0x200;
                  goto LAB_00521c6a;
                }
                *puVar9 = 0x1d0;
                uVar14 = (0x941fdc13u);
                puVar9[1] = uVar16;
                puVar9[2] = 0x11c;
                puVar9[3] = uVar14;
                puVar9[4] = 300;
                puVar9[5] = *(undefined4 *)(*puVar3 + 0x124);
              }
              else {
                uVar16 = (uVar16 & 0xfff) >> 8;
                iVar13 = 2;
                if (uVar16 != 0) {
                  afStack_c4[1] = 0.0f;
                  iVar13 = 3;
                  afStack_c4[2] = (float)g2c_bits_to_float((uint)((*(uint *)((0x6d5dd8u) + uVar16 * 4) | (0xa581606u))));
                }
                *(undefined4 *)(((byte *)&g2c_sp_frame_5202ec[0]) + iVar13 * 8) = (0x18001000u);
                *(undefined4 *)(((byte *)&g2c_sp_frame_5202ec[1]) + iVar13 * 8) = (0xa916426u);
                *(undefined4 *)(((byte *)&g2c_sp_frame_5202ec[0]) + (iVar13 + 1) * 8) = (0x10000002u);
                *(undefined4 *)(((byte *)&g2c_sp_frame_5202ec[1]) + (iVar13 + 1) * 8) = (0x8a5b56a6u);
                display_driver_nema_mode_commit_52294c(0xbc00);
                audio_uart_nema_rop_blend_mode_522956(1);
                audio_uart_nema_instruction_upload_522920((uint)((byte *)&g2c_sp_frame_5202ec[0]),iVar13 + 2,0);
                display_driver_nema_select_522a16(*(uint *)(*puVar3 + 0x124));
              }
            }
            else if ((uVar16 & 0xffff) == 0x501) {
              audio_uart_nema_child_514846(0x1d0,uVar16);
              uVar7 = 0;
              if ((int)(uVar16 << 1) < 0) {
                uVar7 = 0x100000;
              }
              fStack_a0 = g2c_bits_to_float((uint)((0x110bu)));
              uStack_9c = (0x0u);
              uStack_98 = (0x100c1183u);
              uStack_94 = (0x92004u);
              uStack_90 = (0x80c0002u);
              uStack_8c = (0x8081a046u);
              afStack_c4[3] = g2c_bits_to_float((uint)((0x110bu)));
              afStack_c4[4] = (0x0u);
              uStack_b0 = (0x100c1183u);
              uStack_ac = (0x92000u);
              fStack_a8 = g2c_bits_to_float((uint)((0x80c0002u)));
              iStack_a4 = (0x8081a046u);
              uStack_88 = (0x110bu);
              uStack_84 = (0x0u);
              uStack_80 = (0xc0000u);
              uStack_7c = (0x812182u);
              uStack_78 = (0x100c1183u);
              uStack_74 = (0x92004u);
              uStack_70 = (0x80c0002u);
              uStack_6c = (0x8081a046u);
              afStack_c4[1] = g2c_bits_to_float((uint)((0x80c0002u)));
              afStack_c4[2] = g2c_bits_to_float((uint)((0x8081a046u)));
              /* stock 0x521e26 vcmp [r5+0xd0],#1.0; blt 0x521e8c => GE path (ldrb [r5+0xd5] at 0x521e34) (wave19).
                 NZCV word dropped: uVar8 is reassigned on both paths, uVar12 next read masked. */
              uVar12 = uVar12 & 0xfffffff;
              if (*(float *)(paint + 0xd0) >= 1.0f) {
                cVar1 = *(char *)(paint + 0xd5);
                iVar13 = 8;
                uVar8 = 2;
                bVar24 = cVar1 == '\x02';
                if (bVar24) {
                  cVar1 = *(char *)(paint + 0x2c);
                }
                uVar27 = (0x941e8000u);
                if (bVar24 && cVar1 == '\x01') {
                  iVar13 = 0;
                  uVar8 = 3;
                  uVar27 = (0x941da000u);
                }
                if ((int)(uVar16 << 5) < 0) {
                  uStack_98 = uVar7 | (0x100c1183u);
                  pfVar11 = &fStack_a0;
                }
                else {
                  uStack_b0 = uVar7 | (0x100c1183u);
                  pfVar11 = afStack_c4 + 3;
                }
                audio_uart_nema_instruction_upload_522920((int)pfVar11 + iVar13,uVar8,0);
                display_driver_nema_mode_commit_52294c(uVar27 | (0x20 - uVar8) * 0x10000);
              }
              else {
                cVar1 = *(char *)(paint + 0xd5);
                iVar13 = 8;
                uVar8 = 2;
                bVar24 = cVar1 == '\x02';
                if (bVar24) {
                  cVar1 = *(char *)(paint + 0x2c);
                }
                uVar27 = (0x941e8000u);
                if (bVar24 && cVar1 == '\x01') {
                  iVar13 = 0;
                  uVar8 = 3;
                  uVar27 = (0x941da000u);
                }
                if ((int)(uVar16 << 5) < 0) {
                  uVar8 = uVar8 + 1;
                  uStack_78 = uVar7 | (0x100c1183u);
                  puVar9 = &uStack_88;
                }
                audio_uart_nema_instruction_upload_522920((uint)((int)puVar9 + iVar13),uVar8,0);
                display_driver_nema_mode_commit_52294c(uVar27 | (0x20 - uVar8) * 0x10000);
                audio_uart_ambiq_image_alpha_513e2e
                          ((int)(*(float *)(paint + 0xd0) * (255.0f) + 0.5f) << 0x18);
              }
            }
            else {
              bVar24 = cVar1 == '\x02';
              if (bVar24) {
                cVar1 = *(char *)(paint + 0x2c);
              }
              uVar7 = (uVar16 & 0xfff) >> 8;
              uVar8 = 0;
              if ((int)(uVar16 << 1) < 0) {
                uVar8 = 0x100000;
              }
              iVar13 = 1;
              if (bVar24 && cVar1 == '\x01') {
                iVar13 = 2;
              }
              if ((int)(uVar16 << 5) < 0) {
                *(uint *)(((byte *)&g2c_sp_frame_5202ec[0]) + iVar13 * 8) = uVar8 | 0x4c0000;
                *(undefined4 *)(((byte *)&g2c_sp_frame_5202ec[1]) + iVar13 * 8) = (0x1016204u);
                iVar13 = iVar13 + 1;
              }
              uVar27 = (0x184c1001u);
              if ((uVar16 & 0xf) - 6 < 4) {
                *(uint *)(((byte *)&g2c_sp_frame_5202ec[0]) + iVar13 * 8) = (0x184c1001u) | uVar8;
                *(undefined4 *)(((byte *)&g2c_sp_frame_5202ec[1]) + iVar13 * 8) = 0;
                iVar13 = iVar13 + 1;
                uVar27 = (0x184c1000u);
              }
              *(uint *)(((byte *)&g2c_sp_frame_5202ec[0]) + iVar13 * 8) = uVar8 | uVar27;
              *(uint *)(((byte *)&g2c_sp_frame_5202ec[1]) + iVar13 * 8) =
                   (0xa882206u) | *(uint *)((0x6d5dd8u) + 0x40 + (uVar16 & 0xf) * 4);
              iVar15 = iVar13 + 1;
              if (uVar7 != 0) {
                *(undefined4 *)(((byte *)&g2c_sp_frame_5202ec[0]) + iVar15 * 8) = 0;
                *(uint *)(((byte *)&g2c_sp_frame_5202ec[1]) + iVar15 * 8) =
                     *(uint *)((0x6d5dd8u) + 0x40 + uVar7 * 4) | (0xa581606u);
                iVar15 = iVar13 + 2;
              }
              *(undefined4 *)(((byte *)&g2c_sp_frame_5202ec[0]) + iVar15 * 8) = (0x18001000u);
              *(undefined4 *)(((byte *)&g2c_sp_frame_5202ec[1]) + iVar15 * 8) = (0xa912406u);
              *(undefined4 *)(((byte *)&g2c_sp_frame_5202ec[0]) + (iVar15 + 1) * 8) = (0x10000002u);
              *(undefined4 *)(((byte *)&g2c_sp_frame_5202ec[1]) + (iVar15 + 1) * 8) = (0x8a5b1686u);
              display_driver_nema_mode_commit_52294c(0x9c00);
              audio_uart_nema_rop_blend_mode_522956(1);
              audio_uart_nema_instruction_upload_522920((uint)((byte *)&g2c_sp_frame_5202ec[0]),iVar15 + 2,0);
            }
            if (*(char *)(paint + 0xd5) == '\x04') {
              uVar16 = g2c_nema_cl_get_error_4b14fe();
              uVar12 = uVar12 & 0xfffffff;
              fVar25 = *(float *)(paint + 0xc4);
              if (*(float *)(paint + 0xc4) < 0.0f) {
                fVar25 = (0x0u);
              }
              fVar31 = (float)VectorSignedToFloat(*(undefined4 *)(*puVar4 + 0x10),
                                                  (byte)(uVar12 >> 0x16) & 3);
              if (fVar31 < fVar25) {
                fVar25 = fVar31;
              }
              fVar26 = *(float *)(paint + 200);
              if (*(float *)(paint + 200) < 0.0f) {
                fVar26 = (0x0u);
              }
              fVar36 = (float)VectorSignedToFloat(*(undefined4 *)(*puVar4 + 0x14),
                                                  (byte)(uVar12 >> 0x16) & 3);
              if (fVar36 < fVar26) {
                fVar26 = fVar36;
              }
              fVar31 = (fVar31 - fVar25) + 0.5f;
              fVar36 = (fVar36 - fVar26) + 0.5f;
              /* stock 0x522190 vcmp s18,#0; itt gt; vcmpgt 0x52219e s19,#0; ble 0x522204 (wave19). GT = !Z && N==V. */
              uVar8 = uVar12;
              if (fVar31 > 0.0f && fVar36 > 0.0f) {
                audio_uart_nema_matrix_upload_5226e8(paint + 0x34);
                uVar7 = VectorFloatToUnsigned(fVar36,3);
                uVar12 = VectorFloatToUnsigned(fVar31,3);
                if (uVar16 == 0) {
                  audio_uart_display_graphics_target_4b1516((int)fVar25,(int)fVar26,uVar12,uVar7);
                }
                else {
                  g2c_nema_cl_submit_node_4b14ca((int)fVar25,(int)fVar26,uVar12,uVar7);
                }
                g2c_nema_vg_emit_verts_516b34
                          ((float)g2c_bits_to_float((uint)(path[8])),(float)g2c_bits_to_float((uint)(path[9])),(float)g2c_bits_to_float((uint)(path[10])),(float)g2c_bits_to_float((uint)(path[0xb])),
                           (float)g2c_bits_to_float((uint)(path[0xc])),(float)g2c_bits_to_float((uint)(path[0xd])),(float)g2c_bits_to_float((uint)(path[0xe])),(float)g2c_bits_to_float((uint)(path[0xf])));
              }
              fVar36 = fVar25 + 0.5f;
              /* stock 0x52220e vcmp s18(=x+0.5),#0; ble 0x5222c6; 0x522228 vcmp s19,#0; bgt 0x522268 (upload +0x58 at
                 0x52226c) (wave19; GT). RMode bits 22..23 of uVar12 are unchanged by dropping NZCV. */
              uVar12 = uVar8 & 0xfffffff;
              fVar31 = (float)VectorSignedToFloat(*(undefined4 *)(*puVar4 + 0x14),
                                                  (byte)(uVar12 >> 0x16) & 3);
              fVar31 = (fVar31 - fVar26) + 0.5f;
              if (fVar36 > 0.0f) {
                uVar8 = uVar8 & 0xfffffff;
                if (fVar31 > 0.0f) {
                  audio_uart_nema_matrix_upload_5226e8(paint + 0x58);
                  uVar7 = VectorFloatToUnsigned(fVar31,3);
                  uVar12 = VectorFloatToUnsigned(fVar36,3);
                  if (uVar16 == 0) {
                    audio_uart_display_graphics_target_4b1516(0,(int)fVar26,uVar12,uVar7);
                  }
                  else {
                    g2c_nema_cl_submit_node_4b14ca(0,(int)fVar26,uVar12,uVar7);
                  }
                  g2c_nema_vg_emit_verts_516b34
                            ((float)g2c_bits_to_float((uint)(path[8])),(float)g2c_bits_to_float((uint)(path[9])),(float)g2c_bits_to_float((uint)(path[10])),(float)g2c_bits_to_float((uint)(path[0xb])),
                             (float)g2c_bits_to_float((uint)(path[0xc])),(float)g2c_bits_to_float((uint)(path[0xd])),(float)g2c_bits_to_float((uint)(path[0xe])),(float)g2c_bits_to_float((uint)(path[0xf])));
                }
                fVar31 = fVar26 + 0.5f;
                /* stock 0x522236 vcmp s17(=fVar26+0.5),#0; ble 0x5222fc; upload +0x7c at 0x522244 (wave19; GT). */
                uVar12 = uVar8 & 0xfffffff;
                if (fVar31 > 0.0f) {
                  audio_uart_nema_matrix_upload_5226e8(paint + 0x7c);
                  uVar7 = VectorFloatToUnsigned(fVar31,3);
                  uVar8 = VectorFloatToUnsigned(fVar36,3);
                  if (uVar16 == 0) {
                    audio_uart_display_graphics_target_4b1516(0,0,uVar8,uVar7);
                  }
                  else {
                    g2c_nema_cl_submit_node_4b14ca(0,0,uVar8,uVar7);
                  }
                  g2c_nema_vg_emit_verts_516b34
                            ((float)g2c_bits_to_float((uint)(path[8])),(float)g2c_bits_to_float((uint)(path[9])),(float)g2c_bits_to_float((uint)(path[10])),(float)g2c_bits_to_float((uint)(path[0xb])),
                             (float)g2c_bits_to_float((uint)(path[0xc])),(float)g2c_bits_to_float((uint)(path[0xd])),(float)g2c_bits_to_float((uint)(path[0xe])),(float)g2c_bits_to_float((uint)(path[0xf])));
                }
              }
              fVar26 = fVar26 + 0.5f;
              fVar31 = (float)VectorSignedToFloat(*(undefined4 *)(*puVar4 + 0x10),
                                                  (byte)(uVar12 >> 0x16) & 3);
              fVar36 = (fVar31 - fVar25) + 0.5f;
              /* stock 0x522312 vcmp s18,#0; itt gt; vcmpgt 0x52231c s17,#0; ble 0x522382; upload +0xa0 at 0x52232a
                 (wave19; GT both, replaces the decompile's Z/N/NAN split). */
              fVar31 = fVar36;
              if (fVar36 > 0.0f && fVar26 > 0.0f) {
                audio_uart_nema_matrix_upload_5226e8(paint + 0xa0);
                uVar7 = VectorFloatToUnsigned(fVar26,3);
                uVar8 = VectorFloatToUnsigned(fVar36,3);
                if (uVar16 == 0) {
                  audio_uart_display_graphics_target_4b1516((int)fVar25,0,uVar8,uVar7);
                }
                else {
                  g2c_nema_cl_submit_node_4b14ca((int)fVar25,0,uVar8,uVar7);
                }
                g2c_nema_vg_emit_verts_516b34
                          ((float)g2c_bits_to_float((uint)(path[8])),(float)g2c_bits_to_float((uint)(path[9])),(float)g2c_bits_to_float((uint)(path[10])),(float)g2c_bits_to_float((uint)(path[0xb])),
                           (float)g2c_bits_to_float((uint)(path[0xc])),(float)g2c_bits_to_float((uint)(path[0xd])),(float)g2c_bits_to_float((uint)(path[0xe])),(float)g2c_bits_to_float((uint)(path[0xf])));
              }
              uVar16 = g2c_nema_cl_get_error_4b14fe();
              if (uVar16 == 0) {
                audio_uart_display_graphics_finish_4b1548();
              }
              else {
                g2c_nema_cl_submit_node_4b14ca(0,0,0x7fff,0x7fff);
              }
            }
            else {
              g2c_nema_vg_emit_verts_516b34
                        ((float)g2c_bits_to_float((uint)(path[8])),(float)g2c_bits_to_float((uint)(path[9])),(float)g2c_bits_to_float((uint)(path[10])),(float)g2c_bits_to_float((uint)(path[0xb])),
                         (float)g2c_bits_to_float((uint)(path[0xc])),(float)g2c_bits_to_float((uint)(path[0xd])),(float)g2c_bits_to_float((uint)(path[0xe])),(float)g2c_bits_to_float((uint)(path[0xf])));
            }
LAB_00520ce6:
            if (*(char *)(*puVar3 + 0x1bd) != '\0') {
              audio_uart_nema_child_514846(0x388,1);
              *(undefined1 *)(*puVar3 + 0x1bc) = *(undefined1 *)(*puVar3 + 0x1bd);
              *(undefined1 *)(*puVar3 + 0x1bd) = 0;
            }
            return 0;
          }
          if (uVar16 == 0) {
            audio_uart_nema_vg_set_error_51565c(1);
            uVar16 = 1;
          }
          else {
            if (*(int *)(uVar16 + 0x94) != 0) {
              audio_uart_ambiq_texture_color_4b146c(0);
              iVar13 = *(int *)(*puVar3 + 0x94);
              audio_uart_nema_bind_tex_4b1298
                        (2,*(uint *)(iVar13 + 0xc),(uint)*(ushort *)(iVar13 + 0x10),
                         (uint)*(ushort *)(iVar13 + 0x12),(uint)*(byte *)(iVar13 + 0x1c),
                         *(uint *)(iVar13 + 0x14),8);
              bVar24 = *(char *)(*puVar3 + 0x7c) == '\x02' || *(char *)(*puVar3 + 0x7c) == '\x01';
              if (bVar24) {
                uVar16 = *puVar4;
                audio_uart_nema_bind_tex_4b1298
                          (1,*(uint *)(uVar16 + 0xc),*(uint *)(uVar16 + 0x10),
                           *(uint *)(uVar16 + 0x14),8,*(uint *)(uVar16 + 0x10),0);
                uVar7 = 3;
                uVar16 = 1;
              }
              else {
                uVar7 = 0xffffffff;
                uVar16 = 3;
              }
              audio_uart_display_graphics_blend_513924(0x400,uVar16,2,uVar7);
              audio_uart_nema_float_position_5228b0
                        (*(float *)(*puVar3 + 0x98),*(float *)(*puVar3 + 0x9c));
              g2c_nema_vg_emit_verts_516b34
                        ((float)g2c_bits_to_float((uint)(path[8])),(float)g2c_bits_to_float((uint)(path[9])),(float)g2c_bits_to_float((uint)(path[10])),(float)g2c_bits_to_float((uint)(path[0xb])),
                         (float)g2c_bits_to_float((uint)(path[0xc])),(float)g2c_bits_to_float((uint)(path[0xd])),(float)g2c_bits_to_float((uint)(path[0xe])),(float)g2c_bits_to_float((uint)(path[0xf])));
              if (bVar24) {
                audio_uart_nema_child_514846(0x34,*(uint *)(*puVar4 + 0x10) & 0xffff | 0x8000000);
              }
              goto LAB_00521d5a;
            }
            audio_uart_nema_vg_set_error_51565c(0x800);
            uVar16 = 0x800;
          }
        }
      }
LAB_00521c6a:
      uVar7 = *puVar3;
      *(undefined4 *)(uVar7 + 0x114) = 0;
      *(undefined4 *)(uVar7 + 0x118) = 0;
      audio_uart_nema_vg_set_error_51565c(uVar16);
    }
  }
  uVar7 = *puVar3;
  *(undefined4 *)(uVar7 + 0x114) = 0;
  *(undefined4 *)(uVar7 + 0x118) = 0;
LAB_00520d64:
  audio_uart_nema_vg_set_error_51565c(uVar16);
  return uVar16;
}
#undef uStack_b0
#undef uStack_ac
#undef fStack_a8
#undef iStack_a4
#undef fStack_a0
#undef uStack_9c
#undef uStack_98
#undef uStack_94
#undef uStack_90
#undef uStack_8c
#undef uStack_88
#undef uStack_84
#undef uStack_80
#undef uStack_7c
#undef uStack_78
#undef uStack_74
#undef uStack_70
#undef uStack_6c


  

/* ---- lifted 0x522622 ---- */

void g2c_nema_vg_set_flag_522622(uint a)

{
  *(char *)(*(((int *)audio_uart_nema_context_cell)) + 0xfa) = (char)a;
  return;
}

  

/* ---- lifted 0x522f1c ---- */

uint g2c_nema_vg_f2u_522f1c(float a)

{
  int iVar1;
  
  iVar1 = (int)(a * (0.9424778819084167f) + 0.5f);
  if (0x60 < iVar1) {
    return 0x60;
  }
  if (iVar1 < 0x20) {
    return 0x20;
  }
  return iVar1 + 0xf + ((uint)(iVar1 + 0xf >> 3) >> 0x1c) & 0xfffffff0;
}

  

/* ---- lifted 0x522f50 ---- */

int g2c_nema_vg_cubic_approx_522f50
              (float a,float b,float c,float d,float e,float f,float g,float h,float *out0,
              float *out1)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  
  fVar4 = d - b;
  fVar3 = a - c;
  fVar1 = fVar4 * a + fVar3 * b;
  fVar2 = h - f;
  fVar7 = e - g;
  fVar5 = fVar2 * e + fVar7 * f;
  fVar6 = fVar4 * fVar7 - fVar2 * fVar3;
  if (!(ABS(fVar6) < (1.0000000656873453e-05f))) {
    *out0 = (fVar7 * fVar1 - fVar3 * fVar5) / fVar6;
    *out1 = (fVar4 * fVar5 - fVar2 * fVar1) / fVar6;
    return 1;
  }
  return 0;
}

  

/* ---- lifted 0x522fb4 ---- */

void g2c_nema_vg_move_to_522fb4(float a,float b,float c)

{
  undefined4 uVar1;
  int *piVar2;
  float fVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  undefined4 *puVar7;
  float fVar8;
  uint uVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  float value;
  float fVar14;
  float value_00;
  
  iVar13 = (int)(c * (0.9424778819084167f) + 0.5f);
  if (iVar13 < 0x61) {
    if (iVar13 < 0x20) {
      iVar13 = 8;
    }
    else {
      uVar9 = iVar13 + 0xf + ((uint)(iVar13 + 0xf >> 3) >> 0x1c) & 0xfffffff0;
      iVar13 = ((int)(uVar9 + ((uint)((int)uVar9 >> 3) >> 0x1c)) >> 4) << 2;
    }
  }
  else {
    iVar13 = 0x18;
  }
  fVar8 = *(float *)((int)((int *)g2_nema_arc_table_5232d0) /* Proven stock VA DAT_005232d0 */ + iVar13);
  fVar3 = *(float *)((int)((float *)(g2_nema_arc_table_5232d0+6)) /* Proven stock VA UNK_005232e8 */ + iVar13);
  iVar4 = 0xe;
  if (1 < iVar13) {
    iVar4 = (iVar13 + -1) * 0x12 + 0xe;
  }
  iVar4 = g2c_nema_cl_enough_space_514d2c(iVar4);
  if (-1 < iVar4) {
    iVar4 = audio_uart_nema_float_fixed_5242cc(c);
    iVar5 = audio_uart_nema_float_fixed_5242cc(a);
    iVar11 = 0;
    iVar6 = audio_uart_nema_float_fixed_5242cc(b);
    piVar2 = (((int *)audio_uart_nema_context_cell));
    if (1 < iVar13) {
      iVar13 = iVar13 + -1;
      iVar10 = iVar4;
      iVar12 = iVar11;
      fVar14 = (0x0u);
      value = c;
      do {
        value_00 = fVar3 * value + fVar8 * fVar14;
        value = fVar8 * value - fVar3 * fVar14;
        if ((0.5f <= value_00 - fVar14) ||
           (iVar4 = iVar10, iVar11 = iVar12, *(char *)(*piVar2 + 0xfa) != '\0')) {
          iVar4 = audio_uart_nema_float_fixed_5242cc(value);
          iVar11 = audio_uart_nema_float_fixed_5242cc(value_00);
          puVar7 = (undefined4 *)audio_uart_nema_cl_get_space_514aec(9);
          if (puVar7 != (undefined4 *)0x0) {
            *puVar7 = 0x120;
            puVar7[2] = 0x124;
            puVar7[1] = iVar5 - iVar10;
            puVar7[4] = 0x130;
            puVar7[5] = iVar5 - iVar4;
            puVar7[6] = 0x134;
            puVar7[3] = iVar12 + iVar6;
            puVar7[7] = iVar11 + iVar6;
            puVar7[8] = 0x140;
            puVar7[9] = iVar4 + iVar5;
            puVar7[0xb] = iVar11 + iVar6;
            puVar7[0xf] = iVar12 + iVar6;
            uVar1 = (0xff000100u);
            puVar7[10] = 0x144;
            puVar7[0xc] = 0x150;
            puVar7[0xd] = iVar10 + iVar5;
            puVar7[0xe] = 0x154;
            puVar7[0x10] = uVar1;
            puVar7[0x11] = *(uint *)(*piVar2 + 0x18) | 5;
          }
          puVar7 = (undefined4 *)audio_uart_nema_cl_get_space_514aec(9);
          if (puVar7 != (undefined4 *)0x0) {
            *puVar7 = 0x120;
            puVar7[2] = 0x124;
            puVar7[1] = iVar5 - iVar4;
            puVar7[4] = 0x130;
            puVar7[5] = iVar5 - iVar10;
            puVar7[3] = iVar6 - iVar11;
            puVar7[8] = 0x140;
            puVar7[9] = iVar10 + iVar5;
            puVar7[10] = 0x144;
            puVar7[0xf] = iVar6 - iVar11;
            uVar1 = (0xff000100u);
            puVar7[6] = 0x134;
            puVar7[7] = iVar6 - iVar12;
            puVar7[0xb] = iVar6 - iVar12;
            puVar7[0xc] = 0x150;
            puVar7[0xd] = iVar4 + iVar5;
            puVar7[0xe] = 0x154;
            puVar7[0x10] = uVar1;
            puVar7[0x11] = *(uint *)(*piVar2 + 0x18) | 5;
          }
        }
        iVar13 = iVar13 + -1;
        iVar10 = iVar4;
        iVar12 = iVar11;
        fVar14 = value_00;
      } while (iVar13 != 0);
    }
    iVar13 = audio_uart_nema_float_fixed_5242cc(b + c);
    puVar7 = (undefined4 *)audio_uart_nema_cl_get_space_514aec(7);
    if (puVar7 != (undefined4 *)0x0) {
      *puVar7 = 0x120;
      puVar7[1] = iVar5;
      puVar7[2] = 0x124;
      puVar7[4] = 0x130;
      puVar7[5] = iVar5 - iVar4;
      puVar7[3] = iVar13;
      puVar7[6] = 0x134;
      puVar7[7] = iVar11 + iVar6;
      puVar7[0xb] = iVar11 + iVar6;
      puVar7[8] = 0x140;
      uVar1 = (0xff000100u);
      puVar7[9] = iVar4 + iVar5;
      puVar7[10] = 0x144;
      puVar7[0xc] = uVar1;
      uVar9 = *(uint *)(*(((int *)audio_uart_nema_context_cell)) + 0x18);
      if ((int)(uVar9 << 7) < 0) {
        uVar9 = uVar9 | 0x800000;
      }
      else {
        uVar9 = uVar9 & 0xff7fffff;
      }
      puVar7[0xd] = uVar9 | 4;
    }
    iVar13 = audio_uart_nema_float_fixed_5242cc(b - c);
    puVar7 = (undefined4 *)audio_uart_nema_cl_get_space_514aec(7);
    if (puVar7 != (undefined4 *)0x0) {
      *puVar7 = 0x120;
      puVar7[1] = iVar5;
      puVar7[2] = 0x124;
      puVar7[4] = 0x130;
      puVar7[5] = iVar5 - iVar4;
      puVar7[8] = 0x140;
      puVar7[10] = 0x144;
      uVar1 = (0xff000100u);
      puVar7[3] = iVar13;
      puVar7[6] = 0x134;
      puVar7[7] = iVar6 - iVar11;
      puVar7[9] = iVar4 + iVar5;
      puVar7[0xb] = iVar6 - iVar11;
      puVar7[0xc] = uVar1;
      uVar9 = *(uint *)(*(((int *)audio_uart_nema_context_cell)) + 0x18);
      if ((int)(uVar9 << 7) < 0) {
        uVar9 = uVar9 | 0x800000;
      }
      else {
        uVar9 = uVar9 & 0xff7fffff;
      }
      puVar7[0xd] = uVar9 | 4;
    }
  }
  return;
}

  

/* ---- lifted 0x523284 ---- */

void g2c_nema_vg_line_to_523284(float a,float b,float c)

{
  int *piVar1;
  int iVar2;
  uint uVar3;
  
  piVar1 = (((int *)audio_uart_nema_context_cell));
  iVar2 = *(((int *)audio_uart_nema_context_cell));
  uVar3 = *(uint *)(iVar2 + 0x1c);
  *(undefined4 *)(iVar2 + 0x1c) = 0x5000000;
  uVar3 = uVar3 & 0x7800000;
  *(uint *)(iVar2 + 0x18) =
       *(uint *)(iVar2 + 0xc) | *(uint *)(iVar2 + 0x14) | *(uint *)(iVar2 + 0x10) | 0x5000000;
  g2c_nema_vg_move_to_522fb4(a,b,c);
  iVar2 = *piVar1;
  *(uint *)(iVar2 + 0x1c) = uVar3;
  *(uint *)(iVar2 + 0x18) =
       uVar3 | *(uint *)(iVar2 + 0xc) | *(uint *)(iVar2 + 0x14) | *(uint *)(iVar2 + 0x10);
  return;
}

  

/* ---- lifted 0x523a34 ---- */

void g2c_nema_vg_path_transform_523a34(float *m,int a,int b)

{
  bool bVar1;
  int *piVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  undefined4 *puVar10;
  uint uVar11;
  float fVar12;
  float value;
  float value_00;
  float value_01;
  float value_02;
  
  if (a < 3) {
    return;
  }
  fVar12 = m[b * 2 + 1];
  value = m[b * 2];
  value_00 = m[b + 1];
  value_01 = m[b];
  value_02 = m[1];
  iVar4 = audio_uart_nema_float_fixed_5242cc(*m);
  iVar5 = audio_uart_nema_float_fixed_5242cc(value_02);
  iVar6 = audio_uart_nema_float_fixed_5242cc(value_01);
  iVar7 = audio_uart_nema_float_fixed_5242cc(value_00);
  iVar8 = audio_uart_nema_float_fixed_5242cc(value);
  iVar9 = audio_uart_nema_float_fixed_5242cc(fVar12);
  puVar10 = (undefined4 *)audio_uart_nema_cl_get_space_514aec(7);
  if (puVar10 != (undefined4 *)0x0) {
    *puVar10 = 0x120;
    puVar10[2] = 0x124;
    puVar10[1] = iVar4;
    puVar10[3] = iVar5;
    puVar10[4] = 0x130;
    puVar10[5] = iVar6;
    puVar10[6] = 0x134;
    puVar10[7] = iVar7;
    puVar10[8] = 0x140;
    puVar10[10] = 0x144;
    uVar3 = (0xff000100u);
    puVar10[9] = iVar8;
    puVar10[0xb] = iVar9;
    puVar10[0xc] = uVar3;
    uVar11 = *(uint *)(*(((int *)audio_uart_nema_context_cell)) + 0x18);
    if ((int)(uVar11 << 7) < 0) {
      uVar11 = uVar11 | 0x800000;
    }
    else {
      uVar11 = uVar11 & 0xff7fffff;
    }
    puVar10[0xd] = uVar11 | 4;
  }
  uVar3 = (0xff000100u);
  piVar2 = (((int *)audio_uart_nema_context_cell));
  iVar4 = 1;
  if (1 < a + -2) {
    iVar5 = 3;
    do {
      fVar12 = m[b * iVar5 + 1];
      iVar5 = audio_uart_nema_float_fixed_5242cc(m[b * iVar5]);
      iVar6 = audio_uart_nema_float_fixed_5242cc(fVar12);
      puVar10 = (undefined4 *)audio_uart_nema_cl_get_space_514aec(3);
      if (puVar10 != (undefined4 *)0x0) {
        *puVar10 = 0x130;
        puVar10[1] = iVar5;
        puVar10[2] = 0x134;
        puVar10[3] = iVar6;
        puVar10[4] = uVar3;
        uVar11 = *(uint *)(*piVar2 + 0x18);
        if ((int)(uVar11 << 7) < 0) {
          uVar11 = uVar11 | 0x800000;
        }
        else {
          uVar11 = uVar11 & 0xff7fffff;
        }
        puVar10[5] = uVar11 | 4;
      }
      bVar1 = true;
      iVar5 = iVar4;
      while( true ) {
        iVar4 = iVar5 + 1;
        if (a + -2 <= iVar4) {
          return;
        }
        iVar5 = iVar5 + 3;
        if (!bVar1) break;
        fVar12 = m[b * iVar5 + 1];
        iVar5 = audio_uart_nema_float_fixed_5242cc(m[b * iVar5]);
        iVar6 = audio_uart_nema_float_fixed_5242cc(fVar12);
        puVar10 = (undefined4 *)audio_uart_nema_cl_get_space_514aec(3);
        if (puVar10 != (undefined4 *)0x0) {
          *puVar10 = 0x140;
          puVar10[1] = iVar5;
          puVar10[2] = 0x144;
          puVar10[3] = iVar6;
          puVar10[4] = uVar3;
          uVar11 = *(uint *)(*piVar2 + 0x18);
          if ((int)(uVar11 << 7) < 0) {
            uVar11 = uVar11 | 0x800000;
          }
          else {
            uVar11 = uVar11 & 0xff7fffff;
          }
          puVar10[5] = uVar11 | 4;
        }
        bVar1 = false;
        iVar5 = iVar4;
      }
    } while( true );
  }
  return;
}

  

/* ---- lifted 0x524218 ---- */

float g2c_nema_vg_sqrt_524218(float x)

{
  float fVar1;
  
  /* Stock 0x524218: the classic bit-level estimate (x spilled with vpush, reloaded with ldr;
   * result stored with str and reloaded with vldr), then one single-precision Newton step:
   * s1=x*y, s3=(x*0.5)*y, s2=1.5-s3*y (vmls), return s1*s2. */
  fVar1 = g2c_bits_to_float((0x5f3759dfu) - (g2c_float_to_bits(x) >> 1));
  return x * fVar1 * (1.5f - x * 0.5f * fVar1 * fVar1);
}

  

/* ---- lifted 0x540036 ---- */

void audio_uart_ambiq_draw_box_shadow_540036(int task,int dsc,int *coords,uint color)

{
  uint g2c_sp0_540036; /* sp+0 (frame: push 10 regs + sub sp,#184 at 0x540036/0x54003a) */
  byte bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  uint uVar8;
  uint uVar9;
  /* Evidence (wave10): FPSCR scratch was declared here but never read; removed. */
  float fVar10;
  float fVar11;
  /* Stock frame of 0x540036 as one block: locals keep the entry-SP offsets Ghidra named them by
   * (X_Stack_NN at g2c_frame_540036[0xd8-0xNN]) so &local passed to callees spans its stock neighbours. */
  unsigned char g2c_frame_540036[0xd8] __attribute__((aligned(8)));
  typedef int __attribute__((may_alias)) g2c_fa_int;
#define iStack_d4 (*(g2c_fa_int *)(void *)&g2c_frame_540036[0xd8-0xd4])
#define iStack_d0 (*(g2c_fa_int *)(void *)&g2c_frame_540036[0xd8-0xd0])
#define iStack_cc (*(g2c_fa_int *)(void *)&g2c_frame_540036[0xd8-0xcc])
#define iStack_c8 (*(g2c_fa_int *)(void *)&g2c_frame_540036[0xd8-0xc8])
#define iStack_c4 (*(g2c_fa_int *)(void *)&g2c_frame_540036[0xd8-0xc4])
#define iStack_c0 (*(g2c_fa_int *)(void *)&g2c_frame_540036[0xd8-0xc0])
#define iStack_bc (*(g2c_fa_int *)(void *)&g2c_frame_540036[0xd8-0xbc])
#define iStack_b8 (*(g2c_fa_int *)(void *)&g2c_frame_540036[0xd8-0xb8])
#define iStack_b4 (*(g2c_fa_int *)(void *)&g2c_frame_540036[0xd8-0xb4])
#define iStack_b0 (*(g2c_fa_int *)(void *)&g2c_frame_540036[0xd8-0xb0])
#define iStack_ac (*(g2c_fa_int *)(void *)&g2c_frame_540036[0xd8-0xac])
#define iStack_a8 (*(g2c_fa_int *)(void *)&g2c_frame_540036[0xd8-0xa8])
#define iStack_a4 (*(g2c_fa_int *)(void *)&g2c_frame_540036[0xd8-0xa4])
#define iStack_a0 (*(g2c_fa_int *)(void *)&g2c_frame_540036[0xd8-0xa0])
#define iStack_9c (*(g2c_fa_int *)(void *)&g2c_frame_540036[0xd8-0x9c])
#define iStack_98 (*(g2c_fa_int *)(void *)&g2c_frame_540036[0xd8-0x98])
  typedef uint __attribute__((may_alias)) g2c_fa_uint;
#define uStack_94 (*(g2c_fa_uint *)(void *)&g2c_frame_540036[0xd8-0x94])
  typedef byte __attribute__((may_alias)) g2c_fa_byte;
#define bStack_90 (*(g2c_fa_byte *)(void *)&g2c_frame_540036[0xd8-0x90])
#define iStack_8c (*(g2c_fa_int *)(void *)&g2c_frame_540036[0xd8-0x8c])
#define uStack_88 (*(g2c_fa_uint *)(void *)&g2c_frame_540036[0xd8-0x88])
#define iStack_84 (*(g2c_fa_int *)(void *)&g2c_frame_540036[0xd8-0x84])
#define iStack_80 (*(g2c_fa_int *)(void *)&g2c_frame_540036[0xd8-0x80])
#define uStack_74 (*(g2c_fa_uint *)(void *)&g2c_frame_540036[0xd8-0x74])
  typedef undefined4 __attribute__((may_alias)) g2c_fa_undefined4;
#define auStack_70 (((g2c_fa_undefined4 *)(void *)&g2c_frame_540036[0xd8-0x70]))
#define uStack_68 (*(g2c_fa_undefined4 *)(void *)&g2c_frame_540036[0xd8-0x68])
#define uStack_60 (*(g2c_fa_undefined4 *)(void *)&g2c_frame_540036[0xd8-0x60])
#define uStack_5c (*(g2c_fa_undefined4 *)(void *)&g2c_frame_540036[0xd8-0x5c])
#define iStack_4c (*(g2c_fa_int *)(void *)&g2c_frame_540036[0xd8-0x4c])
#define iStack_48 (*(g2c_fa_int *)(void *)&g2c_frame_540036[0xd8-0x48])
#define iStack_44 (*(g2c_fa_int *)(void *)&g2c_frame_540036[0xd8-0x44])
#define iStack_40 (*(g2c_fa_int *)(void *)&g2c_frame_540036[0xd8-0x40])
#define uStack_3c (*(g2c_fa_uint *)(void *)&g2c_frame_540036[0xd8-0x3c])
  typedef undefined1 __attribute__((may_alias)) g2c_fa_undefined1;
#define auStack_38 (((g2c_fa_undefined1 *)(void *)&g2c_frame_540036[0xd8-0x38]))
#define uStack_28 (*(g2c_fa_uint *)(void *)&g2c_frame_540036[0xd8-0x28])
  
  iStack_4c = (*(int *)(dsc + 0x2c) + *coords) - *(int *)(dsc + 0x28);
  iStack_44 = *(int *)(dsc + 0x28) + *(int *)(dsc + 0x2c) + coords[2];
  iStack_48 = (*(int *)(dsc + 0x30) + coords[1]) - *(int *)(dsc + 0x28);
  iStack_40 = *(int *)(dsc + 0x28) + *(int *)(dsc + 0x30) + coords[3];
  iStack_b4 = (iStack_4c - *(int *)(dsc + 0x24) / 2) + -1;
  iStack_ac = *(int *)(dsc + 0x24) / 2 + iStack_44 + 1;
  iStack_b0 = (iStack_48 - *(int *)(dsc + 0x24) / 2) + -1;
  iStack_a8 = *(int *)(dsc + 0x24) / 2 + iStack_40 + 1;
  iStack_8c = *(int *)(task + 0x48);
  iVar6 = *(int *)(iStack_8c + 4);
  iVar7 = *(int *)(iStack_8c + 8);
  uStack_28 = color;
  uStack_74 = audio_uart_lv_area_width_451598(iStack_8c + 4);
  uStack_3c = audio_uart_lv_area_height_4515a4(iStack_8c + 4);
  uStack_94 = *(uint *)(task + 0x4c);
  bVar1 = audio_uart_lv_area_intersect_450bcc((uint)auStack_38,(uint)&iStack_b4,task + 0x38);
  if (bVar1 != 0) {
    g2c_nemavg_area_copy_540024((uint)&iStack_84,(uint)coords);
    audio_uart_lv_area_expand_450b98((uint)&iStack_84,-1,-1);
    uVar8 = *(uint *)(dsc + 0x1c);
    iVar2 = audio_uart_lv_area_width_451598((uint)&iStack_84);
    iVar3 = audio_uart_lv_area_height_4515a4((uint)&iStack_84);
    if (iVar2 < iVar3) {
      iVar2 = audio_uart_lv_area_width_451598((uint)&iStack_84);
    }
    else {
      iVar2 = audio_uart_lv_area_height_4515a4((uint)&iStack_84);
    }
    if (iVar2 >> 1 < (int)uVar8) {
      uVar8 = iVar2 >> 1;
    }
    iVar2 = *(int *)(dsc + 0x1c);
    iVar3 = audio_uart_lv_area_width_451598((uint)&iStack_4c);
    iVar4 = audio_uart_lv_area_height_4515a4((uint)&iStack_4c);
    if (iVar3 < iVar4) {
      iVar3 = audio_uart_lv_area_width_451598((uint)&iStack_4c);
    }
    else {
      iVar3 = audio_uart_lv_area_height_4515a4((uint)&iStack_4c);
    }
    if (iVar3 >> 1 < iVar2) {
      iVar2 = iVar3 >> 1;
    }
    uVar9 = iVar2 + *(int *)(dsc + 0x24);
    uStack_88 = lv_malloc(uVar9 * uVar9);
    if (uStack_88 == 0) {
      lv_log_add(3,(("D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\ambiq\\lv_draw_ambiq_box_shadow.c" /* stock 0x6cd24c */)),0x6f,(("lv_draw_ambiq_box_shadow" /* stock 0x76c85c */)),(("Asserted at expression: %s (%s)" /* stock 0x760ad0 */)));
      do {
      } while( true );
    }
    bStack_90 = *(byte *)(dsc + 0x35) & 1;
    iVar2 = audio_uart_lv_area_width_451598((uint)&iStack_b4);
    iVar3 = iVar2 / 2 + iStack_b4;
    iVar2 = audio_uart_lv_area_height_4515a4((uint)&iStack_b4);
    iVar2 = iVar2 / 2 + iStack_b0;
    uVar5 = audio_uart_ambiq_stencil_adjust_4b0b5a(uStack_94,uStack_74,uStack_74);
    if ((uVar5 & 0xff) == 1) {
      audio_uart_nema_bind_tex_4b1298
                (1,*(uint *)(*(int *)(uStack_94 + 0x40) + 0x10),
                 *(uint *)(*(int *)(uStack_94 + 0x40) + 4) & 0xffff,
                 *(uint *)(*(int *)(uStack_94 + 0x40) + 4) >> 0x10,8,0xffffffff,0);
      audio_uart_nema_bind_tex_4b1298(2,uStack_88,uVar9,uVar9,8,0xffffffff,0);
      audio_uart_ambiq_texture_setup_4b06c0(uStack_94,1,1,2,0xffffffff,0);
      audio_uart_display_graphics_target_4b1516(0,0,uStack_74,uStack_3c);
      iStack_cc = iStack_ac;
      iStack_d4 = (iStack_ac - uVar9) + 1;
      iStack_d0 = iStack_b0;
      iStack_c8 = uVar9 + iStack_b0 + -1;
      g2c_nemavg_area_copy_540024((uint)&iStack_a4,(uint)&iStack_d4);
      iStack_a4 = iVar3;
      if (iVar3 < iStack_d4) {
        iStack_a4 = iStack_d4;
      }
      iStack_98 = iVar2;
      if (iStack_c8 < iVar2) {
        iStack_98 = iStack_c8;
      }
      bVar1 = audio_uart_lv_area_intersect_450bcc((uint)&iStack_c4,(uint)&iStack_a4,task + 0x38);
      if ((bVar1 != 0) &&
         (uVar5 = audio_uart_lv_area_contains_450f28((uint)&iStack_c4,(uint)&iStack_84,uVar8),
         uVar5 == 0)) {
        audio_uart_nema_matrix_identity_561810((uint)auStack_70);
        fVar11 = (float)VectorSignedToFloat(iVar7 - iStack_d0,G2C_FPSCR_RMODE_RN);
        fVar10 = (float)VectorSignedToFloat(iVar6 - iStack_d4,G2C_FPSCR_RMODE_RN);
        audio_uart_nema_matrix_translate_561856(fVar10,fVar11,(uint)auStack_70);
        audio_uart_nema_matrix_upload_5226e8((uint)auStack_70);
        audio_uart_nema_mask_rectangle_522ae0
                  (iStack_c4 - iVar6,iStack_c0 - iVar7,(iStack_bc - iStack_c4) + 1,
                   (iStack_b8 - iStack_c0) + 1);
      }
      iStack_cc = iStack_ac;
      iStack_d4 = (iStack_ac - uVar9) + 1;
      iStack_d0 = (iStack_a8 - uVar9) + 1;
      iStack_c8 = iStack_a8;
      g2c_nemavg_area_copy_540024((uint)&iStack_a4,(uint)&iStack_d4);
      iStack_a4 = iVar3;
      if (iVar3 < iStack_d4) {
        iStack_a4 = iStack_d4;
      }
      iStack_a0 = iStack_d0;
      if (iStack_d0 <= iVar2 + 1) {
        iStack_a0 = iVar2 + 1;
      }
      bVar1 = audio_uart_lv_area_intersect_450bcc((uint)&iStack_c4,(uint)&iStack_a4,task + 0x38);
      if ((bVar1 != 0) &&
         (uVar5 = audio_uart_lv_area_contains_450f28((uint)&iStack_c4,(uint)&iStack_84,uVar8),
         uVar5 == 0)) {
        audio_uart_nema_matrix_identity_561810((uint)auStack_70);
        uStack_60 = g2c_float_to_bits(((-1.0f)));
        uStack_68 = g2c_float_to_bits(VectorSignedToFloat(iStack_d4 - iVar6,G2C_FPSCR_RMODE_RN));
        uStack_5c = g2c_float_to_bits(VectorSignedToFloat((iStack_d0 + uVar9 + -1) - iVar7,
                                        G2C_FPSCR_RMODE_RN));
        audio_uart_nema_matrix_finalize_561b38((uint)auStack_70);
        audio_uart_nema_matrix_upload_5226e8((uint)auStack_70);
        audio_uart_nema_mask_rectangle_522ae0
                  (iStack_c4 - iVar6,iStack_c0 - iVar7,(iStack_bc - iStack_c4) + 1,
                   (iStack_b8 - iStack_c0) + 1);
      }
      iStack_d4 = iStack_b4;
      iStack_cc = uVar9 + iStack_b4 + -1;
      iStack_d0 = (iStack_a8 - uVar9) + 1;
      iStack_c8 = iStack_a8;
      g2c_nemavg_area_copy_540024((uint)&iStack_a4,(uint)&iStack_d4);
      iStack_a0 = iStack_d0;
      if (iStack_d0 <= iVar2 + 1) {
        iStack_a0 = iVar2 + 1;
      }
      iStack_9c = iStack_cc;
      if (iVar3 + -1 <= iStack_cc) {
        iStack_9c = iVar3 + -1;
      }
      bVar1 = audio_uart_lv_area_intersect_450bcc((uint)&iStack_c4,(uint)&iStack_a4,task + 0x38);
      if ((bVar1 != 0) &&
         (uVar5 = audio_uart_lv_area_contains_450f28((uint)&iStack_c4,(uint)&iStack_84,uVar8),
         uVar5 == 0)) {
        audio_uart_nema_matrix_identity_561810((uint)auStack_70);
        auStack_70[0] = 0xbf800000;
        uStack_60 = 0xbf800000;
        uStack_68 = g2c_float_to_bits(VectorSignedToFloat((iStack_d4 + uVar9 + -1) - iVar6,
                                        G2C_FPSCR_RMODE_RN));
        uStack_5c = g2c_float_to_bits(VectorSignedToFloat((iStack_d0 + uVar9 + -1) - iVar7,
                                        G2C_FPSCR_RMODE_RN));
        audio_uart_nema_matrix_finalize_561b38((uint)auStack_70);
        audio_uart_nema_matrix_upload_5226e8((uint)auStack_70);
        audio_uart_nema_mask_rectangle_522ae0
                  (iStack_c4 - iVar6,iStack_c0 - iVar7,(iStack_bc - iStack_c4) + 1,
                   (iStack_b8 - iStack_c0) + 1);
      }
      iStack_d4 = iStack_b4;
      iStack_cc = uVar9 + iStack_b4 + -1;
      iStack_d0 = iStack_b0;
      iStack_c8 = uVar9 + iStack_b0 + -1;
      g2c_nemavg_area_copy_540024((uint)&iStack_a4,(uint)&iStack_d4);
      iStack_9c = iStack_cc;
      if (iVar3 + -1 <= iStack_cc) {
        iStack_9c = iVar3 + -1;
      }
      iStack_98 = iVar2;
      if (iStack_c8 < iVar2) {
        iStack_98 = iStack_c8;
      }
      bVar1 = audio_uart_lv_area_intersect_450bcc((uint)&iStack_c4,(uint)&iStack_a4,task + 0x38);
      if ((bVar1 != 0) &&
         (uVar5 = audio_uart_lv_area_contains_450f28((uint)&iStack_c4,(uint)&iStack_84,uVar8),
         uVar5 == 0)) {
        audio_uart_nema_matrix_identity_561810((uint)auStack_70);
        auStack_70[0] = g2c_float_to_bits(((-1.0f)));
        uStack_68 = g2c_float_to_bits(VectorSignedToFloat((iStack_d4 + uVar9 + -1) - iVar6,
                                        G2C_FPSCR_RMODE_RN));
        uStack_5c = g2c_float_to_bits(VectorSignedToFloat(iStack_d0 - iVar7,G2C_FPSCR_RMODE_RN));
        audio_uart_nema_matrix_finalize_561b38((uint)auStack_70);
        audio_uart_nema_matrix_upload_5226e8((uint)auStack_70);
        audio_uart_nema_mask_rectangle_522ae0
                  (iStack_c4 - iVar6,iStack_c0 - iVar7,(iStack_bc - iStack_c4) + 1,
                   (iStack_b8 - iStack_c0) + 1);
      }
      iStack_d4 = uVar9 + iStack_b4;
      iStack_cc = iStack_ac - uVar9;
      iStack_d0 = iStack_b0;
      iStack_c8 = uVar9 + iStack_b0 + -1;
      g2c_nemavg_area_copy_540024((uint)&iStack_a4,(uint)&iStack_d4);
      iStack_98 = iVar2;
      if (iStack_c8 < iVar2) {
        iStack_98 = iStack_c8;
      }
      bVar1 = audio_uart_lv_area_intersect_450bcc((uint)&iStack_c4,(uint)&iStack_a4,task + 0x38);
      if ((bVar1 != 0) &&
         (uVar5 = audio_uart_lv_area_contains_450f28((uint)&iStack_c4,(uint)&iStack_84,uVar8),
         uVar5 == 0)) {
        audio_uart_nema_matrix_identity_561810((uint)auStack_70);
        fVar11 = (float)VectorSignedToFloat(iVar7 - iStack_d0,G2C_FPSCR_RMODE_RN);
        fVar10 = (float)VectorSignedToFloat(iVar6 - iStack_cc,G2C_FPSCR_RMODE_RN);
        audio_uart_nema_matrix_translate_561856(fVar10,fVar11,(uint)auStack_70);
        audio_uart_nema_matrix_upload_5226e8((uint)auStack_70);
        audio_uart_nema_mask_rectangle_522ae0
                  (iStack_c4 - iVar6,iStack_c0 - iVar7,(iStack_bc - iStack_c4) + 1,
                   (iStack_b8 - iStack_c0) + 1);
      }
      iStack_d4 = uVar9 + iStack_b4;
      iStack_cc = iStack_ac - uVar9;
      iStack_d0 = (iStack_a8 - uVar9) + 1;
      iStack_c8 = iStack_a8;
      g2c_nemavg_area_copy_540024((uint)&iStack_a4,(uint)&iStack_d4);
      iStack_a0 = iStack_d0;
      if (iStack_d0 <= iVar2 + 1) {
        iStack_a0 = iVar2 + 1;
      }
      bVar1 = audio_uart_lv_area_intersect_450bcc((uint)&iStack_c4,(uint)&iStack_a4,task + 0x38);
      if ((bVar1 != 0) &&
         (uVar5 = audio_uart_lv_area_contains_450f28((uint)&iStack_c4,(uint)&iStack_84,uVar8),
         uVar5 == 0)) {
        audio_uart_nema_matrix_identity_561810((uint)auStack_70);
        uStack_60 = g2c_float_to_bits(((-1.0f)));
        uStack_68 = g2c_float_to_bits(VectorSignedToFloat(iStack_cc - iVar6,G2C_FPSCR_RMODE_RN));
        uStack_5c = g2c_float_to_bits(VectorSignedToFloat((iStack_d0 + uVar9 + -1) - iVar7,
                                        G2C_FPSCR_RMODE_RN));
        audio_uart_nema_matrix_finalize_561b38((uint)auStack_70);
        audio_uart_nema_matrix_upload_5226e8((uint)auStack_70);
        audio_uart_nema_mask_rectangle_522ae0
                  (iStack_c4 - iVar6,iStack_c0 - iVar7,(iStack_bc - iStack_c4) + 1,
                   (iStack_b8 - iStack_c0) + 1);
      }
      iStack_d4 = (iStack_ac - uVar9) + 1;
      iStack_cc = iStack_ac;
      iStack_d0 = uVar9 + iStack_b0;
      iStack_c8 = iStack_a8 - uVar9;
      g2c_nemavg_area_copy_540024((uint)&iStack_a4,(uint)&iStack_d4);
      iStack_a0 = iStack_d0;
      if (iVar2 + 1 <= iStack_d0) {
        iStack_a0 = iVar2 + 1;
      }
      iStack_98 = iVar2;
      if (iVar2 < iStack_c8) {
        iStack_98 = iStack_c8;
      }
      iStack_a4 = iVar3;
      if (iVar3 < iStack_d4) {
        iStack_a4 = iStack_d4;
      }
      bVar1 = audio_uart_lv_area_intersect_450bcc((uint)&iStack_c4,(uint)&iStack_a4,task + 0x38);
      if ((bVar1 != 0) &&
         (uVar5 = audio_uart_lv_area_contains_450f28((uint)&iStack_c4,(uint)&iStack_84,uVar8),
         uVar5 == 0)) {
        audio_uart_nema_matrix_identity_561810((uint)auStack_70);
        fVar11 = (float)VectorSignedToFloat(uVar9 + (iVar7 - iStack_d0) + -1,
                                            G2C_FPSCR_RMODE_RN);
        fVar10 = (float)VectorSignedToFloat(iVar6 - iStack_d4,G2C_FPSCR_RMODE_RN);
        audio_uart_nema_matrix_translate_561856(fVar10,fVar11,(uint)auStack_70);
        audio_uart_nema_matrix_upload_5226e8((uint)auStack_70);
        audio_uart_nema_mask_rectangle_522ae0
                  (iStack_c4 - iVar6,iStack_c0 - iVar7,(iStack_bc - iStack_c4) + 1,
                   (iStack_b8 - iStack_c0) + 1);
      }
      iStack_d4 = iStack_b4;
      iStack_cc = uVar9 + iStack_b4 + -1;
      iStack_d0 = uVar9 + iStack_b0;
      iStack_c8 = iStack_a8 - uVar9;
      g2c_nemavg_area_copy_540024((uint)&iStack_a4,(uint)&iStack_d4);
      iStack_a0 = iStack_d0;
      if (iVar2 + 1 <= iStack_d0) {
        iStack_a0 = iVar2 + 1;
      }
      iStack_98 = iVar2;
      if (iVar2 < iStack_c8) {
        iStack_98 = iStack_c8;
      }
      iStack_9c = iStack_cc;
      if (iVar3 + -1 <= iStack_cc) {
        iStack_9c = iVar3 + -1;
      }
      bVar1 = audio_uart_lv_area_intersect_450bcc((uint)&iStack_c4,(uint)&iStack_a4,task + 0x38);
      if ((bVar1 != 0) &&
         (uVar5 = audio_uart_lv_area_contains_450f28((uint)&iStack_c4,(uint)&iStack_84,uVar8),
         uVar5 == 0)) {
        audio_uart_nema_matrix_identity_561810((uint)auStack_70);
        auStack_70[0] = g2c_float_to_bits(((-1.0f)));
        uStack_68 = g2c_float_to_bits(VectorSignedToFloat((iStack_d4 + uVar9 + -1) - iVar6,
                                        G2C_FPSCR_RMODE_RN));
        uStack_5c = g2c_float_to_bits(VectorSignedToFloat(((iStack_d0 - uVar9) + 1) - iVar7,
                                        G2C_FPSCR_RMODE_RN));
        audio_uart_nema_matrix_finalize_561b38((uint)auStack_70);
        audio_uart_nema_matrix_upload_5226e8((uint)auStack_70);
        audio_uart_nema_mask_rectangle_522ae0
                  (iStack_c4 - iVar6,iStack_c0 - iVar7,(iStack_bc - iStack_c4) + 1,
                   (iStack_b8 - iStack_c0) + 1);
      }
      uVar5 = 0xffffffff;
      audio_uart_ambiq_texture_setup_4b06c0(uStack_94,1,1,0xffffffff,0xffffffff,0);
      display_driver_nema_select_522a16(0xff000000);
      iStack_d4 = uVar9 + iStack_b4;
      iStack_cc = iStack_ac - uVar9;
      iStack_d0 = uVar9 + iStack_b0;
      iStack_c8 = iStack_a8 - uVar9;
      g2c_nemavg_area_copy_540024((uint)&iStack_a4,(uint)&iStack_d4);
      iStack_a0 = iStack_d0;
      if (iVar2 + 1 <= iStack_d0) {
        iStack_a0 = iVar2 + 1;
      }
      iStack_98 = iVar2;
      if (iVar2 < iStack_c8) {
        iStack_98 = iStack_c8;
      }
      bVar1 = audio_uart_lv_area_intersect_450bcc((uint)&iStack_c4,(uint)&iStack_a4,task + 0x38);
      if ((bVar1 != 0) &&
         (uVar9 = audio_uart_lv_area_contains_450f28((uint)&iStack_c4,(uint)&iStack_84,uVar8),
         uVar9 == 0)) {
        audio_uart_nema_mask_rectangle_522ae0
                  (iStack_c4 - iVar6,iStack_c0 - iVar7,(iStack_bc - iStack_c4) + 1,
                   (iStack_b8 - iStack_c0) + 1);
      }
      if (bStack_90 == 0) {
        display_driver_nema_select_522a16(0);
        iVar2 = audio_uart_lv_area_height_4515a4((uint)&iStack_84);
        iVar3 = audio_uart_lv_area_width_451598((uint)&iStack_84);
        g2c_nema_raster_rounded_rect_522b30(iStack_84 - iVar6,iStack_80 - iVar7,iVar3,iVar2,uVar8);
        uVar5 = uVar8;
      }
      if (*(char *)(iStack_8c + 0x14) == '\x10') {
        uVar8 = 0x501;
      }
      else {
        uVar8 = 0x504;
      }
      audio_uart_nema_matrix_identity_561810((uint)auStack_70);
      audio_uart_nema_matrix_upload_5226e8((uint)auStack_70);
      /* Evidence (wave17): stock 0x540938 mov r0,sp; adds r1,r5,#32; movs r2,#3; bl memcpy;
       * 0x540948 ldr r0,[sp] -> color_resolve arg0. [sp] last held uVar5 (0x54084a str -1 /
       * 0x540906 str r8), so byte 3 keeps that value. the decompiler dropped the memcpy-into-arg dependency. */
      g2c_sp0_540036 = uVar5;
      memcpy((uint)&g2c_sp0_540036,dsc + 0x20,3);
      uVar9 = audio_uart_ambiq_color_resolve_4b06a8(g2c_sp0_540036,(uint)*(byte *)(dsc + 0x34));
      if (*(char *)(dsc + 0x34) == -1) {
        display_driver_gpu_enable_4b0748(uStack_94,uVar8);
      }
      else {
        display_driver_gpu_enable_4b0748(uStack_94,uVar8 | 0x8000000);
        audio_uart_ambiq_image_alpha_513e2e(uVar9);
      }
      audio_uart_ambiq_texture_color_4b146c(uVar9);
      audio_uart_display_graphics_finish_4b1548();
      iVar2 = audio_uart_lv_area_height_4515a4((uint)&iStack_b4);
      iVar3 = audio_uart_lv_area_width_451598((uint)&iStack_b4);
      audio_uart_nema_mask_rectangle_522ae0(iStack_b4 - iVar6,iStack_b0 - iVar7,iVar3,iVar2);
      uVar8 = audio_uart_nema_cl_get_bound_5144fa();
      audio_uart_nema_cl_submit_514cf2(uVar8);
      audio_uart_nema_cl_wait_514d00(uVar8);
      audio_uart_nema_cl_rewind_514384(uVar8);
      lv_free(uStack_88);
    }
    else {
      lv_free(uStack_88);
    }
  }
  return;
}
#undef iStack_d4
#undef iStack_d0
#undef iStack_cc
#undef iStack_c8
#undef iStack_c4
#undef iStack_c0
#undef iStack_bc
#undef iStack_b8
#undef iStack_b4
#undef iStack_b0
#undef iStack_ac
#undef iStack_a8
#undef iStack_a4
#undef iStack_a0
#undef iStack_9c
#undef iStack_98
#undef uStack_94
#undef bStack_90
#undef iStack_8c
#undef uStack_88
#undef iStack_84
#undef iStack_80
#undef uStack_74
#undef auStack_70
#undef uStack_68
#undef uStack_60
#undef uStack_5c
#undef iStack_4c
#undef iStack_48
#undef iStack_44
#undef iStack_40
#undef uStack_3c
#undef auStack_38
#undef uStack_28


  

/* ---- lifted 0x5619f2 ---- */

void g2c_nema_vg_mat_mul_5619f2(float *a,float *b)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  float fVar8;
  float fVar9;
  float fVar10;
  float fVar11;
  float fVar12;
  float fVar13;
  float fVar14;
  float fVar15;
  float fVar16;
  float fVar17;
  float fVar18;
  
  fVar5 = b[1];
  fVar6 = *a;
  fVar3 = b[4];
  fVar4 = a[1];
  fVar16 = a[3];
  fVar17 = *b;
  fVar1 = b[7];
  fVar2 = a[2];
  fVar13 = b[3];
  fVar14 = a[4];
  fVar9 = b[2];
  fVar10 = b[6];
  fVar11 = a[5];
  fVar18 = a[6];
  fVar8 = b[5];
  fVar15 = a[7];
  fVar7 = b[8];
  fVar12 = a[8];
  *a = fVar6 * fVar17 + fVar4 * fVar13 + fVar2 * fVar10;
  a[1] = fVar6 * fVar5 + fVar4 * fVar3 + fVar2 * fVar1;
  a[2] = fVar6 * fVar9 + fVar4 * fVar8 + fVar2 * fVar7;
  a[3] = fVar16 * fVar17 + fVar14 * fVar13 + fVar11 * fVar10;
  a[4] = fVar16 * fVar5 + fVar14 * fVar3 + fVar11 * fVar1;
  a[5] = fVar16 * fVar9 + fVar14 * fVar8 + fVar11 * fVar7;
  a[6] = fVar18 * fVar17 + fVar15 * fVar13 + fVar12 * fVar10;
  a[7] = fVar18 * fVar5 + fVar15 * fVar3 + fVar12 * fVar1;
  a[8] = fVar18 * fVar9 + fVar15 * fVar8 + fVar12 * fVar7;
  return;
}

  

/* ---- lifted 0x56395c ---- */

void g2c_nema_vg_path_clear_56395c(void)

{
  int *piVar1;
  int iVar2;
  uint uVar3;
  /* Evidence (wave10): FPSCR scratch was declared here but never read; removed. */
  float fVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  
  piVar1 = (((int *)&audio_uart_nema_vg_context_cell));
  iVar2 = *(((int *)&audio_uart_nema_vg_context_cell));
  *(undefined1 *)(iVar2 + 0x2e5) = 1;
  *(undefined4 *)(iVar2 + 0x2fc) = 0;
  *(undefined4 *)(iVar2 + 0x2f8) = 0;
  *(undefined1 *)(iVar2 + 0x2e8) = 0;
  *(undefined1 *)(iVar2 + 0x2e9) = 0;
  if (*(float *)(iVar2 + 0x300) < 0.0f) {
    fVar4 = -*(float *)(iVar2 + 0x300);
    fVar5 = *(float *)(iVar2 + 0x2f4);
    fVar6 = fVar4 / fVar5;
    fVar7 = (float)VectorSignedToFloat((int)fVar6,G2C_FPSCR_RMODE_RN);
    if (0.0f <= fVar6) {
      uVar3 = -(uint)(fVar6 < fVar7);
    }
    else {
      uVar3 = (uint)(fVar7 < fVar6);
    }
    fVar6 = (float)VectorSignedToFloat((int)fVar6 + uVar3,G2C_FPSCR_RMODE_RN
                                      );
    *(float *)(iVar2 + 0x300) = (fVar6 * fVar5 - fVar4) + fVar5;
  }
  *(undefined4 *)(iVar2 + 0x304) = *(undefined4 *)(*piVar1 + 0x300);
  return;
}

  

/* ---- lifted 0x5639e8 ---- */


uint g2c_nema_vg_path_bounds_5639e8(float a,float b,float c,float d)

{
  char cVar1;
  undefined8 uVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  undefined8 uVar5;
  float fVar6;
  int *piVar7;
  uint a_00;
  int iVar8;
  int iVar9;
  int iVar10;
  uint uVar11;
  uint c_00;
  uint d_00;
  uint uVar12;
  uint uVar13;
  undefined4 uVar14;
  uint uVar15;
  undefined4 uVar16;
  undefined4 uVar17;
  undefined4 uVar18;
  undefined4 uVar19;
  byte bVar20;
  bool bVar21;
  float fVar22;
  float fVar23;
  float fVar24;
  float a_01;
  float fVar25;
  float b_00;
  float c_01;
  float fVar26;
  float d_01;
  float d_02;
  float e;
  float e_00;
  float fVar27;
  float fVar28;
  float fVar29;
  /* Stock frame of 0x5639e8 as one block: locals keep the entry-SP offsets Ghidra named them by
   * (X_Stack_NN at g2c_frame_5639e8[0x90-0xNN]) so &local passed to callees spans its stock neighbours. */
  unsigned char g2c_frame_5639e8[0x90] __attribute__((aligned(8)));
  typedef float __attribute__((may_alias)) g2c_fa_float;
#define fStack_8c (*(g2c_fa_float *)(void *)&g2c_frame_5639e8[0x90-0x8c])
#define fStack_88 (*(g2c_fa_float *)(void *)&g2c_frame_5639e8[0x90-0x88])
#define fStack_84 (*(g2c_fa_float *)(void *)&g2c_frame_5639e8[0x90-0x84])
#define fStack_80 (*(g2c_fa_float *)(void *)&g2c_frame_5639e8[0x90-0x80])
  typedef uint __attribute__((may_alias)) g2c_fa_uint;
#define uStack_7c (*(g2c_fa_uint *)(void *)&g2c_frame_5639e8[0x90-0x7c])
  typedef undefined4 __attribute__((may_alias)) g2c_fa_undefined4;
#define uStack_78 (*(g2c_fa_undefined4 *)(void *)&g2c_frame_5639e8[0x90-0x78])
#define fStack_74 (*(g2c_fa_float *)(void *)&g2c_frame_5639e8[0x90-0x74])
#define uStack_70 (*(g2c_fa_undefined4 *)(void *)&g2c_frame_5639e8[0x90-0x70])
  
  iVar9 = *(((int *)&audio_uart_nema_vg_context_cell));
  fVar27 = c - a;
  fVar28 = d - b;
  fVar22 = g2c_nema_vg_sqrt_524218(fVar27 * fVar27 + fVar28 * fVar28);
  fVar6 = (0.05000000447034836f);
  fVar22 = (float)VectorSignedToFloat((int)(fVar22 + 0.5f),G2C_FPSCR_RMODE_RN);
  fVar28 = fVar28 / fVar22;
  fVar27 = fVar27 / fVar22;
  do {
    fVar23 = (0x0u);
    /* Evidence (wave12): stock 0x563e00 vcmp.f32 s16,#0 / vmrs / beq.w 0x563f2e (return path). */
    if (fVar22 == 0.0f) {
      return 0;
    }
    if (*(int *)(iVar9 + 0x2f8) == 0) {
      uVar15 = 1;
      fVar29 = *(float *)(*(int *)(iVar9 + 0x2ec) + *(int *)(iVar9 + 0x2fc) * 4);
    }
    else {
      fVar29 = (float)VectorUnsignedToFloat(*(int *)(iVar9 + 0x2f8),G2C_FPSCR_RMODE_RN) /* vcvt.f32.u32 @0x563e1a; RMode RN, see G2C_FPSCR_RMODE_RN */;
      uVar15 = -(uint)(*(char *)(iVar9 + 0x2e8) == '\0') >> 0x1f;
    }
    if (0.0f <= fVar22 - fVar29) {
      uVar12 = 1;
      uVar11 = *(int *)(iVar9 + 0x2fc) + 1;
      if (uVar11 < *(uint *)(iVar9 + 0x2f0)) {
        *(uint *)(iVar9 + 0x2fc) = uVar11;
      }
      else {
        *(undefined4 *)(iVar9 + 0x2fc) = 0;
      }
    }
    else {
      fVar23 = (float)VectorFloatToUnsigned(fVar29 - fVar22,3);
      uVar12 = 0;
      fVar29 = fVar22;
    }
    *(float *)(iVar9 + 0x2f8) = fVar23;
    fVar24 = *(float *)(iVar9 + 0x304);
    fVar23 = (0x0u);
    fVar25 = fVar29;
    /* Evidence (wave12): stock 0x563a98 vcmp.f32 s0,#0 / blt 0x563ae4 skips this block, so it runs
     * when the value is ordered and >= 0. Inner: 0x563aa6 vcmp.f32 s1,#0 / ble 0x563ad0 (taken when
     * <= 0 or unordered). The old Z bit here came from the incoming FPSCR, not from this compare. */
    if (fVar24 >= 0.0f) {
      fVar25 = fVar29 - fVar24;
      if (!(fVar25 > 0.0f)) {
        fVar23 = fVar24 - fVar29;
        fVar25 = (0x0u);
      }
    }
    *(float *)(iVar9 + 0x304) = fVar23;
    piVar7 = (((int *)&audio_uart_nema_vg_context_cell));
    iVar10 = *(((int *)&audio_uart_nema_vg_context_cell));
    fVar22 = fVar22 - fVar25;
    fVar29 = a + fVar27 * fVar25;
    fVar24 = b + fVar28 * fVar25;
    bVar21 = *(char *)(iVar10 + 0x1c1) != '\0';
    cVar1 = '\0';
    if (bVar21) {
      cVar1 = *(char *)(iVar9 + 0x2e9);
    }
    if (((bVar21 && cVar1 != '\0') &&
        /* stock 0x563b1e vcmp.f32 s16,#0 / beq 0x563b46 */
        fVar22 == 0.0f) && (uVar12 != 0)) {
      uVar12 = 0;
    }
    bVar20 = 0;
    if (*(char *)(iVar9 + 0x2e5) == '\x01') {
      /* stock 0x563b2e vcmpeq.f32 s0,#0 / vmrseq / bne.w 0x563de8 */
      bVar20 = (byte)(fVar23 == 0.0f);
    }
    if (bVar20 != 0) {
      if (((*(char *)(iVar9 + 0x2e8) == '\0') && (*(char *)(iVar9 + 0x2eb) == '\0')) ||
         (*(char *)(iVar9 + 0x2ea) == '\0')) {
        uVar13 = 0;
      }
      else {
        uVar13 = (uint)(*(char *)(iVar9 + 0x2e6) == '\x01') & (uVar15 ^ 1);
      }
      if ((int)((uint)*(byte *)(iVar10 + 0x7d) << 0x1b) < 0) {
        d_00 = 0;
        c_00 = 0;
        uVar11 = 0;
        a_00 = 0;
      }
      else {
        d_00 = -(uint)(*(char *)(iVar10 + 0x2e0) == '\0') >> 0x1f;
        uVar11 = -(uint)(*(char *)(iVar10 + 0x2e1) == '\0') >> 0x1f;
        if ((uVar15 & uVar12) == 0) {
          if (uVar12 == 1 && uVar15 == 0) {
            d_00 = 0;
          }
          else if (uVar15 == 1 && uVar12 == 0) {
            uVar11 = 0;
          }
          else {
            d_00 = 0;
            uVar11 = 0;
          }
        }
        c_00 = 1;
        a_00 = 1;
      }
      uVar11 = audio_uart_nema_stencil_save_52266e(a_00,uVar11,c_00,d_00);
      /* stock 0x563bc4 vcmp.f32 s22,#0 / vmrs / bne 0x563c20 */
      if (fVar25 != 0.0f) {
        iVar10 = *piVar7;
        if (*(int *)(iVar10 + 0x110) == 0) {
          g2c_nema_vg_emit_tri_516bde(a,b,fVar29,fVar24,1,*(int *)(iVar10 + 0x88));
        }
        else {
          fVar26 = fVar29 - a;
          fVar25 = fVar24 - b;
          fVar23 = audio_uart_float_sqrt_4397a8(fVar26 * fVar26 + fVar25 * fVar25);
          fVar25 = *(float *)(iVar10 + 0x130) * 0.5f * fVar25 * (1.0f / fVar23);
          fVar23 = *(float *)(iVar10 + 0x134) * 0.5f * fVar26 * (1.0f / fVar23);
          *(float *)(iVar10 + 0x308) = a - fVar25;
          *(float *)(iVar10 + 0x30c) = fVar23 + b;
          *(float *)(iVar10 + 0x310) = fVar29 - fVar25;
          *(float *)(iVar10 + 0x314) = fVar23 + fVar24;
          *(float *)(iVar10 + 0x318) = fVar25 + fVar29;
          *(float *)(iVar10 + 0x31c) = fVar24 - fVar23;
          *(float *)(iVar10 + 800) = fVar25 + a;
          *(float *)(iVar10 + 0x324) = b - fVar23;
          g2c_nema_vg_emit_verts_516b34
                    (*(float *)(iVar10 + 0x308),*(float *)(iVar10 + 0x30c),
                     *(float *)(iVar10 + 0x310),*(float *)(iVar10 + 0x314),
                     *(float *)(iVar10 + 0x318),*(float *)(iVar10 + 0x31c),*(float *)(iVar10 + 800),
                     *(float *)(iVar10 + 0x324));
          iVar8 = *piVar7;
          uVar14 = *(undefined4 *)(iVar10 + 0x30c);
          uVar16 = *(undefined4 *)(iVar10 + 0x310);
          uVar17 = *(undefined4 *)(iVar10 + 0x314);
          uVar18 = *(undefined4 *)(iVar10 + 0x318);
          *(undefined4 *)(iVar8 + 400) = *(undefined4 *)(iVar10 + 0x308);
          *(undefined4 *)(iVar8 + 0x194) = uVar14;
          *(undefined4 *)(iVar8 + 0x198) = uVar16;
          *(undefined4 *)(iVar8 + 0x19c) = uVar17;
          *(undefined4 *)(iVar8 + 0x1a0) = uVar18;
          uVar14 = *(undefined4 *)(iVar10 + 800);
          uVar16 = *(undefined4 *)(iVar10 + 0x324);
          uVar17 = *(undefined4 *)(iVar10 + 0x328);
          uVar18 = *(undefined4 *)(iVar10 + 0x32c);
          *(undefined4 *)(iVar8 + 0x1a4) = *(undefined4 *)(iVar10 + 0x31c);
          *(undefined4 *)(iVar8 + 0x1a8) = uVar14;
          *(undefined4 *)(iVar8 + 0x1ac) = uVar16;
          *(undefined4 *)(iVar8 + 0x1b0) = uVar17;
          *(undefined4 *)(iVar8 + 0x1b4) = uVar18;
          *(undefined4 *)(iVar8 + 0x1b8) = *(undefined4 *)(iVar10 + 0x330);
          iVar8 = *piVar7;
          uVar14 = *(undefined4 *)(iVar10 + 0x30c);
          uVar16 = *(undefined4 *)(iVar10 + 0x310);
          uVar17 = *(undefined4 *)(iVar10 + 0x314);
          uVar18 = *(undefined4 *)(iVar10 + 0x318);
          uVar19 = *(undefined4 *)(iVar10 + 0x31c);
          *(undefined4 *)(iVar8 + 0x138) = *(undefined4 *)(iVar10 + 0x308);
          *(undefined4 *)(iVar8 + 0x13c) = uVar14;
          *(undefined4 *)(iVar8 + 0x140) = uVar16;
          *(undefined4 *)(iVar8 + 0x144) = uVar17;
          *(undefined4 *)(iVar8 + 0x148) = uVar18;
          *(undefined4 *)(iVar8 + 0x14c) = uVar19;
          uVar14 = *(undefined4 *)(iVar10 + 0x324);
          uVar16 = *(undefined4 *)(iVar10 + 0x328);
          uVar17 = *(undefined4 *)(iVar10 + 0x32c);
          uVar18 = *(undefined4 *)(iVar10 + 0x330);
          *(undefined4 *)(iVar8 + 0x150) = *(undefined4 *)(iVar10 + 800);
          *(undefined4 *)(iVar8 + 0x154) = uVar14;
          *(undefined4 *)(iVar8 + 0x158) = uVar16;
          *(undefined4 *)(iVar8 + 0x15c) = uVar17;
          *(undefined4 *)(iVar8 + 0x160) = uVar18;
          if (uVar13 != 0) {
            iVar10 = *piVar7;
            fVar23 = ABS(*(float *)(iVar10 + 0x358) * *(float *)(iVar10 + 0x330) -
                         *(float *)(iVar10 + 0x35c) * *(float *)(iVar10 + 0x32c));
            /* stock 0x563d52 vcmp.f32 s0,s19 / vmrs / blt 0x563e28 (emit block; lt includes unordered) */
            if (!(fVar23 >= fVar6)) {
              uVar2 = *(undefined8 *)(iVar10 + 0x33c);
              uVar3 = *(undefined8 *)(iVar10 + 0x308);
              uVar4 = *(undefined8 *)(iVar10 + 0x344);
              uVar5 = *(undefined8 *)(iVar10 + 800);
              bVar21 = -1 < (int)((uint)*(byte *)(iVar10 + 0x7d) << 0x1b);
              uVar13 = audio_uart_nema_stencil_save_52266e((uint)bVar21,0,(uint)bVar21,0);
              g2c_nema_vg_emit_verts_516b34
                        ((float)g2c_bits_to_float((uint)(uVar2)),(float)g2c_bits_to_float((uint)(((ulonglong)uVar2 >> 0x20))),(float)g2c_bits_to_float((uint)(uVar3)),
                         (float)g2c_bits_to_float((uint)(((ulonglong)uVar3 >> 0x20))),(float)g2c_bits_to_float((uint)(uVar4)),
                         (float)g2c_bits_to_float((uint)(((ulonglong)uVar4 >> 0x20))),(float)g2c_bits_to_float((uint)(uVar5)),
                         (float)g2c_bits_to_float((uint)(((ulonglong)uVar5 >> 0x20))));
              audio_uart_nema_stencil_restore_5226b2(uVar13);
            }
          }
        }
      }
      else {
        *(float *)(iVar9 + 0x310) = a;
        iVar10 = *piVar7;
        *(float *)(iVar9 + 0x314) = b + *(float *)(iVar10 + 0x130) * -0.5f;
        *(float *)(iVar9 + 0x318) = a;
        *(float *)(iVar9 + 0x31c) = b + *(float *)(iVar10 + 0x130) * 0.5f;
        *(undefined4 *)(iVar9 + 0x308) = *(undefined4 *)(iVar9 + 0x310);
        *(undefined4 *)(iVar9 + 0x30c) = *(undefined4 *)(iVar9 + 0x314);
        *(undefined4 *)(iVar9 + 800) = *(undefined4 *)(iVar9 + 0x318);
        *(undefined4 *)(iVar9 + 0x324) = *(undefined4 *)(iVar9 + 0x31c);
      }
      audio_uart_nema_stencil_restore_5226b2(uVar11);
      iVar10 = *piVar7;
      uVar14 = *(undefined4 *)(iVar9 + 0x30c);
      uVar16 = *(undefined4 *)(iVar9 + 0x310);
      uVar17 = *(undefined4 *)(iVar9 + 0x314);
      uVar18 = *(undefined4 *)(iVar9 + 0x318);
      uVar19 = *(undefined4 *)(iVar9 + 0x31c);
      *(undefined4 *)(iVar10 + 0x164) = *(undefined4 *)(iVar9 + 0x308);
      *(undefined4 *)(iVar10 + 0x168) = uVar14;
      *(undefined4 *)(iVar10 + 0x16c) = uVar16;
      *(undefined4 *)(iVar10 + 0x170) = uVar17;
      *(undefined4 *)(iVar10 + 0x174) = uVar18;
      *(undefined4 *)(iVar10 + 0x178) = uVar19;
      uVar14 = *(undefined4 *)(iVar9 + 0x324);
      uVar16 = *(undefined4 *)(iVar9 + 0x328);
      uVar17 = *(undefined4 *)(iVar9 + 0x32c);
      uVar18 = *(undefined4 *)(iVar9 + 0x330);
      *(undefined4 *)(iVar10 + 0x17c) = *(undefined4 *)(iVar9 + 800);
      *(undefined4 *)(iVar10 + 0x180) = uVar14;
      *(undefined4 *)(iVar10 + 0x184) = uVar16;
      *(undefined4 *)(iVar10 + 0x188) = uVar17;
      *(undefined4 *)(iVar10 + 0x18c) = uVar18;
      iVar10 = *piVar7;
      uVar14 = *(undefined4 *)(iVar9 + 0x30c);
      uVar16 = *(undefined4 *)(iVar9 + 0x310);
      uVar17 = *(undefined4 *)(iVar9 + 0x314);
      uVar18 = *(undefined4 *)(iVar9 + 0x318);
      uVar19 = *(undefined4 *)(iVar9 + 0x31c);
      *(undefined4 *)(iVar10 + 400) = *(undefined4 *)(iVar9 + 0x308);
      *(undefined4 *)(iVar10 + 0x194) = uVar14;
      *(undefined4 *)(iVar10 + 0x198) = uVar16;
      *(undefined4 *)(iVar10 + 0x19c) = uVar17;
      *(undefined4 *)(iVar10 + 0x1a0) = uVar18;
      *(undefined4 *)(iVar10 + 0x1a4) = uVar19;
      uVar14 = *(undefined4 *)(iVar9 + 0x324);
      uVar16 = *(undefined4 *)(iVar9 + 0x328);
      uVar17 = *(undefined4 *)(iVar9 + 0x32c);
      uVar18 = *(undefined4 *)(iVar9 + 0x330);
      *(undefined4 *)(iVar10 + 0x1a8) = *(undefined4 *)(iVar9 + 800);
      *(undefined4 *)(iVar10 + 0x1ac) = uVar14;
      *(undefined4 *)(iVar10 + 0x1b0) = uVar16;
      *(undefined4 *)(iVar10 + 0x1b4) = uVar17;
      *(undefined4 *)(iVar10 + 0x1b8) = uVar18;
      if ((uVar15 & uVar12) == 0) {
        if (uVar12 == 1 && uVar15 == 0) {
          fStack_74 = *(float *)(iVar9 + 0x33c);
          uStack_70 = *(undefined4 *)(iVar9 + 0x340);
          uStack_7c = *(uint *)(iVar9 + 0x308);
          uStack_78 = *(undefined4 *)(iVar9 + 0x30c);
          fVar23 = *(float *)(iVar9 + 0x344);
          fVar25 = *(float *)(iVar9 + 0x348);
          fVar26 = *(float *)(iVar9 + 800);
          d_02 = *(float *)(iVar9 + 0x324);
          e_00 = e;
          fStack_8c = fVar26;
          fStack_88 = d_02;
          fStack_84 = fVar23;
          fStack_80 = fVar25;
          if ((*(char *)(iVar9 + 0x2ea) == '\0') &&
             (uVar13 = g2c_nema_vg_stroke_join_5179d0
                                 (&fStack_74,&uStack_7c,&fStack_84,(uint *)&fStack_8c,0),
             uVar13 != 0)) goto LAB_00563ea2;
          /* Evidence (wave11): after bl 0x5179d0 at 0x563f1c, stock goes to bl 0x51bf7c (0x563f08)
           * without reloading s0-s4. vlive.py shows s0-s4 dead from 0x563f20, and 0x51bf7c never reads
           * s0-s4 ("live: none"; the C arc_seg2 writes d/b/e before reading them). So the callee
           * leftovers do not matter and are no longer copied. */
          uVar13 = g2c_nema_vg_arc_seg2_51bf7c(fVar23,fVar25,fVar26,d_02,e_00);
          goto joined_r0x00563f0e;
        }
        if ((uVar15 == 1 && uVar12 == 0) && (*(char *)(iVar9 + 0x2e8) != '\0')) {
          uVar13 = g2c_nema_vg_arc_seg_51b8f0(a_01,b_00,c_01,d_01,e);
          goto joined_r0x00563f0e;
        }
      }
      else {
        if (*(char *)(iVar9 + 0x2e8) == '\0') {
          uVar13 = g2c_nema_vg_arc_seg2_51bf7c(a_01,b_00,c_01,d_01,e);
        }
        else {
          uVar13 = g2c_nema_vg_arc_seg3_51c5ec(a_01,b_00,c_01,d_01,e);
        }
joined_r0x00563f0e:
        if (uVar13 != 0) {
LAB_00563ea2:
          g2c_nema_vg_set_aa_51778c(0);
          g2c_nema_vg_set_aa2_517796(0);
          audio_uart_nema_vg_set_error_51565c(uVar13);
          return uVar13;
        }
      }
      *(undefined4 *)(iVar9 + 0x334) = *(undefined4 *)(iVar9 + 0x308);
      *(undefined4 *)(iVar9 + 0x338) = *(undefined4 *)(iVar9 + 0x30c);
      *(undefined4 *)(iVar9 + 0x33c) = *(undefined4 *)(iVar9 + 0x310);
      *(undefined4 *)(iVar9 + 0x340) = *(undefined4 *)(iVar9 + 0x314);
      *(undefined4 *)(iVar9 + 0x344) = *(undefined4 *)(iVar9 + 0x318);
      *(undefined4 *)(iVar9 + 0x348) = *(undefined4 *)(iVar9 + 0x31c);
      *(undefined4 *)(iVar9 + 0x34c) = *(undefined4 *)(iVar9 + 800);
      *(undefined4 *)(iVar9 + 0x350) = *(undefined4 *)(iVar9 + 0x324);
      *(undefined4 *)(iVar9 + 0x354) = *(undefined4 *)(iVar9 + 0x328);
      *(undefined4 *)(iVar9 + 0x358) = *(undefined4 *)(iVar9 + 0x32c);
      *(undefined4 *)(iVar9 + 0x35c) = *(undefined4 *)(iVar9 + 0x330);
      if (*(char *)(iVar9 + 0x2e8) == '\0') {
        *(undefined4 *)(iVar9 + 0x360) = *(undefined4 *)(iVar9 + 0x308);
        *(undefined4 *)(iVar9 + 0x364) = *(undefined4 *)(iVar9 + 0x30c);
        *(undefined4 *)(iVar9 + 0x368) = *(undefined4 *)(iVar9 + 0x310);
        *(undefined4 *)(iVar9 + 0x36c) = *(undefined4 *)(iVar9 + 0x314);
        *(undefined4 *)(iVar9 + 0x370) = *(undefined4 *)(iVar9 + 0x318);
        *(undefined4 *)(iVar9 + 0x374) = *(undefined4 *)(iVar9 + 0x31c);
        *(undefined4 *)(iVar9 + 0x378) = *(undefined4 *)(iVar9 + 800);
        *(undefined4 *)(iVar9 + 0x37c) = *(undefined4 *)(iVar9 + 0x324);
        *(undefined4 *)(iVar9 + 0x380) = *(undefined4 *)(iVar9 + 0x328);
        *(undefined4 *)(iVar9 + 900) = *(undefined4 *)(iVar9 + 0x32c);
        *(undefined4 *)(iVar9 + 0x388) = *(undefined4 *)(iVar9 + 0x330);
        *(undefined1 *)(iVar9 + 0x2e8) = 1;
      }
    }
    *(byte *)(iVar9 + 0x2e6) = *(byte *)(iVar9 + 0x2e5);
    b = fVar24;
    a = fVar29;
    if (*(int *)(iVar9 + 0x2f8) == 0) {
      *(byte *)(iVar9 + 0x2e5) = *(byte *)(iVar9 + 0x2e5) ^ 1;
    }
  } while( true );
}
#undef fStack_8c
#undef fStack_88
#undef fStack_84
#undef fStack_80
#undef uStack_7c
#undef uStack_78
#undef fStack_74
#undef uStack_70


  

/* ---- lifted 0x5640e4 ---- */


uint g2c_nema_vg_ellipse_5640e4(float a,float b,float c,float d,float *out)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  float fVar8;
  float fVar9;
  float fVar10;
  float fVar11;
  float fVar12;
  float fVar13;
  
  fVar7 = (1.0000001192092896f);
  iVar3 = *(((int *)&audio_uart_nema_vg_context_cell));
  fVar4 = c - a;
  fVar6 = *(float *)(iVar3 + 0x30);
  fVar5 = d - b;
  fVar9 = *(float *)(iVar3 + 0x34) - fVar6;
  fVar12 = fVar4 * (fVar6 - fVar6) - fVar9 * fVar5;
  fVar8 = ((b - fVar6) * fVar4 + (fVar6 - a) * fVar5) / fVar12;
  uVar2 = 0;
  fVar12 = ((b - fVar6) * fVar9 + (fVar6 - a) * (fVar6 - fVar6)) / fVar12;
  if ((((0.0f <= fVar8) && ((fVar8 < (1.0000001192092896f)))) && (0.0f <= fVar12)) &&
     ((fVar12 < (1.0000001192092896f)))) {
    *out = a + fVar12 * fVar4;
    fVar6 = b + fVar12 * fVar5;
    out[1] = fVar6;
    fVar9 = *out;
    iVar1 = (uint)(fVar9 < 0.0f) << 0x1f;
    if (iVar1 < 0) {
      fVar8 = -fVar9;
    }
    if (-1 < iVar1) {
      fVar8 = fVar9;
    }
    fVar12 = ABS(a);
    if (!(ABS(a) < fVar8)) {
      fVar12 = fVar8;
    }
    fVar10 = a - fVar9;
    if ((fVar10 < 0.0f)) {
      fVar10 = fVar9 - a;
    }
    if (fVar10 <= fVar12 * (9.999999747378752e-06f)) {
      fVar12 = ABS(b);
      if (!(ABS(b) < ABS(out[1]))) {
        fVar12 = ABS(out[1]);
      }
      fVar10 = b - fVar6;
      if ((fVar10 < 0.0f)) {
        fVar10 = fVar6 - b;
      }
      if (fVar10 <= fVar12 * (9.999999747378752e-06f)) goto LAB_0056428c;
    }
    if ((ABS(c) < fVar8)) {
      fVar8 = ABS(c);
    }
    fVar12 = c - fVar9;
    if ((fVar12 < 0.0f)) {
      fVar12 = fVar9 - c;
    }
    if (fVar12 <= fVar8 * (9.999999747378752e-06f)) {
      fVar8 = ABS(d);
      if (!(ABS(d) < ABS(out[1]))) {
        fVar8 = ABS(out[1]);
      }
      fVar9 = d - fVar6;
      if ((fVar9 < 0.0f)) {
        fVar9 = fVar6 - d;
      }
      if (fVar9 <= fVar8 * (9.999999747378752e-06f)) goto LAB_0056428c;
    }
    uVar2 = 1;
  }
LAB_0056428c:
  fVar8 = (9.999999747378752e-06f);
  fVar12 = *(float *)(iVar3 + 0x34);
  fVar9 = fVar12 - fVar12;
  fVar6 = b - fVar12;
  fVar12 = fVar12 - *(float *)(iVar3 + 0x30);
  fVar11 = *(float *)(iVar3 + 0x30) - a;
  fVar13 = fVar4 * fVar9 - fVar12 * fVar5;
  fVar10 = (fVar6 * fVar4 + fVar11 * fVar5) / fVar13;
  fVar13 = (fVar6 * fVar12 + fVar11 * fVar9) / fVar13;
  if (((0.0f <= fVar10) && ((fVar10 < fVar7))) &&
     ((0.0f <= fVar13 && ((fVar13 < fVar7))))) {
    if (uVar2 == 1) {
      fVar12 = *out;
      iVar1 = (uint)(fVar12 < 0.0f) << 0x1f;
      if (iVar1 < 0) {
        fVar9 = -fVar12;
      }
      if (-1 < iVar1) {
        fVar9 = fVar12;
      }
      fVar10 = a + fVar13 * fVar4;
      iVar1 = (uint)(fVar10 < 0.0f) << 0x1f;
      if (iVar1 < 0) {
        fVar6 = -fVar10;
      }
      if (-1 < iVar1) {
        fVar6 = fVar10;
      }
      if (!(fVar9 < fVar6)) {
        fVar9 = fVar6;
      }
      fVar6 = fVar12 - fVar10;
      if ((fVar6 < 0.0f)) {
        fVar6 = fVar10 - fVar12;
      }
      if (fVar6 <= fVar9 * (9.999999747378752e-06f)) {
        fVar9 = b + fVar13 * fVar5;
        iVar1 = (uint)(fVar9 < 0.0f) << 0x1f;
        if (iVar1 < 0) {
          fVar6 = -fVar9;
        }
        if (-1 < iVar1) {
          fVar6 = fVar9;
        }
        fVar12 = ABS(out[1]);
        if (!(ABS(out[1]) < fVar6)) {
          fVar12 = fVar6;
        }
        fVar6 = out[1] - fVar9;
        if ((fVar6 < 0.0f)) {
          fVar6 = fVar9 - out[1];
        }
        if (fVar6 <= fVar12 * (9.999999747378752e-06f)) goto LAB_005644d2;
      }
    }
    out[uVar2 * 2] = a + fVar13 * fVar4;
    out[uVar2 * 2 + 1] = b + fVar13 * fVar5;
    fVar9 = *out;
    iVar1 = (uint)(fVar9 < 0.0f) << 0x1f;
    fVar6 = fVar4;
    if (iVar1 < 0) {
      fVar6 = -fVar9;
    }
    if (-1 < iVar1) {
      fVar6 = fVar9;
    }
    fVar12 = ABS(a);
    if (!(ABS(a) < fVar6)) {
      fVar12 = fVar6;
    }
    fVar10 = a - fVar9;
    if ((fVar10 < 0.0f)) {
      fVar10 = fVar9 - a;
    }
    if (fVar10 <= fVar12 * fVar8) {
      fVar12 = ABS(b);
      if (!(ABS(b) < ABS(out[1]))) {
        fVar12 = ABS(out[1]);
      }
      fVar10 = b - out[1];
      if ((fVar10 < 0.0f)) {
        fVar10 = out[1] - b;
      }
      if (fVar10 <= fVar12 * fVar8) goto LAB_005644d2;
    }
    if ((ABS(c) < fVar6)) {
      fVar6 = ABS(c);
    }
    fVar12 = c - fVar9;
    if ((fVar12 < 0.0f)) {
      fVar12 = fVar9 - c;
    }
    if (fVar12 <= fVar6 * fVar8) {
      fVar6 = ABS(d);
      if (!(ABS(d) < ABS(out[1]))) {
        fVar6 = ABS(out[1]);
      }
      fVar9 = d - out[1];
      if ((fVar9 < 0.0f)) {
        fVar9 = out[1] - d;
      }
      if (fVar9 <= fVar6 * fVar8) goto LAB_005644d2;
    }
    uVar2 = uVar2 + 1;
  }
LAB_005644d2:
  fVar8 = (9.999999747378752e-06f);
  fVar12 = *(float *)(iVar3 + 0x30);
  fVar11 = *(float *)(iVar3 + 0x34) - fVar12;
  fVar6 = b - fVar12;
  fVar9 = fVar4 * fVar11 - (fVar12 - fVar12) * fVar5;
  fVar10 = (fVar6 * fVar4 + (fVar12 - a) * fVar5) / fVar9;
  fVar12 = (fVar6 * (fVar12 - fVar12) + (fVar12 - a) * fVar11) / fVar9;
  if (((0.0f <= fVar10) && ((fVar10 < fVar7))) &&
     ((0.0f <= fVar12 && (((fVar12 < fVar7) && (uVar2 < 2)))))) {
    if (uVar2 == 1) {
      fVar10 = *out;
      iVar1 = (uint)(fVar10 < 0.0f) << 0x1f;
      if (iVar1 < 0) {
        fVar9 = -fVar10;
      }
      if (-1 < iVar1) {
        fVar9 = fVar10;
      }
      fVar11 = a + fVar12 * fVar4;
      iVar1 = (uint)(fVar11 < 0.0f) << 0x1f;
      if (iVar1 < 0) {
        fVar6 = -fVar11;
      }
      if (-1 < iVar1) {
        fVar6 = fVar11;
      }
      if (!(fVar9 < fVar6)) {
        fVar9 = fVar6;
      }
      fVar6 = fVar10 - fVar11;
      if ((fVar6 < 0.0f)) {
        fVar6 = fVar11 - fVar10;
      }
      if (fVar6 <= fVar9 * (9.999999747378752e-06f)) {
        fVar9 = b + fVar12 * fVar5;
        iVar1 = (uint)(fVar9 < 0.0f) << 0x1f;
        if (iVar1 < 0) {
          fVar6 = -fVar9;
        }
        if (-1 < iVar1) {
          fVar6 = fVar9;
        }
        fVar10 = ABS(out[1]);
        if (!(ABS(out[1]) < fVar6)) {
          fVar10 = fVar6;
        }
        fVar6 = out[1] - fVar9;
        if ((fVar6 < 0.0f)) {
          fVar6 = fVar9 - out[1];
        }
        if (fVar6 <= fVar10 * (9.999999747378752e-06f)) goto LAB_00564724;
      }
    }
    out[uVar2 * 2] = a + fVar12 * fVar4;
    out[uVar2 * 2 + 1] = b + fVar12 * fVar5;
    fVar9 = *out;
    iVar1 = (uint)(fVar9 < 0.0f) << 0x1f;
    fVar6 = fVar4;
    if (iVar1 < 0) {
      fVar6 = -fVar9;
    }
    if (-1 < iVar1) {
      fVar6 = fVar9;
    }
    fVar12 = ABS(a);
    if (!(ABS(a) < fVar6)) {
      fVar12 = fVar6;
    }
    fVar10 = a - fVar9;
    if ((fVar10 < 0.0f)) {
      fVar10 = fVar9 - a;
    }
    if (fVar10 <= fVar12 * fVar8) {
      fVar12 = ABS(b);
      if (!(ABS(b) < ABS(out[1]))) {
        fVar12 = ABS(out[1]);
      }
      fVar10 = b - out[1];
      if ((fVar10 < 0.0f)) {
        fVar10 = out[1] - b;
      }
      if (fVar10 <= fVar12 * fVar8) goto LAB_00564724;
    }
    if ((ABS(c) < fVar6)) {
      fVar6 = ABS(c);
    }
    fVar12 = c - fVar9;
    if ((fVar12 < 0.0f)) {
      fVar12 = fVar9 - c;
    }
    if (fVar12 <= fVar6 * fVar8) {
      fVar6 = ABS(d);
      if (!(ABS(d) < ABS(out[1]))) {
        fVar6 = ABS(out[1]);
      }
      fVar9 = d - out[1];
      if ((fVar9 < 0.0f)) {
        fVar9 = out[1] - d;
      }
      if (fVar9 <= fVar6 * fVar8) goto LAB_00564724;
    }
    uVar2 = uVar2 + 1;
  }
LAB_00564724:
  fVar8 = (9.999999747378752e-06f);
  fVar6 = *(float *)(iVar3 + 0x34);
  fVar10 = fVar6 - *(float *)(iVar3 + 0x30);
  fVar11 = b - *(float *)(iVar3 + 0x30);
  fVar9 = fVar4 * fVar10 - (fVar6 - fVar6) * fVar5;
  fVar12 = (fVar11 * fVar4 + (fVar6 - a) * fVar5) / fVar9;
  fVar6 = fVar11 * (fVar6 - fVar6) + (fVar6 - a) * fVar10;
  fVar10 = fVar6 / fVar9;
  if ((((0.0f <= fVar12) && ((fVar12 < fVar7))) && (0.0f <= fVar10)) &&
     (((fVar10 < fVar7) && (uVar2 < 2)))) {
    if (uVar2 == 1) {
      fVar7 = *out;
      iVar3 = (uint)(fVar7 < 0.0f) << 0x1f;
      if (iVar3 < 0) {
        fVar6 = -fVar7;
      }
      if (-1 < iVar3) {
        fVar6 = fVar7;
      }
      fVar12 = a + fVar10 * fVar4;
      iVar3 = (uint)(fVar12 < 0.0f) << 0x1f;
      if (iVar3 < 0) {
        fVar9 = -fVar12;
      }
      if (-1 < iVar3) {
        fVar9 = fVar12;
      }
      if (!(fVar6 < fVar9)) {
        fVar6 = fVar9;
      }
      fVar9 = fVar7 - fVar12;
      if ((fVar9 < 0.0f)) {
        fVar9 = fVar12 - fVar7;
      }
      if (fVar9 <= fVar6 * (9.999999747378752e-06f)) {
        fVar7 = b + fVar10 * fVar5;
        iVar3 = (uint)(fVar7 < 0.0f) << 0x1f;
        if (iVar3 < 0) {
          fVar9 = -fVar7;
        }
        if (-1 < iVar3) {
          fVar9 = fVar7;
        }
        fVar6 = ABS(out[1]);
        if (!(ABS(out[1]) < fVar9)) {
          fVar6 = fVar9;
        }
        fVar9 = out[1] - fVar7;
        if ((fVar9 < 0.0f)) {
          fVar9 = fVar7 - out[1];
        }
        if (fVar9 <= fVar6 * (9.999999747378752e-06f)) {
          return 1;
        }
      }
    }
    out[uVar2 * 2] = a + fVar10 * fVar4;
    fVar7 = b + fVar10 * fVar5;
    out[uVar2 * 2 + 1] = fVar7;
    fVar4 = *out;
    iVar3 = (uint)(fVar4 < 0.0f) << 0x1f;
    if (iVar3 < 0) {
      fVar7 = -fVar4;
    }
    if (-1 < iVar3) {
      fVar7 = fVar4;
    }
    fVar5 = ABS(a);
    if (!(ABS(a) < fVar7)) {
      fVar5 = fVar7;
    }
    fVar6 = a - fVar4;
    if ((fVar6 < 0.0f)) {
      fVar6 = fVar4 - a;
    }
    if (fVar6 <= fVar5 * fVar8) {
      fVar5 = ABS(b);
      if (!(ABS(b) < ABS(out[1]))) {
        fVar5 = ABS(out[1]);
      }
      fVar6 = b - out[1];
      if ((fVar6 < 0.0f)) {
        fVar6 = out[1] - b;
      }
      if (fVar6 <= fVar5 * fVar8) {
        return uVar2;
      }
    }
    if ((ABS(c) < fVar7)) {
      fVar7 = ABS(c);
    }
    fVar5 = c - fVar4;
    if ((fVar5 < 0.0f)) {
      fVar5 = fVar4 - c;
    }
    if (fVar5 <= fVar7 * fVar8) {
      fVar7 = ABS(d);
      if (!(ABS(d) < ABS(out[1]))) {
        fVar7 = ABS(out[1]);
      }
      fVar4 = d - out[1];
      if ((fVar4 < 0.0f)) {
        fVar4 = out[1] - d;
      }
      if (fVar4 <= fVar7 * fVar8) {
        return uVar2;
      }
    }
    uVar2 = uVar2 + 1;
  }
  return uVar2;
}

  

/* ---- lifted 0x564974 ---- */


uint g2c_nema_vg_arc_build_564974(float a,float b,float c,float d)

{
  /* Evidence (wave11): the s1/s2/s3 left by the calls at 0x564b04/0x564cb0/0x564e0c are dead in stock
   * (vlive.py "none"). The C initial copies before each fully-covered or overwritten select are
   * replaced by 0.0f, which is never observed. */
  bool bVar1;
  bool bVar2;
  bool bVar3;
  int *piVar4;
  int iVar5;
  uint *puVar6;
  int iVar7;
  undefined1 uVar8;
  uint uVar9;
  int iVar10;
  uint uVar11;
  uint uVar12;
  float fVar13;
  float fVar14;
  float fVar15;
  float fVar16;
  float fVar17;
  float fVar18;
  /* Stock frame of 0x564974 as one block: locals keep the entry-SP offsets Ghidra named them by
   * (X_Stack_NN at g2c_frame_564974[0x38-0xNN]) so &local passed to callees spans its stock neighbours. */
  unsigned char g2c_frame_564974[0x38] __attribute__((aligned(8)));
  typedef float __attribute__((may_alias)) g2c_fa_float;
#define fStack_38 (*(g2c_fa_float *)(void *)&g2c_frame_564974[0x38-0x38])
#define fStack_34 (*(g2c_fa_float *)(void *)&g2c_frame_564974[0x38-0x34])
  typedef undefined4 __attribute__((may_alias)) g2c_fa_undefined4;
#define uStack_30 (*(g2c_fa_undefined4 *)(void *)&g2c_frame_564974[0x38-0x30])
#define uStack_2c (*(g2c_fa_undefined4 *)(void *)&g2c_frame_564974[0x38-0x2c])
  
  piVar4 = (((int *)&audio_uart_nema_vg_context_cell));
  bVar2 = false;
  puVar6 = (uint *)*(((int *)&audio_uart_nema_vg_context_cell));
  fVar13 = ((float *)(puVar6))[0xd];
  if ((fVar13 < a || (fVar13 < a || fVar13 < b)) ||
     (fVar17 = ((float *)(puVar6))[0xc], a < fVar17 || (a < fVar17 || b < fVar17))) {
    bVar2 = true;
  }
  bVar3 = false;
  bVar1 = fVar13 < c;
  fVar17 = b;
  if (!bVar1) {
    fVar17 = d;
  }
  if ((bVar1 || (bVar1 || fVar13 < fVar17)) ||
     (fVar13 = ((float *)(puVar6))[0xc], c < fVar13 || (c < fVar13 || fVar17 < fVar13))) {
    bVar3 = true;
  }
  fStack_38 = 0.0f;
  fStack_34 = 0.0f;
  uStack_30 = 0;
  uStack_2c = 0;
  if (!bVar3 && !bVar2) {
    if (puVar6[9] == 0x100) {
      uVar9 = puVar6[3];
      if (puVar6[0xb] != 0) {
        puVar6[3] = uVar9 + 1;
        *(undefined4 *)(*piVar4 + 0x24) = 0;
        return 0;
      }
      if (uVar9 < *puVar6) {
        *(undefined1 *)(puVar6[7] + uVar9) = 0;
        *(int *)(*piVar4 + 0xc) = *(int *)(*piVar4 + 0xc) + 1;
        *(undefined4 *)(*piVar4 + 0x24) = 0;
        return 0;
      }
      puVar6[10] = 2;
      puVar6[3] = uVar9 + 1;
      puVar6[0xb] = 1;
      *(undefined4 *)(*piVar4 + 0x24) = 0;
      return 0;
    }
    if (puVar6[9] == 0x1ff) goto LAB_0056505c;
    uVar9 = puVar6[3];
    if (puVar6[0xb] == 0) {
      if (uVar9 < *puVar6) {
        *(undefined1 *)(puVar6[7] + uVar9) = 2;
        *(int *)(*piVar4 + 0xc) = *(int *)(*piVar4 + 0xc) + 1;
      }
      else {
        puVar6[3] = uVar9 + 1;
        puVar6[10] = 2;
        puVar6[0xb] = 1;
      }
    }
    else {
      puVar6[3] = uVar9 + 1;
    }
    iVar7 = *piVar4;
    iVar5 = *(int *)(iVar7 + 8);
    if (*(int *)(iVar7 + 0x2c) != 0) goto LAB_0056538a;
    uVar9 = iVar5 + 1;
    if (uVar9 < *(uint *)(iVar7 + 4)) {
      iVar10 = *(int *)(iVar7 + 0x10);
      *(float *)(iVar10 + iVar5 * 4) = c;
      *(uint *)(iVar7 + 8) = uVar9;
      *(float *)(iVar10 + uVar9 * 4) = d;
      *(int *)(iVar7 + 8) = iVar5 + 2;
      return 0;
    }
    goto LAB_00565370;
  }
  if (!(bool)(bVar3 ^ 1U | bVar2)) {
    g2c_nema_vg_ellipse_5640e4(a,b,c,d,&fStack_38);
    puVar6 = (uint *)*piVar4;
    uVar8 = 2;
    if (puVar6[9] == 0x1ff) {
      uVar8 = 0x82;
    }
    uVar9 = puVar6[3];
    if (puVar6[0xb] == 0) {
      if (uVar9 < *puVar6) {
        *(undefined1 *)(puVar6[7] + uVar9) = uVar8;
        *(int *)(*piVar4 + 0xc) = *(int *)(*piVar4 + 0xc) + 1;
      }
      else {
        puVar6[10] = 2;
        puVar6[3] = puVar6[3] + 1;
        puVar6[0xb] = 1;
      }
    }
    else {
      puVar6[3] = uVar9 + 1;
    }
    puVar6 = (uint *)*piVar4;
    uVar9 = puVar6[2];
    if (puVar6[0xb] == 0) {
      uVar11 = uVar9 + 1;
      if (uVar11 < puVar6[1]) {
        uVar12 = puVar6[4];
        *(float *)(uVar12 + uVar9 * 4) = fStack_38;
        puVar6[2] = uVar11;
        *(float *)(uVar12 + uVar11 * 4) = fStack_34;
        puVar6[2] = uVar9 + 2;
      }
      else {
        puVar6[2] = uVar9 + 2;
        puVar6[10] = 2;
        puVar6[0xb] = 1;
      }
    }
    else {
      puVar6[2] = uVar9 + 2;
    }
    fVar17 = ((float *)(puVar6))[0xc];
    iVar5 = (uint)(c < fVar17) << 0x1f;
    fVar13 = 0.0f;
    if (iVar5 < 0) {
      fVar13 = fVar17;
    }
    if (-1 < iVar5) {
      fVar13 = c;
    }
    fVar15 = ((float *)(puVar6))[0xd];
    if ((fVar15 < fVar13)) {
      fVar13 = fVar15;
    }
    if ((d < fVar17)) {
      d = fVar17;
    }
    if ((fVar15 < d)) {
      d = fVar15;
    }
    if (puVar6[9] == 0x100) {
      uVar9 = puVar6[3];
      if (puVar6[0xb] != 0) {
        puVar6[3] = uVar9 + 1;
        *(undefined4 *)(*piVar4 + 0x24) = 0;
        return 0;
      }
      if (uVar9 < *puVar6) {
        *(undefined1 *)(puVar6[7] + uVar9) = 0x80;
        *(int *)(*piVar4 + 0xc) = *(int *)(*piVar4 + 0xc) + 1;
        *(undefined4 *)(*piVar4 + 0x24) = 0;
        return 0;
      }
      puVar6[3] = uVar9 + 1;
      puVar6[10] = 2;
      puVar6[0xb] = 1;
      *(undefined4 *)(*piVar4 + 0x24) = 0;
      return 0;
    }
    if (puVar6[9] == 0x1ff) {
      puVar6[9] = 0;
      return 0;
    }
    uVar9 = puVar6[3];
    if (puVar6[0xb] == 0) {
      if (uVar9 < *puVar6) {
        *(undefined1 *)(puVar6[7] + uVar9) = 0x82;
        *(int *)(*piVar4 + 0xc) = *(int *)(*piVar4 + 0xc) + 1;
      }
      else {
        puVar6[3] = uVar9 + 1;
        puVar6[10] = 2;
        puVar6[0xb] = 1;
      }
    }
    else {
      puVar6[3] = uVar9 + 1;
    }
    iVar7 = *piVar4;
    iVar5 = *(int *)(iVar7 + 8);
    if (*(int *)(iVar7 + 0x2c) == 0) {
      uVar9 = iVar5 + 1;
      if (uVar9 < *(uint *)(iVar7 + 4)) {
        iVar10 = *(int *)(iVar7 + 0x10);
        *(float *)(iVar10 + iVar5 * 4) = fVar13;
        *(uint *)(iVar7 + 8) = uVar9;
        *(float *)(iVar10 + uVar9 * 4) = d;
        *(int *)(iVar7 + 8) = iVar5 + 2;
        return 0;
      }
      goto LAB_00565370;
    }
    goto LAB_0056538a;
  }
  if ((bool)(bVar2 & (bVar3 ^ 1U))) {
    g2c_nema_vg_ellipse_5640e4(a,b,c,d,&fStack_38);
    puVar6 = (uint *)*piVar4;
    uVar9 = puVar6[3];
    if (puVar6[0xb] == 0) {
      if (uVar9 < *puVar6) {
        *(undefined1 *)(puVar6[7] + uVar9) = 0x82;
        *(int *)(*piVar4 + 0xc) = *(int *)(*piVar4 + 0xc) + 1;
      }
      else {
        puVar6[10] = 2;
        puVar6[3] = puVar6[3] + 1;
        puVar6[0xb] = 1;
      }
    }
    else {
      puVar6[3] = uVar9 + 1;
    }
    puVar6 = (uint *)*piVar4;
    uVar9 = puVar6[2];
    if (puVar6[0xb] == 0) {
      uVar11 = uVar9 + 1;
      if (uVar11 < puVar6[1]) {
        uVar12 = puVar6[4];
        *(float *)(uVar12 + uVar9 * 4) = fStack_38;
        puVar6[2] = uVar11;
        *(float *)(uVar12 + uVar11 * 4) = fStack_34;
        puVar6[2] = uVar9 + 2;
      }
      else {
        puVar6[2] = uVar9 + 2;
        puVar6[10] = 2;
        puVar6[0xb] = 1;
      }
    }
    else {
      puVar6[2] = uVar9 + 2;
    }
    if (puVar6[9] == 0x100) {
      uVar9 = puVar6[3];
      if (puVar6[0xb] != 0) {
        puVar6[3] = uVar9 + 1;
        *(undefined4 *)(*piVar4 + 0x24) = 0;
        return 0;
      }
      if (uVar9 < *puVar6) {
        *(undefined1 *)(puVar6[7] + uVar9) = 0;
        *(int *)(*piVar4 + 0xc) = *(int *)(*piVar4 + 0xc) + 1;
        *(undefined4 *)(*piVar4 + 0x24) = 0;
        return 0;
      }
      puVar6[3] = uVar9 + 1;
      puVar6[10] = 2;
      puVar6[0xb] = 1;
      *(undefined4 *)(*piVar4 + 0x24) = 0;
      return 0;
    }
    if (puVar6[9] == 0x1ff) goto LAB_0056505c;
    uVar9 = puVar6[3];
    if (puVar6[0xb] == 0) {
      if (uVar9 < *puVar6) {
        *(undefined1 *)(puVar6[7] + uVar9) = 2;
        *(int *)(*piVar4 + 0xc) = *(int *)(*piVar4 + 0xc) + 1;
      }
      else {
        puVar6[3] = uVar9 + 1;
        puVar6[10] = 2;
        puVar6[0xb] = 1;
      }
    }
    else {
      puVar6[3] = uVar9 + 1;
    }
    iVar7 = *piVar4;
    iVar5 = *(int *)(iVar7 + 8);
    if (*(int *)(iVar7 + 0x2c) == 0) {
      uVar9 = iVar5 + 1;
      if (uVar9 < *(uint *)(iVar7 + 4)) {
        iVar10 = *(int *)(iVar7 + 0x10);
        *(float *)(iVar10 + iVar5 * 4) = c;
        *(uint *)(iVar7 + 8) = uVar9;
        *(float *)(iVar10 + uVar9 * 4) = d;
        *(int *)(iVar7 + 8) = iVar5 + 2;
        return 0;
      }
      goto LAB_00565370;
    }
    goto LAB_0056538a;
  }
  uVar9 = g2c_nema_vg_ellipse_5640e4(c,d,a,b,&fStack_38);
  puVar6 = (uint *)*piVar4;
  fVar13 = ((float *)(puVar6))[0xc];
  iVar5 = (uint)(a < fVar13) << 0x1f;
  fVar17 = 0.0f;
  if (iVar5 < 0) {
    fVar17 = fVar13;
  }
  if (-1 < iVar5) {
    fVar17 = a;
  }
  fVar15 = ((float *)(puVar6))[0xd];
  if ((fVar15 < fVar17)) {
    fVar17 = fVar15;
  }
  iVar5 = (uint)(b < fVar13) << 0x1f;
  fVar14 = 0.0f;
  if (iVar5 < 0) {
    fVar14 = fVar13;
  }
  if (-1 < iVar5) {
    fVar14 = b;
  }
  if ((fVar15 < fVar14)) {
    fVar14 = fVar15;
  }
  iVar5 = (uint)(c < fVar13) << 0x1f;
  fVar16 = 0.0f;
  if (iVar5 < 0) {
    fVar16 = fVar13;
  }
  if (-1 < iVar5) {
    fVar16 = c;
  }
  if ((fVar15 < fVar16)) {
    fVar16 = fVar15;
  }
  if (!(d < fVar13)) {
    fVar13 = d;
  }
  if ((fVar15 < fVar13)) {
    fVar13 = fVar15;
  }
  if (uVar9 == 2) {
    uVar9 = puVar6[3];
    if (puVar6[0xb] == 0) {
      if (uVar9 < *puVar6) {
        *(undefined1 *)(puVar6[7] + uVar9) = 0x82;
        *(int *)(*piVar4 + 0xc) = *(int *)(*piVar4 + 0xc) + 1;
      }
      else {
        puVar6[3] = uVar9 + 1;
        puVar6[10] = 2;
        puVar6[0xb] = 1;
      }
    }
    else {
      puVar6[3] = uVar9 + 1;
    }
    puVar6 = (uint *)*piVar4;
    uVar8 = 2;
    if (puVar6[9] == 0x1ff) {
      uVar8 = 0x82;
    }
    fVar15 = ABS(fVar17);
    if (!(ABS(fVar17) < ABS(fStack_38))) {
      fVar15 = ABS(fStack_38);
    }
    fVar18 = fVar17 - fStack_38;
    if ((fVar18 < 0.0f)) {
      fVar18 = fStack_38 - fVar17;
    }
    if (fVar18 <= fVar15 * (9.999999747378752e-06f)) {
LAB_00565162:
      uVar9 = puVar6[2];
      if (puVar6[0xb] == 0) {
        uVar11 = uVar9 + 1;
        if (puVar6[1] <= uVar11) {
          puVar6[2] = uVar9 + 2;
          puVar6[10] = 2;
          puVar6[0xb] = 1;
          goto LAB_005651a8;
        }
        uVar12 = puVar6[4];
        *(float *)(uVar12 + uVar9 * 4) = fStack_38;
        puVar6[2] = uVar11;
        *(float *)(uVar12 + uVar11 * 4) = fStack_34;
        puVar6[2] = uVar9 + 2;
        uVar9 = puVar6[3];
        if (uVar9 < *puVar6) {
          *(undefined1 *)(puVar6[7] + uVar9) = uVar8;
          *(int *)(*piVar4 + 0xc) = *(int *)(*piVar4 + 0xc) + 1;
        }
        else {
          puVar6[3] = uVar9 + 1;
          puVar6[10] = 2;
          puVar6[0xb] = 1;
        }
      }
      else {
        puVar6[2] = uVar9 + 2;
LAB_005651a8:
        puVar6[3] = puVar6[3] + 1;
      }
      iVar5 = *piVar4;
      if (*(int *)(iVar5 + 0x2c) == 0) {
        iVar7 = *(int *)(iVar5 + 8);
        uVar9 = iVar7 + 1;
        if (uVar9 < *(uint *)(iVar5 + 4)) {
          iVar10 = *(int *)(iVar5 + 0x10);
          *(undefined4 *)(iVar10 + iVar7 * 4) = uStack_30;
          *(uint *)(iVar5 + 8) = uVar9;
          *(undefined4 *)(iVar10 + uVar9 * 4) = uStack_2c;
          *(int *)(iVar5 + 8) = iVar7 + 2;
        }
        else {
LAB_00565276:
          *(undefined4 *)(iVar5 + 0x28) = 2;
          *(int *)(iVar5 + 8) = *(int *)(iVar5 + 8) + 2;
          *(undefined4 *)(iVar5 + 0x2c) = 1;
        }
      }
      else {
        iVar7 = *(int *)(iVar5 + 8);
LAB_00565286:
        *(int *)(iVar5 + 8) = iVar7 + 2;
      }
    }
    else {
      fVar17 = ABS(fVar14);
      if (!(ABS(fVar14) < ABS(fStack_34))) {
        fVar17 = ABS(fStack_34);
      }
      fVar15 = fVar14 - fStack_34;
      if ((fVar15 < 0.0f)) {
        fVar15 = fStack_34 - fVar14;
      }
      if (fVar15 <= fVar17 * (9.999999747378752e-06f)) goto LAB_00565162;
      uVar9 = puVar6[2];
      if (puVar6[0xb] == 0) {
        uVar11 = uVar9 + 1;
        if (puVar6[1] <= uVar11) {
          puVar6[2] = uVar9 + 2;
          puVar6[10] = 2;
          puVar6[0xb] = 1;
          goto LAB_00565234;
        }
        uVar12 = puVar6[4];
        *(undefined4 *)(uVar12 + uVar9 * 4) = uStack_30;
        puVar6[2] = uVar11;
        *(undefined4 *)(uVar12 + uVar11 * 4) = uStack_2c;
        puVar6[2] = uVar9 + 2;
        uVar9 = puVar6[3];
        if (uVar9 < *puVar6) {
          *(undefined1 *)(puVar6[7] + uVar9) = uVar8;
          *(int *)(*piVar4 + 0xc) = *(int *)(*piVar4 + 0xc) + 1;
        }
        else {
          puVar6[3] = uVar9 + 1;
          puVar6[10] = 2;
          puVar6[0xb] = 1;
        }
      }
      else {
        puVar6[2] = uVar9 + 2;
LAB_00565234:
        puVar6[3] = puVar6[3] + 1;
      }
      iVar5 = *piVar4;
      iVar7 = *(int *)(iVar5 + 8);
      if (*(int *)(iVar5 + 0x2c) != 0) goto LAB_00565286;
      uVar9 = iVar7 + 1;
      if (*(uint *)(iVar5 + 4) <= uVar9) goto LAB_00565276;
      iVar10 = *(int *)(iVar5 + 0x10);
      *(float *)(iVar10 + iVar7 * 4) = fStack_38;
      *(uint *)(iVar5 + 8) = uVar9;
      *(float *)(iVar10 + uVar9 * 4) = fStack_34;
      *(int *)(iVar5 + 8) = iVar7 + 2;
    }
    puVar6 = (uint *)*piVar4;
    if (puVar6[9] == 0x100) {
      uVar9 = puVar6[3];
      if (puVar6[0xb] != 0) {
        puVar6[3] = uVar9 + 1;
        *(undefined4 *)(*piVar4 + 0x24) = 0;
        return 0;
      }
      if (uVar9 < *puVar6) {
        *(undefined1 *)(puVar6[7] + uVar9) = 0x80;
        *(int *)(*piVar4 + 0xc) = *(int *)(*piVar4 + 0xc) + 1;
        *(undefined4 *)(*piVar4 + 0x24) = 0;
        return 0;
      }
      puVar6[10] = 2;
      puVar6[3] = uVar9 + 1;
      puVar6[0xb] = 1;
      *(undefined4 *)(*piVar4 + 0x24) = 0;
      return 0;
    }
    if (puVar6[9] == 0x1ff) {
      puVar6[9] = 0;
      return 0;
    }
    uVar9 = puVar6[3];
    if (puVar6[0xb] == 0) {
      if (uVar9 < *puVar6) {
        *(undefined1 *)(puVar6[7] + uVar9) = 0x82;
        *(int *)(*piVar4 + 0xc) = *(int *)(*piVar4 + 0xc) + 1;
      }
      else {
        puVar6[3] = uVar9 + 1;
        puVar6[10] = 2;
        puVar6[0xb] = 1;
      }
    }
    else {
      puVar6[3] = uVar9 + 1;
    }
  }
  else {
    fVar15 = ABS(fVar17);
    if (!(ABS(fVar17) < ABS(fVar16))) {
      fVar15 = ABS(fVar16);
    }
    fVar18 = fVar17 - fVar16;
    if ((fVar18 < 0.0f)) {
      fVar18 = fVar16 - fVar17;
    }
    if (fVar15 * (9.999999747378752e-06f) < fVar18) {
      fVar15 = ABS(fVar14);
      if (!(ABS(fVar14) < ABS(fVar13))) {
        fVar15 = ABS(fVar13);
      }
      fVar18 = fVar14 - fVar13;
      if ((fVar18 < 0.0f)) {
        fVar18 = fVar13 - fVar14;
      }
      if (fVar15 * (9.999999747378752e-06f) < fVar18) {
        uVar9 = puVar6[3];
        if (puVar6[0xb] == 0) {
          if (uVar9 < *puVar6) {
            *(undefined1 *)(puVar6[7] + uVar9) = 0x82;
            *(int *)(*piVar4 + 0xc) = *(int *)(*piVar4 + 0xc) + 1;
          }
          else {
            puVar6[3] = uVar9 + 1;
            puVar6[10] = 2;
            puVar6[0xb] = 1;
          }
        }
        else {
          puVar6[3] = uVar9 + 1;
        }
        iVar5 = *piVar4;
        if ((ABS((fVar17 - a) * (d - b) + (b - fVar13) * (c - a)) <
                        ABS((fVar16 - a) * (d - b) + (b - fVar14) * (c - a)))) {
          if (*(int *)(iVar5 + 0x2c) == 0) {
            iVar7 = *(int *)(iVar5 + 8);
            uVar9 = iVar7 + 1;
            if (uVar9 < *(uint *)(iVar5 + 4)) {
              iVar10 = *(int *)(iVar5 + 0x10);
              *(float *)(iVar10 + iVar7 * 4) = fVar17;
              *(uint *)(iVar5 + 8) = uVar9;
              *(float *)(iVar10 + uVar9 * 4) = fVar13;
              *(int *)(iVar5 + 8) = iVar7 + 2;
            }
            else {
LAB_00564fd4:
              *(undefined4 *)(iVar5 + 0x28) = 2;
              *(int *)(iVar5 + 8) = *(int *)(iVar5 + 8) + 2;
              *(undefined4 *)(iVar5 + 0x2c) = 1;
            }
          }
          else {
LAB_00564fe6:
            *(int *)(iVar5 + 8) = *(int *)(iVar5 + 8) + 2;
          }
        }
        else {
          if (*(int *)(iVar5 + 0x2c) != 0) goto LAB_00564fe6;
          iVar7 = *(int *)(iVar5 + 8);
          uVar9 = iVar7 + 1;
          if (*(uint *)(iVar5 + 4) <= uVar9) goto LAB_00564fd4;
          iVar10 = *(int *)(iVar5 + 0x10);
          *(float *)(iVar10 + iVar7 * 4) = fVar16;
          *(uint *)(iVar5 + 8) = uVar9;
          *(float *)(iVar10 + uVar9 * 4) = fVar14;
          *(int *)(iVar5 + 8) = iVar7 + 2;
        }
      }
    }
    puVar6 = (uint *)*piVar4;
    if (puVar6[9] == 0x100) {
      uVar9 = puVar6[3];
      if (puVar6[0xb] != 0) {
        puVar6[3] = uVar9 + 1;
        *(undefined4 *)(*piVar4 + 0x24) = 0;
        return 0;
      }
      if (uVar9 < *puVar6) {
        *(undefined1 *)(puVar6[7] + uVar9) = 0x80;
        *(int *)(*piVar4 + 0xc) = *(int *)(*piVar4 + 0xc) + 1;
        *(undefined4 *)(*piVar4 + 0x24) = 0;
        return 0;
      }
      puVar6[3] = uVar9 + 1;
      puVar6[10] = 2;
      puVar6[0xb] = 1;
      *(undefined4 *)(*piVar4 + 0x24) = 0;
      return 0;
    }
    if (puVar6[9] == 0x1ff) {
LAB_0056505c:
      puVar6[9] = 0;
      return 0;
    }
    uVar9 = puVar6[3];
    if (puVar6[0xb] == 0) {
      if (uVar9 < *puVar6) {
        *(undefined1 *)(puVar6[7] + uVar9) = 0x82;
        *(int *)(*piVar4 + 0xc) = *(int *)(*piVar4 + 0xc) + 1;
      }
      else {
        puVar6[3] = uVar9 + 1;
        puVar6[10] = 2;
        puVar6[0xb] = 1;
      }
    }
    else {
      puVar6[3] = uVar9 + 1;
    }
  }
  iVar7 = *piVar4;
  iVar5 = *(int *)(iVar7 + 8);
  if (*(int *)(iVar7 + 0x2c) != 0) {
LAB_0056538a:
    *(int *)(iVar7 + 8) = iVar5 + 2;
    return 0;
  }
  uVar9 = iVar5 + 1;
  if (uVar9 < *(uint *)(iVar7 + 4)) {
    iVar10 = *(int *)(iVar7 + 0x10);
    *(float *)(iVar10 + iVar5 * 4) = fVar16;
    *(uint *)(iVar7 + 8) = uVar9;
    *(float *)(iVar10 + uVar9 * 4) = fVar13;
    *(int *)(iVar7 + 8) = iVar5 + 2;
    return 0;
  }
LAB_00565370:
  *(undefined4 *)(iVar7 + 0x28) = 2;
  *(int *)(iVar7 + 8) = *(int *)(iVar7 + 8) + 2;
  *(undefined4 *)(iVar7 + 0x2c) = 1;
  return 0;
}
#undef fStack_38
#undef fStack_34
#undef uStack_30
#undef uStack_2c


  

/* ---- lifted 0x5653a0 ---- */


uint g2c_nema_vg_arc_draw_5653a0(float a,float b,float c,float d,float e,float f,float g,float h)

{
  bool bVar1;
  byte bVar2;
  float fVar3;
  float fVar4;
  int *piVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  uint *puVar9;
  uint uVar10;
  int iVar11;
  int iVar12;
  bool bVar13;
  float fVar14;
  float fVar15;
  float fVar16;
  float fVar17;
  float fVar18;
  float fVar19;
  float fVar20;
  undefined8 uVar21;
  
  piVar5 = (((int *)&audio_uart_nema_vg_context_cell));
  fVar4 = (50.0f);
  fVar3 = (-50.0f);
  iVar11 = 1;
  uVar21 = CONCAT44(g2c_float_to_bits(f),g2c_float_to_bits(e));
  fVar20 = d;
  do {
    puVar9 = (uint *)*piVar5;
    bVar1 = false;
    fVar14 = ((float *)(puVar9))[0xd];
    /* stock 0x5653ec vcmp; itt ge; vcmpge 0x5653f6; blt 0x565494 (GE ordered; wave19) */
    bVar13 = (fVar14 >= a);
    if (bVar13) {
      bVar13 = (fVar14 >= b);
    }
    fVar16 = (float)g2c_bits_to_float((uint)(uVar21));
    fVar17 = (float)g2c_bits_to_float((uint)(((ulonglong)uVar21 >> 0x20)));
    if (bVar13) {
      fVar15 = ((float *)(puVar9))[0xc];
      /* stock 0x565404/0x56540e itt ge; blt 0x565494 (GE ordered; wave19) */
      bVar13 = (a >= fVar15);
      if (bVar13) {
        bVar13 = (b >= fVar15);
      }
      if (bVar13) {
        /* stock 0x565418/0x565422 itt ge; blt 0x565494 (GE ordered; wave19) */
        bVar13 = (fVar14 >= c);
        if (bVar13) {
          bVar13 = (fVar14 >= fVar20);
        }
        if (bVar13) {
          /* stock 0x56542c/0x565436 itt ge; blt 0x565494 (GE ordered; wave19) */
          bVar13 = (c >= fVar15);
          if (bVar13) {
            bVar13 = (fVar20 >= fVar15);
          }
          if (bVar13) {
            /* stock 0x565440/0x56544a itt ge; blt 0x565494 (GE ordered; wave19) */
            bVar13 = (fVar14 >= fVar16);
            if (bVar13) {
              bVar13 = (fVar14 >= fVar17);
            }
            if (bVar13) {
              /* stock 0x565454/0x56545e itt ge; blt 0x565494 (GE ordered; wave19) */
              bVar13 = (fVar16 >= fVar15);
              if (bVar13) {
                bVar13 = (fVar17 >= fVar15);
              }
              if (bVar13) {
                /* stock 0x565468/0x565476 ittt ge; blt 0x565494 (GE ordered; wave19) */
                bVar13 = (fVar14 >= g);
                if (bVar13) {
                  bVar13 = (fVar14 >= h);
                  d = h;
                }
                if (bVar13) {
                  /* stock 0x565480/0x56548a itt ge; bge 0x565558 (GE ordered; wave19) */
                  bVar13 = (g >= fVar15);
                  if (bVar13) {
                    bVar13 = (d >= fVar15);
                  }
                  if (bVar13) {
                    bVar1 = true;
                  }
                }
              }
            }
          }
        }
      }
    }
    fVar15 = ((float *)(puVar9))[0xc] + fVar4;
    /* stock 0x5654a4 vcmp; itt lt; vcmplt 0x5654be; bge 0x5654dc (LT incl. unordered; wave19) */
    bVar13 = !(a >= fVar15);
    fVar14 = fVar14 + fVar3;
    if (bVar13) {
      bVar13 = !(c >= fVar15);
    }
    if (!bVar13) {
LAB_005654dc:
      /* stock 0x5654dc/0x5654e6 itt lt; bge 0x565504 (LT incl. unordered; wave19) */
      bVar13 = !(fVar14 >= a);
      if (bVar13) {
        bVar13 = !(fVar14 >= c);
      }
      if (bVar13) {
        /* stock 0x5654f0/0x5654fa itt lt; blt 0x565554 (LT incl. unordered; wave19) */
        bVar13 = !(fVar14 >= fVar16);
        if (bVar13) {
          bVar13 = !(fVar14 >= g);
        }
        if (bVar13) goto LAB_00565554;
      }
      /* stock 0x565504/0x56550e itt lt; bge 0x56552c (LT incl. unordered; wave19) */
      bVar13 = !(b >= fVar15);
      if (bVar13) {
        bVar13 = !(fVar20 >= fVar15);
      }
      if (bVar13) {
        /* stock 0x565518/0x565522 itt lt; blt 0x565554 (LT incl. unordered; wave19) */
        bVar13 = !(fVar17 >= fVar15);
        if (bVar13) {
          bVar13 = !(h >= fVar15);
        }
        if (bVar13) goto LAB_00565554;
      }
      if ((fVar14 < b && (fVar14 < b && fVar14 < fVar20)) &&
         (fVar14 < fVar17 && (fVar14 < fVar17 && fVar14 < h))) goto LAB_00565554;
      bVar2 = 0;
    }
    else {
      /* stock 0x5654c8/0x5654d2 itt lt; blt 0x565554 (LT incl. unordered; wave19) */
      bVar13 = !(fVar16 >= fVar15);
      if (bVar13) {
        bVar13 = !(g >= fVar15);
      }
      if (!bVar13) goto LAB_005654dc;
LAB_00565554:
      bVar2 = 1;
    }
    if (bVar1) {
      if ((bool)(bVar2 ^ 1)) {
LAB_0056556a:
        uVar6 = puVar9[3];
        if (puVar9[0xb] == 0) {
          if (uVar6 < *puVar9) {
            *(undefined1 *)(puVar9[7] + uVar6) = 6;
            *(int *)(*piVar5 + 0xc) = *(int *)(*piVar5 + 0xc) + 1;
          }
          else {
            puVar9[10] = 2;
            puVar9[3] = puVar9[3] + 1;
            puVar9[0xb] = 1;
          }
        }
        else {
          puVar9[3] = uVar6 + 1;
        }
        iVar8 = *piVar5;
        iVar7 = *(int *)(iVar8 + 8);
        if (*(int *)(iVar8 + 0x2c) == 0) {
          uVar10 = *(uint *)(iVar8 + 4);
          uVar6 = iVar7 + 1;
          if (uVar6 < uVar10) {
            iVar12 = *(int *)(iVar8 + 0x10);
            *(float *)(iVar12 + iVar7 * 4) = c;
            *(uint *)(iVar8 + 8) = uVar6;
            *(float *)(iVar12 + uVar6 * 4) = fVar20;
            uVar6 = iVar7 + 3;
            *(int *)(iVar8 + 8) = iVar7 + 2;
            if (uVar6 < uVar10) {
              *(float *)(iVar12 + (iVar7 + 2) * 4) = fVar16;
              *(uint *)(iVar8 + 8) = uVar6;
              *(float *)(iVar12 + uVar6 * 4) = fVar17;
              uVar6 = iVar7 + 5;
              *(int *)(iVar8 + 8) = iVar7 + 4;
              if (uVar6 < uVar10) {
                *(float *)(iVar12 + (iVar7 + 4) * 4) = g;
                *(uint *)(iVar8 + 8) = uVar6;
                *(float *)(iVar12 + uVar6 * 4) = h;
                *(int *)(iVar8 + 8) = iVar7 + 6;
                d = h;
              }
              else {
                *(int *)(iVar8 + 8) = iVar7 + 6;
                *(undefined4 *)(iVar8 + 0x28) = 2;
                *(undefined4 *)(iVar8 + 0x2c) = 1;
                d = h;
              }
            }
            else {
              *(undefined4 *)(iVar8 + 0x28) = 2;
              *(int *)(iVar8 + 8) = iVar7 + 4;
              *(undefined4 *)(iVar8 + 0x2c) = 1;
              *(int *)(iVar8 + 8) = *(int *)(iVar8 + 8) + 2;
              d = h;
            }
            goto LAB_005655c8;
          }
          *(int *)(iVar8 + 8) = iVar7 + 2;
          *(undefined4 *)(iVar8 + 0x28) = 2;
          *(undefined4 *)(iVar8 + 0x2c) = 1;
        }
        else {
          *(int *)(iVar8 + 8) = iVar7 + 2;
        }
        *(int *)(iVar8 + 8) = *(int *)(iVar8 + 8) + 2;
        *(int *)(iVar8 + 8) = *(int *)(iVar8 + 8) + 2;
        d = h;
      }
      else {
LAB_005655b8:
        uVar6 = g2c_nema_vg_arc_build_564974(a,b,g,h);
        /* Evidence (wave11): s3 after bl 0x564974 at 0x5655c0 is dead in stock (vlive.py), so it is not copied into d. */
        if (uVar6 != 0) {
          g2c_nema_vg_set_aa_51778c(0);
          g2c_nema_vg_set_aa2_517796(0);
          audio_uart_nema_vg_set_error_51565c(uVar6);
          return uVar6;
        }
      }
LAB_005655c8:
      iVar11 = iVar11 + -1;
      iVar7 = *piVar5;
      if (*(int *)(iVar7 + 700) != 0) {
        iVar8 = *(int *)(iVar7 + 700) + -1;
        *(int *)(iVar7 + 700) = iVar8;
        iVar7 = iVar7 + iVar8 * 0x18;
        c = *(float *)(iVar7 + 0x1cc);
        fVar20 = *(float *)(iVar7 + 0x1d0);
        uVar21 = *(undefined8 *)(iVar7 + 0x1d4);
        a = g;
        b = h;
        g = *(float *)(iVar7 + 0x1dc);
        h = *(float *)(iVar7 + 0x1e0);
      }
    }
    else {
      if (!(bool)(bVar2 ^ 1)) goto LAB_005655b8;
      if (9 < (int)puVar9[0xaf]) goto LAB_0056556a;
      fVar14 = (c + fVar16) * 0.5f;
      fVar15 = (fVar20 + fVar17) * 0.5f;
      fVar16 = (fVar16 + g) * 0.5f;
      fVar17 = (fVar17 + h) * 0.5f;
      fVar18 = (fVar14 + fVar16) * 0.5f;
      puVar9[puVar9[0xaf] * 6 + 0x73] = (uint)g2c_float_to_bits(fVar18);
      fVar19 = (fVar15 + fVar17) * 0.5f;
      puVar9[puVar9[0xaf] * 6 + 0x74] = (uint)g2c_float_to_bits(fVar19);
      fVar20 = (b + fVar20) * 0.5f;
      puVar9[puVar9[0xaf] * 6 + 0x75] = (uint)g2c_float_to_bits(fVar16);
      puVar9[puVar9[0xaf] * 6 + 0x76] = (uint)g2c_float_to_bits(fVar17);
      c = (a + c) * 0.5f;
      puVar9[puVar9[0xaf] * 6 + 0x77] = (uint)g2c_float_to_bits(g);
      fVar14 = (c + fVar14) * 0.5f;
      fVar16 = (fVar20 + fVar15) * 0.5f;
      uVar21 = CONCAT44(g2c_float_to_bits(fVar16),g2c_float_to_bits(fVar14));
      puVar9[puVar9[0xaf] * 6 + 0x78] = (uint)g2c_float_to_bits(h);
      d = fVar14 + fVar18;
      g = d * 0.5f;
      h = (fVar16 + fVar19) * 0.5f;
      puVar9[0xaf] = puVar9[0xaf] + 1;
      iVar11 = iVar11 + 1;
    }
    if (iVar11 == 0) {
      return 0;
    }
  } while( true );
}

  

/* ---- lifted 0x5657d8 ---- */


uint g2c_nema_vg_draw_path_inner_5657d8(uint *a)

{
  /* Evidence (wave11), stock 0x5657d8:
   * - d10 (s20/s21): the entry value is dead. vlive.py from 0x5657e0 shows no read before a write.
   * - d15 (s30/s31): the only use in the function is vstmia to [sp+88] at 0x565802. Disasm
   *   0x5657d8..0x566490 shows no other s30/s31 or #88 access until vstr s16/s17 overwrite that
   *   slot at 0x5662c2/0x5662c6 (after add r1,sp,#88 at 0x5662c0). So the entry value is never
   *   observed, and both pairs start at 0. */
  undefined8 d10_pair = 0;
  undefined8 d15_pair = 0;
  bool bVar1;
  int *piVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  uint *puVar6;
  uint uVar7;
  int iVar8;
  uint uVar9;
  byte bVar10;
  int iVar11;
  uint uVar12;
  byte bVar13;
  bool bVar14;
  bool bVar15;
  float fVar16;
  float fVar17;
  float fVar18;
  float fVar19;
  float fVar20;
  float fVar21;
  float fVar22;
  float fVar23;
  undefined8 uVar24;
  float fVar25;
  float fVar26;
  float fVar27;
  float fVar28;
  float fVar29;
  float fVar30;
  float fVar31;
  undefined8 uVar32;
  /* Stock frame of 0x5657d8 as one block: locals keep the entry-SP offsets Ghidra named them by
   * (X_Stack_NN at g2c_frame_5657d8[0x108-0xNN]) so &local passed to callees spans its stock neighbours. */
  unsigned char g2c_frame_5657d8[0x108] __attribute__((aligned(8)));
  typedef char __attribute__((may_alias)) g2c_fa_char;
#define cStack_108 (*(g2c_fa_char *)(void *)&g2c_frame_5657d8[0x108-0x108])
#define cStack_107 (*(g2c_fa_char *)(void *)&g2c_frame_5657d8[0x108-0x107])
  typedef undefined1 __attribute__((may_alias)) g2c_fa_undefined1;
#define uStack_106 (*(g2c_fa_undefined1 *)(void *)&g2c_frame_5657d8[0x108-0x106])
  typedef byte __attribute__((may_alias)) g2c_fa_byte;
#define bStack_105 (*(g2c_fa_byte *)(void *)&g2c_frame_5657d8[0x108-0x105])
  typedef int __attribute__((may_alias)) g2c_fa_int;
#define iStack_104 (*(g2c_fa_int *)(void *)&g2c_frame_5657d8[0x108-0x104])
#define iStack_100 (*(g2c_fa_int *)(void *)&g2c_frame_5657d8[0x108-0x100])
  typedef float __attribute__((may_alias)) g2c_fa_float;
#define fStack_fc (*(g2c_fa_float *)(void *)&g2c_frame_5657d8[0x108-0xfc])
#define fStack_f8 (*(g2c_fa_float *)(void *)&g2c_frame_5657d8[0x108-0xf8])
#define fStack_f4 (*(g2c_fa_float *)(void *)&g2c_frame_5657d8[0x108-0xf4])
#define fStack_f0 (*(g2c_fa_float *)(void *)&g2c_frame_5657d8[0x108-0xf0])
#define fStack_ec (*(g2c_fa_float *)(void *)&g2c_frame_5657d8[0x108-0xec])
#define fStack_e8 (*(g2c_fa_float *)(void *)&g2c_frame_5657d8[0x108-0xe8])
#define fStack_e4 (*(g2c_fa_float *)(void *)&g2c_frame_5657d8[0x108-0xe4])
#define fStack_e0 (*(g2c_fa_float *)(void *)&g2c_frame_5657d8[0x108-0xe0])
#define fStack_dc (*(g2c_fa_float *)(void *)&g2c_frame_5657d8[0x108-0xdc])
#define fStack_d8 (*(g2c_fa_float *)(void *)&g2c_frame_5657d8[0x108-0xd8])
#define fStack_d4 (*(g2c_fa_float *)(void *)&g2c_frame_5657d8[0x108-0xd4])
#define fStack_d0 (*(g2c_fa_float *)(void *)&g2c_frame_5657d8[0x108-0xd0])
#define fStack_cc (*(g2c_fa_float *)(void *)&g2c_frame_5657d8[0x108-0xcc])
#define fStack_c8 (*(g2c_fa_float *)(void *)&g2c_frame_5657d8[0x108-0xc8])
#define bStack_c4 (*(g2c_fa_byte *)(void *)&g2c_frame_5657d8[0x108-0xc4])
#define fStack_c0 (*(g2c_fa_float *)(void *)&g2c_frame_5657d8[0x108-0xc0])
#define fStack_bc (*(g2c_fa_float *)(void *)&g2c_frame_5657d8[0x108-0xbc])
#define fStack_b8 (*(g2c_fa_float *)(void *)&g2c_frame_5657d8[0x108-0xb8])
#define fStack_b4 (*(g2c_fa_float *)(void *)&g2c_frame_5657d8[0x108-0xb4])
#define fStack_b0 (*(g2c_fa_float *)(void *)&g2c_frame_5657d8[0x108-0xb0])
#define fStack_ac (*(g2c_fa_float *)(void *)&g2c_frame_5657d8[0x108-0xac])
#define fStack_a8 (*(g2c_fa_float *)(void *)&g2c_frame_5657d8[0x108-0xa8])
#define fStack_a4 (*(g2c_fa_float *)(void *)&g2c_frame_5657d8[0x108-0xa4])
#define fStack_a0 (*(g2c_fa_float *)(void *)&g2c_frame_5657d8[0x108-0xa0])
#define fStack_9c (*(g2c_fa_float *)(void *)&g2c_frame_5657d8[0x108-0x9c])
#define fStack_98 (*(g2c_fa_float *)(void *)&g2c_frame_5657d8[0x108-0x98])
#define fStack_94 (*(g2c_fa_float *)(void *)&g2c_frame_5657d8[0x108-0x94])
#define fStack_90 (*(g2c_fa_float *)(void *)&g2c_frame_5657d8[0x108-0x90])
#define fStack_70 (*(g2c_fa_float *)(void *)&g2c_frame_5657d8[0x108-0x70])
#define fStack_6c (*(g2c_fa_float *)(void *)&g2c_frame_5657d8[0x108-0x6c])
  
  audio_uart_lv_memzero_48949c((uint)&cStack_108,0x48);
  piVar2 = (((int *)&audio_uart_nema_vg_context_cell));
  cStack_108 = '\x01';
  uStack_106 = 1;
  uVar9 = 0;
  do {
    fStack_b0 = (float)g2c_bits_to_float((uint)(d15_pair));
    fStack_ac = (float)g2c_bits_to_float((uint)(((ulonglong)d15_pair >> 0x20)));
LAB_0056580e:
    iVar4 = iStack_104;
    if (*a <= uVar9) {
      if (cStack_107 == '\x01') {
        fVar25 = g2c_bits_to_float((uint)((0x0u)));
        fStack_6c = g2c_bits_to_float((uint)((0x0u)));
        if (cStack_108 == '\0') {
          fVar25 = fStack_cc;
          fStack_6c = fStack_c8;
        }
        iVar4 = *piVar2;
        fStack_70 = fVar25;
        if (*(char *)(iVar4 + 0x1bc) != '\0') {
          fStack_70 = *(float *)(iVar4 + 0xec) * fVar25 + *(float *)(iVar4 + 0xf0) * fStack_6c +
                      *(float *)(iVar4 + 0xf4);
          fStack_6c = *(float *)(iVar4 + 0xf8) * fVar25 + *(float *)(iVar4 + 0xfc) * fStack_6c +
                      *(float *)(iVar4 + 0x100);
        }
        *(undefined4 *)(iVar4 + 0x24) = 0x1ff;
        uVar7 = g2c_nema_vg_arc_build_564974(fStack_f4,fStack_f0,fStack_70,fStack_6c);
        if (uVar7 != 0) goto LAB_005671fc;
      }
      return 0;
    }
    puVar6 = (uint *)*piVar2;
    puVar6[9] = 0;
    bVar10 = *(byte *)(a[2] + uVar9);
    uVar12 = (uint)bVar10;
    uVar7 = uVar12 & 0x6f;
    fStack_fc = fStack_f4;
    fStack_f8 = fStack_f0;
    uVar9 = uVar9 + 1;
    bVar15 = -1 < (int)(uVar12 << 0x1b);
    bVar13 = bStack_c4 & 0x6f;
    if (uVar7 == 1) {
      if ((cStack_107 == '\x01') && (iStack_104 != 0)) {
        fVar25 = g2c_bits_to_float((uint)((0x0u)));
        fStack_bc = g2c_bits_to_float((uint)((0x0u)));
        if (cStack_108 == '\0') {
          fVar25 = fStack_cc;
          fStack_bc = fStack_c8;
        }
        fStack_c0 = fVar25;
        if ((char)puVar6[0x6f] != '\0') {
          fStack_c0 = ((float *)(puVar6))[0x3b] * fVar25 + ((float *)(puVar6))[0x3c] * fStack_bc +
                      ((float *)(puVar6))[0x3d];
          fStack_bc = ((float *)(puVar6))[0x3e] * fVar25 + ((float *)(puVar6))[0x3f] * fStack_bc +
                      ((float *)(puVar6))[0x40];
        }
        puVar6[9] = 0x1ff;
        uVar3 = g2c_nema_vg_arc_build_564974(fStack_f4,fStack_f0,fStack_c0,fStack_bc);
        if (uVar3 != 0) goto LAB_005658d2;
      }
      cStack_108 = '\0';
      uStack_106 = 1;
      iStack_100 = iVar4;
      if (bVar15) {
        fStack_f4 = *(float *)(a[3] + iVar4 * 4);
        fStack_f0 = *(float *)(a[3] + (iVar4 + 1) * 4);
      }
      else {
        fStack_f4 = fStack_dc + *(float *)(a[3] + iVar4 * 4);
        fStack_f0 = fStack_d8 + *(float *)(a[3] + (iVar4 + 1) * 4);
      }
      iStack_104 = iVar4 + 2;
      fStack_cc = fStack_f4;
      fStack_c8 = fStack_f0;
LAB_00566188:
      fStack_d8 = fStack_f0;
      iVar4 = *piVar2;
      fStack_dc = fStack_f4;
      bStack_c4 = bVar10;
      if (*(char *)(iVar4 + 0x1bc) != '\0') {
        fVar25 = *(float *)(iVar4 + 0xf0) * fStack_f0;
        fStack_f0 = *(float *)(iVar4 + 0xf8) * fStack_f4 + *(float *)(iVar4 + 0xfc) * fStack_f0 +
                    *(float *)(iVar4 + 0x100);
        fStack_f4 = *(float *)(iVar4 + 0xec) * fStack_f4 + fVar25 + *(float *)(iVar4 + 0xf4);
      }
    }
    else {
      if (uVar12 == 0 || uVar12 == 0x80) {
        if (cStack_108 == '\x01') {
          fStack_f4 = 0.0f;
          fStack_f0 = 0.0f;
        }
        else {
          fStack_f4 = fStack_cc;
          fStack_f0 = fStack_c8;
        }
        uStack_106 = 0;
        cStack_107 = '\0';
        goto LAB_00566188;
      }
      if ((iStack_104 == 0) && (cStack_108 = '\x01', (char)puVar6[0x6f] != '\0')) {
        fStack_fc = ((float *)(puVar6))[0x3b] * fStack_f4 + ((float *)(puVar6))[0x3c] * fStack_f0 +
                    ((float *)(puVar6))[0x3d];
        fStack_f8 = ((float *)(puVar6))[0x3e] * fStack_f4 + ((float *)(puVar6))[0x3f] * fStack_f0 +
                    ((float *)(puVar6))[0x40];
      }
      uStack_106 = 0;
      if (uVar7 == 6) {
        uVar3 = a[3];
        fStack_ec = *(float *)(uVar3 + iStack_104 * 4);
        fStack_e8 = *(float *)(uVar3 + (iStack_104 + 1) * 4);
        fStack_e4 = *(float *)(uVar3 + (iStack_104 + 2) * 4);
        fStack_e0 = *(float *)(uVar3 + (iStack_104 + 3) * 4);
        iStack_104 = iStack_104 + 4;
        if (!bVar15) {
          fStack_ec = fStack_ec + fStack_dc;
          fStack_e8 = fStack_e8 + fStack_d8;
          fStack_e4 = fStack_e4 + fStack_dc;
          fStack_e0 = fStack_e0 + fStack_d8;
        }
LAB_00565bd0:
        fStack_d4 = fStack_e4;
        fStack_d0 = fStack_e0;
        if ((char)puVar6[0x6f] != '\0') {
          fVar25 = ((float *)(puVar6))[0x3c] * fStack_e8;
          fStack_e8 = ((float *)(puVar6))[0x3e] * fStack_ec + ((float *)(puVar6))[0x3f] * fStack_e8 +
                      ((float *)(puVar6))[0x40];
          fVar17 = ((float *)(puVar6))[0x3e] * fStack_e4;
          fStack_e4 = ((float *)(puVar6))[0x3b] * fStack_e4 + ((float *)(puVar6))[0x3c] * fStack_e0 +
                      ((float *)(puVar6))[0x3d];
          fStack_e0 = fVar17 + ((float *)(puVar6))[0x3f] * fStack_e0 + ((float *)(puVar6))[0x40];
          fStack_ec = ((float *)(puVar6))[0x3b] * fStack_ec + fVar25 + ((float *)(puVar6))[0x3d];
        }
      }
      else {
        if (uVar7 == 5) {
          fStack_ec = *(float *)(a[3] + iStack_104 * 4);
          fStack_e8 = *(float *)(a[3] + (iStack_104 + 1) * 4);
          iStack_104 = iStack_104 + 2;
          if (!bVar15) {
            fStack_ec = fStack_ec + fStack_dc;
            fStack_e8 = fStack_e8 + fStack_d8;
          }
        }
        else {
          if (uVar7 != 7) {
            if (uVar7 == 8) {
              if ((bVar13 == 5 || bVar13 == 7) || (bVar13 == 6 || bVar13 == 8)) {
                fStack_ec = fStack_dc * 2.0f - fStack_d4;
                fStack_e8 = fStack_d8 * 2.0f - fStack_d0;
              }
              else {
                fStack_ec = fStack_dc;
                fStack_e8 = fStack_d8;
              }
              fStack_e4 = *(float *)(a[3] + iStack_104 * 4);
              fStack_e0 = *(float *)(a[3] + (iStack_104 + 1) * 4);
              iStack_104 = iStack_104 + 2;
              if (!bVar15) {
                fStack_e4 = fStack_e4 + fStack_dc;
                fStack_e0 = fStack_e0 + fStack_d8;
              }
              goto LAB_00565bd0;
            }
            if ((uVar12 & 0xf) == 9) {
              uVar3 = a[3];
              fStack_ec = *(float *)(uVar3 + iStack_104 * 4);
              fStack_e8 = *(float *)(uVar3 + (iStack_104 + 1) * 4);
              fStack_e4 = *(float *)(uVar3 + (iStack_104 + 2) * 4);
              iStack_104 = iStack_104 + 3;
              fStack_d4 = fStack_dc;
              fStack_d0 = fStack_d8;
              bStack_105 = bVar10;
            }
            goto LAB_00565c84;
          }
          if ((bVar13 == 5 || bVar13 == 7) || (bVar13 == 6 || bVar13 == 8)) {
            fStack_ec = fStack_dc * 2.0f - fStack_d4;
            fStack_e8 = fStack_d8 * 2.0f - fStack_d0;
          }
          else {
            fStack_ec = fStack_dc;
            fStack_e8 = fStack_d8;
          }
        }
        fStack_d4 = fStack_ec;
        fStack_d0 = fStack_e8;
        if ((char)puVar6[0x6f] != '\0') {
          fVar25 = ((float *)(puVar6))[0x3c] * fStack_e8;
          fStack_e8 = ((float *)(puVar6))[0x3e] * fStack_ec + ((float *)(puVar6))[0x3f] * fStack_e8 +
                      ((float *)(puVar6))[0x40];
          fStack_ec = ((float *)(puVar6))[0x3b] * fStack_ec + fVar25 + ((float *)(puVar6))[0x3d];
        }
      }
LAB_00565c84:
      if (uVar7 == 4) {
        fStack_f4 = fStack_dc;
        if (bVar15) {
          fStack_f0 = *(float *)(a[3] + iStack_104 * 4);
LAB_00566156:
          iStack_104 = iStack_104 + 1;
        }
        else {
          iVar4 = iStack_104 * 4;
          iStack_104 = iStack_104 + 1;
          fStack_f0 = fStack_d8 + *(float *)(a[3] + iVar4);
        }
        goto LAB_00566188;
      }
      if (uVar7 == 3) {
        if (bVar15) {
          fStack_f4 = *(float *)(a[3] + iStack_104 * 4);
        }
        else {
          fStack_f4 = fStack_dc + *(float *)(a[3] + iStack_104 * 4);
        }
        iStack_104 = iStack_104 + 1;
        fStack_f0 = fStack_d8;
        goto LAB_00566188;
      }
      if (uVar7 == 10) {
        fVar25 = *(float *)(a[3] + iStack_104 * 4);
        iStack_104 = iStack_104 + 1;
        if (cStack_108 == '\x01') {
          fVar16 = ((float *)(puVar6))[0xc];
          fVar17 = fStack_fc;
          if ((fStack_fc < fVar16)) {
            fVar17 = fVar16;
          }
          fVar19 = ((float *)(puVar6))[0xd];
          if ((fVar19 < fVar17)) {
            fVar17 = fVar19;
          }
          fVar22 = fStack_f8;
          if ((fStack_f8 < fVar16)) {
            fVar22 = fVar16;
          }
          if ((fVar19 < fVar22)) {
            fVar22 = fVar19;
          }
          uVar3 = puVar6[3];
          if (puVar6[0xb] == 0) {
            if (uVar3 < *puVar6) {
              *(undefined1 *)(puVar6[7] + uVar3) = 1;
              *(int *)(*piVar2 + 0xc) = *(int *)(*piVar2 + 0xc) + 1;
            }
            else {
              puVar6[3] = uVar3 + 1;
              puVar6[10] = 2;
              puVar6[0xb] = 1;
            }
          }
          else {
            puVar6[3] = uVar3 + 1;
          }
          iVar5 = *piVar2;
          iVar4 = *(int *)(iVar5 + 8);
          if (*(int *)(iVar5 + 0x2c) == 0) {
            uVar3 = iVar4 + 1;
            if (uVar3 < *(uint *)(iVar5 + 4)) {
              iVar8 = *(int *)(iVar5 + 0x10);
              *(float *)(iVar8 + iVar4 * 4) = fVar17;
              *(uint *)(iVar5 + 8) = uVar3;
              *(float *)(iVar8 + uVar3 * 4) = fVar22;
              *(int *)(iVar5 + 8) = iVar4 + 2;
            }
            else {
              *(int *)(iVar5 + 8) = iVar4 + 2;
              *(undefined4 *)(iVar5 + 0x28) = 2;
              *(undefined4 *)(iVar5 + 0x2c) = 1;
            }
          }
          else {
            *(int *)(iVar5 + 8) = iVar4 + 2;
          }
          cStack_108 = '\0';
        }
        iVar4 = (int)fVar25 / 2;
        if (0 < iVar4) {
          do {
            if (bVar15) {
              fStack_f4 = *(float *)(a[3] + iStack_104 * 4);
              fStack_f0 = *(float *)(a[3] + (iStack_104 + 1) * 4);
            }
            else {
              fStack_f4 = *(float *)(a[3] + iStack_104 * 4) + fStack_dc;
              fStack_f0 = *(float *)(a[3] + (iStack_104 + 1) * 4) + fStack_d8;
            }
            iStack_104 = iStack_104 + 2;
            fStack_d8 = fStack_f0;
            iVar5 = *piVar2;
            fStack_dc = fStack_f4;
            if (*(char *)(iVar5 + 0x1bc) != '\0') {
              fVar25 = *(float *)(iVar5 + 0xf0) * fStack_f0;
              fStack_f0 = *(float *)(iVar5 + 0xf8) * fStack_f4 +
                          *(float *)(iVar5 + 0xfc) * fStack_f0 + *(float *)(iVar5 + 0x100);
              fStack_f4 = *(float *)(iVar5 + 0xec) * fStack_f4 + fVar25 + *(float *)(iVar5 + 0xf4);
            }
            bStack_c4 = bVar10;
            uVar3 = g2c_nema_vg_arc_build_564974(fStack_fc,fStack_f8,fStack_f4,fStack_f0);
            if (uVar3 != 0) goto LAB_005658d2;
            fStack_fc = fStack_f4;
            fStack_f8 = fStack_f0;
            iVar4 = iVar4 + -1;
          } while (iVar4 != 0);
        }
        fVar16 = fStack_f0;
        fVar17 = fStack_f4;
        fVar25 = fStack_dc - fStack_cc;
        bVar15 = fVar25 == 0.0f;
        if (bVar15) {
          fVar25 = fStack_d8 - fStack_c8;
        }
        if (!bVar15 || (!bVar15 || fVar25 != 0.0f)) {
          fStack_f0 = fStack_c8;
          fStack_fc = fStack_f4;
          fStack_f8 = fVar16;
          fStack_f4 = fStack_cc;
          fStack_d8 = fStack_c8;
          iVar4 = *piVar2;
          fStack_dc = fStack_cc;
          if (*(char *)(iVar4 + 0x1bc) != '\0') {
            fStack_f4 = *(float *)(iVar4 + 0xec) * fStack_cc + *(float *)(iVar4 + 0xf0) * fStack_c8
                        + *(float *)(iVar4 + 0xf4);
            fStack_f0 = *(float *)(iVar4 + 0xf8) * fStack_cc + *(float *)(iVar4 + 0xfc) * fStack_c8
                        + *(float *)(iVar4 + 0x100);
          }
          uVar3 = g2c_nema_vg_arc_build_564974(fVar17,fVar16,fStack_f4,fStack_f0);
          if (uVar3 != 0) {
LAB_005658d2:
            g2c_nema_vg_set_aa_51778c(0);
            g2c_nema_vg_set_aa2_517796(0);
            audio_uart_nema_vg_set_error_51565c(uVar3);
            g2c_nema_vg_set_aa_51778c(0);
            g2c_nema_vg_set_aa2_517796(0);
            audio_uart_nema_vg_set_error_51565c(uVar3);
            return uVar3;
          }
        }
        cStack_107 = '\0';
      }
      else {
        if (uVar7 != 0xb) {
          if (bVar15) {
            fStack_f4 = *(float *)(a[3] + iStack_104 * 4);
            iStack_104 = iStack_104 + 1;
            fStack_f0 = *(float *)(a[3] + iStack_104 * 4);
            goto LAB_00566156;
          }
          fStack_f4 = *(float *)(a[3] + iStack_104 * 4) + fStack_dc;
          fStack_f0 = *(float *)(a[3] + (iStack_104 + 1) * 4) + fStack_d8;
          iStack_104 = iStack_104 + 2;
          goto LAB_00566188;
        }
        iVar4 = iStack_104 * 4;
        iStack_104 = iStack_104 + 1;
        fVar25 = *(float *)(a[3] + iVar4);
        if (cStack_108 == '\x01') {
          fVar17 = ((float *)(puVar6))[0xc];
          fVar16 = fStack_fc;
          if ((fStack_fc < fVar17)) {
            fVar16 = fVar17;
          }
          fVar19 = ((float *)(puVar6))[0xd];
          if ((fVar19 < fVar16)) {
            fVar16 = fVar19;
          }
          if (!(fStack_f8 < fVar17)) {
            fVar17 = fStack_f8;
          }
          if ((fVar19 < fVar17)) {
            fVar17 = fVar19;
          }
          uVar3 = puVar6[3];
          if (puVar6[0xb] == 0) {
            if (uVar3 < *puVar6) {
              *(undefined1 *)(puVar6[7] + uVar3) = 1;
              *(int *)(*piVar2 + 0xc) = *(int *)(*piVar2 + 0xc) + 1;
            }
            else {
              puVar6[3] = uVar3 + 1;
              puVar6[10] = 2;
              puVar6[0xb] = 1;
            }
          }
          else {
            puVar6[3] = uVar3 + 1;
          }
          iVar5 = *piVar2;
          iVar4 = *(int *)(iVar5 + 8);
          if (*(int *)(iVar5 + 0x2c) == 0) {
            uVar3 = iVar4 + 1;
            if (uVar3 < *(uint *)(iVar5 + 4)) {
              iVar8 = *(int *)(iVar5 + 0x10);
              *(float *)(iVar8 + iVar4 * 4) = fVar16;
              *(uint *)(iVar5 + 8) = uVar3;
              *(float *)(iVar8 + uVar3 * 4) = fVar17;
              *(int *)(iVar5 + 8) = iVar4 + 2;
            }
            else {
              *(int *)(iVar5 + 8) = iVar4 + 2;
              *(undefined4 *)(iVar5 + 0x28) = 2;
              *(undefined4 *)(iVar5 + 0x2c) = 1;
            }
          }
          else {
            *(int *)(iVar5 + 8) = iVar4 + 2;
          }
          cStack_108 = '\0';
        }
        iVar4 = (int)fVar25 / 2;
        if (0 < iVar4) {
          do {
            if (bVar15) {
              fStack_f4 = *(float *)(a[3] + iStack_104 * 4);
              fStack_f0 = *(float *)(a[3] + (iStack_104 + 1) * 4);
            }
            else {
              fStack_f4 = *(float *)(a[3] + iStack_104 * 4) + fStack_dc;
              fStack_f0 = *(float *)(a[3] + (iStack_104 + 1) * 4) + fStack_d8;
            }
            iStack_104 = iStack_104 + 2;
            fStack_d8 = fStack_f0;
            iVar5 = *piVar2;
            fStack_dc = fStack_f4;
            if (*(char *)(iVar5 + 0x1bc) != '\0') {
              fVar25 = *(float *)(iVar5 + 0xf0) * fStack_f0;
              fStack_f0 = *(float *)(iVar5 + 0xf8) * fStack_f4 +
                          *(float *)(iVar5 + 0xfc) * fStack_f0 + *(float *)(iVar5 + 0x100);
              fStack_f4 = *(float *)(iVar5 + 0xec) * fStack_f4 + fVar25 + *(float *)(iVar5 + 0xf4);
            }
            bStack_c4 = bVar10;
            uVar3 = g2c_nema_vg_arc_build_564974(fStack_fc,fStack_f8,fStack_f4,fStack_f0);
            if (uVar3 != 0) goto LAB_005658d2;
            fStack_fc = fStack_f4;
            fStack_f8 = fStack_f0;
            iVar4 = iVar4 + -1;
          } while (iVar4 != 0);
        }
      }
    }
    fVar21 = fStack_d0;
    fVar22 = fStack_d4;
    fVar19 = fStack_d8;
    fVar16 = fStack_dc;
    fVar17 = fStack_f0;
    fVar25 = fStack_f4;
    if (cStack_108 == '\x01') {
      puVar6 = (uint *)*piVar2;
      fVar18 = ((float *)(puVar6))[0xc];
      fVar23 = fStack_fc;
      if ((fStack_fc < fVar18)) {
        fVar23 = fVar18;
      }
      fVar20 = ((float *)(puVar6))[0xd];
      if ((fVar20 < fVar23)) {
        fVar23 = fVar20;
      }
      fVar26 = fStack_f8;
      if ((fStack_f8 < fVar18)) {
        fVar26 = fVar18;
      }
      if ((fVar20 < fVar26)) {
        fVar26 = fVar20;
      }
      uVar3 = puVar6[3];
      if (puVar6[0xb] == 0) {
        if (uVar3 < *puVar6) {
          *(undefined1 *)(puVar6[7] + uVar3) = 1;
          *(int *)(*piVar2 + 0xc) = *(int *)(*piVar2 + 0xc) + 1;
        }
        else {
          puVar6[3] = uVar3 + 1;
          puVar6[10] = 2;
          puVar6[0xb] = 1;
        }
      }
      else {
        puVar6[3] = uVar3 + 1;
      }
      iVar5 = *piVar2;
      iVar4 = *(int *)(iVar5 + 8);
      if (*(int *)(iVar5 + 0x2c) == 0) {
        uVar3 = iVar4 + 1;
        if (uVar3 < *(uint *)(iVar5 + 4)) {
          iVar8 = *(int *)(iVar5 + 0x10);
          *(float *)(iVar8 + iVar4 * 4) = fVar23;
          *(uint *)(iVar5 + 8) = uVar3;
          *(float *)(iVar8 + uVar3 * 4) = fVar26;
          *(int *)(iVar5 + 8) = iVar4 + 2;
        }
        else {
          *(int *)(iVar5 + 8) = iVar4 + 2;
          *(undefined4 *)(iVar5 + 0x28) = 2;
          *(undefined4 *)(iVar5 + 0x2c) = 1;
        }
      }
      else {
        *(int *)(iVar5 + 8) = iVar4 + 2;
      }
      cStack_108 = '\0';
    }
    if (uVar7 == 5 || uVar7 == 7) {
      fStack_b0 = fStack_f4;
      fStack_ac = fStack_f0;
      iVar4 = 1;
      uVar24 = CONCAT44(g2c_float_to_bits(fStack_e8),g2c_float_to_bits(fStack_ec));
      fStack_b8 = fStack_fc;
      fStack_b4 = fStack_f8;
      uVar32 = CONCAT44(g2c_float_to_bits(fStack_f0),g2c_float_to_bits(fStack_f4));
      do {
        puVar6 = (uint *)*piVar2;
        bVar1 = false;
        fVar16 = ((float *)(puVar6))[0xd];
        /* stock 0x5662ec vcmp; itt ge; vcmpge 0x5662f6; blt 0x566370 (GE ordered; wave19) */
        bVar15 = (fVar16 >= fStack_b8);
        if (bVar15) {
          bVar15 = (fVar16 >= fStack_b4);
        }
        fVar19 = (float)g2c_bits_to_float((uint)(uVar24));
        fVar22 = (float)g2c_bits_to_float((uint)(((ulonglong)uVar24 >> 0x20)));
        fVar23 = (float)g2c_bits_to_float((uint)(((ulonglong)uVar32 >> 0x20)));
        fVar21 = (float)g2c_bits_to_float((uint)(uVar32));
        if (bVar15) {
          fVar18 = ((float *)(puVar6))[0xc];
          /* stock 0x566308/0x566312 itt ge; blt 0x566370 (GE ordered; wave19) */
          bVar15 = (fStack_b8 >= fVar18);
          if (bVar15) {
            bVar15 = (fStack_b4 >= fVar18);
          }
          if (bVar15) {
            /* stock 0x56631c/0x566326 itt ge; blt 0x566370 (GE ordered; wave19) */
            bVar15 = (fVar16 >= fVar19);
            if (bVar15) {
              bVar15 = (fVar16 >= fVar22);
            }
            if (bVar15) {
              /* stock 0x566330/0x56633a itt ge; blt 0x566370 (GE ordered; wave19) */
              bVar15 = (fVar19 >= fVar18);
              if (bVar15) {
                bVar15 = (fVar22 >= fVar18);
              }
              if (bVar15) {
                /* stock 0x566344/0x566352 ittt ge; blt 0x566370 (GE ordered; wave19) */
                bVar15 = (fVar16 >= fVar21);
                fVar20 = fStack_b8;
                if (bVar15) {
                  bVar15 = (fVar16 >= fVar23);
                  fVar20 = fVar23;
                }
                if (bVar15) {
                  /* stock 0x56635c/0x566366 itt ge; bge 0x566418 (GE ordered; wave19) */
                  bVar15 = (fVar21 >= fVar18);
                  if (bVar15) {
                    bVar15 = (fVar20 >= fVar18);
                  }
                  if (bVar15) {
                    bVar1 = true;
                  }
                }
              }
            }
          }
        }
        fVar18 = ((float *)(puVar6))[0xc] + (50.0f);
        /* stock 0x566388 vcmp; itttt lt; vcmplt 0x5663a2, vcmplt 0x5663aa (LT incl. unordered x3, blt 0x566408 = all three LT; wave19) */
        bVar15 = !(fStack_b8 >= fVar18);
        fVar16 = fVar16 + (-50.0f);
        if (bVar15) {
          bVar15 = !(fVar19 >= fVar18);
        }
        if (bVar15) {
          bVar15 = !(fVar21 >= fVar18);
        }
        if (!bVar15) {
          /* stock 0x5663b4 vcmp; itttt lt; vcmplt 0x5663be, vcmplt 0x5663c6 (LT incl. unordered x3, blt 0x566408 = all three LT; wave19) */
          bVar15 = !(fVar16 >= fStack_b8);
          if (bVar15) {
            bVar15 = !(fVar16 >= fVar19);
          }
          if (bVar15) {
            bVar15 = !(fVar16 >= fVar21);
          }
          if (bVar15) goto LAB_00566408;
          /* stock 0x5663d0 vcmp; itttt lt; vcmplt 0x5663da, vcmplt 0x5663e2 (LT incl. unordered x3, blt 0x566408 = all three LT; wave19) */
          bVar15 = !(fStack_b4 >= fVar18);
          if (bVar15) {
            bVar15 = !(fVar22 >= fVar18);
          }
          if (bVar15) {
            bVar15 = !(fVar23 >= fVar18);
          }
          if (bVar15) goto LAB_00566408;
          bVar15 = fVar16 < fStack_b4;
          bVar14 = bVar15 && (bVar15 && fVar16 < fVar22);
          if (bVar15 && (bVar15 && fVar16 < fVar22)) {
            bVar14 = fVar16 < fVar23;
          }
          if (bVar14) goto LAB_00566408;
          bVar15 = true;
        }
        else {
LAB_00566408:
          bVar15 = false;
        }
        if (bVar1) {
          if (bVar15) {
LAB_00566424:
            uVar7 = puVar6[3];
            if (puVar6[0xb] == 0) {
              if (uVar7 < *puVar6) {
                *(undefined1 *)(puVar6[7] + uVar7) = 5;
                *(int *)(*piVar2 + 0xc) = *(int *)(*piVar2 + 0xc) + 1;
              }
              else {
                puVar6[10] = 2;
                puVar6[3] = puVar6[3] + 1;
                puVar6[0xb] = 1;
              }
            }
            else {
              puVar6[3] = uVar7 + 1;
            }
            iVar8 = *piVar2;
            iVar5 = *(int *)(iVar8 + 8);
            if (*(int *)(iVar8 + 0x2c) == 0) {
              uVar12 = *(uint *)(iVar8 + 4);
              uVar7 = iVar5 + 1;
              if (uVar7 < uVar12) {
                iVar11 = *(int *)(iVar8 + 0x10);
                *(float *)(iVar11 + iVar5 * 4) = fVar19;
                *(uint *)(iVar8 + 8) = uVar7;
                *(float *)(iVar11 + uVar7 * 4) = fVar22;
                uVar7 = iVar5 + 3;
                *(int *)(iVar8 + 8) = iVar5 + 2;
                if (uVar7 < uVar12) {
                  *(float *)(iVar11 + (iVar5 + 2) * 4) = fVar21;
                  *(uint *)(iVar8 + 8) = uVar7;
                  *(float *)(iVar11 + uVar7 * 4) = fVar23;
                  *(int *)(iVar8 + 8) = iVar5 + 4;
                }
                else {
                  *(undefined4 *)(iVar8 + 0x28) = 2;
                  *(int *)(iVar8 + 8) = iVar5 + 4;
                  *(undefined4 *)(iVar8 + 0x2c) = 1;
                }
                goto LAB_005665ee;
              }
              *(int *)(iVar8 + 8) = iVar5 + 2;
              *(undefined4 *)(iVar8 + 0x28) = 2;
              *(undefined4 *)(iVar8 + 0x2c) = 1;
            }
            else {
              *(int *)(iVar8 + 8) = iVar5 + 2;
            }
            *(int *)(iVar8 + 8) = *(int *)(iVar8 + 8) + 2;
          }
          else {
LAB_00566446:
            uVar7 = g2c_nema_vg_arc_build_564974(fStack_b8,fStack_b4,fVar21,fVar23);
            if (uVar7 != 0) {
              g2c_nema_vg_set_aa_51778c(0);
              g2c_nema_vg_set_aa2_517796(0);
              audio_uart_nema_vg_set_error_51565c(uVar7);
              g2c_nema_vg_set_aa_51778c(0);
              g2c_nema_vg_set_aa2_517796(0);
              audio_uart_nema_vg_set_error_51565c(uVar7);
              return uVar7;
            }
          }
LAB_005665ee:
          iVar4 = iVar4 + -1;
          iVar5 = *piVar2;
          if (*(int *)(iVar5 + 700) != 0) {
            iVar8 = *(int *)(iVar5 + 700) + -1;
            *(int *)(iVar5 + 700) = iVar8;
            iVar5 = iVar5 + iVar8 * 0x18;
            fStack_b8 = *(float *)(iVar5 + 0x1cc);
            fStack_b4 = *(float *)(iVar5 + 0x1d0);
            uVar32 = *(undefined8 *)(iVar5 + 0x1dc);
            uVar24 = *(undefined8 *)(iVar5 + 0x1d4);
          }
        }
        else {
          if (!bVar15) goto LAB_00566446;
          if (9 < (int)puVar6[0xaf]) goto LAB_00566424;
          fVar18 = (fStack_b4 + fVar22) * 0.5f;
          fVar16 = (fStack_b8 + fVar19) * 0.5f;
          fVar21 = (fVar19 + fVar21) * 0.5f;
          fVar19 = (fVar22 + fVar23) * 0.5f;
          fVar22 = (fVar16 + fVar21) * 0.5f;
          puVar6[puVar6[0xaf] * 6 + 0x73] = (uint)g2c_float_to_bits(fVar22);
          fVar23 = (fVar18 + fVar19) * 0.5f;
          puVar6[puVar6[0xaf] * 6 + 0x74] = (uint)g2c_float_to_bits(fVar23);
          uVar24 = CONCAT44(g2c_float_to_bits(fVar18),g2c_float_to_bits(fVar16));
          puVar6[puVar6[0xaf] * 6 + 0x75] = (uint)g2c_float_to_bits(fVar21);
          uVar32 = CONCAT44(g2c_float_to_bits(fVar23),g2c_float_to_bits(fVar22));
          iVar4 = iVar4 + 1;
          puVar6[puVar6[0xaf] * 6 + 0x76] = (uint)g2c_float_to_bits(fVar19);
          puVar6[puVar6[0xaf] * 6 + 0x77] = (uint)g2c_float_to_bits(fVar25);
          puVar6[puVar6[0xaf] * 6 + 0x78] = (uint)g2c_float_to_bits(fVar17);
          puVar6[0xaf] = puVar6[0xaf] + 1;
        }
      } while (iVar4 != 0);
      fStack_b0 = (float)g2c_bits_to_float((uint)(uVar32));
      fStack_ac = (float)g2c_bits_to_float((uint)(((ulonglong)uVar32 >> 0x20)));
      goto LAB_0056580e;
    }
    if (uVar7 == 6 || uVar7 == 8) {
      uVar7 = g2c_nema_vg_arc_draw_5653a0
                        (fStack_fc,fStack_f8,fStack_ec,fStack_e8,fStack_e4,fStack_e0,fStack_f4,
                         fStack_f0);
joined_r0x0056717a:
      if (uVar7 != 0) goto LAB_005671fc;
      goto LAB_0056580e;
    }
    if ((uVar12 & 0xf) != 9) {
      if (uVar7 == 10 || uVar7 == 0xb) goto LAB_0056580e;
      if ((uVar7 == 2 || uVar7 == 4) || uVar7 == 3) {
        uVar7 = g2c_nema_vg_arc_build_564974(fStack_fc,fStack_f8,fStack_f4,fStack_f0);
      }
      else {
        if (uVar7 == 1) {
          puVar6 = (uint *)*piVar2;
          fVar17 = ((float *)(puVar6))[0xc];
          if ((fStack_f4 < fVar17)) {
            fVar25 = fVar17;
          }
          fVar16 = ((float *)(puVar6))[0xd];
          if ((fVar16 < fVar25)) {
            fVar25 = fVar16;
          }
          fVar19 = fStack_f0;
          if ((fStack_f0 < fVar17)) {
            fVar19 = fVar17;
          }
          if ((fVar16 < fVar19)) {
            fVar19 = fVar16;
          }
          uVar7 = puVar6[3];
          if (puVar6[0xb] == 0) {
            if (uVar7 < *puVar6) {
              *(undefined1 *)(puVar6[7] + uVar7) = 1;
              *(int *)(*piVar2 + 0xc) = *(int *)(*piVar2 + 0xc) + 1;
            }
            else {
              puVar6[3] = uVar7 + 1;
              puVar6[10] = 2;
              puVar6[0xb] = 1;
            }
          }
          else {
            puVar6[3] = uVar7 + 1;
          }
          iVar4 = *piVar2;
          if (*(int *)(iVar4 + 0x2c) == 0) {
            iVar5 = *(int *)(iVar4 + 8);
            uVar7 = iVar5 + 1;
            if (*(uint *)(iVar4 + 4) <= uVar7) {
              *(int *)(iVar4 + 8) = iVar5 + 2;
              *(undefined4 *)(iVar4 + 0x28) = 2;
              *(undefined4 *)(iVar4 + 0x2c) = 1;
              goto LAB_0056580e;
            }
            iVar8 = *(int *)(iVar4 + 0x10);
            *(float *)(iVar8 + iVar5 * 4) = fVar25;
            *(uint *)(iVar4 + 8) = uVar7;
            *(float *)(iVar8 + uVar7 * 4) = fVar19;
          }
          else {
            iVar5 = *(int *)(iVar4 + 8);
          }
          *(int *)(iVar4 + 8) = iVar5 + 2;
          goto LAB_0056580e;
        }
        *(undefined4 *)(*piVar2 + 0x24) = 0x100;
        uVar7 = g2c_nema_vg_arc_build_564974(fStack_fc,fStack_f8,fStack_f4,fStack_f0);
      }
      goto joined_r0x0056717a;
    }
    fVar25 = ABS(fStack_d4);
    if (!(ABS(fStack_d4) < ABS(fStack_dc))) {
      fVar25 = ABS(fStack_dc);
    }
    fVar17 = fStack_d4 - fStack_dc;
    if ((fVar17 < 0.0f)) {
      fVar17 = fStack_dc - fStack_d4;
    }
    if (fVar17 <= fVar25 * (9.999999747378752e-06f)) {
      fVar25 = ABS(fStack_d0);
      if (!(ABS(fStack_d0) < ABS(fStack_d8))) {
        fVar25 = ABS(fStack_d8);
      }
      fVar17 = fStack_d0 - fStack_d8;
      if ((fVar17 < 0.0f)) {
        fVar17 = fStack_d8 - fStack_d0;
      }
      if (fVar17 <= fVar25 * (9.999999747378752e-06f)) goto LAB_0056580e;
    }
    fVar25 = (float)g2c_bits_to_float((uint)(d10_pair));
    fVar17 = ABS(fStack_ec);
    bVar15 = (1.0000000656873453e-05f) <= fVar17;
    if (bVar15) {
      fVar25 = ABS(fStack_e8);
    }
    d10_pair = CONCAT44(g2c_float_to_bits(fVar17),g2c_float_to_bits(fVar25));
    fVar23 = fStack_e8;
    if (bVar15) {
      fVar23 = (1.0000000656873453e-05f);
    }
    if (!bVar15 || (!bVar15 || fVar25 < fVar23)) {
      uVar7 = g2c_nema_vg_arc_build_564974(fStack_fc,fStack_f8,fStack_f4,fStack_f0);
      if (uVar7 != 0) goto LAB_00566cee;
      goto LAB_0056580e;
    }
    bVar13 = bStack_105 >> 6 & 1;
    bVar10 = bVar13;
    if ((int)((uint)bStack_105 << 0x1a) < 0) {
      bVar10 = bVar13 ^ 1;
    }
    fVar18 = fStack_e4 * (0.01745329238474369f);
    fVar23 = audio_uart_float_trig_mode1_50968c(fVar18);
    fVar18 = audio_uart_float_trig_mode0_509690(fVar18);
    fStack_a8 = fVar21 * fVar23 - fVar22 * fVar18;
    fVar26 = fStack_a8 / fVar25;
    fStack_b4 = fVar19 * fVar23 - fVar16 * fVar18;
    fVar21 = fVar22 * fVar23 + fVar21 * fVar18;
    fVar27 = fVar16 * fVar23 + fVar19 * fVar18;
    fVar20 = fVar21 / fVar17;
    fVar28 = fVar27 / fVar17;
    fVar29 = fStack_b4 / fVar25;
    fVar22 = fVar20 + fVar28;
    fVar16 = fVar26 + fVar29;
    fVar30 = fVar20 - fVar28;
    fVar31 = fVar26 - fVar29;
    fVar19 = fVar30 * fVar30 + fVar31 * fVar31;
    if (fVar19 == 0.0f) {
      uVar7 = 0x100;
      goto LAB_005671fc;
    }
    fStack_b8 = 1.0f / fVar19 + -0.25f;
    if ((fStack_b8 < 0.0f)) {
      fStack_b8 = 0.0f;
      fVar16 = audio_uart_float_sqrt_4397a8(fVar19 * 0.25f);
      fVar25 = fVar25 * fVar16;
      fVar17 = fVar17 * fVar16;
      d10_pair = CONCAT44(g2c_float_to_bits(fVar17),g2c_float_to_bits(fVar25));
      fVar20 = fVar21 / fVar17;
      fVar26 = fStack_a8 / fVar25;
      fVar28 = fVar27 / fVar17;
      fVar29 = fStack_b4 / fVar25;
      fVar22 = fVar20 + fVar28;
      fVar16 = fVar26 + fVar29;
      fVar30 = fVar20 - fVar28;
      fVar31 = fVar26 - fVar29;
    }
    fVar17 = audio_uart_float_sqrt_4397a8(fStack_b8);
    fStack_b8 = fVar17 * fVar30;
    fVar27 = fVar22 * 0.5f + fVar17 * fVar31;
    fVar30 = fVar16 * 0.5f - fStack_b8;
    fVar19 = audio_uart_float_two_input_angle_50969c(fVar26 - fVar30,fVar20 - fVar27);
    fVar25 = audio_uart_float_two_input_angle_50969c(fVar29 - fVar30,fVar28 - fVar27);
    fVar19 = fVar19 * (57.295780181884766f);
    fVar25 = fVar25 * (57.295780181884766f);
    fVar21 = fVar25 - fVar19;
    if ((fVar21 < 0.0f)) {
      fVar21 = fVar21 + (360.0f);
    }
    if (((!(fVar21 < (180.0f))) || (bVar10 == 0)) &&
       ((fVar21 < (180.0f) || (bVar10 != 0)))) {
      fVar27 = fVar22 * 0.5f - fVar17 * fVar31;
      fVar30 = fVar16 * 0.5f + fStack_b8;
      fVar19 = audio_uart_float_two_input_angle_50969c(fVar26 - fVar30,fVar20 - fVar27);
      fVar25 = audio_uart_float_two_input_angle_50969c(fVar29 - fVar30,fVar28 - fVar27);
      fVar19 = fVar19 * (57.295780181884766f);
      fVar25 = fVar25 * (57.295780181884766f);
    }
    fVar16 = (0.01745329238474369f);
    fVar17 = (0.01745329238474369f);
    fVar28 = (float)g2c_bits_to_float((uint)(((ulonglong)d10_pair >> 0x20)));
    fVar26 = (float)g2c_bits_to_float((uint)(d10_pair));
    fVar20 = fVar27 * fVar28 * fVar23 - fVar30 * fVar26 * fVar18;
    fVar21 = fVar27 * fVar28 * fVar18 + fVar30 * fVar26 * fVar23;
    fVar22 = fVar19;
    if (bVar13 == 0) {
      fVar22 = fVar25;
      fVar25 = fVar19;
    }
    if ((fVar25 < fVar22)) {
      fVar25 = fVar25 + (360.0f);
    }
    fVar19 = (fStack_e4 / (180.0f)) * (3.1415927410125732f);
    if (bVar13 == 0) {
      d15_pair = CONCAT44(g2c_float_to_bits(fStack_ac),g2c_float_to_bits(fStack_b0));
      iVar4 = 1;
      while ((fVar22 < fVar25)) {
        fVar23 = fVar25 + (-90.0f);
        iVar5 = (uint)(fVar22 < fVar23) << 0x1f;
        fVar17 = (-90.0f);
        if (iVar5 < 0) {
          fVar17 = fVar23;
        }
        if (-1 < iVar5) {
          fVar17 = fVar22;
        }
        if (!(fVar22 < fVar23)) {
          iVar4 = iVar4 + 2;
        }
        fVar25 = fVar25 * fVar16;
        fVar27 = fVar17 * fVar16 - fVar25;
        fVar17 = audio_uart_float_tangent_563f40(fVar27 * 0.25f);
        fVar17 = fVar17 * (1.3333333730697632f);
        fVar18 = audio_uart_float_trig_mode1_50968c(fVar27);
        fStack_a0 = audio_uart_float_trig_mode0_509690(fVar27);
        fStack_94 = fVar18 + fVar17 * fStack_a0;
        fStack_90 = fStack_a0 - fVar17 * fVar18;
        fStack_ac = 1.0f;
        fStack_a8 = 0.0f;
        fStack_9c = 1.0f;
        fStack_a4 = fVar18;
        fStack_98 = fVar17;
        fVar17 = audio_uart_float_trig_mode1_50968c(fVar25);
        fVar25 = audio_uart_float_trig_mode0_509690(fVar25);
        fVar18 = audio_uart_float_trig_mode1_50968c(fVar19);
        fVar27 = audio_uart_float_trig_mode0_509690(fVar19);
        if (iVar4 << 0x1f < 0) {
          fStack_ac = fStack_fc;
          fStack_a8 = fStack_f8;
        }
        else {
          g2c_nema_vg_quad_to_51a660(fVar17,fVar25,1.0f,1.0f,g2c_bits_to_float((uint)((0x0u))),g2c_bits_to_float((uint)((0x0u))),&fStack_ac);
          g2c_nema_vg_quad_to_51a660(fVar18,fVar27,fVar28,fVar26,fVar20,fVar21,&fStack_ac);
          iVar5 = *piVar2;
          if (*(char *)(iVar5 + 0x21) != '\0') {
            fVar29 = *(float *)(iVar5 + 0x3c) * fStack_a8;
            fStack_a8 = *(float *)(iVar5 + 0x44) * fStack_ac + *(float *)(iVar5 + 0x48) * fStack_a8
                        + *(float *)(iVar5 + 0x4c);
            fStack_ac = *(float *)(iVar5 + 0x38) * fStack_ac + fVar29 + *(float *)(iVar5 + 0x40);
          }
        }
        g2c_nema_vg_quad_to_51a660(fVar17,fVar25,1.0f,1.0f,g2c_bits_to_float((uint)((0x0u))),g2c_bits_to_float((uint)((0x0u))),&fStack_9c);
        g2c_nema_vg_quad_to_51a660(fVar18,fVar27,fVar28,fVar26,fVar20,fVar21,&fStack_9c);
        g2c_nema_vg_quad_to_51a660(fVar17,fVar25,1.0f,1.0f,g2c_bits_to_float((uint)((0x0u))),g2c_bits_to_float((uint)((0x0u))),&fStack_94);
        g2c_nema_vg_quad_to_51a660(fVar18,fVar27,fVar28,fVar26,fVar20,fVar21,&fStack_94);
        if (iVar4 << 0x1e < 0) {
          fStack_a4 = fStack_f4;
          fStack_a0 = fStack_f0;
        }
        else {
          g2c_nema_vg_quad_to_51a660(fVar17,fVar25,1.0f,1.0f,g2c_bits_to_float((uint)((0x0u))),g2c_bits_to_float((uint)((0x0u))),&fStack_a4);
          g2c_nema_vg_quad_to_51a660(fVar18,fVar27,fVar28,fVar26,fVar20,fVar21,&fStack_a4);
          iVar4 = *piVar2;
          if (*(char *)(iVar4 + 0x21) != '\0') {
            fVar25 = *(float *)(iVar4 + 0x3c) * fStack_a0;
            fStack_a0 = *(float *)(iVar4 + 0x44) * fStack_a4 + *(float *)(iVar4 + 0x48) * fStack_a0
                        + *(float *)(iVar4 + 0x4c);
            fStack_a4 = *(float *)(iVar4 + 0x38) * fStack_a4 + fVar25 + *(float *)(iVar4 + 0x40);
          }
        }
        iVar4 = *piVar2;
        if (*(char *)(iVar4 + 0x21) != '\0') {
          fVar25 = *(float *)(iVar4 + 0x3c) * fStack_98;
          fStack_98 = *(float *)(iVar4 + 0x44) * fStack_9c + *(float *)(iVar4 + 0x48) * fStack_98 +
                      *(float *)(iVar4 + 0x4c);
          fVar17 = *(float *)(iVar4 + 0x3c) * fStack_90;
          fStack_90 = *(float *)(iVar4 + 0x44) * fStack_94 + *(float *)(iVar4 + 0x48) * fStack_90 +
                      *(float *)(iVar4 + 0x4c);
          fStack_9c = *(float *)(iVar4 + 0x38) * fStack_9c + fVar25 + *(float *)(iVar4 + 0x40);
          fStack_94 = *(float *)(iVar4 + 0x38) * fStack_94 + fVar17 + *(float *)(iVar4 + 0x40);
        }
        uVar7 = g2c_nema_vg_arc_draw_5653a0
                          (fStack_ac,fStack_a8,fStack_9c,fStack_98,fStack_94,fStack_90,fStack_a4,
                           fStack_a0);
        if (uVar7 != 0) goto LAB_00566cdc;
        iVar4 = 0;
        fVar25 = fVar23;
      }
    }
    else {
      d15_pair = CONCAT44(g2c_float_to_bits(fStack_ac),g2c_float_to_bits(fStack_b0));
      iVar4 = 1;
      while ((fVar22 < fVar25)) {
        fVar23 = fVar22 + (90.0f);
        iVar5 = (uint)(fVar23 < fVar25) << 0x1f;
        fVar16 = (90.0f);
        if (iVar5 < 0) {
          fVar16 = fVar23;
        }
        if (-1 < iVar5) {
          fVar16 = fVar25;
        }
        if (!(fVar23 < fVar25)) {
          iVar4 = iVar4 + 2;
        }
        fVar22 = fVar22 * fVar17;
        fVar27 = fVar16 * fVar17 - fVar22;
        fVar16 = audio_uart_float_tangent_563f40(fVar27 * 0.25f);
        fVar16 = fVar16 * (1.3333333730697632f);
        fVar18 = audio_uart_float_trig_mode1_50968c(fVar27);
        fStack_a0 = audio_uart_float_trig_mode0_509690(fVar27);
        fStack_94 = fVar18 + fVar16 * fStack_a0;
        fStack_90 = fStack_a0 - fVar16 * fVar18;
        fStack_ac = 1.0f;
        fStack_a8 = 0.0f;
        fStack_9c = 1.0f;
        fStack_a4 = fVar18;
        fStack_98 = fVar16;
        fVar16 = audio_uart_float_trig_mode1_50968c(fVar22);
        fVar22 = audio_uart_float_trig_mode0_509690(fVar22);
        fVar18 = audio_uart_float_trig_mode1_50968c(fVar19);
        fVar27 = audio_uart_float_trig_mode0_509690(fVar19);
        if (iVar4 << 0x1f < 0) {
          fStack_ac = fStack_fc;
          fStack_a8 = fStack_f8;
        }
        else {
          g2c_nema_vg_quad_to_51a660(fVar16,fVar22,1.0f,1.0f,g2c_bits_to_float((uint)((0x0u))),g2c_bits_to_float((uint)((0x0u))),&fStack_ac);
          g2c_nema_vg_quad_to_51a660(fVar18,fVar27,fVar28,fVar26,fVar20,fVar21,&fStack_ac);
          iVar5 = *piVar2;
          if (*(char *)(iVar5 + 0x21) != '\0') {
            fVar29 = *(float *)(iVar5 + 0x3c) * fStack_a8;
            fStack_a8 = *(float *)(iVar5 + 0x44) * fStack_ac + *(float *)(iVar5 + 0x48) * fStack_a8
                        + *(float *)(iVar5 + 0x4c);
            fStack_ac = *(float *)(iVar5 + 0x38) * fStack_ac + fVar29 + *(float *)(iVar5 + 0x40);
          }
        }
        g2c_nema_vg_quad_to_51a660(fVar16,fVar22,1.0f,1.0f,g2c_bits_to_float((uint)((0x0u))),g2c_bits_to_float((uint)((0x0u))),&fStack_9c);
        g2c_nema_vg_quad_to_51a660(fVar18,fVar27,fVar28,fVar26,fVar20,fVar21,&fStack_9c);
        g2c_nema_vg_quad_to_51a660(fVar16,fVar22,1.0f,1.0f,g2c_bits_to_float((uint)((0x0u))),g2c_bits_to_float((uint)((0x0u))),&fStack_94);
        g2c_nema_vg_quad_to_51a660(fVar18,fVar27,fVar28,fVar26,fVar20,fVar21,&fStack_94);
        if (iVar4 << 0x1e < 0) {
          fStack_a4 = fStack_f4;
          fStack_a0 = fStack_f0;
        }
        else {
          g2c_nema_vg_quad_to_51a660(fVar16,fVar22,1.0f,1.0f,g2c_bits_to_float((uint)((0x0u))),g2c_bits_to_float((uint)((0x0u))),&fStack_a4);
          g2c_nema_vg_quad_to_51a660(fVar18,fVar27,fVar28,fVar26,fVar20,fVar21,&fStack_a4);
          iVar4 = *piVar2;
          if (*(char *)(iVar4 + 0x21) != '\0') {
            fVar16 = *(float *)(iVar4 + 0x3c) * fStack_a0;
            fStack_a0 = *(float *)(iVar4 + 0x44) * fStack_a4 + *(float *)(iVar4 + 0x48) * fStack_a0
                        + *(float *)(iVar4 + 0x4c);
            fStack_a4 = *(float *)(iVar4 + 0x38) * fStack_a4 + fVar16 + *(float *)(iVar4 + 0x40);
          }
        }
        iVar4 = *piVar2;
        if (*(char *)(iVar4 + 0x21) != '\0') {
          fVar16 = *(float *)(iVar4 + 0x3c) * fStack_98;
          fStack_98 = *(float *)(iVar4 + 0x44) * fStack_9c + *(float *)(iVar4 + 0x48) * fStack_98 +
                      *(float *)(iVar4 + 0x4c);
          fVar22 = *(float *)(iVar4 + 0x3c) * fStack_90;
          fStack_90 = *(float *)(iVar4 + 0x44) * fStack_94 + *(float *)(iVar4 + 0x48) * fStack_90 +
                      *(float *)(iVar4 + 0x4c);
          fStack_9c = *(float *)(iVar4 + 0x38) * fStack_9c + fVar16 + *(float *)(iVar4 + 0x40);
          fStack_94 = *(float *)(iVar4 + 0x38) * fStack_94 + fVar22 + *(float *)(iVar4 + 0x40);
        }
        uVar7 = g2c_nema_vg_arc_draw_5653a0
                          (fStack_ac,fStack_a8,fStack_9c,fStack_98,fStack_94,fStack_90,fStack_a4,
                           fStack_a0);
        if (uVar7 != 0) goto LAB_00566cdc;
        iVar4 = 0;
        fVar22 = fVar23;
      }
    }
  } while( true );
LAB_00566cdc:
  g2c_nema_vg_set_aa_51778c(0);
  g2c_nema_vg_set_aa2_517796(0);
  audio_uart_nema_vg_set_error_51565c(uVar7);
LAB_00566cee:
  g2c_nema_vg_set_aa_51778c(0);
  g2c_nema_vg_set_aa2_517796(0);
  audio_uart_nema_vg_set_error_51565c(uVar7);
LAB_005671fc:
  g2c_nema_vg_set_aa_51778c(0);
  g2c_nema_vg_set_aa2_517796(0);
  audio_uart_nema_vg_set_error_51565c(uVar7);
  return uVar7;
}
#undef cStack_108
#undef cStack_107
#undef uStack_106
#undef bStack_105
#undef iStack_104
#undef iStack_100
#undef fStack_fc
#undef fStack_f8
#undef fStack_f4
#undef fStack_f0
#undef fStack_ec
#undef fStack_e8
#undef fStack_e4
#undef fStack_e0
#undef fStack_dc
#undef fStack_d8
#undef fStack_d4
#undef fStack_d0
#undef fStack_cc
#undef fStack_c8
#undef bStack_c4
#undef fStack_c0
#undef fStack_bc
#undef fStack_b8
#undef fStack_b4
#undef fStack_b0
#undef fStack_ac
#undef fStack_a8
#undef fStack_a4
#undef fStack_a0
#undef fStack_9c
#undef fStack_98
#undef fStack_94
#undef fStack_90
#undef fStack_70
#undef fStack_6c


  

/* ---- lifted 0x567230 ---- */

uint g2c_nema_vg_paint_apply_567230(uint a,int b)

{
  int *piVar1;
  int iVar2;
  undefined4 *puVar3;
  uint uVar4;
  int iVar5;
  uint *puVar6;
  bool bVar7;
  float fVar8;
  float fVar9;
  uint auStack_9c [34];
  
  piVar1 = (((int *)&audio_uart_nema_vg_context_cell));
  iVar5 = *(((int *)&audio_uart_nema_vg_context_cell));
  *(undefined4 *)(iVar5 + 0x34) = g2c_float_to_bits((1535.0f));
  *(undefined4 *)(iVar5 + 0x30) = g2c_float_to_bits(((-511.0f)));
  bVar7 = *(int *)(iVar5 + 0x10) != 0;
  iVar2 = 0;
  if (bVar7) {
    iVar2 = *(int *)(iVar5 + 0x1c);
  }
  if (bVar7 && iVar2 != 0) {
    fVar8 = *(float *)(iVar5 + 0x2d8) * 0.5f;
    fVar9 = fVar8 + (-507.0f);
    fVar8 = (1531.0f) - fVar8;
    *(undefined4 *)(iVar5 + 0x2c) = 0;
    *(float *)(iVar5 + 0x30) = fVar9;
    *(float *)(iVar5 + 0x34) = fVar8;
    *(byte *)(iVar5 + 0x21) =
         ((byte)*(undefined4 *)(a + 0x84) | (byte)*(undefined4 *)(iVar5 + 0x90)) & 1;
    iVar2 = *piVar1;
    if (*(char *)(iVar2 + 0x21) != '\0') {
      if ((int)((uint)*(byte *)(iVar2 + 0x90) << 0x1f) < 0) {
        audio_uart_nema_matrix_copy_561830(iVar2 + 0x38,iVar2 + 0xa4);
        if ((int)((uint)*(byte *)(a + 0x84) << 0x1f) < 0) {
          g2c_nema_vg_mat_mul_5619f2((float *)(*piVar1 + 0x38),(float *)(a + 0x60));
        }
      }
      else if ((int)((uint)*(byte *)(a + 0x84) << 0x1f) < 0) {
        audio_uart_nema_matrix_copy_561830(iVar2 + 0x38,a + 0x60);
      }
      else {
        audio_uart_nema_matrix_identity_561810(iVar2 + 0x38);
      }
    }
    iVar2 = *piVar1;
    *(undefined4 *)(iVar2 + 8) = 0;
    *(undefined4 *)(iVar2 + 0xc) = 0;
    *(undefined4 *)(iVar2 + 0x14) = 0;
    *(undefined4 *)(iVar2 + 0x18) = 0;
    *(undefined1 *)(iVar2 + 0x20) = 0;
    *(undefined4 *)(*piVar1 + 0x24) = 0;
    uVar4 = g2c_nema_vg_draw_path_inner_5657d8((uint *)a);
    if (uVar4 == 0) {
      puVar6 = (uint *)*piVar1;
      *puVar6 = puVar6[3];
      puVar6[1] = puVar6[2];
      if (puVar6[10] != 2) {
        audio_uart_display_area_copy_439c04((uint)auStack_9c,a,0x88);
        audio_uart_nema_vg_path_shape_514f3c((uint)auStack_9c,*puVar6,puVar6[7],puVar6[1],puVar6[4])
        ;
        *(undefined1 *)(*piVar1 + 0x7e) = 1;
        uVar4 = audio_uart_ambiq_vector_shape_draw_5202ec(auStack_9c,b);
        *(undefined1 *)(*piVar1 + 0x7e) = 0;
        return uVar4;
      }
      goto LAB_00567316;
    }
  }
  else {
    fVar8 = *(float *)(iVar5 + 0x2d8) * 0.5f;
    fVar9 = fVar8 + (-507.0f);
    fVar8 = (1531.0f) - fVar8;
    *(undefined4 *)(iVar5 + 0x2c) = 1;
    *(float *)(iVar5 + 0x30) = fVar9;
    *(float *)(iVar5 + 0x34) = fVar8;
    *(byte *)(iVar5 + 0x21) =
         ((byte)*(undefined4 *)(a + 0x84) | (byte)*(undefined4 *)(iVar5 + 0x90)) & 1;
    iVar2 = *piVar1;
    if (*(char *)(iVar2 + 0x21) != '\0') {
      if ((int)((uint)*(byte *)(iVar2 + 0x90) << 0x1f) < 0) {
        audio_uart_nema_matrix_copy_561830(iVar2 + 0x38,iVar2 + 0xa4);
        if ((int)((uint)*(byte *)(a + 0x84) << 0x1f) < 0) {
          g2c_nema_vg_mat_mul_5619f2((float *)(*piVar1 + 0x38),(float *)(a + 0x60));
        }
      }
      else if ((int)((uint)*(byte *)(a + 0x84) << 0x1f) < 0) {
        audio_uart_nema_matrix_copy_561830(iVar2 + 0x38,a + 0x60);
      }
      else {
        audio_uart_nema_matrix_identity_561810(iVar2 + 0x38);
      }
    }
    puVar3 = (undefined4 *)*piVar1;
    *puVar3 = 0;
    puVar3[7] = 0;
    puVar3[1] = 0;
    puVar3[4] = 0;
    puVar3[2] = 0;
    puVar3[3] = 0;
    puVar3[5] = 0;
    puVar3[6] = 0;
    *(undefined1 *)(puVar3 + 8) = 0;
    *(undefined4 *)(*piVar1 + 0x24) = 0;
    uVar4 = g2c_nema_vg_draw_path_inner_5657d8((uint *)a);
    if (uVar4 == 0) {
      puVar3 = (undefined4 *)*piVar1;
      *puVar3 = puVar3[3];
      puVar3[1] = puVar3[2];
      goto LAB_00567316;
    }
  }
  g2c_nema_vg_set_aa_51778c(0);
  g2c_nema_vg_set_aa2_517796(0);
  audio_uart_nema_vg_set_error_51565c(uVar4);
LAB_00567316:
  if ((int)((uint)(byte)((uint *)*piVar1)[0x24] << 0x1b) < 0) {
    uVar4 = audio_uart_nema_node_allocate_51416c(*(uint *)*piVar1);
    iVar2 = *piVar1;
    *(uint *)(iVar2 + 0x1c) = uVar4;
    uVar4 = audio_uart_nema_node_allocate_51416c(*(int *)(iVar2 + 4) << 2);
    iVar2 = *piVar1;
    *(uint *)(iVar2 + 0x10) = uVar4;
    if (*(uint *)(iVar2 + 0x1c) != 0) {
      if (*(int *)(iVar2 + 0x10) != 0) {
        fVar8 = *(float *)(iVar2 + 0x2d8) * 0.5f;
        fVar9 = fVar8 + (-507.0f);
        fVar8 = (1531.0f) - fVar8;
        *(undefined4 *)(iVar2 + 0x2c) = 0;
        *(float *)(iVar2 + 0x30) = fVar9;
        *(float *)(iVar2 + 0x34) = fVar8;
        *(byte *)(iVar2 + 0x21) =
             ((byte)*(undefined4 *)(a + 0x84) | (byte)*(undefined4 *)(iVar2 + 0x90)) & 1;
        iVar2 = *piVar1;
        if (*(char *)(iVar2 + 0x21) != '\0') {
          if ((int)((uint)*(byte *)(iVar2 + 0x90) << 0x1f) < 0) {
            audio_uart_nema_matrix_copy_561830(iVar2 + 0x38,iVar2 + 0xa4);
            if ((int)((uint)*(byte *)(a + 0x84) << 0x1f) < 0) {
              g2c_nema_vg_mat_mul_5619f2((float *)(*piVar1 + 0x38),(float *)(a + 0x60));
            }
          }
          else if ((int)((uint)*(byte *)(a + 0x84) << 0x1f) < 0) {
            audio_uart_nema_matrix_copy_561830(iVar2 + 0x38,a + 0x60);
          }
          else {
            audio_uart_nema_matrix_identity_561810(iVar2 + 0x38);
          }
        }
        iVar2 = *piVar1;
        *(undefined4 *)(iVar2 + 8) = 0;
        *(undefined4 *)(iVar2 + 0xc) = 0;
        *(undefined4 *)(iVar2 + 0x14) = 0;
        *(undefined4 *)(iVar2 + 0x18) = 0;
        *(undefined1 *)(iVar2 + 0x20) = 0;
        *(undefined4 *)(*piVar1 + 0x24) = 0;
        uVar4 = g2c_nema_vg_draw_path_inner_5657d8((uint *)a);
        if (uVar4 == 0) {
          puVar6 = (uint *)*piVar1;
          *puVar6 = puVar6[3];
          puVar6[1] = puVar6[2];
          audio_uart_display_area_copy_439c04((uint)auStack_9c,a,0x88);
          audio_uart_nema_vg_path_shape_514f3c
                    ((uint)auStack_9c,*puVar6,puVar6[7],puVar6[1],puVar6[4]);
          *(undefined1 *)(*piVar1 + 0x7e) = 1;
          uVar4 = audio_uart_ambiq_vector_shape_draw_5202ec(auStack_9c,b);
          *(undefined1 *)(*piVar1 + 0x7e) = 0;
        }
        else {
          g2c_nema_vg_set_aa_51778c(0);
          g2c_nema_vg_set_aa2_517796(0);
          audio_uart_nema_vg_set_error_51565c(uVar4);
        }
        if (*(uint *)(*piVar1 + 0x1c) != 0) {
          audio_uart_nema_cl_node_release_514178((void *)(uintptr_t)*(uint *)(*piVar1 + 0x1c));
        }
        if (*(uint *)(*piVar1 + 0x10) != 0) {
          audio_uart_nema_cl_node_release_514178((void *)(uintptr_t)*(uint *)(*piVar1 + 0x10));
        }
        iVar2 = *piVar1;
        *(undefined4 *)(iVar2 + 0x1c) = 0;
        *(undefined4 *)(iVar2 + 0x10) = 0;
        return uVar4;
      }
      audio_uart_nema_cl_node_release_514178((void *)(uintptr_t)*(uint *)(iVar2 + 0x1c));
    }
    if (*(uint *)(*piVar1 + 0x10) != 0) {
      audio_uart_nema_cl_node_release_514178((void *)(uintptr_t)*(uint *)(*piVar1 + 0x10));
    }
    iVar2 = *piVar1;
    *(undefined4 *)(iVar2 + 0x1c) = 0;
    *(undefined4 *)(iVar2 + 0x10) = 0;
  }
  return 2;
}

