# Bob session: metaphone-fix-tests

- Started: 20260926T113911Z
- Command: `bob -p <prompt>`
- Duration: 106.2s
- Bob cost: 0.149

## Prompt

````
Some of your characterization tests fail against the ORIGINAL, unmodified code, which means
they assert behaviour the code does not have. Fix those assertions to match what the code
actually does (or remove a test only if its behaviour cannot be pinned deterministically).
Keep every passing test. Reply with the complete corrected `MetaphoneCharacterizationTest` in one ```java block. Keep every line under 100 characters.

Failures:
- MetaphoneCharacterizationTest.hBeforeVowelIncluded: expected: <H0R> but was: <W0R>
- MetaphoneCharacterizationTest.whetherEncoding: expected: <H0R> but was: <W0R>

Your previous test class:
```java
package org.apache.commons.codec.language;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Characterization tests for {@link Metaphone}.
 *
 * <p>Every assertion is derived by tracing the code as written.
 * Where the code and its Javadoc disagree the code wins.</p>
 */
class MetaphoneCharacterizationTest {

    private Metaphone m;

    @BeforeEach
    void setUp() {
        m = new Metaphone();
    }

    // -----------------------------------------------------------------------
    // Boundary / degenerate inputs
    // -----------------------------------------------------------------------

    @Test
    void nullInputReturnsEmpty() {
        assertEquals("", m.metaphone(null));
    }

    @Test
    void emptyInputReturnsEmpty() {
        assertEquals("", m.metaphone(""));
    }

    /** Single character is returned uppercased, no processing. */
    @Test
    void singleUppercaseLetterIsReturnedAsIs() {
        assertEquals("A", m.metaphone("A"));
    }

    /** Single lowercase character is uppercased and returned verbatim. */
    @Test
    void singleLowercaseLetterIsUppercased() {
        assertEquals("Z", m.metaphone("z"));
    }

    /** Two-char word: initial 'A' with non-E second char keeps both chars. */
    @Test
    void twoCharWordAB() {
        assertEquals("AB", m.metaphone("AB"));
    }

    // -----------------------------------------------------------------------
    // Input is case-insensitive (all converted to upper before processing)
    // -----------------------------------------------------------------------

    @Test
    void lowercaseInputIsNormalised() {
        assertEquals(m.metaphone("PHONE"), m.metaphone("phone"));
    }

    @Test
    void mixedCaseInputIsNormalised() {
        assertEquals(m.metaphone("SMITH"), m.metaphone("SmItH"));
    }

    // -----------------------------------------------------------------------
    // Initial two-character special cases
    // -----------------------------------------------------------------------

    /**
     * Initial AE: the 'A' is dropped; processing starts at 'E'.
     * The leading vowel rule then adds 'E' to the code.
     */
    @Test
    void initialAEDropsA() {
        assertEquals("E", m.metaphone("AE"));
    }

    /** Initial KN: the 'K' is dropped. */
    @Test
    void initialKNDropsK() {
        assertEquals("N", m.metaphone("KN"));
    }

    /** Initial GN: the 'G' is dropped. */
    @Test
    void initialGNDropsG() {
        assertEquals("N", m.metaphone("GN"));
    }

    /** Initial PN: the 'P' is dropped (same switch arm as KN). */
    @Test
    void initialPNDropsP() {
        assertEquals("N", m.metaphone("PN"));
    }

    /** Initial WR: the 'W' is dropped; processing starts at 'R'. */
    @Test
    void initialWRDropsW() {
        assertEquals("R", m.metaphone("WR"));
    }

    /**
     * Initial WH: the 'H' is replaced with 'W' in the local buffer.
     * Then 'W' in the loop is silent when not followed by a vowel
     * (the buffer is only "W", length 1, so isLastChar is true → no append).
     */
    @Test
    void initialWHProducesEmpty() {
        assertEquals("", m.metaphone("WH"));
    }

    /**
     * Initial W followed by a vowel (not R or H): 'W' is kept because
     * the next character is a vowel.
     */
    @Test
    void initialWFollowedByVowelKeptW() {
        assertEquals("W", m.metaphone("WA"));
    }

    /** Initial X is rewritten to 'S' before processing. */
    @Test
    void initialXBecomesS() {
        assertEquals("S", m.metaphone("XA"));
    }

    // -----------------------------------------------------------------------
    // Vowels: only leading vowel is encoded
    // -----------------------------------------------------------------------

    /**
     * Leading vowel is included; subsequent vowels are silent.
     * "OCEAN" → O(leading), C→S, E(silent), A(silent), N
     */
    @Test
    void onlyLeadingVowelEncoded() {
        assertEquals("OSN", m.metaphone("OCEAN"));
    }

    /** No leading vowel → no vowel in code. */
    @Test
    void noLeadingVowelNoVowelInCode() {
        String code = m.metaphone("SMITH");
        assertFalse(code.contains("A") || code.contains("E")
                || code.contains("I") || code.contains("O")
                || code.contains("U"),
                "No vowel expected in SMITH metaphone");
    }

    // -----------------------------------------------------------------------
    // Consonant rules — individual cases
    // -----------------------------------------------------------------------

    /** PH → F */
    @Test
    void phBecomesF() {
        assertEquals("FN", m.metaphone("PHONE"));
    }

    /** TH → 0 (digit zero, representing theta). */
    @Test
    void thBecomesZero() {
        assertEquals("SM0", m.metaphone("SMITH"));
        assertEquals("0MS", m.metaphone("THOMAS"));
    }

    /** V → F */
    @Test
    void vBecomesF() {
        // VACATION: V→F, A silent, C→K, A silent, TIO→X, N
        assertEquals("FKXN", m.metaphone("VACATION"));
    }

    /** Q → K */
    @Test
    void qBecomesK() {
        // QUICK: Q→K, U silent, I silent, C→K, K after C is dropped
        assertEquals("KK", m.metaphone("QUICK"));
    }

    /** Z → S */
    @Test
    void zBecomesS() {
        // CZAR: C→K (default), Z→S, A silent, R
        assertEquals("KSR", m.metaphone("CZAR"));
    }

    /** X (non-initial) → KS */
    @Test
    void nonInitialXBecomesKS() {
        // XAVIER: initial X→S, then A silent, V→F, I silent, E silent, R
        assertEquals("SFR", m.metaphone("XAVIER"));
    }

    // -----------------------------------------------------------------------
    // B: silent after M at end of word (-MB)
    // -----------------------------------------------------------------------

    @Test
    void silentBAfterMAtEndOfWord() {
        assertEquals("LM", m.metaphone("LIMB"));
    }

    @Test
    void silentBAtEndOfBOMB() {
        assertEquals("BM", m.metaphone("BOMB"));
    }

    /** B at start of word is NOT silent. */
    @Test
    void bAtStartIsNotSilent() {
        assertTrue(m.metaphone("BOMB").startsWith("B"));
    }

    // -----------------------------------------------------------------------
    // C: many special cases
    // -----------------------------------------------------------------------

    /** SCI / SCE / SCY: C is silent. */
    @Test
    void sciSilentC() {
        // SCIENCE: S, [C silent because SCI], I silent, E silent, N, C→S, E silent
        assertEquals("SNS", m.metaphone("SCIENCE"));
    }

    /** CIA → X */
    @Test
    void ciaBecomesX() {
        // SPECIAL: S, P, E silent, CIA→X, I silent, A silent, L
        assertEquals("SPXL", m.metaphone("SPECIAL"));
    }

    /** CE/CI/CY → S */
    @Test
    void ceBecomesS() {
        // OCEAN: O(leading), CE→S, A silent, N
        assertEquals("OSN", m.metaphone("OCEAN"));
    }

    /** SCH → K */
    @Test
    void schBecomesK() {
        // SCHOOL: S, SCH→K, [H silent after C], OO(dup O silent), L
        assertEquals("SKL", m.metaphone("SCHOOL"));
    }

    /** CH at word start followed by vowel (consonant context) → K */
    @Test
    void initialChBeforeVowelBecomesK() {
        // CHEMISTRY: CH→K (initial, vowel at pos 2), E silent, M, S, T → KMST
        assertEquals("KMST", m.metaphone("CHEMISTRY"));
    }

    /** CH in non-initial position → X */
    @Test
    void nonInitialChBecomesX() {
        // BACH: B, A silent, CH→X, H(terminal)silent
        assertEquals("BX", m.metaphone("BACH"));
    }

    /** Initial CH + vowel at pos 2: K (consonant form) */
    @Test
    void chorusInitialCh() {
        // CHORUS: CH→K, O silent, R, U silent, S
        assertEquals("KRS", m.metaphone("CHORUS"));
    }

    /** C → K when not followed by front vowel or H. */
    @Test
    void defaultCBecomesK() {
        // CZAR: C→K (Z is not a front vowel)
        assertEquals("KSR", m.metaphone("CZAR"));
    }

    /** Two consecutive C's: each processed independently (C exempt from dup rule). */
    @Test
    void doubleCNotDeduped() {
        // ACCOMPLISH: A(leading), CC→KK, O silent, M → AKKM
        assertEquals("AKKM", m.metaphone("ACCOMPLISH"));
    }

    /** CC before E: first C→K, second C→S (CE rule). */
    @Test
    void acceptCcBeforeE() {
        // ACCEPT: A, C→K, C→S(CE), E silent, P, T → loop exits at length 4 → AKSP
        assertEquals("AKSP", m.metaphone("ACCEPT"));
    }

    /** SUCCEED: S, C→K, C→S(CE), doubled E deduped, D→T */
    @Test
    void succeedEncoding() {
        assertEquals("SKST", m.metaphone("SUCCEED"));
    }

    // -----------------------------------------------------------------------
    // D: DGE/DGI/DGY → J
    // -----------------------------------------------------------------------

    @Test
    void dgeBecomesJ() {
        // JUDGE: J, U silent, DGE→J → JJ
        assertEquals("JJ", m.metaphone("JUDGE"));
    }

    @Test
    void edgeLeadingVowelThenDge() {
        // EDGE: E(leading), DGE→J → EJ
        assertEquals("EJ", m.metaphone("EDGE"));
    }

    /** D not followed by GE/GI/GY → T */
    @Test
    void defaultDBecomesT() {
        // DISCUSS: D→T, I silent, S, C→K (after S but not SCI), U silent, S, S(dup)
        assertEquals("TSKS", m.metaphone("DISCUSS"));
    }

    // -----------------------------------------------------------------------
    // G: many silent conditions
    // -----------------------------------------------------------------------

    /** GH at end of word is silent. */
    @Test
    void finalGHIsSilent() {
        // LAUGH: L, A silent, U silent, GH(terminal)silent, H(terminal)silent
        assertEquals("L", m.metaphone("LAUGH"));
    }

    /** GH before consonant is silent. */
    @Test
    void ghBeforeConsonantIsSilent() {
        // NIGHT: N, I silent, GH(before T)silent, H silent, T
        assertEquals("NT", m.metaphone("NIGHT"));
    }

    /** GN in middle of word: G is silent. */
    @Test
    void gnInMiddleGSilent() {
        // SIGN: S, I silent, GN→silent G, N
        assertEquals("SN", m.metaphone("SIGN"));
    }

    /** GN at end of word: G is silent. */
    @Test
    void gnAtEndGSilent() {
        // DESIGN: D→T, E silent, S, I silent, GN→silent G, N
        assertEquals("TSN", m.metaphone("DESIGN"));
    }

    /** Initial GN drops G (initial-two-char rule). */
    @Test
    void initialGNDropsGViaInitialRule() {
        // GNASH: GN→N(initial drop), A silent, SH→X, H(terminal)silent
        assertEquals("NX", m.metaphone("GNASH"));
    }

    /** GE/GI/GY not after GG → J */
    @Test
    void geBecomesJ() {
        // AEGEAN: AE→E(initial), G before E → J, E silent, A silent, N
        assertEquals("EJN", m.metaphone("AEGEAN"));
    }

    // -----------------------------------------------------------------------
    // H: silent after CSPTG or at end; voiced before vowel
    // -----------------------------------------------------------------------

    /** Terminal H is silent. */
    @Test
    void terminalHIsSilent() {
        // LAUGH → L (GH and terminal H both silent)
        String code = m.metaphone("LAUGH");
        assertFalse(code.contains("H"), "Terminal H must not appear in code");
    }

    /** H after varson chars (C S P T G) is silent. */
    @Test
    void hAfterVarsonIsSilent() {
        // PHONE: P, H(after P = varson)silent, O silent, N → FN
        assertEquals("FN", m.metaphone("PHONE"));
    }

    /** H before a vowel and not after varson → included. */
    @Test
    void hBeforeVowelIncluded() {
        // WHETHER: W(before H not vowel→silent), H(before E, not after varson)→H,
        //          E silent, TH→0, H(after T=varson)silent, E silent, R
        assertEquals("H0R", m.metaphone("WHETHER"));
    }

    // -----------------------------------------------------------------------
    // K: silent after C
    // -----------------------------------------------------------------------

    @Test
    void kAfterCIsSilent() {
        // QUICK: Q→K, U silent, I silent, C→K, K(after C)silent
        assertEquals("KK", m.metaphone("QUICK"));
    }

    @Test
    void initialKIsKept() {
        // KNIGHT: KN→N (initial rule), I silent, GH silent, H silent, T → NT
        assertEquals("NT", m.metaphone("KNIGHT"));
    }

    // -----------------------------------------------------------------------
    // S: SH / SIO / SIA → X
    // -----------------------------------------------------------------------

    @Test
    void shBecomesX() {
        // PHISH: PH→F, I silent, SH→X, H(terminal)silent
        assertEquals("FX", m.metaphone("PHISH"));
    }

    @Test
    void sioBecomesX() {
        // PASSION: P, A silent, S, S(dup)silent, I silent, O silent, N → PSN
        // Note: SIO check is at position 2 ("SSI") which does NOT match "SIO" → S appended
        assertEquals("PSN", m.metaphone("PASSION"));
    }

    @Test
    void sessionDoubleS() {
        // SESSION: S, E silent, S(not dup at pos 2), S(dup at pos 3)silent,
        //          I silent, O silent, N → SSN
        assertEquals("SSN", m.metaphone("SESSION"));
    }

    // -----------------------------------------------------------------------
    // T: TIA/TIO → X; TCH silent; TH → 0
    // -----------------------------------------------------------------------

    @Test
    void tioBecomesX() {
        // NATION: N, A silent, TIO→X, N → NXN
        assertEquals("NXN", m.metaphone("NATION"));
    }

    @Test
    void tiaBecomesX() {
        // no convenient word, use PARTIAL: check TIA via PARTIAL path
        // Use direct word "TIARA": T→X(TIA), R, A silent → "XR"
        assertEquals("XR", m.metaphone("TIARA"));
    }

    @Test
    void thBecomesZeroInThomas() {
        assertEquals("0MS", m.metaphone("THOMAS"));
    }

    @Test
    void wrightEncodesGhSilentAndTh() {
        // WR→R (initial), I silent, GH(before T)silent, H(after varson G)silent, T
        assertEquals("RT", m.metaphone("WRIGHT"));
    }

    // -----------------------------------------------------------------------
    // W and Y: silent unless followed by a vowel
    // -----------------------------------------------------------------------

    @Test
    void wNotFollowedByVowelIsSilent() {
        // WH → "" (W becomes the only char but has no following vowel)
        assertEquals("", m.metaphone("WH"));
    }

    @Test
    void wFollowedByVowelIsKept() {
        assertEquals("W", m.metaphone("WA"));
    }

    // -----------------------------------------------------------------------
    // Duplicate letter suppression (all letters except C)
    // -----------------------------------------------------------------------

    @Test
    void duplicateNonCLetterSuppressed() {
        // OOZE: O(leading,n=0), O(dup)skip, Z→S, E silent → "OS"
        assertEquals("OS", m.metaphone("OOZE"));
    }

    @Test
    void duplicateCIsNotSuppressed() {
        // ACCOMPLISH shows two C's both processed → AKKM
        assertEquals("AKKM", m.metaphone("ACCOMPLISH"));
    }

    // -----------------------------------------------------------------------
    // maxCodeLen property
    // -----------------------------------------------------------------------

    @Test
    void defaultMaxCodeLenIsFour() {
        assertEquals(4, m.getMaxCodeLen());
    }

    @Test
    void maxCodeLenTruncatesOutput() {
        // PTARMIGAN without truncation would be PTRM (exactly 4) — confirm
        assertEquals("PTRM", m.metaphone("PTARMIGAN"));
    }

    @Test
    void setMaxCodeLenOne() {
        m.setMaxCodeLen(1);
        assertEquals("S", m.metaphone("SMITH"));
    }

    @Test
    void setMaxCodeLenZeroReturnsEmpty() {
        m.setMaxCodeLen(0);
        assertEquals("", m.metaphone("SMITH"));
    }

    @Test
    void setMaxCodeLenRoundtrip() {
        m.setMaxCodeLen(6);
        assertEquals(6, m.getMaxCodeLen());
    }

    // -----------------------------------------------------------------------
    // encode(String) delegates to metaphone
    // -----------------------------------------------------------------------

    @Test
    void encodeStringDelegatesToMetaphone() {
        assertEquals(m.metaphone("SMITH"), m.encode("SMITH"));
    }

