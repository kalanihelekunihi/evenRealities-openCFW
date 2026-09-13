/* @(#)e_exp.c 1.3 95/01/18 */
/*
 * ====================================================
 * Copyright (C) 1993 by Sun Microsystems, Inc. All rights reserved.
 *
 * Developed at SunSoft, a Sun Microsystems, Inc. business.
 * Permission to use, copy, modify, and distribute this
 * software is freely granted, provided that this notice 
 * is preserved.
 * ====================================================
 */

/* Adapted from freemint/fdlibm e_exp.c at
 * 61c059fed98e2ed8d26ca39617321134b33e535a.
 * Stock special paths: NaN uses x+x; overflow multiplies runtime huge
 * operands; deep underflow returns zero directly. No binary helper binding.
 * Unsigned exponent updates avoid left-shifting a negative signed integer.
 */
#include <stdint.h>
#define IC(x) UINT32_C(x)
#define IEEE754_DOUBLE_SHIFT 20
#define GET_HIGH_WORD(dst, value) do { union { double d; uint64_t u; } b = { .d = (value) }; (dst) = (uint32_t)(b.u >> 32); } while (0)
#define GET_LOW_WORD(dst, value) do { union { double d; uint64_t u; } b = { .d = (value) }; (dst) = (uint32_t)b.u; } while (0)
#define SET_HIGH_WORD(value, high) do { union { double d; uint64_t u; } b = { .d = (value) }; b.u = (b.u & UINT64_C(0xffffffff)) | ((uint64_t)(uint32_t)(high) << 32); (value) = b.d; } while (0)

double open_cfw_gx8002_backup_exp(double x)			/* default IEEE double exp */
{
	double y, hi, lo, c, t;
	int32_t k, xsb;
	uint32_t hx;

	static const double one = 1.0;
	static const double halF[2] = { 0.5, -0.5 };

	static const double hugeval = 1.0e+300;
	static const double twom1000 = 9.33263618503218878990e-302;		/* 2**-1000=0x01700000,0 */
	static const double o_threshold = 7.09782712893383973096e+02;	/* 0x40862E42, 0xFEFA39EF */
	static const double u_threshold = -7.45133219101941108420e+02;	/* 0xc0874910, 0xD52D3051 */
	static const double ln2HI[2] = {
		6.93147180369123816490e-01,	/* 0x3fe62e42, 0xfee00000 */
		-6.93147180369123816490e-01	/* 0xbfe62e42, 0xfee00000 */
	};

	static const double ln2LO[2] = {
		1.90821492927058770002e-10,	/* 0x3dea39ef, 0x35793c76 */
		-1.90821492927058770002e-10	/* 0xbdea39ef, 0x35793c76 */
	};

	static const double invln2 = 1.44269504088896338700e+00;	/* 0x3ff71547, 0x652b82fe */
	static const double P1 = 1.66666666666666019037e-01;		/* 0x3FC55555, 0x5555553E */
	static const double P2 = -2.77777777770155933842e-03;		/* 0xBF66C16C, 0x16BEBD93 */
	static const double P3 = 6.61375632143793436117e-05;		/* 0x3F11566A, 0xAF25DE2C */
	static const double P4 = -1.65339022054652515390e-06;		/* 0xBEBBBD41, 0xC5D26BF1 */
	static const double P5 = 4.13813679705723846039e-08;		/* 0x3E663769, 0x72BEA4D0 */

	GET_HIGH_WORD(hx, x);				/* high word of x */
	xsb = (hx >> 31) & 1;				/* sign bit of x */
	hx &= IC(0x7fffffff);				/* high word of |x| */

	/* filter out non-finite argument */
	if (hx >= IC(0x40862E42))
	{									/* if |x|>=709.78... */
		if (hx >= IC(0x7ff00000))
		{
			GET_LOW_WORD(k, x);
			if (((hx & IC(0xfffff)) | k) != 0)
				return x + x;			/* stock NaN arithmetic path */
			return (xsb == 0) ? x : 0.0;	/* exp(+-inf)={inf,0} */
		}
		if (x > o_threshold)			/* overflow */
		{
			volatile double operand = hugeval;
			return operand * operand;
		}
		if (x < u_threshold)			/* underflow */
		{
			return 0;
		}
	}

	/* argument reduction */
	if (hx > IC(0x3fd62e42))
	{									/* if  |x| > 0.5 ln2 */
		if (hx < IC(0x3FF0A2B2))
		{								/* and |x| < 1.5 ln2 */
			hi = x - ln2HI[xsb];
			lo = ln2LO[xsb];
			k = 1 - xsb - xsb;
		} else
		{
			k = invln2 * x + halF[xsb];
			t = k;
			hi = x - t * ln2HI[0];		/* t*ln2HI is exact here */
			lo = t * ln2LO[0];
		}
		x = hi - lo;
	} else if (hx < IC(0x3e300000))
	{									/* when |x|<2**-28 */
		if (hugeval + x > one)
			return one + x;				/* trigger inexact */
		return one;
	} else
	{
		k = 0;
		lo = 0;
		hi = 0;
	}

	/* x is now in primary range */
	t = x * x;
	c = x - t * (P1 + t * (P2 + t * (P3 + t * (P4 + t * P5))));
	if (k == 0)
		return one - ((x * c) / (c - 2.0) - x);
	y = one - ((lo - (x * c) / (2.0 - c)) - hi);
	GET_HIGH_WORD(hx, y);
	if (k >= -1021)
	{
		hx += ((uint32_t)k << IEEE754_DOUBLE_SHIFT);			/* add k to y's exponent */
		SET_HIGH_WORD(y, hx);
		return y;
	} else
	{
		hx += ((uint32_t)(k + 1000) << IEEE754_DOUBLE_SHIFT);	/* add k to y's exponent */
		SET_HIGH_WORD(y, hx);
		return y * twom1000;
	}
}

