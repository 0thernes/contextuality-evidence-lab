/* Actual pinned Tsotchke seeded software mixer: no hardware entropy. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include "quantum_rng.h"
int main(int argc, char **argv) {
    if (argc != 3) return 2;
    char *end; errno = 0;
    unsigned long long seed = strtoull(argv[1], &end, 10);
    if (errno || !*argv[1] || *end || *argv[1] == '-') return 2;
    errno = 0;
    unsigned long n = strtoul(argv[2], &end, 10);
    if (errno || !*argv[2] || *end || *argv[2] == '-' || n > 16777216UL) return 2;
    uint8_t s[16];
    for (int i=0; i<8; ++i) s[i]=(uint8_t)(seed >> (8*i));
    memcpy(s+8, "CTX-EVID", 8);
    qrng_ctx *ctx = NULL;
    if (qrng_init(&ctx, s, sizeof s) != QRNG_SUCCESS) return 3;
    uint8_t bytes[4096];
    while(n) {
        size_t take=n < sizeof bytes ? n : sizeof bytes;
        if(qrng_bytes(ctx, bytes, take) != QRNG_SUCCESS) { qrng_free(ctx); return 4; }
        for(size_t j=0;j<take;++j) printf("%02x", bytes[j]);
        n-=take;
    }
    qrng_free(ctx);
    return 0;
}
