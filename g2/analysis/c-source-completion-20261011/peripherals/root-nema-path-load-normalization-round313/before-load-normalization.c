#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
/* Research full-body draft: NOT selected or native-qualified. */
struct pp306_state {uint8_t flag_start,flag_open,flag_point,arc_command;uint32_t coordinate_cursor,subpath_coordinate_start;float previous_x,previous_y,current_x,current_y,control1_x,control1_y,control2_x,control2_y,last_x,last_y,last_control_x,last_control_y,subpath_start_x,subpath_start_y;uint8_t previous_command,padding[3];};
_Static_assert(sizeof(struct pp306_state)==72,"native72byte state");
_Static_assert(offsetof(struct pp306_state,previous_command)==68,"nativecommandoffset");
extern void audio_uart_nema_vg_path_bounds_reset_514e0c(void *);
extern void audio_uart_lv_memzero_48949c(void *,uint32_t);
extern __attribute__((pcs("aapcs-vfp"))) float audio_uart_float_sqrt_4397a8(float);
extern __attribute__((pcs("aapcs-vfp"))) float audio_uart_float_trig_mode1_50968c(float);
extern __attribute__((pcs("aapcs-vfp"))) float audio_uart_float_trig_mode0_509690(float);
extern __attribute__((pcs("aapcs-vfp"))) float audio_uart_float_two_input_angle_50969c(float,float);
extern __attribute__((pcs("aapcs-vfp"))) float audio_uart_float_tangent_563f40(float);
extern __attribute__((pcs("aapcs-vfp"))) float audio_uart_float_remainder_577c3c(float,float);
extern __attribute__((pcs("aapcs-vfp"))) float audio_uart_float_inverse_ratio_58ec74(float);
extern __attribute__((pcs("aapcs-vfp"))) float audio_uart_float_inverse_magnitude_58ecbc(float);
static float pp306_float(uint32_t b){union{uint32_t b;float f;}v={.b=b};return v.f;}
static uint32_t pp306_bits(float f){union{uint32_t b;float f;}v={.f=f};return v.b;}
static uint32_t pp306_fpscr(void){uint32_t v;__asm__ volatile("vmrs %0,fpscr":"=r"(v));return v;}
static int32_t pp306_i32(float f){float v;__asm__ volatile("vcvt.s32.f32 %0,%1":"=t"(v):"t"(f));return (int32_t)pp306_bits(v);}
static uint32_t VectorSignedToFloat(int32_t i,uint32_t rounding){(void)rounding;float f=pp306_float((uint32_t)i),v;__asm__ volatile("vcvt.f32.s32 %0,%1":"=t"(v):"t"(f));return pp306_bits(v);}
#define ABS(v) pp306_float(pp306_bits(v)&0x7fffffffu)
#define NAN(v) ((pp306_bits(v)&0x7fffffffu)>0x7f800000u)
#define SUB41(a,b) ((uint8_t)(((uint32_t)(a))>>((b)*8u)))
#define CONCAT44(a,b) (((uint64_t)pp306_bits(a)<<32)|pp306_bits(b))

/* 562c62..562c66 and 562cf4..562cf8 round division before negation. */
static inline float pp309_divide_then_negate(float a, float b)
{
  float result;
  __asm__ volatile("vdiv.f32 %0,%1,%2\n\tvneg.f32 %0,%0"
                   : "=&t"(result) : "t"(a), "t"(b));
  return result;
}
static inline float pp309_cubic_discriminant(float b, float c, float a)
{
  float result, product; float four = 4.0f;
  __asm__ volatile("vmul.f32 %0,%2,%2\n\tvmul.f32 %1,%3,%5\n\tvmls.f32 %0,%1,%4"
                   : "=&t"(result), "=&t"(product)
                   : "t"(b), "t"(c), "t"(a), "t"(four));
  return result;
}
static inline float pp309_cubic_second_root(float b, float root, float denominator)
{
  float result;
  __asm__ volatile("vneg.f32 %0,%1\n\tvsub.f32 %0,%0,%2\n\tvdiv.f32 %0,%0,%3"
                   : "=&t"(result) : "t"(b), "t"(root), "t"(denominator));
  return result;
}
static inline float pp309_conditional_add(float a, float b)
{
  float result;
  __asm__ volatile("vadd.f32 %0,%1,%2" : "=t"(result) : "t"(a), "t"(b));
  return result;
}
/* Native VCMP N condition: unordered is PL, unlike C ordered >=. */
static inline int pp308_negative_compare(float a, float b)
{
  uint32_t flags;
  __asm__ volatile("vcmp.f32 %1,%2\n\tvmrs %0,fpscr"
                   : "=r"(flags) : "t"(a), "t"(b) : "cc");
  return (int)(flags >> 31);
}
static inline int pp308_arc_excludes(float angle, float low, float high)
{
  if (pp308_negative_compare(angle, low)) return 1;
  return pp308_negative_compare(high, angle);
}
void audio_uart_nema_vg_path_process_561c68(void *path)

