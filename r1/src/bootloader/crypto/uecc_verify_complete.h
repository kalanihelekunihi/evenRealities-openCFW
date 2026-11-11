/* Derived from Kenneth MacKay's BSD-2-Clause micro-ecc verification code.
 * The upstream notices remain in the generated translation unit.
 * Complete the mixed-add exceptional cases used by public ECDSA verification.
 * This helper operates on public data; it is not a signing primitive.
 */
static void r1_verify_mixed_add(uECC_word_t *rx, uECC_word_t *ry,
                              uECC_word_t *z, const uECC_word_t *point,
                              uECC_Curve curve) {
    wordcount_t words = curve->num_words;
    uECC_word_t tx[uECC_MAX_WORDS], ty[uECC_MAX_WORDS], difference[uECC_MAX_WORDS];
    if (uECC_vli_isZero(z, words)) {
        uECC_vli_set(rx, point, words);
        uECC_vli_set(ry, point + words, words);
        uECC_vli_clear(z, words);
        z[0] = 1;
        return;
    }
    uECC_vli_set(tx, point, words);
    uECC_vli_set(ty, point + words, words);
    apply_z(tx, ty, z, curve);
    if (uECC_vli_equal(rx, tx, words)) {
        if (uECC_vli_equal(ry, ty, words)) {
            curve->double_jacobian(rx, ry, z, curve);
        } else {
            /* Opposite points sum to infinity, represented by Z = 0. */
            uECC_vli_clear(z, words);
        }
        return;
    }
    uECC_vli_modSub(difference, rx, tx, curve->p, words);
    XYcZ_add(tx, ty, rx, ry, tx, curve);
    uECC_vli_modMult_fast(z, z, difference, curve);
}

int uECC_verify(const uint8_t *public_key,
                const uint8_t *message_hash,
                unsigned hash_size,
                const uint8_t *signature,
                uECC_Curve curve) {
    uECC_word_t u1[uECC_MAX_WORDS], u2[uECC_MAX_WORDS];
    uECC_word_t z[uECC_MAX_WORDS];
    uECC_word_t sum[uECC_MAX_WORDS * 2];
    uECC_word_t rx[uECC_MAX_WORDS];
    uECC_word_t ry[uECC_MAX_WORDS];
    const uECC_word_t *points[4];
    const uECC_word_t *point;
    bitcount_t num_bits;
    bitcount_t i;
#if uECC_VLI_NATIVE_LITTLE_ENDIAN
    uECC_word_t *_public = (uECC_word_t *)public_key;
#else
    uECC_word_t _public[uECC_MAX_WORDS * 2];
#endif
    uECC_word_t r[uECC_MAX_WORDS], s[uECC_MAX_WORDS];
    wordcount_t num_words = curve->num_words;
    wordcount_t num_n_words = BITS_TO_WORDS(curve->num_n_bits);

    rx[num_n_words - 1] = 0;
    r[num_n_words - 1] = 0;
    s[num_n_words - 1] = 0;

#if uECC_VLI_NATIVE_LITTLE_ENDIAN
    bcopy((uint8_t *) r, signature, curve->num_bytes);
    bcopy((uint8_t *) s, signature + curve->num_bytes, curve->num_bytes);
#else
    uECC_vli_bytesToNative(_public, public_key, curve->num_bytes);
    uECC_vli_bytesToNative(
        _public + num_words, public_key + curve->num_bytes, curve->num_bytes);
    uECC_vli_bytesToNative(r, signature, curve->num_bytes);
    uECC_vli_bytesToNative(s, signature + curve->num_bytes, curve->num_bytes);
#endif

    /* r, s must not be 0. */
    if (uECC_vli_isZero(r, num_words) || uECC_vli_isZero(s, num_words)) {
        return 0;
    }

    /* r, s must be < n. */
    if (uECC_vli_cmp_unsafe(curve->n, r, num_n_words) != 1 ||
            uECC_vli_cmp_unsafe(curve->n, s, num_n_words) != 1) {
        return 0;
    }

    /* Calculate u1 and u2. */
    uECC_vli_modInv(z, s, curve->n, num_n_words); /* z = 1/s */
    u1[num_n_words - 1] = 0;
    bits2int(u1, message_hash, hash_size, curve);
    uECC_vli_modMult(u1, u1, z, curve->n, num_n_words); /* u1 = e/s */
    uECC_vli_modMult(u2, r, z, curve->n, num_n_words); /* u2 = r/s */

    /* Validate the imported public point before using mixed-add assumptions. */
    if (!uECC_valid_point(_public, curve)) {
        return 0;
    }
    /* Precompute G + Q, including Q = G and Q = -G. */
    uECC_vli_set(sum, _public, num_words);
    uECC_vli_set(sum + num_words, _public + num_words, num_words);
    uECC_vli_clear(z, num_words);
    z[0] = 1;
    r1_verify_mixed_add(sum, sum + num_words, z, curve->G, curve);
    points[0] = 0;
    points[1] = curve->G;
    points[2] = _public;
    points[3] = 0;
    if (!uECC_vli_isZero(z, num_words)) {
        uECC_vli_modInv(z, z, curve->p, num_words);
        apply_z(sum, sum + num_words, z, curve);
        points[3] = sum;
    }
    num_bits = smax(uECC_vli_numBits(u1, num_n_words),
                    uECC_vli_numBits(u2, num_n_words));

    /* Start at infinity; a selected precomputed point may also be infinity. */
    uECC_vli_clear(rx, num_words);
    uECC_vli_clear(ry, num_words);
    uECC_vli_clear(z, num_words);
    for (i = num_bits - 1; i >= 0; --i) {
        uECC_word_t index;
        if (!uECC_vli_isZero(z, num_words)) {
            curve->double_jacobian(rx, ry, z, curve);
        }
        index = (!!uECC_vli_testBit(u1, i)) | ((!!uECC_vli_testBit(u2, i)) << 1);
        point = points[index];
        if (point) {
            r1_verify_mixed_add(rx, ry, z, point, curve);
        }
    }
    if (uECC_vli_isZero(z, num_words)) {
        return 0;
    }

    uECC_vli_modInv(z, z, curve->p, num_words); /* Z = 1/Z */
    apply_z(rx, ry, z, curve);

    /* v = x1 (mod n) */
    if (uECC_vli_cmp_unsafe(curve->n, rx, num_n_words) != 1) {
        uECC_vli_sub(rx, rx, curve->n, num_n_words);
    }

    /* Accept only if v == r. */
    return (int)(uECC_vli_equal(rx, r, num_words));
}