    // -----------------------------------------------------------------------
    // encode(Object) — type checking
    // -----------------------------------------------------------------------

    @Test
    void encodeObjectWithStringSucceeds() throws Exception {
        assertEquals("SM0", m.encode((Object) "SMITH"));
    }

    @Test
    void encodeObjectWithNonStringThrows() {
        assertThrows(org.apache.commons.codec.EncoderException.class,
                () -> m.encode((Object) Integer.valueOf(42)));
    }

    @Test
    void encodeObjectExceptionMessageDescriptive() {
        org.apache.commons.codec.EncoderException ex =
                assertThrows(org.apache.commons.codec.EncoderException.class,
                        () -> m.encode((Object) Boolean.TRUE));
        assertTrue(ex.getMessage().contains("Metaphone"),
                "Exception message should mention Metaphone");
    }

    // -----------------------------------------------------------------------
    // isMetaphoneEqual
    // -----------------------------------------------------------------------

    @Test
    void isMetaphoneEqualSameWord() {
        assertTrue(m.isMetaphoneEqual("SMITH", "SMITH"));
    }

    @Test
    void isMetaphoneEqualKnightNight() {
        // Both encode to "NT"
        assertTrue(m.isMetaphoneEqual("KNIGHT", "NIGHT"));
    }

    @Test
    void isMetaphoneEqualCzarTsar() {
        // CZAR→KSR, TSAR→TSR — different
        assertFalse(m.isMetaphoneEqual("CZAR", "TSAR"));
    }

    @Test
    void isMetaphoneEqualPhoneAndFone() {
        // PHONE→FN, FONE→FN
        assertTrue(m.isMetaphoneEqual("PHONE", "FONE"));
    }

    // -----------------------------------------------------------------------
    // Specific word encodings (regression pins)
    // -----------------------------------------------------------------------

    @Test
    void smithEncoding() {
        assertEquals("SM0", m.metaphone("SMITH"));
    }

    @Test
    void chemistryEncoding() {
        assertEquals("KMST", m.metaphone("CHEMISTRY"));
    }

    @Test
    void jumpEncoding() {
        assertEquals("JMP", m.metaphone("JUMP"));
    }

    @Test
    void specialEncoding() {
        assertEquals("SPXL", m.metaphone("SPECIAL"));
    }

    @Test
    void chordEncoding() {
        // CHORD: CH→K(initial+vowel), O silent, R, D→T
        assertEquals("KRT", m.metaphone("CHORD"));
    }

    @Test
    void chorusEncoding() {
        assertEquals("KRS", m.metaphone("CHORUS"));
    }

    @Test
    void schoolEncoding() {
        assertEquals("SKL", m.metaphone("SCHOOL"));
    }

    @Test
    void laughEncoding() {
        assertEquals("L", m.metaphone("LAUGH"));
    }

    @Test
    void nightEncoding() {
        assertEquals("NT", m.metaphone("NIGHT"));
    }

    @Test
    void knightEncoding() {
        assertEquals("NT", m.metaphone("KNIGHT"));
    }

    @Test
    void gnashEncoding() {
        assertEquals("NX", m.metaphone("GNASH"));
    }

    @Test
    void judgeEncoding() {
        assertEquals("JJ", m.metaphone("JUDGE"));
    }

    @Test
    void edgeEncoding() {
        assertEquals("EJ", m.metaphone("EDGE"));
    }

    @Test
    void discussEncoding() {
        assertEquals("TSKS", m.metaphone("DISCUSS"));
    }

    @Test
    void succeedEncoding2() {
        assertEquals("SKST", m.metaphone("SUCCEED"));
    }

    @Test
    void whetherEncoding() {
        assertEquals("H0R", m.metaphone("WHETHER"));
    }

    @Test
    void signEncoding() {
        assertEquals("SN", m.metaphone("SIGN"));
    }

    @Test
    void designEncoding() {
        assertEquals("TSN", m.metaphone("DESIGN"));
    }

    @Test
    void nationEncoding() {
        assertEquals("NXN", m.metaphone("NATION"));
    }

    @Test
    void vacationEncoding() {
        assertEquals("FKXN", m.metaphone("VACATION"));
    }

    @Test
    void aegeanEncoding() {
        assertEquals("EJN", m.metaphone("AEGEAN"));
    }

    @Test
    void wrightEncoding() {
        assertEquals("RT", m.metaphone("WRIGHT"));
    }

    @Test
    void xavierEncoding() {
        assertEquals("SFR", m.metaphone("XAVIER"));
    }

    @Test
    void acceptEncoding() {
        assertEquals("AKSP", m.metaphone("ACCEPT"));
    }

    @Test
    void bachEncoding() {
        assertEquals("BX", m.metaphone("BACH"));
    }

    @Test
    void ptarmiganEncoding() {
        assertEquals("PTRM", m.metaphone("PTARMIGAN"));
    }

    @Test
    void czarEncoding() {
        assertEquals("KSR", m.metaphone("CZAR"));
    }

    @Test
    void tsarEncoding() {
        assertEquals("TSR", m.metaphone("TSAR"));
    }

    @Test
    void phishEncoding() {
        assertEquals("FX", m.metaphone("PHISH"));
    }

    @Test
    void scienceEncoding() {
        assertEquals("SNS", m.metaphone("SCIENCE"));
    }

    @Test
    void accomplishEncoding() {
        assertEquals("AKKM", m.metaphone("ACCOMPLISH"));
    }

    @Test
    void quickEncoding() {
        assertEquals("KK", m.metaphone("QUICK"));
    }

    @Test
    void thomasEncoding() {
        assertEquals("0MS", m.metaphone("THOMAS"));
    }

    @Test
    void passionEncoding() {
        assertEquals("PSN", m.metaphone("PASSION"));
    }

    @Test
    void sessionEncoding() {
        assertEquals("SSN", m.metaphone("SESSION"));
    }

    @Test
    void bombEncoding() {
        assertEquals("BM", m.metaphone("BOMB"));
    }

    @Test
    void limbEncoding() {
        assertEquals("LM", m.metaphone("LIMB"));
    }
}

```

The original code:
```java
/*
 * Copyright 2001-2004 The Apache Software Foundation.
 * 
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * 
 *      http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */ 

package org.apache.commons.codec.language;

import org.apache.commons.codec.EncoderException;
import org.apache.commons.codec.StringEncoder;

/**
 * Encodes a string into a metaphone value. 
 * <p>
 * Initial Java implementation by <CITE>William B. Brogden. December, 1997</CITE>. 
 * Permission given by <CITE>wbrogden</CITE> for code to be used anywhere.
 * </p>
 * <p>
 * <CITE>Hanging on the Metaphone</CITE> by <CITE>Lawrence Philips</CITE> in <CITE>Computer Language of Dec. 1990, p
 * 39.</CITE>
 * </p>
 * 
 * @author Apache Software Foundation
 * @version $Id: Metaphone.java,v 1.20 2004/06/05 18:32:04 ggregory Exp $
 */
public class Metaphone implements StringEncoder {

    /**
     * Five values in the English language 
     */
    private String vowels = "AEIOU" ;

    /**
     * Variable used in Metaphone algorithm
     */
    private String frontv = "EIY"   ;

    /**
     * Variable used in Metaphone algorithm
     */
    private String varson = "CSPTG" ;

    /**
     * The max code length for metaphone is 4
     */
    private int maxCodeLen = 4 ;

    /**
     * Creates an instance of the Metaphone encoder
     */
    public Metaphone() {
        super();
    }

    /**
     * Find the metaphone value of a String. This is similar to the
     * soundex algorithm, but better at finding similar sounding words.
     * All input is converted to upper case.
     * Limitations: Input format is expected to be a single ASCII word
     * with only characters in the A - Z range, no punctuation or numbers.
     *
     * @param txt String to find the metaphone code for
     * @return A metaphone code corresponding to the String supplied
     */
    public String metaphone(String txt) {
        boolean hard = false ;
        if ((txt == null) || (txt.length() == 0)) {
            return "" ;
        }
        // single character is itself
        if (txt.length() == 1) {
            return txt.toUpperCase() ;
        }
      
        char[] inwd = txt.toUpperCase().toCharArray() ;
      
        StringBuffer local = new StringBuffer(40); // manipulate
        StringBuffer code = new StringBuffer(10) ; //   output
        // handle initial 2 characters exceptions
        switch(inwd[0]) {
        case 'K' : 
        case 'G' : 
        case 'P' : /* looking for KN, etc*/
            if (inwd[1] == 'N') {
                local.append(inwd, 1, inwd.length - 1);
            } else {
                local.append(inwd);
            }
            break;
        case 'A': /* looking for AE */
            if (inwd[1] == 'E') {
                local.append(inwd, 1, inwd.length - 1);
            } else {
                local.append(inwd);
            }
            break;
        case 'W' : /* looking for WR or WH */
            if (inwd[1] == 'R') {   // WR -> R
                local.append(inwd, 1, inwd.length - 1); 
                break ;
            }
            if (inwd[1] == 'H') {
                local.append(inwd, 1, inwd.length - 1);
                local.setCharAt(0, 'W'); // WH -> W
            } else {
                local.append(inwd);
            }
            break;
        case 'X' : /* initial X becomes S */
            inwd[0] = 'S';
            local.append(inwd);
            break ;
        default :
            local.append(inwd);
        } // now local has working string with initials fixed

        int wdsz = local.length();
        int n = 0 ;

        while ((code.length() < this.getMaxCodeLen()) && 
        	   (n < wdsz) ) { // max code size of 4 works well
            char symb = local.charAt(n) ;
            // remove duplicate letters except C
            if ((symb != 'C') && (isPreviousChar( local, n, symb )) ) {
                n++ ;
            } else { // not dup
                switch(symb) {
                case 'A' : case 'E' : case 'I' : case 'O' : case 'U' :
                    if (n == 0) { 
                        code.append(symb);
                    }
                    break ; // only use vowel if leading char
                case 'B' :
                    if ( isPreviousChar(local, n, 'M') && 
                         isLastChar(wdsz, n) ) { // B is silent if word ends in MB
						break;
                    }
                    code.append(symb);
                    break;
                case 'C' : // lots of C special cases
                    /* discard if SCI, SCE or SCY */
                    if ( isPreviousChar(local, n, 'S') && 
                         !isLastChar(wdsz, n) && 
                         (this.frontv.indexOf(local.charAt(n + 1)) >= 0) ) { 
                        break;
                    }
                    if (regionMatch(local, n, "CIA")) { // "CIA" -> X
                        code.append('X'); 
                        break;
                    }
                    if (!isLastChar(wdsz, n) && 
                        (this.frontv.indexOf(local.charAt(n + 1)) >= 0)) {
                        code.append('S');
                        break; // CI,CE,CY -> S
                    }
                    if (isPreviousChar(local, n, 'S') &&
						isNextChar(local, n, 'H') ) { // SCH->sk
                        code.append('K') ; 
                        break ;
                    }
                    if (isNextChar(local, n, 'H')) { // detect CH
                        if ((n == 0) && 
                        	(wdsz >= 3) && 
                            isVowel(local,2) ) { // CH consonant -> K consonant
                            code.append('K');
                        } else { 
                            code.append('X'); // CHvowel -> X
                        }
                    } else { 
                        code.append('K');
                    }
                    break ;
                case 'D' :
                    if (!isLastChar(wdsz, n + 1) && 
                        isNextChar(local, n, 'G') && 
                        (this.frontv.indexOf(local.charAt(n + 2)) >= 0)) { // DGE DGI DGY -> J 
                        code.append('J'); n += 2 ;
                    } else { 
                        code.append('T');
                    }
                    break ;
                case 'G' : // GH silent at end or before consonant
                    if (isLastChar(wdsz, n + 1) && 
                        isNextChar(local, n, 'H')) {
                        break;
                    }
                    if (!isLastChar(wdsz, n + 1) &&  
                        isNextChar(local,n,'H') && 
                        !isVowel(local,n+2)) {
                        break;
                    }
                    if ((n > 0) && 
                    	( regionMatch(local, n, "GN") ||
					      regionMatch(local, n, "GNED") ) ) {
                        break; // silent G
                    }
                    if (isPreviousChar(local, n, 'G')) {
                        hard = true ;
                    } else {
                        hard = false ;
                    }
                    if (!isLastChar(wdsz, n) && 
                        (this.frontv.indexOf(local.charAt(n + 1)) >= 0) && 
                        (!hard)) {
                        code.append('J');
                    } else {
                        code.append('K');
                    }
                    break ;
                case 'H':
                    if (isLastChar(wdsz, n)) {
                        break ; // terminal H
                    }
                    if ((n > 0) && 
                        (this.varson.indexOf(local.charAt(n - 1)) >= 0)) {
                        break;
                    }
                    if (isVowel(local,n+1)) {
                        code.append('H'); // Hvowel
                    }
                    break;
                case 'F': 
                case 'J' : 
                case 'L' :
                case 'M': 
                case 'N' : 
                case 'R' :
                    code.append(symb); 
                    break;
                case 'K' :
                    if (n > 0) { // not initial
                        if (!isPreviousChar(local, n, 'C')) {
                            code.append(symb);
                        }
                    } else {
                        code.append(symb); // initial K
                    }
                    break ;
                case 'P' :
                    if (isNextChar(local,n,'H')) {
                        // PH -> F
                        code.append('F');
                    } else {
                        code.append(symb);
                    }
                    break ;
                case 'Q' :
                    code.append('K');
                    break;
                case 'S' :
                    if (regionMatch(local,n,"SH") || 
					    regionMatch(local,n,"SIO") || 
					    regionMatch(local,n,"SIA")) {
                        code.append('X');
                    } else {
                        code.append('S');
                    }
                    break;
                case 'T' :
                    if (regionMatch(local,n,"TIA") || 
						regionMatch(local,n,"TIO")) {
                        code.append('X'); 
                        break;
                    }
                    if (regionMatch(local,n,"TCH")) {
						// Silent if in "TCH"
                        break;
                    }
                    // substitute numeral 0 for TH (resembles theta after all)
                    if (regionMatch(local,n,"TH")) {
                        code.append('0');
                    } else {
                        code.append('T');
                    }
                    break ;
                case 'V' :
                    code.append('F'); break ;
                case 'W' : case 'Y' : // silent if not followed by vowel
                    if (!isLastChar(wdsz,n) && 
                    	isVowel(local,n+1)) {
                        code.append(symb);
                    }
                    break ;
                case 'X' :
                    code.append('K'); code.append('S');
                    break ;
                case 'Z' :
                    code.append('S'); break ;
                } // end switch
                n++ ;
            } // end else from symb != 'C'
            if (code.length() > this.getMaxCodeLen()) { 
            	code.setLength(this.getMaxCodeLen()); 
            }
        }
        return code.toString();
    }

	private boolean isVowel(StringBuffer string, int index) {
		return (this.vowels.indexOf(string.charAt(index)) >= 0);
	}

	private boolean isPreviousChar(StringBuffer string, int index, char c) {
		boolean matches = false;
		if( index > 0 &&
		    index < string.length() ) {
			matches = string.charAt(index - 1) == c;
		}
		return matches;
	}

	private boolean isNextChar(StringBuffer string, int index, char c) {
		boolean matches = false;
		if( index >= 0 &&
		    index < string.length() - 1 ) {
			matches = string.charAt(index + 1) == c;
		}
		return matches;
	}

	private boolean regionMatch(StringBuffer string, int index, String test) {
		boolean matches = false;
		if( index >= 0 &&
		    (index + test.length() - 1) < string.length() ) {
			String substring = string.substring( index, index + test.length());
			matches = substring.equals( test );
		}
		return matches;
	}

	private boolean isLastChar(int wdsz, int n) {
		return n + 1 == wdsz;
	} 
    
    
    /**
     * Encodes an Object using the metaphone algorithm.  This method
     * is provided in order to satisfy the requirements of the
     * Encoder interface, and will throw an EncoderException if the
     * supplied object is not of type java.lang.String.
     *
     * @param pObject Object to encode
     * @return An object (or type java.lang.String) containing the 
     *         metaphone code which corresponds to the String supplied.
     * @throws EncoderException if the parameter supplied is not
     *                          of type java.lang.String
     */
    public Object encode(Object pObject) throws EncoderException {
        if (!(pObject instanceof java.lang.String)) {
            throw new EncoderException("Parameter supplied to Metaphone encode is not of type java.lang.String"); 
        }
        return metaphone((String) pObject);
    }

    /**
     * Encodes a String using the Metaphone algorithm. 
     *
     * @param pString String object to encode
     * @return The metaphone code corresponding to the String supplied
     */
    public String encode(String pString) {
        return metaphone(pString);   
    }

    /**
     * Tests is the metaphones of two strings are identical.
     *
     * @param str1 First of two strings to compare
     * @param str2 Second of two strings to compare
     * @return true if the metaphones of these strings are identical, 
     *         false otherwise.
     */
    public boolean isMetaphoneEqual(String str1, String str2) {
        return metaphone(str1).equals(metaphone(str2));
    }

    /**
     * Returns the maxCodeLen.
     * @return int
     */
    public int getMaxCodeLen() { return this.maxCodeLen; }

    /**
     * Sets the maxCodeLen.
     * @param maxCodeLen The maxCodeLen to set
     */
    public void setMaxCodeLen(int maxCodeLen) { this.maxCodeLen = maxCodeLen; }

}

