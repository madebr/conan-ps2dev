#ifdef _EE
# error "_EE definition detected (should not be there)"
#endif

#ifndef __R3000__
# error "__R3000__ definition  not detected"
#endif

#ifdef __R5900__
# error "__R5900__ definition detected (should not be there)"
#endif

int super_sum(int a, int b) {
    return a + b;
}