{
  typedef uint32_t uint;typedef uint8_t byte;typedef uint32_t undefined4;typedef uint64_t ulonglong;
  volatile uint32_t *param_1=path;
  struct pp306_state state;
  undefined4 uVar1;
  volatile float *pfVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  volatile float *pfVar7;
  int iVar8;
  volatile float *pfVar9;
  volatile float *pfVar10;
  volatile float *pfVar11;
  volatile float *pfVar12;
  byte bVar13;
  bool bVar14;
  byte bVar15;
  bool bVar16;
  uint in_fpscr=pp306_fpscr();
  float fVar17;
  float fVar18;
  float fVar19;
  float fVar20;
  float fVar21;
  float fVar22;
  ulonglong unaff_d9; /* Every live read is dominated by local arc assignments. */
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
  float fVar33;
  float local_a8 [6];
  uint local_90;
  float local_8c [8];
  volatile float *local_6c;
  
  audio_uart_nema_vg_path_bounds_reset_514e0c(path);
  audio_uart_lv_memzero_48949c(&state,72u);
  state.flag_start = '\x01';
  state.flag_open = '\x01';
  state.flag_point = 1u;
  uint32_t initial_count = *param_1;
  if (initial_count != 0) {
    uVar3 = *(byte *)param_1[2] & 0xffffff6f;
  }
  if (initial_count != 0 && uVar3 != 1) {
    fVar17 = pp306_float(param_1[4]);
    in_fpscr = in_fpscr & 0xfffffff;
    if (0.0f < fVar17) {
      fVar17 = 0.0f;
    }
    param_1[4] = pp306_bits(fVar17);
    fVar17 = pp306_float(param_1[5]);
    if (0.0f < fVar17) {
      fVar17 = 0.0f;
    }
    param_1[5] = pp306_bits(fVar17);
    fVar17 = pp306_float(param_1[6]);
    if (fVar17 < 0.0f) {
      fVar17 = 0.0f;
    }
    param_1[6] = pp306_bits(fVar17);
    fVar17 = pp306_float(param_1[7]);
    if (fVar17 < 0.0f) {
      fVar17 = 0.0f;
    }
    param_1[7] = pp306_bits(fVar17);
  }
  if (*param_1 != 0) {
    local_90 = 0;
    do {
      bVar13 = *(byte *)(param_1[2] + local_90);
      uVar3 = (uint)bVar13;
      state.previous_x = state.current_x;
      state.previous_y = state.current_y;
      bVar16 = (int)(uVar3 << 0x1b) < 0;
      uVar5 = uVar3 & 0x6f;
      bVar15 = state.previous_command & 0x6f;
      if (uVar5 == 1) {
        if ((state.flag_open == '\x01') && (state.coordinate_cursor != 0)) {
          fVar17 = 0.0f;
          fVar20 = 0.0f;
          if (state.flag_start == '\0') {
            fVar17 = state.subpath_start_x;
            fVar20 = state.subpath_start_y;
          }
          in_fpscr = in_fpscr & 0xfffffff;
          fVar21 = pp306_float(param_1[4]);
          if (fVar17 < pp306_float(param_1[4])) {
            fVar21 = fVar17;
          }
          param_1[4] = pp306_bits(fVar21);
          fVar21 = pp306_float(param_1[5]);
          if (fVar20 < pp306_float(param_1[5])) {
            fVar21 = fVar20;
          }
          param_1[5] = pp306_bits(fVar21);
          if (fVar17 <= pp306_float(param_1[6])) {
            fVar17 = pp306_float(param_1[6]);
          }
          param_1[6] = pp306_bits(fVar17);
          if (fVar20 <= pp306_float(param_1[7])) {
            fVar20 = pp306_float(param_1[7]);
          }
          param_1[7] = pp306_bits(fVar20);
        }
        state.flag_start = '\0';
        state.flag_point = 1;
        state.subpath_coordinate_start = state.coordinate_cursor;
        uVar3 = param_1[3];
        state.current_x = *(volatile float *)(uVar3 + state.coordinate_cursor * 4);
        if (bVar16) {
          state.current_x = state.last_x + state.current_x;
          state.current_y = state.last_y + *(volatile float *)(uVar3 + (state.coordinate_cursor + 1) * 4);
        }
        else {
          state.current_y = *(volatile float *)(uVar3 + (state.coordinate_cursor + 1) * 4);
        }
        state.coordinate_cursor = state.coordinate_cursor + 2;
        state.subpath_start_x = state.current_x;
        state.subpath_start_y = state.current_y;
LAB_00562754:
        state.last_x = state.current_x;
        state.last_y = state.current_y;
        iVar6 = state.coordinate_cursor;
        state.previous_command = bVar13;
      }
      else {
        if (uVar3 == 0 || uVar3 == 0x80) {
          if (state.flag_start == '\x01') {
            state.current_x = 0.0f;
            state.current_y = 0.0f;
          }
          else {
            state.current_x = state.subpath_start_x;
            state.current_y = state.subpath_start_y;
          }
          state.flag_point = 0;
          state.flag_open = '\0';
          goto LAB_00562754;
        }
        if (state.coordinate_cursor == 0) {
          state.flag_start = '\x01';
        }
        state.flag_point = 0;
        if (uVar5 == 6) {
          uVar3 = param_1[3];
          state.control1_x = *(volatile float *)(uVar3 + state.coordinate_cursor * 4);
          state.control1_y = *(volatile float *)(uVar3 + (state.coordinate_cursor + 1) * 4);
          state.control2_x = *(volatile float *)(uVar3 + (state.coordinate_cursor + 2) * 4);
          state.control2_y = *(volatile float *)(uVar3 + (state.coordinate_cursor + 3) * 4);
          state.coordinate_cursor = state.coordinate_cursor + 4;
          if (bVar16) {
            state.control1_x = state.control1_x + state.last_x;
            state.control1_y = state.control1_y + state.last_y;
            state.control2_x = state.control2_x + state.last_x;
            state.control2_y = state.control2_y + state.last_y;
            state.last_control_x = state.control2_x;
            state.last_control_y = state.control2_y;
            goto LAB_00561f3e;
          }
LAB_00562014:
          state.last_control_x = state.control2_x;
          state.last_control_y = state.control2_y;
LAB_00561edc:
          uVar3 = param_1[3];
          state.current_x = *(volatile float *)(uVar3 + state.coordinate_cursor * 4);
          state.coordinate_cursor = state.coordinate_cursor + 1;
LAB_005620a8:
          state.current_y = *(volatile float *)(uVar3 + state.coordinate_cursor * 4);
          state.coordinate_cursor = state.coordinate_cursor + 1;
          goto LAB_00562754;
        }
        if (uVar5 == 5) {
          state.control1_x = *(volatile float *)(param_1[3] + state.coordinate_cursor * 4);
          state.control1_y = *(volatile float *)(param_1[3] + (state.coordinate_cursor + 1) * 4);
          state.coordinate_cursor = state.coordinate_cursor + 2;
          state.last_control_x = state.control1_x;
          state.last_control_y = state.control1_y;
          if (!bVar16) goto LAB_00561edc;
          state.control1_x = state.control1_x + state.last_x;
          state.control1_y = state.control1_y + state.last_y;
          state.last_control_x = state.control1_x;
          state.last_control_y = state.control1_y;
LAB_00561f3e:
          state.current_x = *(volatile float *)(param_1[3] + state.coordinate_cursor * 4) + state.last_x;
          state.current_y = *(volatile float *)(param_1[3] + (state.coordinate_cursor + 1) * 4) + state.last_y;
          state.coordinate_cursor = state.coordinate_cursor + 2;
          goto LAB_00562754;
        }
        if (uVar5 == 7) {
          if ((bVar15 == 5 || bVar15 == 7) ||
             (state.control1_x = state.last_x, state.control1_y = state.last_y, fVar17 = state.last_x, fVar20 = state.last_y,
             bVar15 == 6 || bVar15 == 8)) {
            state.control1_x = state.last_x * 2.0f - state.last_control_x;
            state.control1_y = state.last_y * 2.0f - state.last_control_y;
            fVar17 = state.control1_x;
            fVar20 = state.control1_y;
          }
LAB_00561f3a:
          state.last_control_y = fVar20;
          state.last_control_x = fVar17;
          if (!bVar16) goto LAB_00561edc;
          goto LAB_00561f3e;
        }
        if (uVar5 == 8) {
          if ((bVar15 == 5 || bVar15 == 7) || (bVar15 == 6 || bVar15 == 8)) {
            state.control1_x = state.last_x * 2.0f - state.last_control_x;
            state.control1_y = state.last_y * 2.0f - state.last_control_y;
          }
          else {
            state.control1_x = state.last_x;
            state.control1_y = state.last_y;
          }
          state.control2_x = *(volatile float *)(param_1[3] + state.coordinate_cursor * 4);
          state.control2_y = *(volatile float *)(param_1[3] + (state.coordinate_cursor + 1) * 4);
          state.coordinate_cursor = state.coordinate_cursor + 2;
          if (!bVar16) goto LAB_00562014;
          state.control2_x = state.control2_x + state.last_x;
          state.control2_y = state.control2_y + state.last_y;
          state.last_control_x = state.control2_x;
          state.last_control_y = state.control2_y;
          goto LAB_00561f3e;
        }
        if ((uVar3 & 0xf) == 9) {
          uVar3 = param_1[3];
          state.control1_x = *(volatile float *)(uVar3 + state.coordinate_cursor * 4);
          state.control1_y = *(volatile float *)(uVar3 + (state.coordinate_cursor + 1) * 4);
          state.control2_x = *(volatile float *)(uVar3 + (state.coordinate_cursor + 2) * 4);
          state.coordinate_cursor = state.coordinate_cursor + 3;
          state.last_control_y = state.last_y;
          state.last_control_x = state.last_x;
          state.arc_command = bVar13;
        }
        if (uVar5 == 4) {
          uVar3 = param_1[3];
          state.current_x = state.last_x;
          if (!bVar16) goto LAB_005620a8;
          iVar6 = state.coordinate_cursor * 4;
          state.coordinate_cursor = state.coordinate_cursor + 1;
          state.current_y = state.last_y + *(volatile float *)(uVar3 + iVar6);
          goto LAB_00562754;
        }
        if (uVar5 == 3) {
          state.current_x = *(volatile float *)(param_1[3] + state.coordinate_cursor * 4);
          if (bVar16) {
            state.current_x = state.last_x + state.current_x;
          }
          state.coordinate_cursor = state.coordinate_cursor + 1;
          state.current_y = state.last_y;
          goto LAB_00562754;
        }
        if (uVar5 == 10) {
          iVar6 = state.coordinate_cursor + 1;
          fVar20 = *(volatile float *)(param_1[3] + state.coordinate_cursor * 4);
          uVar3 = in_fpscr & 0xfffffff;
          fVar17 = pp306_float(param_1[4]);
          if (pp308_negative_compare(state.current_x, pp306_float(param_1[4]))) {
            fVar17 = state.current_x;
          }
          param_1[4] = pp306_bits(fVar17);
          fVar17 = pp306_float(param_1[5]);
          if (pp308_negative_compare(state.current_y, pp306_float(param_1[5]))) {
            fVar17 = state.current_y;
          }
          param_1[5] = pp306_bits(fVar17);
          fVar17 = state.current_x;
          if (!pp308_negative_compare(pp306_float(param_1[6]), state.current_x)) {
            fVar17 = pp306_float(param_1[6]);
          }
          param_1[6] = pp306_bits(fVar17);
          fVar17 = state.current_y;
          if (!pp308_negative_compare(pp306_float(param_1[7]), state.current_y)) {
            fVar17 = pp306_float(param_1[7]);
          }
          param_1[7] = pp306_bits(fVar17);
          uVar5 = pp306_i32(fVar20) / 2;
          if (0 < (int)uVar5) {
            if ((int)(uVar5 << 0x1f) < 0) {
              uVar4 = param_1[3];
              state.current_x = *(volatile float *)(uVar4 + iVar6 * 4);
              if (bVar16) {
                state.current_x = state.current_x + state.last_x;
                state.current_y = *(volatile float *)(uVar4 + (state.coordinate_cursor + 2) * 4) + state.last_y;
              }
              else {
                state.current_y = *(volatile float *)(uVar4 + (state.coordinate_cursor + 2) * 4);
              }
              state.last_x = state.current_x;
              state.last_y = state.current_y;
              fVar17 = pp306_float(param_1[4]);
              if (pp308_negative_compare(state.current_x, pp306_float(param_1[4]))) {
                fVar17 = state.current_x;
              }
              param_1[4] = pp306_bits(fVar17);
              fVar17 = pp306_float(param_1[5]);
              if (pp308_negative_compare(state.current_y, pp306_float(param_1[5]))) {
                fVar17 = state.current_y;
              }
              param_1[5] = pp306_bits(fVar17);
              fVar17 = state.current_x;
              if (!pp308_negative_compare(pp306_float(param_1[6]), state.current_x)) {
                fVar17 = pp306_float(param_1[6]);
              }
              param_1[6] = pp306_bits(fVar17);
              fVar17 = state.current_y;
              if (!pp308_negative_compare(pp306_float(param_1[7]), state.current_y)) {
                fVar17 = pp306_float(param_1[7]);
              }
              param_1[7] = pp306_bits(fVar17);
              iVar6 = state.coordinate_cursor + 3;
              state.previous_command = bVar13;
            }
            state.coordinate_cursor = iVar6;
            for (uVar5 = uVar5 >> 1; iVar6 = state.coordinate_cursor, uVar5 != 0; uVar5 = uVar5 - 1) {
              uVar4 = param_1[3];
              state.current_x = *(volatile float *)(uVar4 + state.coordinate_cursor * 4);
              if (bVar16) {
                state.current_x = state.current_x + state.last_x;
                state.current_y = *(volatile float *)(uVar4 + (state.coordinate_cursor + 1) * 4) + state.last_y;
              }
              else {
                state.current_y = *(volatile float *)(uVar4 + (state.coordinate_cursor + 1) * 4);
              }
              fVar17 = pp306_float(param_1[4]);
              if (pp308_negative_compare(state.current_x, pp306_float(param_1[4]))) {
                fVar17 = state.current_x;
              }
              param_1[4] = pp306_bits(fVar17);
              fVar17 = pp306_float(param_1[5]);
              if (pp308_negative_compare(state.current_y, pp306_float(param_1[5]))) {
                fVar17 = state.current_y;
              }
              param_1[5] = pp306_bits(fVar17);
              fVar17 = state.current_x;
              if (!pp308_negative_compare(pp306_float(param_1[6]), state.current_x)) {
                fVar17 = pp306_float(param_1[6]);
              }
              param_1[6] = pp306_bits(fVar17);
              fVar17 = state.current_y;
              if (!pp308_negative_compare(pp306_float(param_1[7]), state.current_y)) {
                fVar17 = pp306_float(param_1[7]);
              }
              param_1[7] = pp306_bits(fVar17);
              uVar4 = param_1[3];
              fVar17 = *(volatile float *)(uVar4 + (state.coordinate_cursor + 2) * 4);
              if (bVar16) {
                state.current_y = pp309_conditional_add(*(volatile float *)(uVar4 + (state.coordinate_cursor + 3) * 4), state.current_y);
                state.current_x = pp309_conditional_add(fVar17, state.current_x);
              }
              else {
                state.current_y = *(volatile float *)(uVar4 + (state.coordinate_cursor + 3) * 4);
                state.current_x = fVar17;
              }
              state.coordinate_cursor = state.coordinate_cursor + 4;
              fVar17 = pp306_float(param_1[4]);
              if (pp308_negative_compare(state.current_x, pp306_float(param_1[4]))) {
                fVar17 = state.current_x;
              }
              param_1[4] = pp306_bits(fVar17);
              fVar17 = pp306_float(param_1[5]);
              if (pp308_negative_compare(state.current_y, pp306_float(param_1[5]))) {
                fVar17 = state.current_y;
              }
              param_1[5] = pp306_bits(fVar17);
              fVar17 = state.current_x;
              if (!pp308_negative_compare(pp306_float(param_1[6]), state.current_x)) {
                fVar17 = pp306_float(param_1[6]);
              }
              param_1[6] = pp306_bits(fVar17);
              fVar17 = state.current_y;
              if (!pp308_negative_compare(pp306_float(param_1[7]), state.current_y)) {
                fVar17 = pp306_float(param_1[7]);
              }
              param_1[7] = pp306_bits(fVar17);
              state.last_x = state.current_x;
              state.last_y = state.current_y;
              state.previous_command = bVar13;
            }
          }
          state.coordinate_cursor = iVar6;
          in_fpscr = uVar3 | (uint)(state.last_x - state.subpath_start_x == 0.0f) << 0x1e;
          bVar13 = 0;
          if ((byte)(in_fpscr >> 0x1e) != 0) {
            in_fpscr = uVar3 | (uint)(state.last_y - state.subpath_start_y == 0.0f) << 0x1e;
            bVar13 = (byte)(in_fpscr >> 0x1e);
          }
          state.previous_x = state.current_x;
          state.previous_y = state.current_y;
          if (bVar13 == 0) {
            state.current_y = state.subpath_start_y;
            state.current_x = state.subpath_start_x;
            state.last_x = state.subpath_start_x;
            state.last_y = state.subpath_start_y;
            in_fpscr = in_fpscr & 0xfffffff;
            fVar17 = pp306_float(param_1[4]);
            if (pp308_negative_compare(state.subpath_start_x, pp306_float(param_1[4]))) {
              fVar17 = state.subpath_start_x;
            }
            param_1[4] = pp306_bits(fVar17);
            fVar17 = pp306_float(param_1[5]);
            if (pp308_negative_compare(state.subpath_start_y, pp306_float(param_1[5]))) {
              fVar17 = state.subpath_start_y;
            }
            param_1[5] = pp306_bits(fVar17);
            fVar17 = state.subpath_start_x;
            if (!pp308_negative_compare(pp306_float(param_1[6]), state.subpath_start_x)) {
              fVar17 = pp306_float(param_1[6]);
            }
            param_1[6] = pp306_bits(fVar17);
            fVar17 = state.subpath_start_y;
            if (!pp308_negative_compare(pp306_float(param_1[7]), state.subpath_start_y)) {
              fVar17 = pp306_float(param_1[7]);
            }
            param_1[7] = pp306_bits(fVar17);
          }
          state.flag_open = '\0';
          iVar6 = state.coordinate_cursor;
        }
        else {
          fVar17 = state.last_control_x;
          fVar20 = state.last_control_y;
          if (uVar5 != 0xb) goto LAB_00561f3a;
          iVar6 = state.coordinate_cursor + 1;
          fVar20 = *(volatile float *)(param_1[3] + state.coordinate_cursor * 4);
          in_fpscr = in_fpscr & 0xfffffff;
          fVar17 = pp306_float(param_1[4]);
          if (pp308_negative_compare(state.current_x, pp306_float(param_1[4]))) {
            fVar17 = state.current_x;
          }
          param_1[4] = pp306_bits(fVar17);
          fVar17 = pp306_float(param_1[5]);
          if (pp308_negative_compare(state.current_y, pp306_float(param_1[5]))) {
            fVar17 = state.current_y;
          }
          param_1[5] = pp306_bits(fVar17);
          fVar17 = state.current_x;
          if (!pp308_negative_compare(pp306_float(param_1[6]), state.current_x)) {
            fVar17 = pp306_float(param_1[6]);
          }
          param_1[6] = pp306_bits(fVar17);
          fVar17 = state.current_y;
          if (!pp308_negative_compare(pp306_float(param_1[7]), state.current_y)) {
            fVar17 = pp306_float(param_1[7]);
          }
          param_1[7] = pp306_bits(fVar17);
          uVar3 = pp306_i32(fVar20) / 2;
          if (0 < (int)uVar3) {
            if ((int)(uVar3 << 0x1f) < 0) {
              uVar5 = param_1[3];
              state.current_x = *(volatile float *)(uVar5 + iVar6 * 4);
              if (bVar16) {
                state.current_x = state.current_x + state.last_x;
                state.current_y = *(volatile float *)(uVar5 + (state.coordinate_cursor + 2) * 4) + state.last_y;
              }
              else {
                state.current_y = *(volatile float *)(uVar5 + (state.coordinate_cursor + 2) * 4);
              }
              state.last_x = state.current_x;
              state.last_y = state.current_y;
              fVar17 = pp306_float(param_1[4]);
              if (pp308_negative_compare(state.current_x, pp306_float(param_1[4]))) {
                fVar17 = state.current_x;
              }
              param_1[4] = pp306_bits(fVar17);
              fVar17 = pp306_float(param_1[5]);
              if (pp308_negative_compare(state.current_y, pp306_float(param_1[5]))) {
                fVar17 = state.current_y;
              }
              param_1[5] = pp306_bits(fVar17);
              fVar17 = state.current_x;
              if (!pp308_negative_compare(pp306_float(param_1[6]), state.current_x)) {
                fVar17 = pp306_float(param_1[6]);
              }
              param_1[6] = pp306_bits(fVar17);
              fVar17 = state.current_y;
              if (!pp308_negative_compare(pp306_float(param_1[7]), state.current_y)) {
                fVar17 = pp306_float(param_1[7]);
              }
              param_1[7] = pp306_bits(fVar17);
              iVar6 = state.coordinate_cursor + 3;
              state.previous_command = bVar13;
            }
            state.coordinate_cursor = iVar6;
            state.previous_x = state.current_x;
            state.previous_y = state.current_y;
            for (uVar3 = uVar3 >> 1; iVar6 = state.coordinate_cursor, state.current_x = state.previous_x, state.current_y = state.previous_y,
                uVar3 != 0; uVar3 = uVar3 - 1) {
              uVar5 = param_1[3];
              state.current_x = *(volatile float *)(uVar5 + state.coordinate_cursor * 4);
              if (bVar16) {
                state.current_x = state.current_x + state.last_x;
                state.current_y = *(volatile float *)(uVar5 + (state.coordinate_cursor + 1) * 4) + state.last_y;
              }
              else {
                state.current_y = *(volatile float *)(uVar5 + (state.coordinate_cursor + 1) * 4);
              }
              fVar17 = pp306_float(param_1[4]);
              if (pp308_negative_compare(state.current_x, pp306_float(param_1[4]))) {
                fVar17 = state.current_x;
              }
              param_1[4] = pp306_bits(fVar17);
              fVar17 = pp306_float(param_1[5]);
              if (pp308_negative_compare(state.current_y, pp306_float(param_1[5]))) {
                fVar17 = state.current_y;
              }
              param_1[5] = pp306_bits(fVar17);
              fVar17 = state.current_x;
              if (!pp308_negative_compare(pp306_float(param_1[6]), state.current_x)) {
                fVar17 = pp306_float(param_1[6]);
              }
              param_1[6] = pp306_bits(fVar17);
              fVar17 = state.current_y;
              if (!pp308_negative_compare(pp306_float(param_1[7]), state.current_y)) {
                fVar17 = pp306_float(param_1[7]);
              }
              param_1[7] = pp306_bits(fVar17);
              uVar5 = param_1[3];
              fVar17 = *(volatile float *)(uVar5 + (state.coordinate_cursor + 2) * 4);
              if (bVar16) {
                state.current_y = *(volatile float *)(uVar5 + (state.coordinate_cursor + 3) * 4) + state.current_y;
                state.current_x = pp309_conditional_add(fVar17, state.current_x);
              }
              else {
                state.current_y = *(volatile float *)(uVar5 + (state.coordinate_cursor + 3) * 4);
                state.current_x = fVar17;
              }
              state.coordinate_cursor = state.coordinate_cursor + 4;
              fVar17 = pp306_float(param_1[4]);
              if (pp308_negative_compare(state.current_x, pp306_float(param_1[4]))) {
                fVar17 = state.current_x;
              }
              param_1[4] = pp306_bits(fVar17);
              fVar17 = pp306_float(param_1[5]);
              if (pp308_negative_compare(state.current_y, pp306_float(param_1[5]))) {
                fVar17 = state.current_y;
              }
              param_1[5] = pp306_bits(fVar17);
              fVar17 = state.current_x;
              if (!pp308_negative_compare(pp306_float(param_1[6]), state.current_x)) {
                fVar17 = pp306_float(param_1[6]);
              }
              param_1[6] = pp306_bits(fVar17);
              fVar17 = state.current_y;
              if (!pp308_negative_compare(pp306_float(param_1[7]), state.current_y)) {
                fVar17 = pp306_float(param_1[7]);
              }
              param_1[7] = pp306_bits(fVar17);
              state.previous_x = state.current_x;
              state.previous_y = state.current_y;
              state.last_x = state.current_x;
              state.last_y = state.current_y;
              state.previous_command = bVar13;
            }
          }
        }
      }
      state.coordinate_cursor = iVar6;
      bVar13 = *(byte *)(param_1[2] + local_90) & 0x6f;
      if (bVar13 == 6 || bVar13 == 8) {
        local_a8[0] = 0.0f;
        local_a8[1] = 0.0f;
        uVar3 = in_fpscr & 0xfffffff;
        fVar17 = pp306_float(param_1[4]);
        if (!pp308_negative_compare(pp306_float(param_1[4]), state.current_x)) {
          fVar17 = state.current_x;
        }
        param_1[4] = pp306_bits(fVar17);
        fVar17 = pp306_float(param_1[5]);
        if (!pp308_negative_compare(pp306_float(param_1[5]), state.current_y)) {
          fVar17 = state.current_y;
        }
        param_1[5] = pp306_bits(fVar17);
        fVar17 = pp306_float(param_1[6]);
        if (!pp308_negative_compare(state.current_x, pp306_float(param_1[6]))) {
          fVar17 = state.current_x;
        }
        param_1[6] = pp306_bits(fVar17);
        fVar17 = pp306_float(param_1[7]);
        if (!pp308_negative_compare(state.current_y, pp306_float(param_1[7]))) {
          fVar17 = state.current_y;
        }
        local_a8[2] = pp306_float(param_1[4]);
        param_1[7] = pp306_bits(fVar17);
        local_a8[3] = pp306_float(param_1[5]);
        local_a8[4] = pp306_float(param_1[6]);
        local_a8[5] = pp306_float(param_1[7]);
        local_8c[0] = state.control1_x;
        uVar5 = uVar3 | (uint)(state.control1_x < local_a8[2]) << 0x1f;
        in_fpscr = uVar5 | (uint)(NAN(state.control1_x) || NAN(local_a8[2])) << 0x1c;
        local_8c[1] = state.control1_y;
        local_8c[2] = state.control2_x;
        local_8c[3] = state.control2_y;
        bVar13 = (byte)(uVar5 >> 0x1f);
        bVar15 = (byte)(in_fpscr >> 0x1c) & 1;
        if (bVar13 == bVar15) {
          in_fpscr = uVar3 | (uint)(local_a8[4] < state.control1_x) << 0x1f |
                     (uint)(NAN(local_a8[4]) || NAN(state.control1_x)) << 0x1c;
          bVar15 = (byte)(in_fpscr >> 0x18);
          bVar13 = bVar15 >> 7;
          bVar15 = bVar15 >> 4 & 1;
        }
        if (bVar13 == bVar15) {
          uVar3 = in_fpscr & 0xfffffff;
          uVar5 = uVar3 | (uint)(state.control1_y < local_a8[3]) << 0x1f;
          in_fpscr = uVar5 | (uint)(NAN(state.control1_y) || NAN(local_a8[3])) << 0x1c;
          bVar13 = (byte)(uVar5 >> 0x1f);
          bVar15 = (byte)(in_fpscr >> 0x1c) & 1;
          if (bVar13 == bVar15) {
            in_fpscr = uVar3 | (uint)(local_a8[5] < state.control1_y) << 0x1f |
                       (uint)(NAN(local_a8[5]) || NAN(state.control1_y)) << 0x1c;
            bVar15 = (byte)(in_fpscr >> 0x18);
            bVar13 = bVar15 >> 7;
            bVar15 = bVar15 >> 4 & 1;
          }
          if (bVar13 == bVar15) {
            uVar3 = in_fpscr & 0xfffffff;
            uVar5 = uVar3 | (uint)(state.control2_x < local_a8[2]) << 0x1f;
            in_fpscr = uVar5 | (uint)(NAN(state.control2_x) || NAN(local_a8[2])) << 0x1c;
            bVar13 = (byte)(uVar5 >> 0x1f);
            bVar15 = (byte)(in_fpscr >> 0x1c) & 1;
            if (bVar13 == bVar15) {
              in_fpscr = uVar3 | (uint)(local_a8[4] < state.control2_x) << 0x1f |
                         (uint)(NAN(local_a8[4]) || NAN(state.control2_x)) << 0x1c;
              bVar15 = (byte)(in_fpscr >> 0x18);
              bVar13 = bVar15 >> 7;
              bVar15 = bVar15 >> 4 & 1;
            }
            if (bVar13 == bVar15) {
              uVar3 = in_fpscr & 0xfffffff;
              uVar5 = uVar3 | (uint)(state.control2_y < local_a8[3]) << 0x1f;
              in_fpscr = uVar5 | (uint)(NAN(state.control2_y) || NAN(local_a8[3])) << 0x1c;
              bVar13 = (byte)(uVar5 >> 0x1f);
              bVar15 = (byte)(in_fpscr >> 0x1c) & 1;
              if (bVar13 == bVar15) {
                in_fpscr = uVar3 | (uint)(local_a8[5] < state.control2_y) << 0x1f |
                           (uint)(NAN(local_a8[5]) || NAN(state.control2_y)) << 0x1c;
                bVar15 = (byte)(in_fpscr >> 0x18);
                bVar13 = bVar15 >> 7;
                bVar15 = bVar15 >> 4 & 1;
              }
              if (bVar13 == bVar15) goto LAB_0056385a;
            }
          }
        }
        local_8c[6] = state.current_x;
        local_8c[7] = state.current_y;
        local_8c[4] = state.previous_x;
        pfVar7 = local_8c + 4;
        pfVar12 = local_8c;
        local_8c[5] = state.previous_y;
        pfVar2 = local_a8;
        pfVar9 = local_8c + 2;
        pfVar10 = local_8c + 6;
        pfVar11 = local_a8 + 2;
        iVar6 = 2;
        local_6c = pfVar2;
        do {
          fVar20 = *pfVar7;
          fVar23 = *pfVar12;
          fVar22 = *pfVar9;
          unaff_d9 = CONCAT44(fVar23,fVar22);
          fVar21 = *pfVar10;
          fVar26 = fVar20 * -3.0f + fVar23 * 9.0f + fVar22 * -9.0f + fVar21 * 3.0f;
          iVar8 = 0;
          uVar3 = in_fpscr & 0xfffffff;
          fVar24 = fVar20 * 6.0f + fVar23 * -12.0f + fVar22 * 6.0f;
          fVar17 = fVar20 * -3.0f + fVar23 * 3.0f;
          if (1e-07f <= ABS(fVar26)) {
            fVar17 = pp309_cubic_discriminant(fVar24, fVar17, fVar26);
            uVar3 = uVar3 | (uint)(fVar17 < 1.0000001e-07f) << 0x1f;
            in_fpscr = uVar3 | (uint)NAN(fVar17) << 0x1c;
            if ((byte)(uVar3 >> 0x1f) == ((byte)(in_fpscr >> 0x1c) & 1)) {
              fVar17 = audio_uart_float_sqrt_4397a8(fVar17);
              fVar18 = (fVar17 - fVar24) / (fVar26 * 2.0f);
              uVar3 = in_fpscr & 0xfffffff;
              if ((1.0000001e-07f <= fVar18) && (fVar18 < 0.9999999f)) {
                local_a8[0] = fVar18;
                iVar8 = 1;
              }
              fVar17 = pp309_cubic_second_root(fVar24, fVar17, fVar26 * 2.0f);
              uVar5 = uVar3 | (uint)(fVar17 < 1.0000001e-07f) << 0x1f;
              in_fpscr = uVar5 | (uint)NAN(fVar17) << 0x1c;
              if (((byte)(uVar5 >> 0x1f) == ((byte)(in_fpscr >> 0x1c) & 1)) &&
                 (in_fpscr = uVar3, fVar17 < 0.9999999f)) {
                pfVar2 = local_6c + iVar8;
                iVar8 = iVar8 + 1;
                *pfVar2 = fVar17;
              }
              pfVar2 = (volatile float *)0x0;
              if (iVar8 != 0) goto LAB_005629ce;
            }
          }
          else {
            fVar26 = ABS(fVar24);
            uVar5 = uVar3 | (uint)(fVar26 < 1.0000001e-07f) << 0x1f;
            in_fpscr = uVar5 | (uint)NAN(fVar26) << 0x1c;
            bVar13 = (byte)(uVar5 >> 0x1f);
            bVar15 = (byte)(in_fpscr >> 0x1c) & 1;
            if (bVar13 == bVar15) {
              fVar26 = pp309_divide_then_negate(fVar17, fVar24);
              in_fpscr = uVar3 | (uint)(fVar26 < 1.0000001e-07f) << 0x1f | (uint)NAN(fVar26) << 0x1c;
              bVar15 = (byte)(in_fpscr >> 0x18);
              bVar13 = bVar15 >> 7;
              bVar15 = bVar15 >> 4 & 1;
            }
            if ((bVar13 == bVar15) && (in_fpscr = in_fpscr & 0xfffffff, fVar26 < 0.9999999f)) {
              local_a8[0] = fVar26;
              iVar8 = 1;
LAB_005629ce:
              uVar1 = 0;
              if (iVar8 << 0x1f < 0) {
                fVar17 = 1.0f - local_a8[0];
                fVar17 = fVar17 * fVar17 * fVar17 * fVar20 +
                         fVar17 * 3.0f * fVar17 * local_a8[0] * fVar23 +
                         fVar17 * 3.0f * local_a8[0] * local_a8[0] * fVar22 +
                         local_a8[0] * local_a8[0] * local_a8[0] * fVar21;
                fVar24 = *pfVar11;
                if (fVar17 <= *pfVar11) {
                  fVar24 = fVar17;
                }
                *pfVar11 = fVar24;
                fVar24 = pfVar11[2];
                uVar3 = (in_fpscr & 0xfffffff) | (uint)(fVar17 < fVar24) << 0x1f;
                in_fpscr = uVar3 | (uint)(NAN(fVar17) || NAN(fVar24)) << 0x1c;
                if ((byte)(uVar3 >> 0x1f) != ((byte)(in_fpscr >> 0x1c) & 1)) {
                  fVar17 = fVar24;
                }
                pfVar11[2] = fVar17;
                uVar1 = 1;
              }
              /* Native562a44..562b3a: root count inR7, odd index inR0.
                 Structural research draft; native/C geometry qualification pending. */
              uint loop_pairs = ((uint)iVar8) >> 1;
              iVar8 = (int)uVar1;
              while(loop_pairs != 0) {
              fVar17 = local_a8[iVar8];
              fVar24 = 1.0f - fVar17;
              fVar24 = fVar24 * fVar24 * fVar24 * fVar20 + fVar24 * 3.0f * fVar24 * fVar17 * fVar23 +
                       fVar24 * 3.0f * fVar17 * fVar17 * fVar22 + fVar17 * fVar17 * fVar17 * fVar21;
              fVar17 = *pfVar11;
              if (fVar24 <= *pfVar11) {
                fVar17 = fVar24;
              }
              *pfVar11 = fVar17;
              if (fVar24 < pfVar11[2] || NAN(fVar24) || NAN(pfVar11[2])) {
                fVar24 = pfVar11[2];
              }
              pfVar11[2] = fVar24;
              fVar17 = local_a8[iVar8 + 1];
              fVar24 = 1.0f - fVar17;
              fVar20 = fVar24 * fVar24 * fVar24 * fVar20 + fVar24 * 3.0f * fVar24 * fVar17 * fVar23 +
                       fVar24 * 3.0f * fVar17 * fVar17 * fVar22 + fVar17 * fVar17 * fVar17 * fVar21;
              fVar17 = *pfVar11;
              if (fVar20 <= *pfVar11) {
                fVar17 = fVar20;
              }
              *pfVar11 = fVar17;
              fVar17 = pfVar11[2];
              uVar3 = (in_fpscr & 0xfffffff) | (uint)(fVar20 < fVar17) << 0x1f;
              in_fpscr = uVar3 | (uint)(NAN(fVar20) || NAN(fVar17)) << 0x1c;
              if ((byte)(uVar3 >> 0x1f) == ((byte)(in_fpscr >> 0x1c) & 1)) {
                fVar17 = fVar20;
              }
              pfVar11[2] = fVar17;
              iVar8 += 2;
              --loop_pairs;
              } /* Native LE decrements loop counter; no external call. */
            }
          }
          pfVar7 = pfVar7 + 1;
          pfVar11 = pfVar11 + 1;
          pfVar10 = pfVar10 + 1;
          pfVar9 = pfVar9 + 1;
          pfVar12 = pfVar12 + 1;
          iVar6 = iVar6 + -1;
        } while (iVar6 != 0);
        param_1[4] = pp306_bits(local_a8[2]);
        param_1[5] = pp306_bits(local_a8[3]);
        param_1[6] = pp306_bits(local_a8[4]);
        param_1[7] = pp306_bits(local_a8[5]);
      }
      else if ((bVar13 == 1 || bVar13 == 2) || (bVar13 == 4 || bVar13 == 3)) {
LAB_00563802:
        in_fpscr = in_fpscr & 0xfffffff;
        fVar17 = pp306_float(param_1[4]);
        if (pp308_negative_compare(state.current_x, pp306_float(param_1[4]))) {
          fVar17 = state.current_x;
        }
        param_1[4] = pp306_bits(fVar17);
        fVar17 = pp306_float(param_1[5]);
        if (pp308_negative_compare(state.current_y, pp306_float(param_1[5]))) {
          fVar17 = state.current_y;
        }
        param_1[5] = pp306_bits(fVar17);
        fVar17 = state.current_x;
        if (!pp308_negative_compare(pp306_float(param_1[6]), state.current_x)) {
          fVar17 = pp306_float(param_1[6]);
        }
        param_1[6] = pp306_bits(fVar17);
        fVar17 = state.current_y;
        if (!pp308_negative_compare(pp306_float(param_1[7]), state.current_y)) {
          fVar17 = pp306_float(param_1[7]);
        }
        param_1[7] = pp306_bits(fVar17);
      }
      else if (bVar13 == 5 || bVar13 == 7) {
        uVar3 = in_fpscr & 0xfffffff;
        fVar17 = pp306_float(param_1[4]);
        if (!pp308_negative_compare(pp306_float(param_1[4]), state.current_x)) {
          fVar17 = state.current_x;
        }
        param_1[4] = pp306_bits(fVar17);
        fVar17 = pp306_float(param_1[5]);
        if (!pp308_negative_compare(pp306_float(param_1[5]), state.current_y)) {
          fVar17 = state.current_y;
        }
        param_1[5] = pp306_bits(fVar17);
        fVar17 = pp306_float(param_1[6]);
        if (!pp308_negative_compare(state.current_x, pp306_float(param_1[6]))) {
          fVar17 = state.current_x;
        }
        param_1[6] = pp306_bits(fVar17);
        fVar17 = pp306_float(param_1[7]);
        if (!pp308_negative_compare(state.current_y, pp306_float(param_1[7]))) {
          fVar17 = state.current_y;
        }
        fVar20 = pp306_float(param_1[4]);
        param_1[7] = pp306_bits(fVar17);
        uVar5 = uVar3 | (uint)(state.control1_x < fVar20) << 0x1f;
        in_fpscr = uVar5 | (uint)(NAN(state.control1_x) || NAN(fVar20)) << 0x1c;
        fVar17 = pp306_float(param_1[5]);
        fVar21 = pp306_float(param_1[6]);
        fVar22 = pp306_float(param_1[7]);
        bVar13 = (byte)(uVar5 >> 0x1f);
        bVar15 = (byte)(in_fpscr >> 0x1c) & 1;
        if (bVar13 == bVar15) {
          in_fpscr = uVar3 | (uint)(fVar21 < state.control1_x) << 0x1f |
                     (uint)(NAN(fVar21) || NAN(state.control1_x)) << 0x1c;
          bVar15 = (byte)(in_fpscr >> 0x18);
          bVar13 = bVar15 >> 7;
          bVar15 = bVar15 >> 4 & 1;
        }
        if (bVar13 == bVar15) {
          uVar3 = in_fpscr & 0xfffffff;
          uVar5 = uVar3 | (uint)(state.control1_y < fVar17) << 0x1f;
          in_fpscr = uVar5 | (uint)(NAN(state.control1_y) || NAN(fVar17)) << 0x1c;
          bVar13 = (byte)(uVar5 >> 0x1f);
          bVar15 = (byte)(in_fpscr >> 0x1c) & 1;
          if (bVar13 == bVar15) {
            in_fpscr = uVar3 | (uint)(fVar22 < state.control1_y) << 0x1f |
                       (uint)(NAN(fVar22) || NAN(state.control1_y)) << 0x1c;
            bVar15 = (byte)(in_fpscr >> 0x18);
            bVar13 = bVar15 >> 7;
            bVar15 = bVar15 >> 4 & 1;
          }
          if (bVar13 == bVar15) goto LAB_0056385a;
        }
        fVar23 = state.control1_x * 2.0f + state.previous_x * -2.0f;
        fVar24 = (state.current_x * 2.0f + state.control1_x * -2.0f) - fVar23;
        fVar26 = ABS(fVar24);
        bVar16 = NAN(fVar26);
        uVar3 = (in_fpscr & 0xfffffff) | (uint)(fVar26 < 1.0000001e-07f) << 0x1f;
        bVar14 = SUB41(uVar3 >> 0x1f,0);
        if (bVar14 == bVar16) {
          fVar23 = pp309_divide_then_negate(fVar23, fVar24);
          bVar16 = NAN(fVar23);
          uVar3 = (in_fpscr & 0xfffffff) | (uint)(fVar23 < 1.0000001e-07f) << 0x1f;
          bVar14 = SUB41(uVar3 >> 0x1f,0);
        }
        if ((bVar14 == bVar16) && (uVar3 = uVar3 & 0xfffffff, fVar23 < 0.9999999f)) {
          fVar24 = 1.0f - fVar23;
          fVar23 = fVar24 * fVar24 * state.previous_x + fVar24 * 2.0f * fVar23 * state.control1_x +
                   fVar23 * fVar23 * state.current_x;
          if (!pp308_negative_compare(fVar20, fVar23)) {
            fVar20 = fVar23;
          }
          if (!pp308_negative_compare(fVar23, fVar21)) {
            fVar21 = fVar23;
          }
        }
        fVar23 = state.control1_y * 2.0f + state.previous_y * -2.0f;
        fVar24 = (state.current_y * 2.0f + state.control1_y * -2.0f) - fVar23;
        fVar26 = ABS(fVar24);
        uVar5 = (uVar3 & 0xfffffff) | (uint)(fVar26 < 1.0000001e-07f) << 0x1f;
        in_fpscr = uVar5 | (uint)NAN(fVar26) << 0x1c;
        bVar13 = (byte)(uVar5 >> 0x1f);
        bVar15 = (byte)(in_fpscr >> 0x1c) & 1;
        if (bVar13 == bVar15) {
          fVar23 = pp309_divide_then_negate(fVar23, fVar24);
          in_fpscr = (uVar3 & 0xfffffff) | (uint)(fVar23 < 1.0000001e-07f) << 0x1f |
                     (uint)NAN(fVar23) << 0x1c;
          bVar15 = (byte)(in_fpscr >> 0x18);
          bVar13 = bVar15 >> 7;
          bVar15 = bVar15 >> 4 & 1;
        }
        if ((bVar13 == bVar15) && (in_fpscr = in_fpscr & 0xfffffff, fVar23 < 0.9999999f)) {
          fVar24 = 1.0f - fVar23;
          fVar23 = fVar24 * fVar24 * state.previous_y + fVar24 * 2.0f * fVar23 * state.control1_y +
                   fVar23 * fVar23 * state.current_y;
          if (!pp308_negative_compare(fVar17, fVar23)) {
            fVar17 = fVar23;
          }
          if (!pp308_negative_compare(fVar23, fVar22)) {
            fVar22 = fVar23;
          }
        }
        param_1[4] = pp306_bits(fVar20);
        param_1[5] = pp306_bits(fVar17);
        param_1[6] = pp306_bits(fVar21);
        param_1[7] = pp306_bits(fVar22);
      }
      else if ((bVar13 & 0xf) == 9) {
        fVar20 = ABS(state.control1_x);
        uVar3 = in_fpscr & 0xfffffff;
        in_fpscr = uVar3 | (uint)(fVar20 < 1.0000001e-05f) << 0x1f;
        bVar13 = -(char)((int)in_fpscr >> 0x1f);
        if (bVar13 == 0) {
          fVar17 = ABS(state.control1_y);
          unaff_d9 = (ulonglong)pp306_bits(fVar17);
          in_fpscr = uVar3 | (uint)(fVar17 < 1.0000001e-05f) << 0x1f;
          bVar13 = (byte)(in_fpscr >> 0x1f);
        }
        if (bVar13 != 0) goto LAB_00563802;
        local_a8[5] = state.control2_x;
        fVar26 = state.control2_x * 0.017453292f;
        local_a8[3] = state.last_control_x;
        local_a8[2] = state.last_control_y;
        local_a8[1] = state.last_x;
        local_a8[0] = state.last_y;
        local_a8[4] = (float)audio_uart_float_trig_mode1_50968c(fVar26);
        fVar23 = (float)audio_uart_float_trig_mode0_509690(fVar26);
        fVar28 = local_a8[3] * local_a8[4] + local_a8[2] * fVar23;
        fVar29 = fVar28 / fVar20;
        fVar30 = local_a8[2] * local_a8[4] - local_a8[3] * fVar23;
        fVar31 = local_a8[1] * local_a8[4] + local_a8[0] * fVar23;
        fVar25 = fVar31 / fVar20;
        fVar32 = local_a8[0] * local_a8[4] - local_a8[1] * fVar23;
        fVar21 = fVar29 + fVar25;
        fVar18 = fVar30 / fVar17;
        unaff_d9 = CONCAT44(fVar18,fVar17);
        fVar27 = fVar32 / fVar17;
        fVar22 = fVar18 + fVar27;
        fVar33 = fVar29 - fVar25;
        fVar18 = fVar18 - fVar27;
        fVar24 = fVar33 * fVar33 + fVar18 * fVar18;
        uVar3 = in_fpscr & 0xfffffff;
        in_fpscr = uVar3 | (uint)(fVar24 == 0.0f) << 0x1e;
        if ((byte)(in_fpscr >> 0x1e) != 0) goto LAB_0056385a;
        local_8c[0] = 1.0f / fVar24 + -0.25f;
        if (local_8c[0] < 0.0f) {
          local_8c[0] = 0.0f;
          fVar21 = (float)audio_uart_float_sqrt_4397a8(fVar24 * 0.25f);
          fVar20 = fVar20 * fVar21;
          fVar17 = fVar17 * fVar21;
          fVar29 = fVar28 / fVar20;
          fVar30 = fVar30 / fVar17;
          unaff_d9 = CONCAT44(fVar30,fVar17);
          fVar25 = fVar31 / fVar20;
          fVar21 = fVar29 + fVar25;
          fVar27 = fVar32 / fVar17;
          fVar22 = fVar30 + fVar27;
          fVar33 = fVar29 - fVar25;
          fVar18 = fVar30 - fVar27;
        }
        fVar17 = (float)audio_uart_float_sqrt_4397a8(local_8c[0]);
        fVar31 = fVar21 * 0.5f + fVar17 * fVar18;
        fVar32 = fVar22 * 0.5f - fVar17 * fVar33;
        fVar24 = (float)audio_uart_float_two_input_angle_50969c(pp306_float((uint32_t)(unaff_d9>>32)) - fVar32,fVar29 - fVar31);
        fVar28 = pp306_float((uint32_t)unaff_d9);
        fVar30 = (float)audio_uart_float_two_input_angle_50969c(fVar27 - fVar32,fVar25 - fVar31);
        fVar24 = fVar30 * 57.29578f - fVar24 * 57.29578f;
        if (fVar24 < 0.0f) {
          fVar24 = fVar24 + 360.0f;
        }
        bVar13 = state.arc_command >> 6;
        bVar15 = bVar13 & 1;
        if ((int)((uint)state.arc_command << 0x1a) < 0) {
          bVar15 = bVar15 ^ 1;
        }
        if (((180.0f <= fVar24) || (bVar15 == 0)) && ((fVar24 < 180.0f || (bVar15 != 0)))) {
          fVar31 = fVar21 * 0.5f - fVar17 * fVar18;
          fVar32 = fVar22 * 0.5f + fVar17 * fVar33;
        }
        fVar17 = fVar31 * fVar20 * fVar23 + fVar32 * fVar28 * local_a8[4];
        uVar5 = (uVar3 & 0xfffffff) | (uint)(local_a8[5] == 0.0f) << 0x1e;
        fVar21 = fVar31 * fVar20 * local_a8[4] - fVar32 * fVar28 * fVar23;
        local_a8[4] = -1.0f;
        bVar15 = (byte)(uVar5 >> 0x1e);
        if (bVar15 == 0) {
          uVar5 = (uVar3 & 0xfffffff) | (uint)(local_a8[5] == 180.0f) << 0x1e;
          bVar15 = (byte)(uVar5 >> 0x1e);
        }
        if (bVar15 == 0) {
          uVar3 = (uVar5 & 0xfffffff) | (uint)(local_a8[5] == 90.0f) << 0x1e;
          bVar15 = (byte)(uVar3 >> 0x1e);
          if (bVar15 == 0) {
            uVar3 = (uVar5 & 0xfffffff) | (uint)(local_a8[5] == 270.0f) << 0x1e;
            bVar15 = (byte)(uVar3 >> 0x1e);
          }
          fVar29 = -1.0f;
          if (bVar15 == 0) {
            fVar22 = (float)audio_uart_float_tangent_563f40(fVar26);
            fVar18 = (float)audio_uart_float_inverse_ratio_58ec74((fVar28 * fVar22) / fVar20);
            fVar18 = -fVar18;
            fVar22 = (float)audio_uart_float_tangent_563f40(fVar26);
            fVar30 = (float)audio_uart_float_inverse_ratio_58ec74((fVar28 * fVar22) / fVar20);
            fVar30 = 3.1415927f - fVar30;
            fVar22 = (float)audio_uart_float_trig_mode1_50968c(fVar18);
            fVar23 = (float)audio_uart_float_trig_mode1_50968c(fVar26);
            fVar24 = (float)audio_uart_float_trig_mode0_509690(fVar18);
            fVar25 = (float)audio_uart_float_trig_mode0_509690(fVar26);
            fVar23 = (fVar21 + fVar20 * fVar22 * fVar23) - fVar28 * fVar24 * fVar25;
            fVar22 = (float)audio_uart_float_trig_mode1_50968c(fVar30);
            fVar24 = (float)audio_uart_float_trig_mode1_50968c(fVar26);
            fVar25 = (float)audio_uart_float_trig_mode0_509690(fVar30);
            fVar27 = (float)audio_uart_float_trig_mode0_509690(fVar26);
            fVar25 = (fVar21 + fVar20 * fVar22 * fVar24) - fVar28 * fVar25 * fVar27;
            uVar3 = uVar3 & 0xfffffff;
            fVar22 = fVar25;
            fVar24 = fVar18;
            if (fVar25 < fVar23) {
              fVar22 = fVar23;
              fVar24 = fVar30;
              fVar23 = fVar25;
              fVar30 = fVar18;
            }
            fVar18 = (float)audio_uart_float_trig_mode1_50968c(fVar24);
            fVar25 = (float)audio_uart_float_trig_mode0_509690(fVar26);
            fVar24 = (float)audio_uart_float_trig_mode0_509690(fVar24);
            fVar27 = (float)audio_uart_float_trig_mode1_50968c(fVar26);
            fVar18 = (fVar17 + fVar20 * fVar18 * fVar25 + fVar28 * fVar24 * fVar27) - fVar17;
            uVar3 = (uVar3 & 0xfffffff) | (uint)(fVar18 < 0.0f) << 0x1f | (uint)(fVar18 == 0.0f) << 0x1e
            ;
            uVar5 = uVar3 | (uint)NAN(fVar18) << 0x1c;
            fVar25 = fVar23 - fVar21;
            bVar15 = (byte)(uVar3 >> 0x18);
            fVar24 = fVar29;
            if (!(bool)(bVar15 >> 6 & 1) && bVar15 >> 7 == ((byte)(uVar5 >> 0x1c) & 1)) {
              fVar24 = 1.0f;
            }
            fVar18 = (float)audio_uart_float_sqrt_4397a8(fVar25 * fVar25 + fVar18 * fVar18);
            fVar18 = (float)audio_uart_float_inverse_magnitude_58ecbc(fVar25 / fVar18);
            fVar18 = (float)audio_uart_float_remainder_577c3c(fVar24 * fVar18 + 6.2831855f,pp306_float(0x40c90fdbu));
            fVar24 = (float)audio_uart_float_trig_mode1_50968c(fVar30);
            fVar25 = (float)audio_uart_float_trig_mode0_509690(fVar26);
            fVar30 = (float)audio_uart_float_trig_mode0_509690(fVar30);
            fVar27 = (float)audio_uart_float_trig_mode1_50968c(fVar26);
            fVar30 = (fVar17 + fVar20 * fVar24 * fVar25 + fVar28 * fVar30 * fVar27) - fVar17;
            uVar5 = (uVar5 & 0xfffffff) | (uint)(fVar30 < 0.0f) << 0x1f | (uint)(fVar30 == 0.0f) << 0x1e
            ;
            uVar3 = uVar5 | (uint)NAN(fVar30) << 0x1c;
            fVar25 = fVar22 - fVar21;
            bVar15 = (byte)(uVar5 >> 0x18);
            fVar24 = fVar29;
            if (!(bool)(bVar15 >> 6 & 1) && bVar15 >> 7 == ((byte)(uVar3 >> 0x1c) & 1)) {
              fVar24 = 1.0f;
            }
            fVar30 = (float)audio_uart_float_sqrt_4397a8(fVar25 * fVar25 + fVar30 * fVar30);
            fVar30 = (float)audio_uart_float_inverse_magnitude_58ecbc(fVar25 / fVar30);
            fVar30 = (float)audio_uart_float_remainder_577c3c(fVar24 * fVar30 + 6.2831855f,pp306_float(0x40c90fdbu));
            fVar24 = (float)audio_uart_float_tangent_563f40(fVar26);
            fVar32 = (float)audio_uart_float_inverse_ratio_58ec74(fVar28 / (fVar24 * fVar20));
            fVar24 = (float)audio_uart_float_tangent_563f40(fVar26);
            fVar31 = (float)audio_uart_float_inverse_ratio_58ec74(fVar28 / (fVar24 * fVar20));
            fVar31 = fVar31 + 3.1415927f;
            fVar24 = (float)audio_uart_float_trig_mode1_50968c(fVar32);
            fVar25 = (float)audio_uart_float_trig_mode0_509690(fVar26);
            fVar27 = (float)audio_uart_float_trig_mode0_509690(fVar32);
            fVar33 = (float)audio_uart_float_trig_mode1_50968c(fVar26);
            fVar24 = fVar17 + fVar20 * fVar24 * fVar25 + fVar28 * fVar27 * fVar33;
            fVar25 = (float)audio_uart_float_trig_mode1_50968c(fVar31);
            fVar27 = (float)audio_uart_float_trig_mode0_509690(fVar26);
            fVar33 = (float)audio_uart_float_trig_mode0_509690(fVar31);
            fVar19 = (float)audio_uart_float_trig_mode1_50968c(fVar26);
            fVar33 = fVar17 + fVar20 * fVar25 * fVar27 + fVar28 * fVar33 * fVar19;
            uVar3 = uVar3 & 0xfffffff;
            fVar25 = fVar33;
            fVar27 = fVar32;
            if (fVar33 < fVar24) {
              fVar25 = fVar24;
              fVar27 = fVar31;
              fVar24 = fVar33;
              fVar31 = fVar32;
            }
            local_a8[4] = (float)audio_uart_float_trig_mode1_50968c(fVar27);
            fVar32 = (float)audio_uart_float_trig_mode1_50968c(fVar26);
            fVar27 = (float)audio_uart_float_trig_mode0_509690(fVar27);
            fVar33 = (float)audio_uart_float_trig_mode0_509690(fVar26);
            fVar19 = fVar24 - fVar17;
            uVar3 = (uVar3 & 0xfffffff) | (uint)(fVar19 < 0.0f) << 0x1f | (uint)(fVar19 == 0.0f) << 0x1e
            ;
            uVar5 = uVar3 | (uint)NAN(fVar19) << 0x1c;
            fVar32 = ((fVar21 + fVar20 * local_a8[4] * fVar32) - fVar28 * fVar27 * fVar33) - fVar21;
            bVar15 = (byte)(uVar3 >> 0x18);
            fVar27 = fVar29;
            if (!(bool)(bVar15 >> 6 & 1) && bVar15 >> 7 == ((byte)(uVar5 >> 0x1c) & 1)) {
              fVar27 = 1.0f;
            }
            fVar33 = (float)audio_uart_float_sqrt_4397a8(fVar32 * fVar32 + fVar19 * fVar19);
            fVar32 = (float)audio_uart_float_inverse_magnitude_58ecbc(fVar32 / fVar33);
            fVar27 = (float)audio_uart_float_remainder_577c3c(fVar27 * fVar32 + 6.2831855f,pp306_float(0x40c90fdbu));
            fVar32 = (float)audio_uart_float_trig_mode1_50968c(fVar31);
            fVar33 = (float)audio_uart_float_trig_mode1_50968c(fVar26);
            fVar31 = (float)audio_uart_float_trig_mode0_509690(fVar31);
            fVar26 = (float)audio_uart_float_trig_mode0_509690(fVar26);
            fVar19 = fVar25 - fVar17;
            uVar3 = (uVar5 & 0xfffffff) | (uint)(fVar19 < 0.0f) << 0x1f | (uint)(fVar19 == 0.0f) << 0x1e
            ;
            uVar5 = uVar3 | (uint)NAN(fVar19) << 0x1c;
            fVar20 = ((fVar21 + fVar32 * fVar20 * fVar33) - fVar31 * fVar28 * fVar26) - fVar21;
            bVar15 = (byte)(uVar3 >> 0x18);
            if (!(bool)(bVar15 >> 6 & 1) && bVar15 >> 7 == ((byte)(uVar5 >> 0x1c) & 1)) {
              fVar29 = 1.0f;
            }
            fVar26 = (float)audio_uart_float_sqrt_4397a8(fVar20 * fVar20 + fVar19 * fVar19);
            fVar20 = (float)audio_uart_float_inverse_magnitude_58ecbc(fVar20 / fVar26);
            fVar20 = fVar29 * fVar20 + 6.2831855f;
          }
          else {
            fVar23 = -fVar28;
            fVar22 = (float)audio_uart_float_sqrt_4397a8(fVar23 * fVar23);
            fVar22 = (float)audio_uart_float_inverse_magnitude_58ecbc(fVar23 / fVar22);
            fVar18 = (float)audio_uart_float_remainder_577c3c(fVar22 * -1.0f + 6.2831855f,pp306_float(0x40c90fdbu));
            fVar22 = (float)audio_uart_float_sqrt_4397a8(fVar28 * fVar28);
            fVar22 = (float)audio_uart_float_inverse_magnitude_58ecbc(fVar28 / fVar22);
            fVar30 = (float)audio_uart_float_remainder_577c3c(fVar22 * -1.0f + 6.2831855f,pp306_float(0x40c90fdbu));
            fVar25 = -fVar20;
            uVar3 = (uVar3 & 0xfffffff) | (uint)(fVar25 < 0.0f) << 0x1f | (uint)(fVar25 == 0.0f) << 0x1e
            ;
            uVar5 = uVar3 | (uint)NAN(fVar25) << 0x1c;
            fVar23 = fVar21 - fVar28;
            fVar22 = fVar21 + fVar28;
            fVar24 = fVar17 - fVar20;
            bVar15 = (byte)(uVar3 >> 0x18);
            fVar26 = fVar29;
            if (!(bool)(bVar15 >> 6 & 1) && bVar15 >> 7 == ((byte)(uVar5 >> 0x1c) & 1)) {
              fVar26 = 1.0f;
            }
            fVar25 = (float)audio_uart_float_sqrt_4397a8(fVar25 * fVar25);
            fVar25 = (float)audio_uart_float_inverse_magnitude_58ecbc(0.0f / fVar25);
            fVar27 = (float)audio_uart_float_remainder_577c3c(fVar26 * fVar25 + 6.2831855f,pp306_float(0x40c90fdbu));
            uVar3 = (uVar5 & 0xfffffff) | (uint)(fVar20 < 0.0f) << 0x1f | (uint)(fVar20 == 0.0f) << 0x1e
            ;
            uVar5 = uVar3 | (uint)NAN(fVar20) << 0x1c;
            fVar25 = fVar17 + fVar20;
            bVar15 = (byte)(uVar3 >> 0x18);
            if (!(bool)(bVar15 >> 6 & 1) && bVar15 >> 7 == ((byte)(uVar5 >> 0x1c) & 1)) {
              fVar29 = 1.0f;
            }
            fVar20 = (float)audio_uart_float_sqrt_4397a8(fVar20 * fVar20);
            fVar20 = (float)audio_uart_float_inverse_magnitude_58ecbc(0.0f / fVar20);
            fVar20 = fVar29 * fVar20 + 6.2831855f;
          }
        }
        else {
          fVar23 = -fVar20;
          fVar22 = (float)audio_uart_float_sqrt_4397a8(fVar23 * fVar23);
          fVar22 = (float)audio_uart_float_inverse_magnitude_58ecbc(fVar23 / fVar22);
          fVar18 = (float)audio_uart_float_remainder_577c3c(fVar22 * -1.0f + 6.2831855f,pp306_float(0x40c90fdbu));
          fVar22 = (float)audio_uart_float_sqrt_4397a8(fVar20 * fVar20);
          fVar22 = (float)audio_uart_float_inverse_magnitude_58ecbc(fVar20 / fVar22);
          fVar30 = (float)audio_uart_float_remainder_577c3c(fVar22 * -1.0f + 6.2831855f,pp306_float(0x40c90fdbu));
          fVar26 = -fVar28;
          uVar3 = (uVar5 & 0xfffffff) | (uint)(fVar26 < 0.0f) << 0x1f | (uint)(fVar26 == 0.0f) << 0x1e;
          uVar5 = uVar3 | (uint)NAN(fVar26) << 0x1c;
          fVar23 = fVar21 - fVar20;
          fVar22 = fVar21 + fVar20;
          fVar24 = fVar17 - fVar28;
          bVar15 = (byte)(uVar3 >> 0x18);
          if ((bool)(bVar15 >> 6 & 1) || bVar15 >> 7 != ((byte)(uVar5 >> 0x1c) & 1)) {
            fVar20 = -1.0f;
          }
          else {
            fVar20 = 1.0f;
          }
          fVar26 = (float)audio_uart_float_sqrt_4397a8(fVar26 * fVar26);
          fVar26 = (float)audio_uart_float_inverse_magnitude_58ecbc(0.0f / fVar26);
          fVar27 = (float)audio_uart_float_remainder_577c3c(fVar20 * fVar26 + 6.2831855f,pp306_float(0x40c90fdbu));
          uVar3 = (uVar5 & 0xfffffff) | (uint)(fVar28 < 0.0f) << 0x1f | (uint)(fVar28 == 0.0f) << 0x1e;
          uVar5 = uVar3 | (uint)NAN(fVar28) << 0x1c;
          fVar25 = fVar17 + fVar28;
          bVar15 = (byte)(uVar3 >> 0x18);
          if ((bool)(bVar15 >> 6 & 1) || bVar15 >> 7 != ((byte)(uVar5 >> 0x1c) & 1)) {
            fVar20 = -1.0f;
          }
          else {
            fVar20 = 1.0f;
          }
          fVar26 = (float)audio_uart_float_sqrt_4397a8(fVar28 * fVar28);
          fVar26 = (float)audio_uart_float_inverse_magnitude_58ecbc(0.0f / fVar26);
          fVar20 = fVar20 * fVar26 + 6.2831855f;
        }
        fVar31 = -1.0f;
        fVar26 = (float)audio_uart_float_remainder_577c3c(fVar20,pp306_float(0x40c90fdbu));
        fVar28 = local_a8[2] - fVar17;
        uVar3 = (uVar5 & 0xfffffff) | (uint)(fVar28 < 0.0f) << 0x1f | (uint)(fVar28 == 0.0f) << 0x1e;
        uVar5 = uVar3 | (uint)NAN(fVar28) << 0x1c;
        fVar29 = local_a8[3] - fVar21;
        bVar15 = (byte)(uVar3 >> 0x18);
        fVar20 = fVar31;
        if (!(bool)(bVar15 >> 6 & 1) && bVar15 >> 7 == ((byte)(uVar5 >> 0x1c) & 1)) {
          fVar20 = 1.0f;
        }
        fVar28 = (float)audio_uart_float_sqrt_4397a8(fVar29 * fVar29 + fVar28 * fVar28);
        fVar28 = (float)audio_uart_float_inverse_magnitude_58ecbc(fVar29 / fVar28);
        fVar20 = (float)audio_uart_float_remainder_577c3c(fVar20 * fVar28 + 6.2831855f,pp306_float(0x40c90fdbu));
        fVar17 = local_a8[0] - fVar17;
        uVar3 = (uVar5 & 0xfffffff) | (uint)(fVar17 < 0.0f) << 0x1f | (uint)(fVar17 == 0.0f) << 0x1e;
        in_fpscr = uVar3 | (uint)NAN(fVar17) << 0x1c;
        fVar21 = local_a8[1] - fVar21;
        unaff_d9 = CONCAT44(fVar21,fVar20);
        bVar15 = (byte)(uVar3 >> 0x18);
        if (!(bool)(bVar15 >> 6 & 1) && bVar15 >> 7 == ((byte)(in_fpscr >> 0x1c) & 1)) {
          fVar31 = 1.0f;
        }
        fVar17 = (float)audio_uart_float_sqrt_4397a8(fVar21 * fVar21 + fVar17 * fVar17);
        fVar17 = (float)audio_uart_float_inverse_magnitude_58ecbc(fVar21 / fVar17);
        fVar17 = (float)audio_uart_float_remainder_577c3c(fVar31 * fVar17 + 6.2831855f,pp306_float(0x40c90fdbu));
        if ((bVar13 & 1) == 0) {
          unaff_d9 = (ulonglong)pp306_bits(fVar17);
          fVar17 = fVar20;
        }
        bVar16 = false;
        fVar20 = pp306_float((uint32_t)unaff_d9);
        in_fpscr = in_fpscr & 0xfffffff;
        /* 563620..56374e uses N/PL, including unordered outcomes. */
        {
          int wrapped = pp308_negative_compare(fVar17, fVar20);
          float low = wrapped ? fVar17 : fVar20;
          float high = wrapped ? fVar20 : fVar17;
          if (pp308_arc_excludes(fVar18, low, high) != wrapped)
            fVar23 = pp308_negative_compare(local_a8[3], local_a8[1])
                       ? local_a8[3] : local_a8[1];
          if (pp308_arc_excludes(fVar30, low, high) != wrapped)
            fVar22 = pp308_negative_compare(local_a8[1], local_a8[3])
                       ? local_a8[3] : local_a8[1];
          if (pp308_arc_excludes(fVar27, low, high) != wrapped)
            fVar24 = pp308_negative_compare(local_a8[2], local_a8[0])
                       ? local_a8[2] : local_a8[0];
          if (pp308_arc_excludes(fVar26, low, high) != wrapped)
            fVar25 = pp308_negative_compare(local_a8[0], local_a8[2])
                       ? local_a8[2] : local_a8[0];
        }
        fVar17 = pp306_float(param_1[4]);
        if (fVar23 < pp306_float(param_1[4])) {
          fVar17 = fVar23;
        }
        param_1[4] = pp306_bits(fVar17);
        fVar17 = pp306_float(param_1[5]);
        if (fVar24 < pp306_float(param_1[5])) {
          fVar17 = fVar24;
        }
        param_1[5] = pp306_bits(fVar17);
        fVar17 = pp306_float(param_1[6]);
        if (pp306_float(param_1[6]) < fVar23) {
          fVar17 = fVar23;
        }
        param_1[6] = pp306_bits(fVar17);
        fVar17 = pp306_float(param_1[7]);
        if (pp306_float(param_1[7]) < fVar24) {
          fVar17 = fVar24;
        }
        param_1[7] = pp306_bits(fVar17);
        fVar17 = pp306_float(param_1[4]);
        if (fVar22 < pp306_float(param_1[4])) {
          fVar17 = fVar22;
        }
        param_1[4] = pp306_bits(fVar17);
        fVar17 = pp306_float(param_1[5]);
        if (fVar25 < pp306_float(param_1[5])) {
          fVar17 = fVar25;
        }
        param_1[5] = pp306_bits(fVar17);
        fVar17 = pp306_float(param_1[6]);
        if (pp306_float(param_1[6]) < fVar22) {
          fVar17 = fVar22;
        }
        param_1[6] = pp306_bits(fVar17);
        fVar17 = pp306_float(param_1[7]);
        if (pp306_float(param_1[7]) < fVar25) {
          fVar17 = fVar25;
        }
        param_1[7] = pp306_bits(fVar17);
      }
LAB_0056385a:
      local_90 = local_90 + 1;
    } while (local_90 < *param_1);
  }
  float bound_4 = pp306_float(param_1[4]);
  iVar6 = pp306_i32(bound_4);
  fVar17 = pp306_float(VectorSignedToFloat(iVar6,0));
  uVar3 = VectorSignedToFloat((uint32_t)iVar6 - (uint32_t)pp308_negative_compare(bound_4, fVar17),0);
  param_1[4] = uVar3;
  float bound_5 = pp306_float(param_1[5]);
  iVar6 = pp306_i32(bound_5);
  fVar17 = pp306_float(VectorSignedToFloat(iVar6,0));
  uVar3 = VectorSignedToFloat((uint32_t)iVar6 - (uint32_t)pp308_negative_compare(bound_5, fVar17),0);
  param_1[5] = uVar3;
  float bound_6 = pp306_float(param_1[6]);
  iVar6 = pp306_i32(bound_6);
  fVar17 = pp306_float(VectorSignedToFloat(iVar6,0));
  uVar3 = VectorSignedToFloat((uint32_t)iVar6 + (uint32_t)pp308_negative_compare(fVar17, bound_6),0);
  param_1[6] = uVar3;
  float bound_7 = pp306_float(param_1[7]);
  iVar6 = pp306_i32(bound_7);
  fVar17 = pp306_float(VectorSignedToFloat(iVar6,0));
  uVar3 = VectorSignedToFloat((uint32_t)iVar6 + (uint32_t)pp308_negative_compare(fVar17, bound_7),0);
  param_1[7] = uVar3;
  param_1[0x14] = pp306_bits(pp306_float(param_1[6]) - pp306_float(param_1[4]));
  param_1[0x15] = pp306_bits(pp306_float(param_1[7]) - pp306_float(param_1[5]));
  return;
}


#undef ABS
#undef NAN
#undef SUB41
#undef CONCAT44