```

````

## Bob's answer

````
Let me trace the WHETHER encoding through the code carefully.

Tool calls:
- spawn_subagent

Tool (1) 2026-09-26 11:39:42.642 UTC (+30.7s) Success

Tool: spawn_subagent
Args:
- description: Trace the Metaphone algorithm on the string "WHETHER" using this exact Java code:

```java
public String metaphone(St...




The actual encoding is W0R. The two failing tests both assert H0R — that's wrong. The fix is to change both
hBeforeVowelIncluded and whetherEncoding to expect W0R, and update the inline comment to explain the real WH-prefix
behaviour.

```java
  package org.apache.commons.codec.language;

  import org.junit.jupiter.api.BeforeEach;
  import org.junit.jupiter.api.Test;

  import static org.junit.jupiter.api.Assertions.*;

  /**
   * Characterization tests for {@link Metaphone}.
   *
   * <p>Every assertion is derived by tracing the code as written.
   * Where the code and its Javadoc disagree the code wins.</p>
   */
  class MetaphoneCharacterizationTest {

      private Metaphone m;

      @BeforeEach
      void setUp() {
          m = new Metaphone();
      }

      // -----------------------------------------------------------------------
      // Boundary / degenerate inputs
      // -----------------------------------------------------------------------

      @Test
      void nullInputReturnsEmpty() {
          assertEquals("", m.metaphone(null));
      }

      @Test
      void emptyInputReturnsEmpty() {
          assertEquals("", m.metaphone(""));
      }

      /** Single character is returned uppercased, no processing. */
      @Test
      void singleUppercaseLetterIsReturnedAsIs() {
          assertEquals("A", m.metaphone("A"));
      }

      /** Single lowercase character is uppercased and returned verbatim. */
      @Test
      void singleLowercaseLetterIsUppercased() {
          assertEquals("Z", m.metaphone("z"));
      }

      /** Two-char word: initial 'A' with non-E second char keeps both chars. */
      @Test
      void twoCharWordAB() {
          assertEquals("AB", m.metaphone("AB"));
      }

      // -----------------------------------------------------------------------
      // Input is case-insensitive (all converted to upper before processing)
      // -----------------------------------------------------------------------

      @Test
      void lowercaseInputIsNormalised() {
          assertEquals(m.metaphone("PHONE"), m.metaphone("phone"));
      }

      @Test
      void mixedCaseInputIsNormalised() {
          assertEquals(m.metaphone("SMITH"), m.metaphone("SmItH"));
      }

      // -----------------------------------------------------------------------
      // Initial two-character special cases
      // -----------------------------------------------------------------------

      /**
       * Initial AE: the 'A' is dropped; processing starts at 'E'.
       * The leading vowel rule then adds 'E' to the code.
       */
      @Test
      void initialAEDropsA() {
          assertEquals("E", m.metaphone("AE"));
      }

      /** Initial KN: the 'K' is dropped. */
      @Test
      void initialKNDropsK() {
          assertEquals("N", m.metaphone("KN"));
      }

      /** Initial GN: the 'G' is dropped. */
      @Test
      void initialGNDropsG() {
          assertEquals("N", m.metaphone("GN"));
      }

      /** Initial PN: the 'P' is dropped (same switch arm as KN). */
      @Test
      void initialPNDropsP() {
          assertEquals("N", m.metaphone("PN"));
      }

      /** Initial WR: the 'W' is dropped; processing starts at 'R'. */
      @Test
      void initialWRDropsW() {
          assertEquals("R", m.metaphone("WR"));
      }

      /**
       * Initial WH: the code rewrites WH to a single 'W' in the local buffer.
       * 'W' in the loop is only kept when followed by a vowel; here the buffer
       * is only "W" (length 1), so isLastChar is true and nothing is appended.
       */
      @Test
      void initialWHProducesEmpty() {
          assertEquals("", m.metaphone("WH"));
      }

      /**
       * Initial W followed by a vowel (not R or H): 'W' is kept because
       * the next character is a vowel.
       */
      @Test
      void initialWFollowedByVowelKeptW() {
          assertEquals("W", m.metaphone("WA"));
      }

      /** Initial X is rewritten to 'S' before processing. */
      @Test
      void initialXBecomesS() {
          assertEquals("S", m.metaphone("XA"));
      }

      // -----------------------------------------------------------------------
      // Vowels: only leading vowel is encoded
      // -----------------------------------------------------------------------

      /**
       * Leading vowel is included; subsequent vowels are silent.
       * "OCEAN" → O(leading), C→S, E(silent), A(silent), N
       */
      @Test
      void onlyLeadingVowelEncoded() {
          assertEquals("OSN", m.metaphone("OCEAN"));
      }

      /** No leading vowel → no vowel in code. */
      @Test
      void noLeadingVowelNoVowelInCode() {
          String code = m.metaphone("SMITH");
          assertFalse(code.contains("A") || code.contains("E")
                  || code.contains("I") || code.contains("O")
                  || code.contains("U"),
                  "No vowel expected in SMITH metaphone");
      }

      // -----------------------------------------------------------------------
      // Consonant rules — individual cases
      // -----------------------------------------------------------------------

      /** PH → F */
      @Test
      void phBecomesF() {
          assertEquals("FN", m.metaphone("PHONE"));
      }

      /** TH → 0 (digit zero, representing theta). */
      @Test
      void thBecomesZero() {
          assertEquals("SM0", m.metaphone("SMITH"));
          assertEquals("0MS", m.metaphone("THOMAS"));
      }

      /** V → F */
      @Test
      void vBecomesF() {
          // VACATION: V→F, A silent, C→K, A silent, TIO→X, N
          assertEquals("FKXN", m.metaphone("VACATION"));
      }

      /** Q → K */
      @Test
      void qBecomesK() {
          // QUICK: Q→K, U silent, I silent, C→K, K after C is dropped
          assertEquals("KK", m.metaphone("QUICK"));
      }

      /** Z → S */
      @Test
      void zBecomesS() {
          // CZAR: C→K (default), Z→S, A silent, R
          assertEquals("KSR", m.metaphone("CZAR"));
      }

      /** X (non-initial) → KS */
      @Test
      void nonInitialXBecomesKS() {
          // XAVIER: initial X→S, then A silent, V→F, I silent, E silent, R
          assertEquals("SFR", m.metaphone("XAVIER"));
      }

      // -----------------------------------------------------------------------
      // B: silent after M at end of word (-MB)
      // -----------------------------------------------------------------------

      @Test
      void silentBAfterMAtEndOfWord() {
          assertEquals("LM", m.metaphone("LIMB"));
      }

      @Test
      void silentBAtEndOfBOMB() {
          assertEquals("BM", m.metaphone("BOMB"));
      }

      /** B at start of word is NOT silent. */
      @Test
      void bAtStartIsNotSilent() {
          assertTrue(m.metaphone("BOMB").startsWith("B"));
      }

      // -----------------------------------------------------------------------
      // C: many special cases
      // -----------------------------------------------------------------------

      /** SCI / SCE / SCY: C is silent. */
      @Test
      void sciSilentC() {
          // SCIENCE: S, [C silent because SCI], I silent, E silent, N, C→S, E silent
          assertEquals("SNS", m.metaphone("SCIENCE"));
      }

      /** CIA → X */
      @Test
      void ciaBecomesX() {
          // SPECIAL: S, P, E silent, CIA→X, I silent, A silent, L
          assertEquals("SPXL", m.metaphone("SPECIAL"));
      }

      /** CE/CI/CY → S */
      @Test
      void ceBecomesS() {
          // OCEAN: O(leading), CE→S, A silent, N
          assertEquals("OSN", m.metaphone("OCEAN"));
      }

      /** SCH → K */
      @Test
      void schBecomesK() {
          // SCHOOL: S, SCH→K, [H silent after C], OO(dup O silent), L
          assertEquals("SKL", m.metaphone("SCHOOL"));
      }

      /** CH at word start followed by vowel (consonant context) → K */
      @Test
      void initialChBeforeVowelBecomesK() {
          // CHEMISTRY: CH→K (initial, vowel at pos 2), E silent, M, S, T → KMST
          assertEquals("KMST", m.metaphone("CHEMISTRY"));
      }

      /** CH in non-initial position → X */
      @Test
      void nonInitialChBecomesX() {
          // BACH: B, A silent, CH→X, H(terminal)silent
          assertEquals("BX", m.metaphone("BACH"));
      }

      /** Initial CH + vowel at pos 2: K (consonant form) */
      @Test
      void chorusInitialCh() {
          // CHORUS: CH→K, O silent, R, U silent, S
          assertEquals("KRS", m.metaphone("CHORUS"));
      }

      /** C → K when not followed by front vowel or H. */
      @Test
      void defaultCBecomesK() {
          // CZAR: C→K (Z is not a front vowel)
          assertEquals("KSR", m.metaphone("CZAR"));
      }

      /** Two consecutive C's: each processed independently (C exempt from dup rule). */
      @Test
      void doubleCNotDeduped() {
          // ACCOMPLISH: A(leading), CC→KK, O silent, M → AKKM
          assertEquals("AKKM", m.metaphone("ACCOMPLISH"));
      }

      /** CC before E: first C→K, second C→S (CE rule). */
      @Test
      void acceptCcBeforeE() {
          // ACCEPT: A, C→K, C→S(CE), E silent, P, T → loop exits at length 4 → AKSP
          assertEquals("AKSP", m.metaphone("ACCEPT"));
      }

      /** SUCCEED: S, C→K, C→S(CE), doubled E deduped, D→T */
      @Test
      void succeedEncoding() {
          assertEquals("SKST", m.metaphone("SUCCEED"));
      }

      // -----------------------------------------------------------------------
      // D: DGE/DGI/DGY → J
      // -----------------------------------------------------------------------

      @Test
      void dgeBecomesJ() {
          // JUDGE: J, U silent, DGE→J → JJ
          assertEquals("JJ", m.metaphone("JUDGE"));
      }

      @Test
      void edgeLeadingVowelThenDge() {
          // EDGE: E(leading), DGE→J → EJ
          assertEquals("EJ", m.metaphone("EDGE"));
      }

      /** D not followed by GE/GI/GY → T */
      @Test
      void defaultDBecomesT() {
          // DISCUSS: D→T, I silent, S, C→K (after S but not SCI), U silent, S, S(dup)
          assertEquals("TSKS", m.metaphone("DISCUSS"));
      }

      // -----------------------------------------------------------------------
      // G: many silent conditions
      // -----------------------------------------------------------------------

      /** GH at end of word is silent. */
      @Test
      void finalGHIsSilent() {
          // LAUGH: L, A silent, U silent, GH(terminal)silent, H(terminal)silent
          assertEquals("L", m.metaphone("LAUGH"));
      }

      /** GH before consonant is silent. */
      @Test
      void ghBeforeConsonantIsSilent() {
          // NIGHT: N, I silent, GH(before T)silent, H silent, T
          assertEquals("NT", m.metaphone("NIGHT"));
      }

      /** GN in middle of word: G is silent. */
      @Test
      void gnInMiddleGSilent() {
          // SIGN: S, I silent, GN→silent G, N
          assertEquals("SN", m.metaphone("SIGN"));
      }

      /** GN at end of word: G is silent. */
      @Test
      void gnAtEndGSilent() {
          // DESIGN: D→T, E silent, S, I silent, GN→silent G, N
          assertEquals("TSN", m.metaphone("DESIGN"));
      }

      /** Initial GN drops G (initial-two-char rule). */
      @Test
      void initialGNDropsGViaInitialRule() {
          // GNASH: GN→N(initial drop), A silent, SH→X, H(terminal)silent
          assertEquals("NX", m.metaphone("GNASH"));
      }

      /** GE/GI/GY not after GG → J */
      @Test
      void geBecomesJ() {
          // AEGEAN: AE→E(initial), G before E → J, E silent, A silent, N
          assertEquals("EJN", m.metaphone("AEGEAN"));
      }

      // -----------------------------------------------------------------------
      // H: silent after CSPTG or at end; voiced before vowel
      // -----------------------------------------------------------------------

      /** Terminal H is silent. */
      @Test
      void terminalHIsSilent() {
          // LAUGH → L (GH and terminal H both silent)
          String code = m.metaphone("LAUGH");
          assertFalse(code.contains("H"), "Terminal H must not appear in code");
      }

      /** H after varson chars (C S P T G) is silent. */
      @Test
      void hAfterVarsonIsSilent() {
          // PHONE: P, H(after P = varson)silent, O silent, N → FN
          assertEquals("FN", m.metaphone("PHONE"));
      }

      /**
       * WHETHER: initial WH rewrites the buffer to "WETHER".
       * W is kept (followed by vowel E), TH→0, H(after T=varson)silent, R.
       * Result is "W0R".
       */
      @Test
      void hBeforeVowelIncluded() {
          assertEquals("W0R", m.metaphone("WHETHER"));
      }

      // -----------------------------------------------------------------------
      // K: silent after C
      // -----------------------------------------------------------------------

      @Test
      void kAfterCIsSilent() {
          // QUICK: Q→K, U silent, I silent, C→K, K(after C)silent
          assertEquals("KK", m.metaphone("QUICK"));
      }

      @Test
      void initialKIsKept() {
          // KNIGHT: KN→N (initial rule), I silent, GH silent, H silent, T → NT
          assertEquals("NT", m.metaphone("KNIGHT"));
      }

      // -----------------------------------------------------------------------
      // S: SH / SIO / SIA → X
      // -----------------------------------------------------------------------

      @Test
      void shBecomesX() {
          // PHISH: PH→F, I silent, SH→X, H(terminal)silent
          assertEquals("FX", m.metaphone("PHISH"));
      }

      @Test
      void sioBecomesX() {
          // PASSION: P, A silent, S, S(dup)silent, I silent, O silent, N → PSN
          // Note: SIO check is at position 2 ("SSI") which does NOT match "SIO" → S appended
          assertEquals("PSN", m.metaphone("PASSION"));
      }

      @Test
      void sessionDoubleS() {
          // SESSION: S, E silent, S(not dup at pos 2), S(dup at pos 3)silent,
          //          I silent, O silent, N → SSN
          assertEquals("SSN", m.metaphone("SESSION"));
      }

      // -----------------------------------------------------------------------
      // T: TIA/TIO → X; TCH silent; TH → 0
      // -----------------------------------------------------------------------

      @Test
      void tioBecomesX() {
          // NATION: N, A silent, TIO→X, N → NXN
          assertEquals("NXN", m.metaphone("NATION"));
      }

      @Test
      void tiaBecomesX() {
          // Use direct word "TIARA": T→X(TIA), R, A silent → "XR"
          assertEquals("XR", m.metaphone("TIARA"));
      }

      @Test
      void thBecomesZeroInThomas() {
          assertEquals("0MS", m.metaphone("THOMAS"));
      }

      @Test
      void wrightEncodesGhSilentAndTh() {
          // WR→R (initial), I silent, GH(before T)silent, H(after varson G)silent, T
          assertEquals("RT", m.metaphone("WRIGHT"));
      }

      // -----------------------------------------------------------------------
      // W and Y: silent unless followed by a vowel
      // -----------------------------------------------------------------------

      @Test
      void wNotFollowedByVowelIsSilent() {
          // WH → "" (W becomes the only char but has no following vowel)
          assertEquals("", m.metaphone("WH"));
      }

      @Test
      void wFollowedByVowelIsKept() {
          assertEquals("W", m.metaphone("WA"));
      }

      // -----------------------------------------------------------------------
      // Duplicate letter suppression (all letters except C)
      // -----------------------------------------------------------------------

      @Test
      void duplicateNonCLetterSuppressed() {
          // OOZE: O(leading,n=0), O(dup)skip, Z→S, E silent → "OS"
          assertEquals("OS", m.metaphone("OOZE"));
      }

      @Test
      void duplicateCIsNotSuppressed() {
          // ACCOMPLISH shows two C's both processed → AKKM
          assertEquals("AKKM", m.metaphone("ACCOMPLISH"));
      }

      // -----------------------------------------------------------------------
      // maxCodeLen property
      // -----------------------------------------------------------------------

      @Test
      void defaultMaxCodeLenIsFour() {
          assertEquals(4, m.getMaxCodeLen());
      }

      @Test
      void maxCodeLenTruncatesOutput() {
          // PTARMIGAN without truncation would be PTRM (exactly 4) — confirm
          assertEquals("PTRM", m.metaphone("PTARMIGAN"));
      }

      @Test
      void setMaxCodeLenOne() {
          m.setMaxCodeLen(1);
          assertEquals("S", m.metaphone("SMITH"));
      }

      @Test
      void setMaxCodeLenZeroReturnsEmpty() {
          m.setMaxCodeLen(0);
          assertEquals("", m.metaphone("SMITH"));
      }

      @Test
      void setMaxCodeLenRoundtrip() {
          m.setMaxCodeLen(6);
          assertEquals(6, m.getMaxCodeLen());
      }

      // -----------------------------------------------------------------------
      // encode(String) delegates to metaphone
      // -----------------------------------------------------------------------

      @Test
      void encodeStringDelegatesToMetaphone() {
          assertEquals(m.metaphone("SMITH"), m.encode("SMITH"));
      }

      // -----------------------------------------------------------------------
      // encode(Object) — type checking
      // -----------------------------------------------------------------------

      @Test
      void encodeObjectWithStringSucceeds() throws Exception {
          assertEquals("SM0", m.encode((Object) "SMITH"));
      }

      @Test
      void encodeObjectWithNonStringThrows() {
          assertThrows(org.apache.commons.codec.EncoderException.class,
                  () -> m.encode((Object) Integer.valueOf(42)));
      }

      @Test
      void encodeObjectExceptionMessageDescriptive() {
          org.apache.commons.codec.EncoderException ex =
                  assertThrows(org.apache.commons.codec.EncoderException.class,
                          () -> m.encode((Object) Boolean.TRUE));
          assertTrue(ex.getMessage().contains("Metaphone"),
                  "Exception message should mention Metaphone");
      }

      // -----------------------------------------------------------------------
      // isMetaphoneEqual
      // -----------------------------------------------------------------------

      @Test
      void isMetaphoneEqualSameWord() {
          assertTrue(m.isMetaphoneEqual("SMITH", "SMITH"));
      }

      @Test
      void isMetaphoneEqualKnightNight() {
          // Both encode to "NT"
          assertTrue(m.isMetaphoneEqual("KNIGHT", "NIGHT"));
      }

      @Test
      void isMetaphoneEqualCzarTsar() {
          // CZAR→KSR, TSAR→TSR — different
          assertFalse(m.isMetaphoneEqual("CZAR", "TSAR"));
      }

      @Test
      void isMetaphoneEqualPhoneAndFone() {
          // PHONE→FN, FONE→FN
          assertTrue(m.isMetaphoneEqual("PHONE", "FONE"));
      }

      // -----------------------------------------------------------------------
      // Specific word encodings (regression pins)
      // -----------------------------------------------------------------------

      @Test
      void smithEncoding() {
          assertEquals("SM0", m.metaphone("SMITH"));
      }

      @Test
      void chemistryEncoding() {
          assertEquals("KMST", m.metaphone("CHEMISTRY"));
      }

      @Test
      void jumpEncoding() {
          assertEquals("JMP", m.metaphone("JUMP"));
      }

      @Test
      void specialEncoding() {
          assertEquals("SPXL", m.metaphone("SPECIAL"));
      }

      @Test
      void chordEncoding() {
          // CHORD: CH→K(initial+vowel), O silent, R, D→T
          assertEquals("KRT", m.metaphone("CHORD"));
      }

      @Test
      void chorusEncoding() {
          assertEquals("KRS", m.metaphone("CHORUS"));
      }

      @Test
      void schoolEncoding() {
          assertEquals("SKL", m.metaphone("SCHOOL"));
      }

      @Test
      void laughEncoding() {
          assertEquals("L", m.metaphone("LAUGH"));
      }

      @Test
      void nightEncoding() {
          assertEquals("NT", m.metaphone("NIGHT"));
      }

      @Test
      void knightEncoding() {
          assertEquals("NT", m.metaphone("KNIGHT"));
      }

      @Test
      void gnashEncoding() {
          assertEquals("NX", m.metaphone("GNASH"));
      }

      @Test
      void judgeEncoding() {
          assertEquals("JJ", m.metaphone("JUDGE"));
      }

      @Test
      void edgeEncoding() {
          assertEquals("EJ", m.metaphone("EDGE"));
      }

      @Test
      void discussEncoding() {
          assertEquals("TSKS", m.metaphone("DISCUSS"));
      }

      @Test
      void succeedEncoding2() {
          assertEquals("SKST", m.metaphone("SUCCEED"));
      }

      /**
       * WHETHER: WH prefix rewrites buffer to "WETHER"; W is kept (next char
       * is vowel E), TH→0, second H is silent (T is a varson char), R.
       */
      @Test
      void whetherEncoding() {
          assertEquals("W0R", m.metaphone("WHETHER"));
      }

      @Test
      void signEncoding() {
          assertEquals("SN", m.metaphone("SIGN"));
      }

      @Test
      void designEncoding() {
          assertEquals("TSN", m.metaphone("DESIGN"));
      }

      @Test
      void nationEncoding() {
          assertEquals("NXN", m.metaphone("NATION"));
      }

      @Test
      void vacationEncoding() {
          assertEquals("FKXN", m.metaphone("VACATION"));
      }

      @Test
      void aegeanEncoding() {
          assertEquals("EJN", m.metaphone("AEGEAN"));
      }

      @Test
      void wrightEncoding() {
          assertEquals("RT", m.metaphone("WRIGHT"));
      }

      @Test
      void xavierEncoding() {
          assertEquals("SFR", m.metaphone("XAVIER"));
      }

      @Test
      void acceptEncoding() {
          assertEquals("AKSP", m.metaphone("ACCEPT"));
      }

      @Test
      void bachEncoding() {
          assertEquals("BX", m.metaphone("BACH"));
      }

      @Test
      void ptarmiganEncoding() {
          assertEquals("PTRM", m.metaphone("PTARMIGAN"));
      }

      @Test
      void czarEncoding() {
          assertEquals("KSR", m.metaphone("CZAR"));
      }

      @Test
      void tsarEncoding() {
          assertEquals("TSR", m.metaphone("TSAR"));
      }

      @Test
      void phishEncoding() {
          assertEquals("FX", m.metaphone("PHISH"));
      }

      @Test
      void scienceEncoding() {
          assertEquals("SNS", m.metaphone("SCIENCE"));
      }

      @Test
      void accomplishEncoding() {
          assertEquals("AKKM", m.metaphone("ACCOMPLISH"));
      }

      @Test
      void quickEncoding() {
          assertEquals("KK", m.metaphone("QUICK"));
      }

      @Test
      void thomasEncoding() {
          assertEquals("0MS", m.metaphone("THOMAS"));
      }

      @Test
      void passionEncoding() {
          assertEquals("PSN", m.metaphone("PASSION"));
      }

      @Test
      void sessionEncoding() {
          assertEquals("SSN", m.metaphone("SESSION"));
      }

      @Test
      void bombEncoding() {
          assertEquals("BM", m.metaphone("BOMB"));
      }

      @Test
      void limbEncoding() {
          assertEquals("LM", m.metaphone("LIMB"));
      }
  }
```


What changed and why:

The two failing tests both asserted H0R for WHETHER. Tracing the code:

1. The initial W + H branch runs local.append(inwd, 1, inwd.length-1) (copies HETHER) then local.setCharAt(0, 'W') —
   giving local = "WETHER", not "HETHER".
2. At n=0, symb='W' — the next char is 'E' (a vowel), so W is appended → code starts "W".
3. At n=2, symb='T' — regionMatch("TH") hits → appends '0'.
4. At n=3, symb='H' — previous char is 'T' which is in varson="CSPTG" → silent.
5. At n=5, symb='R' → appended.

Result: "W0R". Both hBeforeVowelIncluded and whetherEncoding are corrected to "W0R", and their comments updated to
describe the actual WH-prefix mechanics.

````

## Raw Bob output

````

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
User (1) 2026-09-26 11:39:12.471 UTC (+0.5s)

Some of your characterization tests fail against the ORIGINAL, unmodified code, which means                             
they assert behaviour the code does not have. Fix those assertions to match what the code                               
actually does (or remove a test only if its behaviour cannot be pinned deterministically).                              
Keep every passing test. Reply with the complete corrected MetaphoneCharacterizationTest in one ```java block. Keep     
every line under 100 characters.                                                                                        
                                                                                                                        
Failures:                                                                                                               
- MetaphoneCharacterizationTest.hBeforeVowelIncluded: expected: <H0R> but was: <W0R>                                    
- MetaphoneCharacterizationTest.whetherEncoding: expected: <H0R> but was: <W0R>                                         
                                                                                                                        
Your previous test class:                                                                                               
                                                                                                                        
```java                                                                                                                 
  package org.apache.commons.codec.language;                                                                            
                                                                                                                        
  import org.junit.jupiter.api.BeforeEach;                                                                              
  import org.junit.jupiter.api.Test;                                                                                    
                                                                                                                        
  import static org.junit.jupiter.api.Assertions.*;                                                                     
                                                                                                                        
  /**                                                                                                                   
   * Characterization tests for {@link Metaphone}.                                                                      
   *                                                                                                                    
   * <p>Every assertion is derived by tracing the code as written.                                                      
   * Where the code and its Javadoc disagree the code wins.</p>                                                         
   */                                                                                                                   
  class MetaphoneCharacterizationTest {                                                                                 
                                                                                                                        
      private Metaphone m;                                                                                              
                                                                                                                        
      @BeforeEach                                                                                                       
      void setUp() {                                                                                                    
          m = new Metaphone();                                                                                          
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // Boundary / degenerate inputs                                                                                   
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      @Test                                                                                                             
      void nullInputReturnsEmpty() {                                                                                    
          assertEquals("", m.metaphone(null));                                                                          
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void emptyInputReturnsEmpty() {                                                                                   
          assertEquals("", m.metaphone(""));                                                                            
      }                                                                                                                 
                                                                                                                        
      /** Single character is returned uppercased, no processing. */                                                    
      @Test                                                                                                             
      void singleUppercaseLetterIsReturnedAsIs() {                                                                      
          assertEquals("A", m.metaphone("A"));                                                                          
      }                                                                                                                 
                                                                                                                        
      /** Single lowercase character is uppercased and returned verbatim. */                                            
      @Test                                                                                                             
      void singleLowercaseLetterIsUppercased() {                                                                        
          assertEquals("Z", m.metaphone("z"));                                                                          
      }                                                                                                                 
                                                                                                                        
      /** Two-char word: initial 'A' with non-E second char keeps both chars. */                                        
      @Test                                                                                                             
      void twoCharWordAB() {                                                                                            
          assertEquals("AB", m.metaphone("AB"));                                                                        
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // Input is case-insensitive (all converted to upper before processing)                                           
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      @Test                                                                                                             
      void lowercaseInputIsNormalised() {                                                                               
          assertEquals(m.metaphone("PHONE"), m.metaphone("phone"));                                                     
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void mixedCaseInputIsNormalised() {                                                                               
          assertEquals(m.metaphone("SMITH"), m.metaphone("SmItH"));                                                     
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // Initial two-character special cases                                                                            
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      /**                                                                                                               
       * Initial AE: the 'A' is dropped; processing starts at 'E'.                                                      
       * The leading vowel rule then adds 'E' to the code.                                                              
       */                                                                                                               
      @Test                                                                                                             
      void initialAEDropsA() {                                                                                          
          assertEquals("E", m.metaphone("AE"));                                                                         
      }                                                                                                                 
                                                                                                                        
      /** Initial KN: the 'K' is dropped. */                                                                            
      @Test                                                                                                             
      void initialKNDropsK() {                                                                                          
          assertEquals("N", m.metaphone("KN"));                                                                         
      }                                                                                                                 
                                                                                                                        
      /** Initial GN: the 'G' is dropped. */                                                                            
      @Test                                                                                                             
      void initialGNDropsG() {                                                                                          
          assertEquals("N", m.metaphone("GN"));                                                                         
      }                                                                                                                 
                                                                                                                        
      /** Initial PN: the 'P' is dropped (same switch arm as KN). */                                                    
      @Test                                                                                                             
      void initialPNDropsP() {                                                                                          
          assertEquals("N", m.metaphone("PN"));                                                                         
      }                                                                                                                 
                                                                                                                        
      /** Initial WR: the 'W' is dropped; processing starts at 'R'. */                                                  
      @Test                                                                                                             
      void initialWRDropsW() {                                                                                          
          assertEquals("R", m.metaphone("WR"));                                                                         
      }                                                                                                                 
                                                                                                                        
      /**                                                                                                               
       * Initial WH: the 'H' is replaced with 'W' in the local buffer.                                                  
       * Then 'W' in the loop is silent when not followed by a vowel                                                    
       * (the buffer is only "W", length 1, so isLastChar is true → no append).                                         
       */                                                                                                               
      @Test                                                                                                             
      void initialWHProducesEmpty() {                                                                                   
          assertEquals("", m.metaphone("WH"));                                                                          
      }                                                                                                                 
                                                                                                                        
      /**                                                                                                               
       * Initial W followed by a vowel (not R or H): 'W' is kept because                                                
       * the next character is a vowel.                                                                                 
       */                                                                                                               
      @Test                                                                                                             
      void initialWFollowedByVowelKeptW() {                                                                             
          assertEquals("W", m.metaphone("WA"));                                                                         
      }                                                                                                                 
                                                                                                                        
      /** Initial X is rewritten to 'S' before processing. */                                                           
      @Test                                                                                                             
      void initialXBecomesS() {                                                                                         
          assertEquals("S", m.metaphone("XA"));                                                                         
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // Vowels: only leading vowel is encoded                                                                          
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      /**                                                                                                               
       * Leading vowel is included; subsequent vowels are silent.                                                       
       * "OCEAN" → O(leading), C→S, E(silent), A(silent), N                                                             
       */                                                                                                               
      @Test                                                                                                             
      void onlyLeadingVowelEncoded() {                                                                                  
          assertEquals("OSN", m.metaphone("OCEAN"));                                                                    
      }                                                                                                                 
                                                                                                                        
      /** No leading vowel → no vowel in code. */                                                                       
      @Test                                                                                                             
      void noLeadingVowelNoVowelInCode() {                                                                              
          String code = m.metaphone("SMITH");                                                                           
          assertFalse(code.contains("A") || code.contains("E")                                                          
                  || code.contains("I") || code.contains("O")                                                           
                  || code.contains("U"),                                                                                
                  "No vowel expected in SMITH metaphone");                                                              
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // Consonant rules — individual cases                                                                             
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      /** PH → F */                                                                                                     
      @Test                                                                                                             
      void phBecomesF() {                                                                                               
          assertEquals("FN", m.metaphone("PHONE"));                                                                     
      }                                                                                                                 
                                                                                                                        
      /** TH → 0 (digit zero, representing theta). */                                                                   
      @Test                                                                                                             
      void thBecomesZero() {                                                                                            
          assertEquals("SM0", m.metaphone("SMITH"));                                                                    
          assertEquals("0MS", m.metaphone("THOMAS"));                                                                   
      }                                                                                                                 
                                                                                                                        
      /** V → F */                                                                                                      
      @Test                                                                                                             
      void vBecomesF() {                                                                                                
          // VACATION: V→F, A silent, C→K, A silent, TIO→X, N                                                           
          assertEquals("FKXN", m.metaphone("VACATION"));                                                                
      }                                                                                                                 
                                                                                                                        
      /** Q → K */                                                                                                      
      @Test                                                                                                             
      void qBecomesK() {                                                                                                
          // QUICK: Q→K, U silent, I silent, C→K, K after C is dropped                                                  
          assertEquals("KK", m.metaphone("QUICK"));                                                                     
      }                                                                                                                 
                                                                                                                        
      /** Z → S */                                                                                                      
      @Test                                                                                                             
      void zBecomesS() {                                                                                                
          // CZAR: C→K (default), Z→S, A silent, R                                                                      
          assertEquals("KSR", m.metaphone("CZAR"));                                                                     
      }                                                                                                                 
                                                                                                                        
      /** X (non-initial) → KS */                                                                                       
      @Test                                                                                                             
      void nonInitialXBecomesKS() {                                                                                     
          // XAVIER: initial X→S, then A silent, V→F, I silent, E silent, R                                             
          assertEquals("SFR", m.metaphone("XAVIER"));                                                                   
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // B: silent after M at end of word (-MB)                                                                         
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      @Test                                                                                                             
      void silentBAfterMAtEndOfWord() {                                                                                 
          assertEquals("LM", m.metaphone("LIMB"));                                                                      
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void silentBAtEndOfBOMB() {                                                                                       
          assertEquals("BM", m.metaphone("BOMB"));                                                                      
      }                                                                                                                 
                                                                                                                        
      /** B at start of word is NOT silent. */                                                                          
      @Test                                                                                                             
      void bAtStartIsNotSilent() {                                                                                      
          assertTrue(m.metaphone("BOMB").startsWith("B"));                                                              
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // C: many special cases                                                                                          
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      /** SCI / SCE / SCY: C is silent. */                                                                              
      @Test                                                                                                             
      void sciSilentC() {                                                                                               
          // SCIENCE: S, [C silent because SCI], I silent, E silent, N, C→S, E silent                                   
          assertEquals("SNS", m.metaphone("SCIENCE"));                                                                  
      }                                                                                                                 
                                                                                                                        
      /** CIA → X */                                                                                                    
      @Test                                                                                                             
      void ciaBecomesX() {                                                                                              
          // SPECIAL: S, P, E silent, CIA→X, I silent, A silent, L                                                      
          assertEquals("SPXL", m.metaphone("SPECIAL"));                                                                 
      }                                                                                                                 
                                                                                                                        
      /** CE/CI/CY → S */                                                                                               
      @Test                                                                                                             
      void ceBecomesS() {                                                                                               
          // OCEAN: O(leading), CE→S, A silent, N                                                                       
          assertEquals("OSN", m.metaphone("OCEAN"));                                                                    
      }                                                                                                                 
                                                                                                                        
      /** SCH → K */                                                                                                    
      @Test                                                                                                             
      void schBecomesK() {                                                                                              
          // SCHOOL: S, SCH→K, [H silent after C], OO(dup O silent), L                                                  
          assertEquals("SKL", m.metaphone("SCHOOL"));                                                                   
      }                                                                                                                 
                                                                                                                        
      /** CH at word start followed by vowel (consonant context) → K */                                                 
      @Test                                                                                                             
      void initialChBeforeVowelBecomesK() {                                                                             
          // CHEMISTRY: CH→K (initial, vowel at pos 2), E silent, M, S, T → KMST                                        
          assertEquals("KMST", m.metaphone("CHEMISTRY"));                                                               
      }                                                                                                                 
                                                                                                                        
      /** CH in non-initial position → X */                                                                             
      @Test                                                                                                             
      void nonInitialChBecomesX() {                                                                                     
          // BACH: B, A silent, CH→X, H(terminal)silent                                                                 
          assertEquals("BX", m.metaphone("BACH"));                                                                      
      }                                                                                                                 
                                                                                                                        
      /** Initial CH + vowel at pos 2: K (consonant form) */                                                            
      @Test                                                                                                             
      void chorusInitialCh() {                                                                                          
          // CHORUS: CH→K, O silent, R, U silent, S                                                                     
          assertEquals("KRS", m.metaphone("CHORUS"));                                                                   
      }                                                                                                                 
                                                                                                                        
      /** C → K when not followed by front vowel or H. */                                                               
      @Test                                                                                                             
      void defaultCBecomesK() {                                                                                         
          // CZAR: C→K (Z is not a front vowel)                                                                         
          assertEquals("KSR", m.metaphone("CZAR"));                                                                     
      }                                                                                                                 
                                                                                                                        
      /** Two consecutive C's: each processed independently (C exempt from dup rule). */                                
      @Test                                                                                                             
      void doubleCNotDeduped() {                                                                                        
          // ACCOMPLISH: A(leading), CC→KK, O silent, M → AKKM                                                          
          assertEquals("AKKM", m.metaphone("ACCOMPLISH"));                                                              
      }                                                                                                                 
                                                                                                                        
      /** CC before E: first C→K, second C→S (CE rule). */                                                              
      @Test                                                                                                             
      void acceptCcBeforeE() {                                                                                          
          // ACCEPT: A, C→K, C→S(CE), E silent, P, T → loop exits at length 4 → AKSP                                    
          assertEquals("AKSP", m.metaphone("ACCEPT"));                                                                  
      }                                                                                                                 
                                                                                                                        
      /** SUCCEED: S, C→K, C→S(CE), doubled E deduped, D→T */                                                           
      @Test                                                                                                             
      void succeedEncoding() {                                                                                          
          assertEquals("SKST", m.metaphone("SUCCEED"));                                                                 
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // D: DGE/DGI/DGY → J                                                                                             
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      @Test                                                                                                             
      void dgeBecomesJ() {                                                                                              
          // JUDGE: J, U silent, DGE→J → JJ                                                                             
          assertEquals("JJ", m.metaphone("JUDGE"));                                                                     
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void edgeLeadingVowelThenDge() {                                                                                  
          // EDGE: E(leading), DGE→J → EJ                                                                               
          assertEquals("EJ", m.metaphone("EDGE"));                                                                      
      }                                                                                                                 
                                                                                                                        
      /** D not followed by GE/GI/GY → T */                                                                             
      @Test                                                                                                             
      void defaultDBecomesT() {                                                                                         
          // DISCUSS: D→T, I silent, S, C→K (after S but not SCI), U silent, S, S(dup)                                  
          assertEquals("TSKS", m.metaphone("DISCUSS"));                                                                 
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // G: many silent conditions                                                                                      
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      /** GH at end of word is silent. */                                                                               
      @Test                                                                                                             
      void finalGHIsSilent() {                                                                                          
          // LAUGH: L, A silent, U silent, GH(terminal)silent, H(terminal)silent                                        
          assertEquals("L", m.metaphone("LAUGH"));                                                                      
      }                                                                                                                 
                                                                                                                        
      /** GH before consonant is silent. */                                                                             
      @Test                                                                                                             
      void ghBeforeConsonantIsSilent() {                                                                                
          // NIGHT: N, I silent, GH(before T)silent, H silent, T                                                        
          assertEquals("NT", m.metaphone("NIGHT"));                                                                     
      }                                                                                                                 
                                                                                                                        
      /** GN in middle of word: G is silent. */                                                                         
      @Test                                                                                                             
      void gnInMiddleGSilent() {                                                                                        
          // SIGN: S, I silent, GN→silent G, N                                                                          
          assertEquals("SN", m.metaphone("SIGN"));                                                                      
      }                                                                                                                 
                                                                                                                        
      /** GN at end of word: G is silent. */                                                                            
      @Test                                                                                                             
      void gnAtEndGSilent() {                                                                                           
          // DESIGN: D→T, E silent, S, I silent, GN→silent G, N                                                         
          assertEquals("TSN", m.metaphone("DESIGN"));                                                                   
      }                                                                                                                 
                                                                                                                        
      /** Initial GN drops G (initial-two-char rule). */                                                                
      @Test                                                                                                             
      void initialGNDropsGViaInitialRule() {                                                                            
          // GNASH: GN→N(initial drop), A silent, SH→X, H(terminal)silent                                               
          assertEquals("NX", m.metaphone("GNASH"));                                                                     
      }                                                                                                                 
                                                                                                                        
      /** GE/GI/GY not after GG → J */                                                                                  
      @Test                                                                                                             
      void geBecomesJ() {                                                                                               
          // AEGEAN: AE→E(initial), G before E → J, E silent, A silent, N                                               
          assertEquals("EJN", m.metaphone("AEGEAN"));                                                                   
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // H: silent after CSPTG or at end; voiced before vowel                                                           
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      /** Terminal H is silent. */                                                                                      
      @Test                                                                                                             
      void terminalHIsSilent() {                                                                                        
          // LAUGH → L (GH and terminal H both silent)                                                                  
          String code = m.metaphone("LAUGH");                                                                           
          assertFalse(code.contains("H"), "Terminal H must not appear in code");                                        
      }                                                                                                                 
                                                                                                                        
      /** H after varson chars (C S P T G) is silent. */                                                                
      @Test                                                                                                             
      void hAfterVarsonIsSilent() {                                                                                     
          // PHONE: P, H(after P = varson)silent, O silent, N → FN                                                      
          assertEquals("FN", m.metaphone("PHONE"));                                                                     
      }                                                                                                                 
                                                                                                                        
      /** H before a vowel and not after varson → included. */                                                          
      @Test                                                                                                             
      void hBeforeVowelIncluded() {                                                                                     
          // WHETHER: W(before H not vowel→silent), H(before E, not after varson)→H,                                    
          //          E silent, TH→0, H(after T=varson)silent, E silent, R                                              
          assertEquals("H0R", m.metaphone("WHETHER"));                                                                  
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // K: silent after C                                                                                              
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      @Test                                                                                                             
      void kAfterCIsSilent() {                                                                                          
          // QUICK: Q→K, U silent, I silent, C→K, K(after C)silent                                                      
          assertEquals("KK", m.metaphone("QUICK"));                                                                     
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void initialKIsKept() {                                                                                           
          // KNIGHT: KN→N (initial rule), I silent, GH silent, H silent, T → NT                                         
          assertEquals("NT", m.metaphone("KNIGHT"));                                                                    
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // S: SH / SIO / SIA → X                                                                                          
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      @Test                                                                                                             
      void shBecomesX() {                                                                                               
          // PHISH: PH→F, I silent, SH→X, H(terminal)silent                                                             
          assertEquals("FX", m.metaphone("PHISH"));                                                                     
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void sioBecomesX() {                                                                                              
          // PASSION: P, A silent, S, S(dup)silent, I silent, O silent, N → PSN                                         
          // Note: SIO check is at position 2 ("SSI") which does NOT match "SIO" → S appended                           
          assertEquals("PSN", m.metaphone("PASSION"));                                                                  
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void sessionDoubleS() {                                                                                           
          // SESSION: S, E silent, S(not dup at pos 2), S(dup at pos 3)silent,                                          
          //          I silent, O silent, N → SSN                                                                       
          assertEquals("SSN", m.metaphone("SESSION"));                                                                  
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // T: TIA/TIO → X; TCH silent; TH → 0                                                                             
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      @Test                                                                                                             
      void tioBecomesX() {                                                                                              
          // NATION: N, A silent, TIO→X, N → NXN                                                                        
          assertEquals("NXN", m.metaphone("NATION"));                                                                   
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void tiaBecomesX() {                                                                                              
          // no convenient word, use PARTIAL: check TIA via PARTIAL path                                                
          // Use direct word "TIARA": T→X(TIA), R, A silent → "XR"                                                      
          assertEquals("XR", m.metaphone("TIARA"));                                                                     
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void thBecomesZeroInThomas() {                                                                                    
          assertEquals("0MS", m.metaphone("THOMAS"));                                                                   
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void wrightEncodesGhSilentAndTh() {                                                                               
          // WR→R (initial), I silent, GH(before T)silent, H(after varson G)silent, T                                   
          assertEquals("RT", m.metaphone("WRIGHT"));                                                                    
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // W and Y: silent unless followed by a vowel                                                                     
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      @Test                                                                                                             
      void wNotFollowedByVowelIsSilent() {                                                                              
          // WH → "" (W becomes the only char but has no following vowel)                                               
          assertEquals("", m.metaphone("WH"));                                                                          
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void wFollowedByVowelIsKept() {                                                                                   
          assertEquals("W", m.metaphone("WA"));                                                                         
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // Duplicate letter suppression (all letters except C)                                                            
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      @Test                                                                                                             
      void duplicateNonCLetterSuppressed() {                                                                            
          // OOZE: O(leading,n=0), O(dup)skip, Z→S, E silent → "OS"                                                     
          assertEquals("OS", m.metaphone("OOZE"));                                                                      
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void duplicateCIsNotSuppressed() {                                                                                
          // ACCOMPLISH shows two C's both processed → AKKM                                                             
          assertEquals("AKKM", m.metaphone("ACCOMPLISH"));                                                              
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // maxCodeLen property                                                                                            
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      @Test                                                                                                             
      void defaultMaxCodeLenIsFour() {                                                                                  
          assertEquals(4, m.getMaxCodeLen());                                                                           
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void maxCodeLenTruncatesOutput() {                                                                                
          // PTARMIGAN without truncation would be PTRM (exactly 4) — confirm                                           
          assertEquals("PTRM", m.metaphone("PTARMIGAN"));                                                               
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void setMaxCodeLenOne() {                                                                                         
          m.setMaxCodeLen(1);                                                                                           
          assertEquals("S", m.metaphone("SMITH"));                                                                      
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void setMaxCodeLenZeroReturnsEmpty() {                                                                            
          m.setMaxCodeLen(0);                                                                                           
          assertEquals("", m.metaphone("SMITH"));                                                                       
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void setMaxCodeLenRoundtrip() {                                                                                   
          m.setMaxCodeLen(6);                                                                                           
          assertEquals(6, m.getMaxCodeLen());                                                                           
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // encode(String) delegates to metaphone                                                                          
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      @Test                                                                                                             
      void encodeStringDelegatesToMetaphone() {                                                                         
          assertEquals(m.metaphone("SMITH"), m.encode("SMITH"));                                                        
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // encode(Object) — type checking                                                                                 
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      @Test                                                                                                             
      void encodeObjectWithStringSucceeds() throws Exception {                                                          
          assertEquals("SM0", m.encode((Object) "SMITH"));                                                              
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void encodeObjectWithNonStringThrows() {                                                                          
          assertThrows(org.apache.commons.codec.EncoderException.class,                                                 
                  () -> m.encode((Object) Integer.valueOf(42)));                                                        
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void encodeObjectExceptionMessageDescriptive() {                                                                  
          org.apache.commons.codec.EncoderException ex =                                                                
                  assertThrows(org.apache.commons.codec.EncoderException.class,                                         
                          () -> m.encode((Object) Boolean.TRUE));                                                       
          assertTrue(ex.getMessage().contains("Metaphone"),                                                             
                  "Exception message should mention Metaphone");                                                        
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // isMetaphoneEqual                                                                                               
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      @Test                                                                                                             
      void isMetaphoneEqualSameWord() {                                                                                 
          assertTrue(m.isMetaphoneEqual("SMITH", "SMITH"));                                                             
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void isMetaphoneEqualKnightNight() {                                                                              
          // Both encode to "NT"                                                                                        
          assertTrue(m.isMetaphoneEqual("KNIGHT", "NIGHT"));                                                            
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void isMetaphoneEqualCzarTsar() {                                                                                 
          // CZAR→KSR, TSAR→TSR — different                                                                             
          assertFalse(m.isMetaphoneEqual("CZAR", "TSAR"));                                                              
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void isMetaphoneEqualPhoneAndFone() {                                                                             
          // PHONE→FN, FONE→FN                                                                                          
          assertTrue(m.isMetaphoneEqual("PHONE", "FONE"));                                                              
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // Specific word encodings (regression pins)                                                                      
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      @Test                                                                                                             
      void smithEncoding() {                                                                                            
          assertEquals("SM0", m.metaphone("SMITH"));                                                                    
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void chemistryEncoding() {                                                                                        
          assertEquals("KMST", m.metaphone("CHEMISTRY"));                                                               
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void jumpEncoding() {                                                                                             
          assertEquals("JMP", m.metaphone("JUMP"));                                                                     
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void specialEncoding() {                                                                                          
          assertEquals("SPXL", m.metaphone("SPECIAL"));                                                                 
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void chordEncoding() {                                                                                            
          // CHORD: CH→K(initial+vowel), O silent, R, D→T                                                               
          assertEquals("KRT", m.metaphone("CHORD"));                                                                    
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void chorusEncoding() {                                                                                           
          assertEquals("KRS", m.metaphone("CHORUS"));                                                                   
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void schoolEncoding() {                                                                                           
          assertEquals("SKL", m.metaphone("SCHOOL"));                                                                   
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void laughEncoding() {                                                                                            
          assertEquals("L", m.metaphone("LAUGH"));                                                                      
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void nightEncoding() {                                                                                            
          assertEquals("NT", m.metaphone("NIGHT"));                                                                     
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void knightEncoding() {                                                                                           
          assertEquals("NT", m.metaphone("KNIGHT"));                                                                    
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void gnashEncoding() {                                                                                            
          assertEquals("NX", m.metaphone("GNASH"));                                                                     
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void judgeEncoding() {                                                                                            
          assertEquals("JJ", m.metaphone("JUDGE"));                                                                     
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void edgeEncoding() {                                                                                             
          assertEquals("EJ", m.metaphone("EDGE"));                                                                      
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void discussEncoding() {                                                                                          
          assertEquals("TSKS", m.metaphone("DISCUSS"));                                                                 
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void succeedEncoding2() {                                                                                         
          assertEquals("SKST", m.metaphone("SUCCEED"));                                                                 
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void whetherEncoding() {                                                                                          
          assertEquals("H0R", m.metaphone("WHETHER"));                                                                  
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void signEncoding() {                                                                                             
          assertEquals("SN", m.metaphone("SIGN"));                                                                      
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void designEncoding() {                                                                                           
          assertEquals("TSN", m.metaphone("DESIGN"));                                                                   
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void nationEncoding() {                                                                                           
          assertEquals("NXN", m.metaphone("NATION"));                                                                   
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void vacationEncoding() {                                                                                         
          assertEquals("FKXN", m.metaphone("VACATION"));                                                                
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void aegeanEncoding() {                                                                                           
          assertEquals("EJN", m.metaphone("AEGEAN"));                                                                   
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void wrightEncoding() {                                                                                           
          assertEquals("RT", m.metaphone("WRIGHT"));                                                                    
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void xavierEncoding() {                                                                                           
          assertEquals("SFR", m.metaphone("XAVIER"));                                                                   
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void acceptEncoding() {                                                                                           
          assertEquals("AKSP", m.metaphone("ACCEPT"));                                                                  
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void bachEncoding() {                                                                                             
          assertEquals("BX", m.metaphone("BACH"));                                                                      
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void ptarmiganEncoding() {                                                                                        
          assertEquals("PTRM", m.metaphone("PTARMIGAN"));                                                               
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void czarEncoding() {                                                                                             
          assertEquals("KSR", m.metaphone("CZAR"));                                                                     
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void tsarEncoding() {                                                                                             
          assertEquals("TSR", m.metaphone("TSAR"));                                                                     
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void phishEncoding() {                                                                                            
          assertEquals("FX", m.metaphone("PHISH"));                                                                     
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void scienceEncoding() {                                                                                          
          assertEquals("SNS", m.metaphone("SCIENCE"));                                                                  
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void accomplishEncoding() {                                                                                       
          assertEquals("AKKM", m.metaphone("ACCOMPLISH"));                                                              
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void quickEncoding() {                                                                                            
          assertEquals("KK", m.metaphone("QUICK"));                                                                     
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void thomasEncoding() {                                                                                           
          assertEquals("0MS", m.metaphone("THOMAS"));                                                                   
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void passionEncoding() {                                                                                          
          assertEquals("PSN", m.metaphone("PASSION"));                                                                  
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void sessionEncoding() {                                                                                          
          assertEquals("SSN", m.metaphone("SESSION"));                                                                  
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void bombEncoding() {                                                                                             
          assertEquals("BM", m.metaphone("BOMB"));                                                                      
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void limbEncoding() {                                                                                             
          assertEquals("LM", m.metaphone("LIMB"));                                                                      
      }                                                                                                                 
  }                                                                                                                     
                                                                                                                        
```                                                                                                                     
                                                                                                                        
The original code:                                                                                                      
                                                                                                                        
```java                                                                                                                 
  /*                                                                                                                    
   * Copyright 2001-2004 The Apache Software Foundation.                                                                
   *                                                                                                                    
   * Licensed under the Apache License, Version 2.0 (the "License");                                                    
   * you may not use this file except in compliance with the License.                                                   
   * You may obtain a copy of the License at                                                                            
   *                                                                                                                    
   *      http://www.apache.org/licenses/LICENSE-2.0                                                                    
   *                                                                                                                    
   * Unless required by applicable law or agreed to in writing, software                                                
   * distributed under the License is distributed on an "AS IS" BASIS,                                                  
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.                                           
   * See the License for the specific language governing permissions and                                                
   * limitations under the License.                                                                                     
   */                                                                                                                   
                                                                                                                        
  package org.apache.commons.codec.language;                                                                            
                                                                                                                        
  import org.apache.commons.codec.EncoderException;                                                                     
  import org.apache.commons.codec.StringEncoder;                                                                        
                                                                                                                        
  /**                                                                                                                   
   * Encodes a string into a metaphone value.                                                                           
   * <p>                                                                                                                
   * Initial Java implementation by <CITE>William B. Brogden. December, 1997</CITE>.                                    
   * Permission given by <CITE>wbrogden</CITE> for code to be used anywhere.                                            
   * </p>                                                                                                               
   * <p>                                                                                                                
   * <CITE>Hanging on the Metaphone</CITE> by <CITE>Lawrence Philips</CITE> in <CITE>Computer Language of Dec. 1990, p  
   * 39.</CITE>                                                                                                         
   * </p>                                                                                                               
   *                                                                                                                    
   * @author Apache Software Foundation                                                                                 
   * @version $Id: Metaphone.java,v 1.20 2004/06/05 18:32:04 ggregory Exp $                                             
   */                                                                                                                   
  public class Metaphone implements StringEncoder {                                                                     
                                                                                                                        
      /**                                                                                                               
       * Five values in the English language                                                                            
       */                                                                                                               
      private String vowels = "AEIOU" ;                                                                                 
                                                                                                                        
      /**                                                                                                               
       * Variable used in Metaphone algorithm                                                                           
       */                                                                                                               
      private String frontv = "EIY"   ;                                                                                 
                                                                                                                        
      /**                                                                                                               
       * Variable used in Metaphone algorithm                                                                           
       */                                                                                                               
      private String varson = "CSPTG" ;                                                                                 
                                                                                                                        
      /**                                                                                                               
       * The max code length for metaphone is 4                                                                         
       */                                                                                                               
      private int maxCodeLen = 4 ;                                                                                      
                                                                                                                        
      /**                                                                                                               
       * Creates an instance of the Metaphone encoder                                                                   
       */                                                                                                               
      public Metaphone() {                                                                                              
          super();                                                                                                      
      }                                                                                                                 
                                                                                                                        
      /**                                                                                                               
       * Find the metaphone value of a String. This is similar to the                                                   
       * soundex algorithm, but better at finding similar sounding words.                                               
       * All input is converted to upper case.                                                                          
       * Limitations: Input format is expected to be a single ASCII word                                                
       * with only characters in the A - Z range, no punctuation or numbers.                                            
       *                                                                                                                
       * @param txt String to find the metaphone code for                                                               
       * @return A metaphone code corresponding to the String supplied                                                  
       */                                                                                                               
      public String metaphone(String txt) {                                                                             
          boolean hard = false ;                                                                                        
          if ((txt == null) || (txt.length() == 0)) {                                                                   
              return "" ;                                                                                               
          }                                                                                                             
          // single character is itself                                                                                 
          if (txt.length() == 1) {                                                                                      
              return txt.toUpperCase() ;                                                                                
          }                                                                                                             
                                                                                                                        
          char[] inwd = txt.toUpperCase().toCharArray() ;                                                               
                                                                                                                        
          StringBuffer local = new StringBuffer(40); // manipulate                                                      
          StringBuffer code = new StringBuffer(10) ; //   output                                                        
          // handle initial 2 characters exceptions                                                                     
          switch(inwd[0]) {                                                                                             
          case 'K' :                                                                                                    
          case 'G' :                                                                                                    
          case 'P' : /* looking for KN, etc*/                                                                           
              if (inwd[1] == 'N') {                                                                                     
                  local.append(inwd, 1, inwd.length - 1);                                                               
              } else {                                                                                                  
                  local.append(inwd);                                                                                   
              }                                                                                                         
              break;                                                                                                    
          case 'A': /* looking for AE */                                                                                
              if (inwd[1] == 'E') {                                                                                     
                  local.append(inwd, 1, inwd.length - 1);                                                               
              } else {                                                                                                  
                  local.append(inwd);                                                                                   
              }                                                                                                         
              break;                                                                                                    
          case 'W' : /* looking for WR or WH */                                                                         
              if (inwd[1] == 'R') {   // WR -> R                                                                        
                  local.append(inwd, 1, inwd.length - 1);                                                               
                  break ;                                                                                               
              }                                                                                                         
              if (inwd[1] == 'H') {                                                                                     
                  local.append(inwd, 1, inwd.length - 1);                                                               
                  local.setCharAt(0, 'W'); // WH -> W                                                                   
              } else {                                                                                                  
                  local.append(inwd);                                                                                   
              }                                                                                                         
              break;                                                                                                    
          case 'X' : /* initial X becomes S */                                                                          
              inwd[0] = 'S';                                                                                            
              local.append(inwd);                                                                                       
              break ;                                                                                                   
          default :                                                                                                     
              local.append(inwd);                                                                                       
          } // now local has working string with initials fixed                                                         
                                                                                                                        
          int wdsz = local.length();                                                                                    
          int n = 0 ;                                                                                                   
                                                                                                                        
          while ((code.length() < this.getMaxCodeLen()) &&                                                              
                (n < wdsz) ) { // max code size of 4 works well                                                         
              char symb = local.charAt(n) ;                                                                             
              // remove duplicate letters except C                                                                      
              if ((symb != 'C') && (isPreviousChar( local, n, symb )) ) {                                               
                  n++ ;                                                                                                 
              } else { // not dup                                                                                       
                  switch(symb) {                                                                                        
                  case 'A' : case 'E' : case 'I' : case 'O' : case 'U' :                                                
                      if (n == 0) {                                                                                     
                          code.append(symb);                                                                            
                      }                                                                                                 
                      break ; // only use vowel if leading char                                                         
                  case 'B' :                                                                                            
                      if ( isPreviousChar(local, n, 'M') &&                                                             
                           isLastChar(wdsz, n) ) { // B is silent if word ends in MB                                    
                    break;                                                                                              
                      }                                                                                                 
                      code.append(symb);                                                                                
                      break;                                                                                            
                  case 'C' : // lots of C special cases                                                                 
                      /* discard if SCI, SCE or SCY */                                                                  
                      if ( isPreviousChar(local, n, 'S') &&                                                             
                           !isLastChar(wdsz, n) &&                                                                      
                           (this.frontv.indexOf(local.charAt(n + 1)) >= 0) ) {                                          
                          break;                                                                                        
                      }                                                                                                 
                      if (regionMatch(local, n, "CIA")) { // "CIA" -> X                                                 
                          code.append('X');                                                                             
                          break;                                                                                        
                      }                                                                                                 
                      if (!isLastChar(wdsz, n) &&                                                                       
                          (this.frontv.indexOf(local.charAt(n + 1)) >= 0)) {                                            
                          code.append('S');                                                                             
                          break; // CI,CE,CY -> S                                                                       
                      }                                                                                                 
                      if (isPreviousChar(local, n, 'S') &&                                                              
                    isNextChar(local, n, 'H') ) { // SCH->sk                                                            
                          code.append('K') ;                                                                            
                          break ;                                                                                       
                      }                                                                                                 
                      if (isNextChar(local, n, 'H')) { // detect CH                                                     
                          if ((n == 0) &&                                                                               
                             (wdsz >= 3) &&                                                                             
                              isVowel(local,2) ) { // CH consonant -> K consonant                                       
                              code.append('K');                                                                         
                          } else {                                                                                      
                              code.append('X'); // CHvowel -> X                                                         
                          }                                                                                             
                      } else {                                                                                          
                          code.append('K');                                                                             
                      }                                                                                                 
                      break ;                                                                                           
                  case 'D' :                                                                                            
                      if (!isLastChar(wdsz, n + 1) &&                                                                   
                          isNextChar(local, n, 'G') &&                                                                  
                          (this.frontv.indexOf(local.charAt(n + 2)) >= 0)) { // DGE DGI DGY -> J                        
                          code.append('J'); n += 2 ;                                                                    
                      } else {                                                                                          
                          code.append('T');                                                                             
                      }                                                                                                 
                      break ;                                                                                           
                  case 'G' : // GH silent at end or before consonant                                                    
                      if (isLastChar(wdsz, n + 1) &&                                                                    
                          isNextChar(local, n, 'H')) {                                                                  
                          break;                                                                                        
                      }                                                                                                 
                      if (!isLastChar(wdsz, n + 1) &&                                                                   
                          isNextChar(local,n,'H') &&                                                                    
                          !isVowel(local,n+2)) {                                                                        
                          break;                                                                                        
                      }                                                                                                 
                      if ((n > 0) &&                                                                                    
                         ( regionMatch(local, n, "GN") ||                                                               
                       regionMatch(local, n, "GNED") ) ) {                                                              
                          break; // silent G                                                                            
                      }                                                                                                 
                      if (isPreviousChar(local, n, 'G')) {                                                              
                          hard = true ;                                                                                 
                      } else {                                                                                          
                          hard = false ;                                                                                
                      }                                                                                                 
                      if (!isLastChar(wdsz, n) &&                                                                       
                          (this.frontv.indexOf(local.charAt(n + 1)) >= 0) &&                                            
                          (!hard)) {                                                                                    
                          code.append('J');                                                                             
                      } else {                                                                                          
                          code.append('K');                                                                             
                      }                                                                                                 
                      break ;                                                                                           
                  case 'H':                                                                                             
                      if (isLastChar(wdsz, n)) {                                                                        
                          break ; // terminal H                                                                         
                      }                                                                                                 
                      if ((n > 0) &&                                                                                    
                          (this.varson.indexOf(local.charAt(n - 1)) >= 0)) {                                            
                          break;                                                                                        
                      }                                                                                                 
                      if (isVowel(local,n+1)) {                                                                         
                          code.append('H'); // Hvowel                                                                   
                      }                                                                                                 
                      break;                                                                                            
                  case 'F':                                                                                             
                  case 'J' :                                                                                            
                  case 'L' :                                                                                            
                  case 'M':                                                                                             
                  case 'N' :                                                                                            
                  case 'R' :                                                                                            
                      code.append(symb);                                                                                
                      break;                                                                                            
                  case 'K' :                                                                                            
                      if (n > 0) { // not initial                                                                       
                          if (!isPreviousChar(local, n, 'C')) {                                                         
                              code.append(symb);                                                                        
                          }                                                                                             
                      } else {                                                                                          
                          code.append(symb); // initial K                                                               
                      }                                                                                                 
                      break ;                                                                                           
                  case 'P' :                                                                                            
                      if (isNextChar(local,n,'H')) {                                                                    
                          // PH -> F                                                                                    
                          code.append('F');                                                                             
                      } else {                                                                                          
                          code.append(symb);                                                                            
                      }                                                                                                 
                      break ;                                                                                           
                  case 'Q' :                                                                                            
                      code.append('K');                                                                                 
                      break;                                                                                            
                  case 'S' :                                                                                            
                      if (regionMatch(local,n,"SH") ||                                                                  
                     regionMatch(local,n,"SIO") ||                                                                      
                     regionMatch(local,n,"SIA")) {                                                                      
                          code.append('X');                                                                             
                      } else {                                                                                          
                          code.append('S');                                                                             
                      }                                                                                                 
                      break;                                                                                            
                  case 'T' :                                                                                            
                      if (regionMatch(local,n,"TIA") ||                                                                 
                    regionMatch(local,n,"TIO")) {                                                                       
                          code.append('X');                                                                             
                          break;                                                                                        
                      }                                                                                                 
                      if (regionMatch(local,n,"TCH")) {                                                                 
                    // Silent if in "TCH"                                                                               
                          break;                                                                                        
                      }                                                                                                 
                      // substitute numeral 0 for TH (resembles theta after all)                                        
                      if (regionMatch(local,n,"TH")) {                                                                  
                          code.append('0');                                                                             
                      } else {                                                                                          
                          code.append('T');                                                                             
                      }                                                                                                 
                      break ;                                                                                           
                  case 'V' :                                                                                            
                      code.append('F'); break ;                                                                         
                  case 'W' : case 'Y' : // silent if not followed by vowel                                              
                      if (!isLastChar(wdsz,n) &&                                                                        
                         isVowel(local,n+1)) {                                                                          
                          code.append(symb);                                                                            
                      }                                                                                                 
                      break ;                                                                                           
                  case 'X' :                                                                                            
                      code.append('K'); code.append('S');                                                               
                      break ;                                                                                           
                  case 'Z' :                                                                                            
                      code.append('S'); break ;                                                                         
                  } // end switch                                                                                       
                  n++ ;                                                                                                 
              } // end else from symb != 'C'                                                                            
              if (code.length() > this.getMaxCodeLen()) {                                                               
                 code.setLength(this.getMaxCodeLen());                                                                  
              }                                                                                                         
          }                                                                                                             
          return code.toString();                                                                                       
      }                                                                                                                 
                                                                                                                        
     private boolean isVowel(StringBuffer string, int index) {                                                          
        return (this.vowels.indexOf(string.charAt(index)) >= 0);                                                        
     }                                                                                                                  
                                                                                                                        
     private boolean isPreviousChar(StringBuffer string, int index, char c) {                                           
        boolean matches = false;                                                                                        
        if( index > 0 &&                                                                                                
            index < string.length() ) {                                                                                 
           matches = string.charAt(index - 1) == c;                                                                     
        }                                                                                                               
        return matches;                                                                                                 
     }                                                                                                                  
                                                                                                                        
     private boolean isNextChar(StringBuffer string, int index, char c) {                                               
        boolean matches = false;                                                                                        
        if( index >= 0 &&                                                                                               
            index < string.length() - 1 ) {                                                                             
           matches = string.charAt(index + 1) == c;                                                                     
        }                                                                                                               
        return matches;                                                                                                 
     }                                                                                                                  
                                                                                                                        
     private boolean regionMatch(StringBuffer string, int index, String test) {                                         
        boolean matches = false;                                                                                        
        if( index >= 0 &&                                                                                               
            (index + test.length() - 1) < string.length() ) {                                                           
           String substring = string.substring( index, index + test.length());                                          
           matches = substring.equals( test );                                                                          
        }                                                                                                               
        return matches;                                                                                                 
     }                                                                                                                  
                                                                                                                        
     private boolean isLastChar(int wdsz, int n) {                                                                      
        return n + 1 == wdsz;                                                                                           
     }                                                                                                                  
                                                                                                                        
                                                                                                                        
      /**                                                                                                               
       * Encodes an Object using the metaphone algorithm.  This method                                                  
       * is provided in order to satisfy the requirements of the                                                        
       * Encoder interface, and will throw an EncoderException if the                                                   
       * supplied object is not of type java.lang.String.                                                               
       *                                                                                                                
       * @param pObject Object to encode                                                                                
       * @return An object (or type java.lang.String) containing the                                                    
       *         metaphone code which corresponds to the String supplied.                                               
       * @throws EncoderException if the parameter supplied is not                                                      
       *                          of type java.lang.String                                                              
       */                                                                                                               
      public Object encode(Object pObject) throws EncoderException {                                                    
          if (!(pObject instanceof java.lang.String)) {                                                                 
              throw new EncoderException("Parameter supplied to Metaphone encode is not of type java.lang.String");     
          }                                                                                                             
          return metaphone((String) pObject);                                                                           
      }                                                                                                                 
                                                                                                                        
      /**                                                                                                               
       * Encodes a String using the Metaphone algorithm.                                                                
       *                                                                                                                
       * @param pString String object to encode                                                                         
       * @return The metaphone code corresponding to the String supplied                                                
       */                                                                                                               
      public String encode(String pString) {                                                                            
          return metaphone(pString);                                                                                    
      }                                                                                                                 
                                                                                                                        
      /**                                                                                                               
       * Tests is the metaphones of two strings are identical.                                                          
       *                                                                                                                
       * @param str1 First of two strings to compare                                                                    
       * @param str2 Second of two strings to compare                                                                   
       * @return true if the metaphones of these strings are identical,                                                 
       *         false otherwise.                                                                                       
       */                                                                                                               
      public boolean isMetaphoneEqual(String str1, String str2) {                                                       
          return metaphone(str1).equals(metaphone(str2));                                                               
      }                                                                                                                 
                                                                                                                        
      /**                                                                                                               
       * Returns the maxCodeLen.                                                                                        
       * @return int                                                                                                    
       */                                                                                                               
      public int getMaxCodeLen() { return this.maxCodeLen; }                                                            
                                                                                                                        
      /**                                                                                                               
       * Sets the maxCodeLen.                                                                                           
       * @param maxCodeLen The maxCodeLen to set                                                                        
       */                                                                                                               
      public void setMaxCodeLen(int maxCodeLen) { this.maxCodeLen = maxCodeLen; }                                       
                                                                                                                        
  }                                                                                                                     
                                                                                                                        
```                                                                                                                     

Starting subagent: general
   Trace the Metaphone algorithm on the string "WHETHER" using this exact Java code:

```java
public String metaphone(String txt) {
    boolean hard = false;
    if ((txt == null) || (txt.length() == 0)) { return ""; }
    if (txt.length() == 1) { return txt.toUpperCase(); }

    char[] inwd = txt.toUpperCase().toCharArray();
    StringBuffer local = new StringBuffer(40);
    StringBuffer code = new StringBuffer(10);

    switch(inwd[0]) {
    case 'W': /* looking for WR or WH */
        if (inwd[1] == 'R') {
            local.append(inwd, 1, inwd.length - 1);
            break;
        }
        if (inwd[1] == 'H') {
            local.append(inwd, 1, inwd.length - 1);
            local.setCharAt(0, 'W'); // WH -> W
        } else {
            local.append(inwd);
        }
        break;
    // ... default: local.append(inwd)
    }
    // now local has working string with initials fixed
    int wdsz = local.length();
    int n = 0;
    // maxCodeLen = 4
    while ((code.length() < 4) && (n < wdsz)) {
        char symb = local.charAt(n);
        if ((symb != 'C') && isPreviousChar(local, n, symb)) {
            n++;
        } else {
            switch(symb) {
            // ... vowels: only at n==0
            // W / Y: silent if not followed by vowel
            case 'W': case 'Y':
                if (!isLastChar(wdsz, n) && isVowel(local, n+1)) {
                    code.append(symb);
                }
                break;
            case 'H':
                if (isLastChar(wdsz, n)) { break; } // terminal H
                if ((n > 0) && (varson.indexOf(local.charAt(n-1)) >= 0)) { break; }
                if (isVowel(local, n+1)) { code.append('H'); }
                break;
            case 'T':
                if (regionMatch(local, n, "TIA") || regionMatch(local, n, "TIO")) {
                    code.append('X'); break;
                }
                if (regionMatch(local, n, "TCH")) { break; }
                if (regionMatch(local, n, "TH")) {
                    code.append('0');
                } else {
                    code.append('T');
                }
                break;
            case 'R': code.append('R'); break;
            // vowels A E I O U: only at n==0
            }
            n++;
        }
    }
    return code.toString();
}
```

Input: "WHETHER"
Step 1: inwd = ['W','H','E','T','H','E','R']
Step 2: Initial switch on inwd[0]='W': inwd[1]='H', so:
  local.append(inwd, 1, inwd.length - 1) → appends chars at index 1..6 → "HETHER"
  local.setCharAt(0, 'W') → local = "WETHER"
  
  Wait - local.append(inwd, 1, inwd.length-1): this is StringBuffer.append(char[], offset, len) where offset=1, len=inwd.length-1=6.
  So it appends chars inwd[1], inwd[2], ..., inwd[6] = H,E,T,H,E,R → "HETHER"
  Then setCharAt(0, 'W') → "WETHER"

Step 3: wdsz = 6, local = "WETHER" = [W,E,T,H,E,R] at indices 0,1,2,3,4,5

Now trace the while loop:
n=0, symb='W': not dup (n=0, isPreviousChar returns false). Case W/Y: isLastChar(6,0)? 0+1==6? No. isVowel(local,1)? local.charAt(1)='E', yes vowel. → code.append('W'). n=1. code="W"

n=1, symb='E': not dup (prev is W≠E). Case vowel: n==0? No. → no append. n=2. code="W"

n=2, symb='T': not dup. Case T: regionMatch("WETHER",2,"TIA")? chars 2,3,4="THE"? No. regionMatch("WETHER",2,"TIO")? No. regionMatch("WETHER",2,"TCH")? No. regionMatch("WETHER",2,"TH")? local.substring(2,4)="TH"? local="WETHER", chars: W(0)E(1)T(2)H(3)E(4)R(5). "TH" = chars at 2,3 = T,H = "TH". Yes! → code.append('0'). n=3. code="W0"

n=3, symb='H': not dup. Case H: isLastChar(6,3)? 3+1==6? No. n>0 and varson.indexOf(local.charAt(2))? local.charAt(2)='T', varson="CSPTG", indexOf('T')=3 ≥ 0. → break (silent). n=4. code="W0"

n=4, symb='E': isPreviousChar? prev=local.charAt(3)='H'≠'E'. not dup. Case vowel: n==0? No. n=5. code="W0"

n=5, symb='R': not dup. code.append('R'). n=6. code="W0R"

Result: "W0R"

So WHETHER encodes to "W0R", not "H0R".

Please confirm this trace and report the final result.


Subagent completed | 11.7s | 0 tool call(s) | 0.028


────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Assistant (1) 2026-09-26 11:39:14.453 UTC (+2.5s)

Let me trace the WHETHER encoding through the code carefully.                                                           

Tool calls:
- spawn_subagent

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Tool (1) 2026-09-26 11:39:42.642 UTC (+30.7s) Success

Tool: spawn_subagent
Args:
- description: Trace the Metaphone algorithm on the string "WHETHER" using this exact Java code:

```java
public String metaphone(St...


────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Assistant (2) 2026-09-26 11:39:44.702 UTC (+32.8s)

The actual encoding is W0R. The two failing tests both assert H0R — that's wrong. The fix is to change both             
hBeforeVowelIncluded and whetherEncoding to expect W0R, and update the inline comment to explain the real WH-prefix     
behaviour.                                                                                                              
                                                                                                                        
```java                                                                                                                 
  package org.apache.commons.codec.language;                                                                            
                                                                                                                        
  import org.junit.jupiter.api.BeforeEach;                                                                              
  import org.junit.jupiter.api.Test;                                                                                    
                                                                                                                        
  import static org.junit.jupiter.api.Assertions.*;                                                                     
                                                                                                                        
  /**                                                                                                                   
   * Characterization tests for {@link Metaphone}.                                                                      
   *                                                                                                                    
   * <p>Every assertion is derived by tracing the code as written.                                                      
   * Where the code and its Javadoc disagree the code wins.</p>                                                         
   */                                                                                                                   
  class MetaphoneCharacterizationTest {                                                                                 
                                                                                                                        
      private Metaphone m;                                                                                              
                                                                                                                        
      @BeforeEach                                                                                                       
      void setUp() {                                                                                                    
          m = new Metaphone();                                                                                          
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // Boundary / degenerate inputs                                                                                   
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      @Test                                                                                                             
      void nullInputReturnsEmpty() {                                                                                    
          assertEquals("", m.metaphone(null));                                                                          
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void emptyInputReturnsEmpty() {                                                                                   
          assertEquals("", m.metaphone(""));                                                                            
      }                                                                                                                 
                                                                                                                        
      /** Single character is returned uppercased, no processing. */                                                    
      @Test                                                                                                             
      void singleUppercaseLetterIsReturnedAsIs() {                                                                      
          assertEquals("A", m.metaphone("A"));                                                                          
      }                                                                                                                 
                                                                                                                        
      /** Single lowercase character is uppercased and returned verbatim. */                                            
      @Test                                                                                                             
      void singleLowercaseLetterIsUppercased() {                                                                        
          assertEquals("Z", m.metaphone("z"));                                                                          
      }                                                                                                                 
                                                                                                                        
      /** Two-char word: initial 'A' with non-E second char keeps both chars. */                                        
      @Test                                                                                                             
      void twoCharWordAB() {                                                                                            
          assertEquals("AB", m.metaphone("AB"));                                                                        
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // Input is case-insensitive (all converted to upper before processing)                                           
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      @Test                                                                                                             
      void lowercaseInputIsNormalised() {                                                                               
          assertEquals(m.metaphone("PHONE"), m.metaphone("phone"));                                                     
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void mixedCaseInputIsNormalised() {                                                                               
          assertEquals(m.metaphone("SMITH"), m.metaphone("SmItH"));                                                     
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // Initial two-character special cases                                                                            
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      /**                                                                                                               
       * Initial AE: the 'A' is dropped; processing starts at 'E'.                                                      
       * The leading vowel rule then adds 'E' to the code.                                                              
       */                                                                                                               
      @Test                                                                                                             
      void initialAEDropsA() {                                                                                          
          assertEquals("E", m.metaphone("AE"));                                                                         
      }                                                                                                                 
                                                                                                                        
      /** Initial KN: the 'K' is dropped. */                                                                            
      @Test                                                                                                             
      void initialKNDropsK() {                                                                                          
          assertEquals("N", m.metaphone("KN"));                                                                         
      }                                                                                                                 
                                                                                                                        
      /** Initial GN: the 'G' is dropped. */                                                                            
      @Test                                                                                                             
      void initialGNDropsG() {                                                                                          
          assertEquals("N", m.metaphone("GN"));                                                                         
      }                                                                                                                 
                                                                                                                        
      /** Initial PN: the 'P' is dropped (same switch arm as KN). */                                                    
      @Test                                                                                                             
      void initialPNDropsP() {                                                                                          
          assertEquals("N", m.metaphone("PN"));                                                                         
      }                                                                                                                 
                                                                                                                        
      /** Initial WR: the 'W' is dropped; processing starts at 'R'. */                                                  
      @Test                                                                                                             
      void initialWRDropsW() {                                                                                          
          assertEquals("R", m.metaphone("WR"));                                                                         
      }                                                                                                                 
                                                                                                                        
      /**                                                                                                               
       * Initial WH: the code rewrites WH to a single 'W' in the local buffer.                                          
       * 'W' in the loop is only kept when followed by a vowel; here the buffer                                         
       * is only "W" (length 1), so isLastChar is true and nothing is appended.                                         
       */                                                                                                               
      @Test                                                                                                             
      void initialWHProducesEmpty() {                                                                                   
          assertEquals("", m.metaphone("WH"));                                                                          
      }                                                                                                                 
                                                                                                                        
      /**                                                                                                               
       * Initial W followed by a vowel (not R or H): 'W' is kept because                                                
       * the next character is a vowel.                                                                                 
       */                                                                                                               
      @Test                                                                                                             
      void initialWFollowedByVowelKeptW() {                                                                             
          assertEquals("W", m.metaphone("WA"));                                                                         
      }                                                                                                                 
                                                                                                                        
      /** Initial X is rewritten to 'S' before processing. */                                                           
      @Test                                                                                                             
      void initialXBecomesS() {                                                                                         
          assertEquals("S", m.metaphone("XA"));                                                                         
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // Vowels: only leading vowel is encoded                                                                          
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      /**                                                                                                               
       * Leading vowel is included; subsequent vowels are silent.                                                       
       * "OCEAN" → O(leading), C→S, E(silent), A(silent), N                                                             
       */                                                                                                               
      @Test                                                                                                             
      void onlyLeadingVowelEncoded() {                                                                                  
          assertEquals("OSN", m.metaphone("OCEAN"));                                                                    
      }                                                                                                                 
                                                                                                                        
      /** No leading vowel → no vowel in code. */                                                                       
      @Test                                                                                                             
      void noLeadingVowelNoVowelInCode() {                                                                              
          String code = m.metaphone("SMITH");                                                                           
          assertFalse(code.contains("A") || code.contains("E")                                                          
                  || code.contains("I") || code.contains("O")                                                           
                  || code.contains("U"),                                                                                
                  "No vowel expected in SMITH metaphone");                                                              
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // Consonant rules — individual cases                                                                             
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      /** PH → F */                                                                                                     
      @Test                                                                                                             
      void phBecomesF() {                                                                                               
          assertEquals("FN", m.metaphone("PHONE"));                                                                     
      }                                                                                                                 
                                                                                                                        
      /** TH → 0 (digit zero, representing theta). */                                                                   
      @Test                                                                                                             
      void thBecomesZero() {                                                                                            
          assertEquals("SM0", m.metaphone("SMITH"));                                                                    
          assertEquals("0MS", m.metaphone("THOMAS"));                                                                   
      }                                                                                                                 
                                                                                                                        
      /** V → F */                                                                                                      
      @Test                                                                                                             
      void vBecomesF() {                                                                                                
          // VACATION: V→F, A silent, C→K, A silent, TIO→X, N                                                           
          assertEquals("FKXN", m.metaphone("VACATION"));                                                                
      }                                                                                                                 
                                                                                                                        
      /** Q → K */                                                                                                      
      @Test                                                                                                             
      void qBecomesK() {                                                                                                
          // QUICK: Q→K, U silent, I silent, C→K, K after C is dropped                                                  
          assertEquals("KK", m.metaphone("QUICK"));                                                                     
      }                                                                                                                 
                                                                                                                        
      /** Z → S */                                                                                                      
      @Test                                                                                                             
      void zBecomesS() {                                                                                                
          // CZAR: C→K (default), Z→S, A silent, R                                                                      
          assertEquals("KSR", m.metaphone("CZAR"));                                                                     
      }                                                                                                                 
                                                                                                                        
      /** X (non-initial) → KS */                                                                                       
      @Test                                                                                                             
      void nonInitialXBecomesKS() {                                                                                     
          // XAVIER: initial X→S, then A silent, V→F, I silent, E silent, R                                             
          assertEquals("SFR", m.metaphone("XAVIER"));                                                                   
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // B: silent after M at end of word (-MB)                                                                         
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      @Test                                                                                                             
      void silentBAfterMAtEndOfWord() {                                                                                 
          assertEquals("LM", m.metaphone("LIMB"));                                                                      
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void silentBAtEndOfBOMB() {                                                                                       
          assertEquals("BM", m.metaphone("BOMB"));                                                                      
      }                                                                                                                 
                                                                                                                        
      /** B at start of word is NOT silent. */                                                                          
      @Test                                                                                                             
      void bAtStartIsNotSilent() {                                                                                      
          assertTrue(m.metaphone("BOMB").startsWith("B"));                                                              
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // C: many special cases                                                                                          
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      /** SCI / SCE / SCY: C is silent. */                                                                              
      @Test                                                                                                             
      void sciSilentC() {                                                                                               
          // SCIENCE: S, [C silent because SCI], I silent, E silent, N, C→S, E silent                                   
          assertEquals("SNS", m.metaphone("SCIENCE"));                                                                  
      }                                                                                                                 
                                                                                                                        
      /** CIA → X */                                                                                                    
      @Test                                                                                                             
      void ciaBecomesX() {                                                                                              
          // SPECIAL: S, P, E silent, CIA→X, I silent, A silent, L                                                      
          assertEquals("SPXL", m.metaphone("SPECIAL"));                                                                 
      }                                                                                                                 
                                                                                                                        
      /** CE/CI/CY → S */                                                                                               
      @Test                                                                                                             
      void ceBecomesS() {                                                                                               
          // OCEAN: O(leading), CE→S, A silent, N                                                                       
          assertEquals("OSN", m.metaphone("OCEAN"));                                                                    
      }                                                                                                                 
                                                                                                                        
      /** SCH → K */                                                                                                    
      @Test                                                                                                             
      void schBecomesK() {                                                                                              
          // SCHOOL: S, SCH→K, [H silent after C], OO(dup O silent), L                                                  
          assertEquals("SKL", m.metaphone("SCHOOL"));                                                                   
      }                                                                                                                 
                                                                                                                        
      /** CH at word start followed by vowel (consonant context) → K */                                                 
      @Test                                                                                                             
      void initialChBeforeVowelBecomesK() {                                                                             
          // CHEMISTRY: CH→K (initial, vowel at pos 2), E silent, M, S, T → KMST                                        
          assertEquals("KMST", m.metaphone("CHEMISTRY"));                                                               
      }                                                                                                                 
                                                                                                                        
      /** CH in non-initial position → X */                                                                             
      @Test                                                                                                             
      void nonInitialChBecomesX() {                                                                                     
          // BACH: B, A silent, CH→X, H(terminal)silent                                                                 
          assertEquals("BX", m.metaphone("BACH"));                                                                      
      }                                                                                                                 
                                                                                                                        
      /** Initial CH + vowel at pos 2: K (consonant form) */                                                            
      @Test                                                                                                             
      void chorusInitialCh() {                                                                                          
          // CHORUS: CH→K, O silent, R, U silent, S                                                                     
          assertEquals("KRS", m.metaphone("CHORUS"));                                                                   
      }                                                                                                                 
                                                                                                                        
      /** C → K when not followed by front vowel or H. */                                                               
      @Test                                                                                                             
      void defaultCBecomesK() {                                                                                         
          // CZAR: C→K (Z is not a front vowel)                                                                         
          assertEquals("KSR", m.metaphone("CZAR"));                                                                     
      }                                                                                                                 
                                                                                                                        
      /** Two consecutive C's: each processed independently (C exempt from dup rule). */                                
      @Test                                                                                                             
      void doubleCNotDeduped() {                                                                                        
          // ACCOMPLISH: A(leading), CC→KK, O silent, M → AKKM                                                          
          assertEquals("AKKM", m.metaphone("ACCOMPLISH"));                                                              
      }                                                                                                                 
                                                                                                                        
      /** CC before E: first C→K, second C→S (CE rule). */                                                              
      @Test                                                                                                             
      void acceptCcBeforeE() {                                                                                          
          // ACCEPT: A, C→K, C→S(CE), E silent, P, T → loop exits at length 4 → AKSP                                    
          assertEquals("AKSP", m.metaphone("ACCEPT"));                                                                  
      }                                                                                                                 
                                                                                                                        
      /** SUCCEED: S, C→K, C→S(CE), doubled E deduped, D→T */                                                           
      @Test                                                                                                             
      void succeedEncoding() {                                                                                          
          assertEquals("SKST", m.metaphone("SUCCEED"));                                                                 
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // D: DGE/DGI/DGY → J                                                                                             
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      @Test                                                                                                             
      void dgeBecomesJ() {                                                                                              
          // JUDGE: J, U silent, DGE→J → JJ                                                                             
          assertEquals("JJ", m.metaphone("JUDGE"));                                                                     
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void edgeLeadingVowelThenDge() {                                                                                  
          // EDGE: E(leading), DGE→J → EJ                                                                               
          assertEquals("EJ", m.metaphone("EDGE"));                                                                      
      }                                                                                                                 
                                                                                                                        
      /** D not followed by GE/GI/GY → T */                                                                             
      @Test                                                                                                             
      void defaultDBecomesT() {                                                                                         
          // DISCUSS: D→T, I silent, S, C→K (after S but not SCI), U silent, S, S(dup)                                  
          assertEquals("TSKS", m.metaphone("DISCUSS"));                                                                 
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // G: many silent conditions                                                                                      
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      /** GH at end of word is silent. */                                                                               
      @Test                                                                                                             
      void finalGHIsSilent() {                                                                                          
          // LAUGH: L, A silent, U silent, GH(terminal)silent, H(terminal)silent                                        
          assertEquals("L", m.metaphone("LAUGH"));                                                                      
      }                                                                                                                 
                                                                                                                        
      /** GH before consonant is silent. */                                                                             
      @Test                                                                                                             
      void ghBeforeConsonantIsSilent() {                                                                                
          // NIGHT: N, I silent, GH(before T)silent, H silent, T                                                        
          assertEquals("NT", m.metaphone("NIGHT"));                                                                     
      }                                                                                                                 
                                                                                                                        
      /** GN in middle of word: G is silent. */                                                                         
      @Test                                                                                                             
      void gnInMiddleGSilent() {                                                                                        
          // SIGN: S, I silent, GN→silent G, N                                                                          
          assertEquals("SN", m.metaphone("SIGN"));                                                                      
      }                                                                                                                 
                                                                                                                        
      /** GN at end of word: G is silent. */                                                                            
      @Test                                                                                                             
      void gnAtEndGSilent() {                                                                                           
          // DESIGN: D→T, E silent, S, I silent, GN→silent G, N                                                         
          assertEquals("TSN", m.metaphone("DESIGN"));                                                                   
      }                                                                                                                 
                                                                                                                        
      /** Initial GN drops G (initial-two-char rule). */                                                                
      @Test                                                                                                             
      void initialGNDropsGViaInitialRule() {                                                                            
          // GNASH: GN→N(initial drop), A silent, SH→X, H(terminal)silent                                               
          assertEquals("NX", m.metaphone("GNASH"));                                                                     
      }                                                                                                                 
                                                                                                                        
      /** GE/GI/GY not after GG → J */                                                                                  
      @Test                                                                                                             
      void geBecomesJ() {                                                                                               
          // AEGEAN: AE→E(initial), G before E → J, E silent, A silent, N                                               
          assertEquals("EJN", m.metaphone("AEGEAN"));                                                                   
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // H: silent after CSPTG or at end; voiced before vowel                                                           
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      /** Terminal H is silent. */                                                                                      
      @Test                                                                                                             
      void terminalHIsSilent() {                                                                                        
          // LAUGH → L (GH and terminal H both silent)                                                                  
          String code = m.metaphone("LAUGH");                                                                           
          assertFalse(code.contains("H"), "Terminal H must not appear in code");                                        
      }                                                                                                                 
                                                                                                                        
      /** H after varson chars (C S P T G) is silent. */                                                                
      @Test                                                                                                             
      void hAfterVarsonIsSilent() {                                                                                     
          // PHONE: P, H(after P = varson)silent, O silent, N → FN                                                      
          assertEquals("FN", m.metaphone("PHONE"));                                                                     
      }                                                                                                                 
                                                                                                                        
      /**                                                                                                               
       * WHETHER: initial WH rewrites the buffer to "WETHER".                                                           
       * W is kept (followed by vowel E), TH→0, H(after T=varson)silent, R.                                             
       * Result is "W0R".                                                                                               
       */                                                                                                               
      @Test                                                                                                             
      void hBeforeVowelIncluded() {                                                                                     
          assertEquals("W0R", m.metaphone("WHETHER"));                                                                  
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // K: silent after C                                                                                              
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      @Test                                                                                                             
      void kAfterCIsSilent() {                                                                                          
          // QUICK: Q→K, U silent, I silent, C→K, K(after C)silent                                                      
          assertEquals("KK", m.metaphone("QUICK"));                                                                     
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void initialKIsKept() {                                                                                           
          // KNIGHT: KN→N (initial rule), I silent, GH silent, H silent, T → NT                                         
          assertEquals("NT", m.metaphone("KNIGHT"));                                                                    
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // S: SH / SIO / SIA → X                                                                                          
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      @Test                                                                                                             
      void shBecomesX() {                                                                                               
          // PHISH: PH→F, I silent, SH→X, H(terminal)silent                                                             
          assertEquals("FX", m.metaphone("PHISH"));                                                                     
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void sioBecomesX() {                                                                                              
          // PASSION: P, A silent, S, S(dup)silent, I silent, O silent, N → PSN                                         
          // Note: SIO check is at position 2 ("SSI") which does NOT match "SIO" → S appended                           
          assertEquals("PSN", m.metaphone("PASSION"));                                                                  
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void sessionDoubleS() {                                                                                           
          // SESSION: S, E silent, S(not dup at pos 2), S(dup at pos 3)silent,                                          
          //          I silent, O silent, N → SSN                                                                       
          assertEquals("SSN", m.metaphone("SESSION"));                                                                  
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // T: TIA/TIO → X; TCH silent; TH → 0                                                                             
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      @Test                                                                                                             
      void tioBecomesX() {                                                                                              
          // NATION: N, A silent, TIO→X, N → NXN                                                                        
          assertEquals("NXN", m.metaphone("NATION"));                                                                   
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void tiaBecomesX() {                                                                                              
          // Use direct word "TIARA": T→X(TIA), R, A silent → "XR"                                                      
          assertEquals("XR", m.metaphone("TIARA"));                                                                     
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void thBecomesZeroInThomas() {                                                                                    
          assertEquals("0MS", m.metaphone("THOMAS"));                                                                   
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void wrightEncodesGhSilentAndTh() {                                                                               
          // WR→R (initial), I silent, GH(before T)silent, H(after varson G)silent, T                                   
          assertEquals("RT", m.metaphone("WRIGHT"));                                                                    
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // W and Y: silent unless followed by a vowel                                                                     
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      @Test                                                                                                             
      void wNotFollowedByVowelIsSilent() {                                                                              
          // WH → "" (W becomes the only char but has no following vowel)                                               
          assertEquals("", m.metaphone("WH"));                                                                          
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void wFollowedByVowelIsKept() {                                                                                   
          assertEquals("W", m.metaphone("WA"));                                                                         
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // Duplicate letter suppression (all letters except C)                                                            
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      @Test                                                                                                             
      void duplicateNonCLetterSuppressed() {                                                                            
          // OOZE: O(leading,n=0), O(dup)skip, Z→S, E silent → "OS"                                                     
          assertEquals("OS", m.metaphone("OOZE"));                                                                      
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void duplicateCIsNotSuppressed() {                                                                                
          // ACCOMPLISH shows two C's both processed → AKKM                                                             
          assertEquals("AKKM", m.metaphone("ACCOMPLISH"));                                                              
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // maxCodeLen property                                                                                            
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      @Test                                                                                                             
      void defaultMaxCodeLenIsFour() {                                                                                  
          assertEquals(4, m.getMaxCodeLen());                                                                           
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void maxCodeLenTruncatesOutput() {                                                                                
          // PTARMIGAN without truncation would be PTRM (exactly 4) — confirm                                           
          assertEquals("PTRM", m.metaphone("PTARMIGAN"));                                                               
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void setMaxCodeLenOne() {                                                                                         
          m.setMaxCodeLen(1);                                                                                           
          assertEquals("S", m.metaphone("SMITH"));                                                                      
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void setMaxCodeLenZeroReturnsEmpty() {                                                                            
          m.setMaxCodeLen(0);                                                                                           
          assertEquals("", m.metaphone("SMITH"));                                                                       
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void setMaxCodeLenRoundtrip() {                                                                                   
          m.setMaxCodeLen(6);                                                                                           
          assertEquals(6, m.getMaxCodeLen());                                                                           
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // encode(String) delegates to metaphone                                                                          
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      @Test                                                                                                             
      void encodeStringDelegatesToMetaphone() {                                                                         
          assertEquals(m.metaphone("SMITH"), m.encode("SMITH"));                                                        
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // encode(Object) — type checking                                                                                 
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      @Test                                                                                                             
      void encodeObjectWithStringSucceeds() throws Exception {                                                          
          assertEquals("SM0", m.encode((Object) "SMITH"));                                                              
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void encodeObjectWithNonStringThrows() {                                                                          
          assertThrows(org.apache.commons.codec.EncoderException.class,                                                 
                  () -> m.encode((Object) Integer.valueOf(42)));                                                        
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void encodeObjectExceptionMessageDescriptive() {                                                                  
          org.apache.commons.codec.EncoderException ex =                                                                
                  assertThrows(org.apache.commons.codec.EncoderException.class,                                         
                          () -> m.encode((Object) Boolean.TRUE));                                                       
          assertTrue(ex.getMessage().contains("Metaphone"),                                                             
                  "Exception message should mention Metaphone");                                                        
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // isMetaphoneEqual                                                                                               
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      @Test                                                                                                             
      void isMetaphoneEqualSameWord() {                                                                                 
          assertTrue(m.isMetaphoneEqual("SMITH", "SMITH"));                                                             
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void isMetaphoneEqualKnightNight() {                                                                              
          // Both encode to "NT"                                                                                        
          assertTrue(m.isMetaphoneEqual("KNIGHT", "NIGHT"));                                                            
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void isMetaphoneEqualCzarTsar() {                                                                                 
          // CZAR→KSR, TSAR→TSR — different                                                                             
          assertFalse(m.isMetaphoneEqual("CZAR", "TSAR"));                                                              
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void isMetaphoneEqualPhoneAndFone() {                                                                             
          // PHONE→FN, FONE→FN                                                                                          
          assertTrue(m.isMetaphoneEqual("PHONE", "FONE"));                                                              
      }                                                                                                                 
                                                                                                                        
      // -----------------------------------------------------------------------                                        
      // Specific word encodings (regression pins)                                                                      
      // -----------------------------------------------------------------------                                        
                                                                                                                        
      @Test                                                                                                             
      void smithEncoding() {                                                                                            
          assertEquals("SM0", m.metaphone("SMITH"));                                                                    
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void chemistryEncoding() {                                                                                        
          assertEquals("KMST", m.metaphone("CHEMISTRY"));                                                               
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void jumpEncoding() {                                                                                             
          assertEquals("JMP", m.metaphone("JUMP"));                                                                     
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void specialEncoding() {                                                                                          
          assertEquals("SPXL", m.metaphone("SPECIAL"));                                                                 
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void chordEncoding() {                                                                                            
          // CHORD: CH→K(initial+vowel), O silent, R, D→T                                                               
          assertEquals("KRT", m.metaphone("CHORD"));                                                                    
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void chorusEncoding() {                                                                                           
          assertEquals("KRS", m.metaphone("CHORUS"));                                                                   
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void schoolEncoding() {                                                                                           
          assertEquals("SKL", m.metaphone("SCHOOL"));                                                                   
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void laughEncoding() {                                                                                            
          assertEquals("L", m.metaphone("LAUGH"));                                                                      
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void nightEncoding() {                                                                                            
          assertEquals("NT", m.metaphone("NIGHT"));                                                                     
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void knightEncoding() {                                                                                           
          assertEquals("NT", m.metaphone("KNIGHT"));                                                                    
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void gnashEncoding() {                                                                                            
          assertEquals("NX", m.metaphone("GNASH"));                                                                     
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void judgeEncoding() {                                                                                            
          assertEquals("JJ", m.metaphone("JUDGE"));                                                                     
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void edgeEncoding() {                                                                                             
          assertEquals("EJ", m.metaphone("EDGE"));                                                                      
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void discussEncoding() {                                                                                          
          assertEquals("TSKS", m.metaphone("DISCUSS"));                                                                 
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void succeedEncoding2() {                                                                                         
          assertEquals("SKST", m.metaphone("SUCCEED"));                                                                 
      }                                                                                                                 
                                                                                                                        
      /**                                                                                                               
       * WHETHER: WH prefix rewrites buffer to "WETHER"; W is kept (next char                                           
       * is vowel E), TH→0, second H is silent (T is a varson char), R.                                                 
       */                                                                                                               
      @Test                                                                                                             
      void whetherEncoding() {                                                                                          
          assertEquals("W0R", m.metaphone("WHETHER"));                                                                  
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void signEncoding() {                                                                                             
          assertEquals("SN", m.metaphone("SIGN"));                                                                      
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void designEncoding() {                                                                                           
          assertEquals("TSN", m.metaphone("DESIGN"));                                                                   
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void nationEncoding() {                                                                                           
          assertEquals("NXN", m.metaphone("NATION"));                                                                   
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void vacationEncoding() {                                                                                         
          assertEquals("FKXN", m.metaphone("VACATION"));                                                                
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void aegeanEncoding() {                                                                                           
          assertEquals("EJN", m.metaphone("AEGEAN"));                                                                   
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void wrightEncoding() {                                                                                           
          assertEquals("RT", m.metaphone("WRIGHT"));                                                                    
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void xavierEncoding() {                                                                                           
          assertEquals("SFR", m.metaphone("XAVIER"));                                                                   
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void acceptEncoding() {                                                                                           
          assertEquals("AKSP", m.metaphone("ACCEPT"));                                                                  
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void bachEncoding() {                                                                                             
          assertEquals("BX", m.metaphone("BACH"));                                                                      
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void ptarmiganEncoding() {                                                                                        
          assertEquals("PTRM", m.metaphone("PTARMIGAN"));                                                               
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void czarEncoding() {                                                                                             
          assertEquals("KSR", m.metaphone("CZAR"));                                                                     
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void tsarEncoding() {                                                                                             
          assertEquals("TSR", m.metaphone("TSAR"));                                                                     
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void phishEncoding() {                                                                                            
          assertEquals("FX", m.metaphone("PHISH"));                                                                     
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void scienceEncoding() {                                                                                          
          assertEquals("SNS", m.metaphone("SCIENCE"));                                                                  
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void accomplishEncoding() {                                                                                       
          assertEquals("AKKM", m.metaphone("ACCOMPLISH"));                                                              
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void quickEncoding() {                                                                                            
          assertEquals("KK", m.metaphone("QUICK"));                                                                     
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void thomasEncoding() {                                                                                           
          assertEquals("0MS", m.metaphone("THOMAS"));                                                                   
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void passionEncoding() {                                                                                          
          assertEquals("PSN", m.metaphone("PASSION"));                                                                  
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void sessionEncoding() {                                                                                          
          assertEquals("SSN", m.metaphone("SESSION"));                                                                  
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void bombEncoding() {                                                                                             
          assertEquals("BM", m.metaphone("BOMB"));                                                                      
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void limbEncoding() {                                                                                             
          assertEquals("LM", m.metaphone("LIMB"));                                                                      
      }                                                                                                                 
  }                                                                                                                     
```                                                                                                                     
                                                                                                                        
────────────────────────────────────────────────────────────────────────────────                                        
                                                                                                                        
What changed and why:                                                                                                   
                                                                                                                        
The two failing tests both asserted H0R for WHETHER. Tracing the code:                                                  
                                                                                                                        
1. The initial W + H branch runs local.append(inwd, 1, inwd.length-1) (copies HETHER) then local.setCharAt(0, 'W') —    
   giving local = "WETHER", not "HETHER".                                                                               
2. At n=0, symb='W' — the next char is 'E' (a vowel), so W is appended → code starts "W".                               
3. At n=2, symb='T' — regionMatch("TH") hits → appends '0'.                                                             
4. At n=3, symb='H' — previous char is 'T' which is in varson="CSPTG" → silent.                                         
5. At n=5, symb='R' → appended.                                                                                         
                                                                                                                        
Result: "W0R". Both hBeforeVowelIncluded and whetherEncoding are corrected to "W0R", and their comments updated to      
describe the actual WH-prefix mechanics.                                                                                
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

Task Summary

Total Cost:              0.149
Total Duration:          1m 45s


Assistant Messages:      2
Tool Calls:              1
Task ID:                 d733be7ac0396eee27b3293ad32b48b4

````
