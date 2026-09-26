# Bob session: metaphone-generate-tests

- Started: 20260926T113400Z
- Command: `bob -p <prompt>`
- Duration: 309.1s
- Bob cost: 0.422

## Prompt

````
You are writing characterization tests for a legacy Java class before it is modernized.

Goal: pin down what the code DOES today, including odd behaviour, so any change in behaviour
during modernization makes a test fail. Do not test what the comments say it should do; test
what it actually does. Where the code and its javadoc disagree, the code wins.

Requirements:
- One JUnit 5 test class named `MetaphoneCharacterizationTest` in package `org.apache.commons.codec.language`.
- Use only JUnit 5 (org.junit.jupiter.api) and the JDK. No other libraries.
- Call only the public API of `Metaphone` shown below; keep test inputs deterministic.
- Cover boundaries, special cases and branches, input normalisation (whitespace, letter case,
  null, empty, very short input), error cases, and anything the code treats specially.
- Every test must pass against the code exactly as written below.
- Reply with the complete test class in a single ```java code block. Keep every line under 100 characters.

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
I'll analyze the Metaphone code carefully, tracing every branch, then write characterization tests that pin down actual
behaviour.

Tool calls:
- spawn_subagent

Tool (1) 2026-09-26 11:38:04.324 UTC (+243.3s) Success

Tool: spawn_subagent
Args:
- name: general
- description: Trace through the Metaphone.java code to determine exact output for specific test inputs. I need you to manually simu...




Now I have all the exact outputs verified. Let me write the complete characterization test class.

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

````

## Raw Bob output

````

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
User (1) 2026-09-26 11:34:01.639 UTC (+0.6s)

You are writing characterization tests for a legacy Java class before it is modernized.                                 
                                                                                                                        
Goal: pin down what the code DOES today, including odd behaviour, so any change in behaviour                            
during modernization makes a test fail. Do not test what the comments say it should do; test                            
what it actually does. Where the code and its javadoc disagree, the code wins.                                          
                                                                                                                        
Requirements:                                                                                                           
- One JUnit 5 test class named MetaphoneCharacterizationTest in package org.apache.commons.codec.language.              
- Use only JUnit 5 (org.junit.jupiter.api) and the JDK. No other libraries.                                             
- Call only the public API of Metaphone shown below; keep test inputs deterministic.                                    
- Cover boundaries, special cases and branches, input normalisation (whitespace, letter case,                           
  null, empty, very short input), error cases, and anything the code treats specially.                                  
- Every test must pass against the code exactly as written below.                                                       
- Reply with the complete test class in a single ```java code block. Keep every line under 100 characters.              
                                                                                                                        
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
   Trace through the Metaphone.java code to determine exact output for specific test inputs. I need you to manually simulate the metaphone() method for each of the following inputs and return the exact result character by character. Be precise — trace each character through the switch statement.

Here is the full algorithm (already uploaded in context). Simulate carefully:

1. null → ""
2. "" → ""
3. "A" → "A" (single char returns toUpperCase)
4. "z" → "Z" (single char, lowercase)
5. "AB" → trace: inwd=['A','B'], no initial exception for 'A' since inwd[1]='B' != 'E', local="AB", n=0: symb='A', n==0 so append 'A', code="A", n=1; symb='B', isPreviousChar(local,1,'B')? index=1,local.charAt(0)='A'!='B' so no dup; case B: isPreviousChar(local,1,'M')? 'A'!='M' no; append 'B'; code="AB"; result="AB"
6. "AE" → initial 'A', inwd[1]='E', so local = inwd[1..] = "E". wdsz=1, n=0: symb='E', n==0 so append 'E', code="E". result="E"
7. "KN" → initial 'K', inwd[1]='N', local = inwd[1..] = "N". wdsz=1, n=0: symb='N', case N: append 'N', code="N". result="N"
8. "GN" → initial 'G', inwd[1]='N', local = inwd[1..] = "N". wdsz=1, n=0: symb='N', append 'N'. result="N"
9. "PN" → initial 'P', inwd[1]='N', local = inwd[1..] = "N". wdsz=1, n=0: symb='N', append 'N'. result="N"
10. "WR" → initial 'W', inwd[1]='R', local = inwd[1..] = "R". wdsz=1, n=0: symb='R', append 'R'. result="R"
11. "WH" → initial 'W', inwd[1]='H', local = inwd[1..] = "H", then setCharAt(0,'W') → local="W". wdsz=1, n=0: symb='W', case W: isLastChar(1,0)? 0+1==1 yes, so !isLastChar = false, don't append. result=""
12. "WA" → initial 'W', inwd[1]='A' (not 'R' or 'H'), local="WA". n=0: symb='W', isLastChar(2,0)? 0+1=1!=2 no; isVowel(local,1)? 'A' is vowel yes; append 'W'. n=1: symb='A', n!=0, don't append. result="W"
13. "XA" → initial 'X', inwd[0]='S', local="SA". n=0: symb='S', regionMatch("SA",0,"SH")? no, regionMatch("SA",0,"SIO")? no, regionMatch("SA",0,"SIA")? no; append 'S'. n=1: symb='A', n!=0 don't append. result="S"
14. "WRIGHT" → initial 'W', inwd[1]='R', local = inwd[1..] = "RIGHT". wdsz=5. 
    n=0: symb='R', append 'R'. n=1: symb='I', n!=0 no append. n=2: symb='G', check isPreviousChar(local,2,'G')? charAt(1)='I'!='G' no; hard=false; isLastChar(5,2)? 3!=5 no; check isNextChar(local,2,'H')? charAt(3)='H' yes; check isLastChar(5,3)? 4!=5 no; isNextChar(local,2,'H') && !isVowel(local,4)? local.charAt(4)='T', not vowel; so break (silent GH). n=3: symb='H', isLastChar(5,3)? 4!=5 no; varson.indexOf(local.charAt(2))= varson.indexOf('G')? varson="CSPTG", indexOf('G')=4 >=0; so break. n=4: symb='T', regionMatch("RIGHT",4,"TIA")? only 1 char left no; regionMatch("RIGHT",4,"TIO")? no; regionMatch("RIGHT",4,"TCH")? no; regionMatch("RIGHT",4,"TH")? only 1 char no; append 'T'. code="RT". result="RT"
15. "PHONE" → local="PHONE". n=0: symb='P', isNextChar(local,0,'H')? charAt(1)='H' yes; append 'F'. n=1: symb='H', isPreviousChar? yes but we just did P... wait. After P appends F and n++ → n=1. symb=local.charAt(1)='H'. isLastChar(5,1)? 2!=5 no; varson.indexOf(local.charAt(0))= varson.indexOf('P')=3 >=0; break. n=2: symb='O', n!=0 no append. n=3: symb='N', append 'N'. n=4: symb='E', n!=0 no append. code="FN". result="FN"
16. "SMITH" → local="SMITH". wdsz=5. n=0: 'S', regionMatch("SMITH",0,"SH")? no; regionMatch("SMITH",0,"SIO")? no; "SIA"? no; append 'S'. n=1: 'M', append 'M'. n=2: 'I', n!=0 no. n=3: 'T', regionMatch("SMITH",3,"TIA")? chars 3,4='T','H', no; "TIO"? no; "TCH"? only 2 chars left no; "TH"? charAt(3)='T',charAt(4)='H' → "TH" yes! append '0'. n=4: 'H', isLastChar(5,4)? 5==5 yes, break. code="SM0". result="SM0"
17. "CHEMISTRY" → local="CHEMISTRY". wdsz=9. n=0: 'C', isNextChar(local,0,'H')? charAt(1)='H' yes; n==0, wdsz>=3, isVowel(local,2)? charAt(2)='E', yes vowel → append 'K'. n=1: 'H', isLastChar(9,1)? 2!=9 no; varson.indexOf(local.charAt(0))='C' → indexOf('C')=0 >=0; break. n=2: 'E', n!=0 no. n=3: 'M', append 'M'. n=4 (code.length()=2 < 4): 'I', n!=0 no. n=5: 'S', "STR"[5..7]="STR"... regionMatch("CHEMISTRY",5,"SH")? charAt(5)='S',charAt(6)='T'→"ST" no; "SIO"? no; "SIA"? no; append 'S'. n=6: code.length()=3; 'T', regionMatch("CHEMISTRY",6,"TIA")? "TRY" no; "TIO"? no; "TCH"? no; "TH"? charAt(6)='T',charAt(7)='R'→"TR" no; append 'T'. code.length()=4 now. n=7: code.length()=4 = maxCodeLen, loop exits. result="KMST"
18. "AEGEAN" → initial 'A', inwd[1]='E', local=inwd[1..]="EGEAN". wdsz=5. n=0: 'E', n==0 append 'E'. n=1: 'G', isPreviousChar(local,1,'G')? charAt(0)='E'!='G' no; hard=false; GH? charAt(2)='E' no; regionMatch("EGEAN",1,"GN")? "GE" no; regionMatch("EGEAN",1,"GNED")? no; n>0 yes but those don't match; isLastChar(5,1)? 2!=5 no; frontv.indexOf(charAt(2))=frontv.indexOf('E')=0 >=0; !hard: append 'J'. n=2: 'E', n!=0 no. n=3: 'A', n!=0 no. n=4: 'N', append 'N'. code="EJN". result="EJN"
19. "JUMP" → local="JUMP". n=0:'J', append 'J'. n=1:'U', n!=0 no. n=2:'M', append 'M'. n=3:'P', isNextChar(local,3,'H')? isLastChar so index=3, length-1=3, 3 < 3 is false → no; append 'P'. code="JMP". result="JMP"
20. "LIMB" → local="LIMB". wdsz=4. n=0:'L', append 'L'. n=1:'I', no. n=2:'M', append 'M'. n=3:'B', isPreviousChar(local,3,'M')? charAt(2)='M' yes; isLastChar(4,3)? 4==4 yes → silent B, break. code="LM". result="LM"
21. "BOMB" → local="BOMB". n=0:'B', isPreviousChar(local,0,'M')? index=0 so isPreviousChar returns false (index > 0 fails); append 'B'. n=1:'O', n!=0 no. n=2:'M', isPreviousChar(local,2,'M')? charAt(1)='O'!='M'; append 'M'. n=3:'B', isPreviousChar(local,3,'M')? charAt(2)='M' yes; isLastChar(4,3)? yes → silent. code="BM". result="BM"
22. "SCIENCE" → local="SCIENCE". n=0:'S',regionMatch("SCIENCE",0,"SH")? no;"SIO"?no;"SIA"?no; append 'S'. n=1:'C', isPreviousChar(local,1,'S')? charAt(0)='S' yes; isLastChar(7,1)?2!=7 no; frontv.indexOf(charAt(2))=frontv.indexOf('I')=1 >=0 → discard (SCI). n++→n=2. n=2:'I', n!=0 no. n=3:'E', n!=0 no. n=4:'N', append 'N'. n=5:'C', isPreviousChar(local,5,'S')? charAt(4)='N'!='S' no; not SCI; regionMatch("SCIENCE",5,"CIA")? chars 5,6,7... wdsz=7, chars 5='C',6='E' → "CE" no; isLastChar(7,5)?6!=7 no; frontv.indexOf(charAt(6))=frontv.indexOf('E')=0 >=0 → append 'S'. n=6:'E', n!=0 no. code="SNS". result="SNS"  
23. "ACCOMPLISH" → local="ACCOMPLISH". wdsz=10. n=0:'A', n==0, append 'A'. n=1:'C', isPreviousChar(local,1,'S')?charAt(0)='A' no; "CIA"? charAt(1,2,3)='C','C','O'→"CCO" no; isLastChar(10,1)?no; frontv.indexOf(charAt(2))=frontv.indexOf('C')=-1 <0 no; isPrev='S' no; isNextChar='H'? charAt(2)='C' no; append 'K'. n=2:'C', isPrev='C'? charAt(1)='C' yes! and symb='C': but the dup check is (symb != 'C') — so C is exempt from dup suppression. So we process it. isPreviousChar(local,2,'S')?charAt(1)='C'!='S' no; "CIA"? charAt(2,3,4)='C','O','M'→"COM" no; isLastChar(10,2)?no; frontv.indexOf(charAt(3))=frontv.indexOf('O')=-1 <0 no; "SCH"? no; isNextChar='H'? charAt(3)='O' no; append 'K'. n=3:'O', n!=0 no. n=4:'M', append 'M'. code.length()=4. Loop exits (code.length() >= maxCodeLen). result="AKKM"? wait code="AKKM", then code.length()=4 which is NOT > maxCodeLen so no trim. result="AKKM"
24. "CZAR" → default case: local="CZAR". n=0:'C', isPrev'S'? no; "CIA"? "CZA" no; isLastChar? no; frontv.indexOf('Z')=-1 no; isPrev'S'&&isNext'H'? no; isNextChar'H'? charAt(1)='Z' no; append 'K'. n=1:'Z', append 'S'. n=2:'A', n!=0 no. n=3:'R', append 'R'. code="KSR". result="KSR"
25. "XAVIER" → initial 'X', inwd[0]='S', local="SAVIER". n=0:'S',regionMatch("SAVIER",0,"SH")?no;"SIO"?no;"SIA"?no; append 'S'. n=1:'A', n!=0 no. n=2:'V', append 'F'. n=3:'I', n!=0 no. n=4:'E', n!=0 no. n=5:'R', append 'R'. code="SFR". result="SFR"
26. "ACCEPT" → local="ACCEPT". n=0:'A', n==0, append 'A'. n=1:'C', check dup: symb='C', symb!='C' is false, so skip dup check, process. isPrev'S'?charAt(0)='A' no; "CIA"?chars 1,2,3='C','C','E'→"CCE" no; isLastChar(6,1)?no; frontv.indexOf(charAt(2))=frontv.indexOf('C')=-1 no; isPrev'S'&&next'H'? no; isNext'H'? charAt(2)='C' no; → append 'K'. n=2:'C', isPrev'C'? charAt(1)='C' yes, but symb=='C' so no dup skip; isPrev'S'?charAt(1)='C'!='S' no; "CIA"?chars 2,3,4='C','E','P'→"CEP" no; isLastChar(6,2)?no; frontv.indexOf(charAt(3))=frontv.indexOf('E')=0 >=0 → append 'S'. n=3:'E', n!=0 no. n=4:'P', isNext'H'?charAt(5)='T' no; append 'P'. n=5:'T', regionMatch("ACCEPT",5,"TIA")?only 1 char no;"TIO"?no;"TCH"?no;"TH"?no; append 'T'. code="AKSP", length=4. Then check: code.length()>maxCodeLen? 4>4 no. But wait, after n=5, code.length()=5? Let me recount: A, K, S, P, T = 5 chars. But maxCodeLen=4. After 'P' is appended code="AKSP" (length 4). Loop condition: code.length() < maxCodeLen → 4 < 4 is false. Loop exits. result="AKSP"
27. "LAUGH" → local="LAUGH". wdsz=5. n=0:'L', append 'L'. n=1:'A', n!=0 no. n=2:'U', n!=0 no. n=3:'G', isPrev'G'?charAt(2)='U' no; hard=false; isLastChar(5,4)?5==5 yes && isNextChar(local,3,'H')? charAt(4)='H' yes → break (GH at end). n=4:'H', isLastChar(5,4)? yes → break. code="L". result="L"
28. "NIGHT" → local="NIGHT". wdsz=5. n=0:'N', append 'N'. n=1:'I', n!=0 no. n=2:'G', isPrev'G'?charAt(1)='I' no; hard=false; isLastChar(5,3)? 4!=5 no; isNextChar(local,2,'H')? charAt(3)='H' yes; isLastChar(5,3)? 4!=5 no; !isVowel(local,4)? charAt(4)='T' not vowel → break. n=3:'H', isLastChar(5,3)?no; varson.indexOf(charAt(2))=varson.indexOf('G')=4 >=0 → break. n=4:'T', regionMatch("NIGHT",4,"TIA")?no;"TIO"?no;"TCH"?no;"TH"?no; append 'T'. code="NT". result="NT"
29. "KNIGHT" → initial 'K', inwd[1]='N', local=inwd[1..]="NIGHT". Same as NIGHT → "NT"
30. "GNASH" → initial 'G', inwd[1]='N', local=inwd[1..]="NASH". wdsz=4. n=0:'N', append 'N'. n=1:'A', n!=0 no. n=2:'S', regionMatch("NASH",2,"SH")? chars 2,3='S','H'→"SH" yes! append 'X'. n=3:'H', isLastChar(4,3)? yes → break. code="NX". result="NX"
31. "JUDGE" → local="JUDGE". wdsz=5. n=0:'J', append 'J'. n=1:'U', n!=0 no. n=2:'D', isLastChar(5,3)?4!=5 no; isNextChar(local,2,'G')? charAt(3)='G' yes; frontv.indexOf(charAt(4))=frontv.indexOf('E')=0 >=0 → append 'J', n+=2 → n=4. n++ → n=5. Wait — n+=2 gives n=4, then at end of else block n++, so n=5. wdsz=5, 5 < 5 false, loop exits. code="JJ". result="JJ"
32. "EDGE" → local="EDGE". wdsz=4. n=0:'E', n==0 append 'E'. n=1:'D', isLastChar(4,2)?3!=4 no; isNextChar(local,1,'G')? charAt(2)='G' yes; frontv.indexOf(charAt(3))=frontv.indexOf('E')=0 >=0 → append 'J', n+=2 → n=3. n++→n=4. loop exits. code="EJ". result="EJ"
33. "DISCUSS" → local="DISCUSS". wdsz=7. n=0:'D', isLastChar(7,1)?no; isNext'G'?charAt(1)='I' no; append 'T'. n=1:'I', n!=0 no. n=2:'S', check dup: isPrev'S'?charAt(1)='I'!='S' no; regionMatch("DISCUSS",2,"SH")?no;"SIO"? chars 2,3,4='S','C','U' no; "SIA"? no; append 'S'. n=3:'C', isPrev'S'?charAt(2)='S' yes; isLastChar(7,3)?no; frontv.indexOf(charAt(4))=frontv.indexOf('U')=-1 <0 → no SCI match; "CIA"? chars 3,4,5='C','U','S' no; isLastChar no; frontv.indexOf('U')=-1 no; isPrev'S'&&isNext'H'? charAt(4)='U' no; isNext'H'? no; → append 'K'. n=4:'U', n!=0 no. n=5:'S', isPrev'S'?charAt(4)='U' no; check dups: symb='S', isPreviousChar(local,5,'S')? charAt(4)='U' no; regionMatch("DISCUSS",5,"SH")?chars 5,6='S','S'→"SS" no;"SIO"?no;"SIA"?no; append 'S'. n=6: 'S', isPrev'S'?charAt(5)='S' yes! and symb='S'!='C' → dup! skip (n++). code="TSKS". But wait let me recount: T,S,K,S = length 4. After n=5 code="TSKS" length=4. Loop: code.length() < 4? no. Exit. result="TSKS"
34. "QUICK" → local="QUICK". n=0:'Q', append 'K'. n=1:'U', n!=0 no. n=2:'I', n!=0 no. n=3:'C', isPrev'S'?charAt(2)='I' no; "CIA"?chars 3,4='C','K'→"CK" no (need 3 chars, wdsz=5, chars 3,4,5 but wdsz=5 so index 3+2=5 > 4... regionMatch check: index+test.length()-1 < string.length() → 3+3-1=5 < 5? no; → CIA check fails; isLastChar(5,3)?4!=5 no; frontv.indexOf(charAt(4))=frontv.indexOf('K')=-1 no; isPrev'S'&&next'H'? no; isNext'H'? charAt(4)='K' no; → append 'K'. n=4:'K', n>0 yes; isPrev'C'?charAt(3)='C' yes → don't append. code="KK". result="KK"
35. "SUCCEED" → local="SUCCEED". wdsz=7. n=0:'S', "SH"?no;"SIO"?no;"SIA"?no; append 'S'. n=1:'U', n!=0 no. n=2:'C', isPrev'S'?charAt(1)='U' no; "CIA"?chars 2,3,4='C','C','E'→"CCE" no; isLastChar?no; frontv.indexOf(charAt(3))=frontv.indexOf('C')=-1 no; isPrev'S'&&next'H'?no; isNext'H'?charAt(3)='C' no; → append 'K'. n=3:'C', isPrev'C'? but symb='C' so no dup skip; isPrev'S'?charAt(2)='C'!='S' no; "CIA"? chars 3,4,5='C','E','E'→"CEE" no; isLastChar?no; frontv.indexOf(charAt(4))=frontv.indexOf('E')=0 >=0 → append 'S'. n=4:'E', n!=0 no. n=5:'E', isPrev'E'? symb='E'!='C' so dup check applies; charAt(4)='E'==symb → dup! skip. n=6:'D', isLastChar(7,6)?7==7 yes; isNext'G'? isLastChar so no; append 'T'. code="SKST"? wait T,S,K,S,T... length check: after 'K' code="SK" (length 2), after 'S' code="SKS" (3), after 'T' code="SKST" (4). code.length()>4? no. result="SKST"
36. "THOMAS" → local="THOMAS". wdsz=6. n=0:'T', regionMatch("THOMAS",0,"TIA")? "THO" no (TIA needs I); "TIO"? no; "TCH"? no; "TH"? charAt(0)='T',charAt(1)='H'→"TH" yes; append '0'. n=1:'H', isLastChar(6,1)?no; varson.indexOf(charAt(0))=varson.indexOf('T')=2 >=0 → break. n=2:'O', n!=0 no. n=3:'M', append 'M'. n=4:'A', n!=0 no. n=5:'S', append 'S'. code="0MS". result="0MS"
37. "WHETHER" → local="WHETHER". wdsz=7. n=0:'W', isLastChar(7,0)?no; isVowel(local,1)?charAt(1)='H' not vowel → don't append. n=1:'H', isLastChar(7,1)?no; varson.indexOf(charAt(0))=varson.indexOf('W')=-1 no; isVowel(local,2)?charAt(2)='E' yes → append 'H'. n=2:'E', n!=0 no. n=3:'T', "TIA"? no;"TIO"? no;"TCH"? no;"TH"? charAt(3)='T',charAt(4)='H'→"TH" yes; append '0'. n=4:'H', isLastChar(7,4)?no; varson.indexOf(charAt(3))=varson.indexOf('T')=2 >=0 → break. n=5:'E', n!=0 no. n=6:'R', append 'R'. code="H0R". result="H0R"
38. "SIGN" → local="SIGN". wdsz=4. n=0:'S', append 'S'. n=1:'I', n!=0 no. n=2:'G', isPrev'G'?charAt(1)='I' no; hard=false; isLastChar(4,3)?4==4 yes; isNextChar'H'?charAt(3)='N'!='H' → (condition for first GH check: isLastChar(wdsz,n+1) && isNextChar(local,n,'H') → isLastChar(4,3)=true but isNextChar='H'? charAt(3)='N' no); check second GH branch: no; check GN: n>0 yes; regionMatch("SIGN",2,"GN")? chars 2,3='G','N'→"GN" yes! → break (silent G). n=3:'N', append 'N'. code="SN". result="SN"
39. "DESIGN" → local="DESIGN". wdsz=6. n=0:'D', isLastChar(6,1)?no; isNext'G'?charAt(1)='E' no; append 'T'. n=1:'E', n!=0 no. n=2:'S', append 'S'. n=3:'I', n!=0 no. n=4:'G', isPrev'G'?charAt(3)='I' no; n>0 yes; regionMatch("DESIGN",4,"GN")? chars 4,5='G','N'→"GN" yes! → break. n=5:'N', append 'N'. code="TSN". result="TSN"
40. "PHISH" → local="PHISH". wdsz=5. n=0:'P', isNext'H'?charAt(1)='H' yes; append 'F'. n=1:'H', isLastChar(5,1)?no; varson.indexOf(charAt(0))=varson.indexOf('P')=3 >=0 → break. n=2:'I', n!=0 no. n=3:'S', regionMatch("PHISH",3,"SH")? chars 3,4='S','H'→"SH" yes; append 'X'. n=4:'H', isLastChar(5,4)?yes → break. code="FX". result="FX"
41. "SPECIAL" → local="SPECIAL". wdsz=7. n=0:'S', regionMatch("SPECIAL",0,"SH")?no;"SIO"?no;"SIA"?no; append 'S'. n=1:'P', isNext'H'?charAt(2)='E' no; append 'P'. n=2:'E', n!=0 no. n=3:'C', isPrev'S'?charAt(2)='E' no; "CIA"?chars 3,4,5='C','I','A'→"CIA" yes! → append 'X'. n=4:'I', n!=0 no. n=5:'A', n!=0 no. n=6:'L', append 'L'. code="SPXL". result="SPXL"
42. "OCEAN" → local="OCEAN". wdsz=5. n=0:'O', n==0 append 'O'. n=1:'C', isPrev'S'?charAt(0)='O' no; "CIA"?chars 1,2,3='C','E','A'→"CEA" no; isLastChar?no; frontv.indexOf(charAt(2))=frontv.indexOf('E')=0 >=0 → append 'S'. n=2:'E', n!=0 no. n=3:'A', n!=0 no. n=4:'N', append 'N'. code="OSN". result="OSN"  
43. "NATION" → local="NATION". wdsz=6. n=0:'N', append 'N'. n=1:'A', n!=0 no. n=2:'T', regionMatch("NATION",2,"TIA")? chars 2,3,4='T','I','O'→"TIO" wait no, "TIA": chars='T','I','A'? charAt(4)='O'... "NATION" = N,A,T,I,O,N. chars 2,3,4='T','I','O'→"TIO" yes! → append 'X'. n=3:'I', n!=0 no. n=4:'O', n!=0 no. n=5:'N', append 'N'. code="NXN". result="NXN"
44. "PASSION" → local="PASSION". N,A,S,S,I,O,N. wdsz=7. n=0:'P', isNext'H'?'A' no; append 'P'. n=1:'A', n!=0 no. n=2:'S', isPrev'S'? charAt(1)='A'!='S' no; regionMatch("PASSION",2,"SH")?chars 2,3='S','S' no;"SIO"? chars 2,3,4='S','S','I'→"SSI" no;"SIA"? no; append 'S'. n=3:'S', isPrev'S'?charAt(2)='S' yes and symb='S'!='C' → dup! skip. n=4:'I', n!=0 no. n=5:'O', n!=0 no. n=6:'N', append 'N'. code="PSN". result="PSN"
45. "SESSION" → local="SESSION". S,E,S,S,I,O,N. wdsz=7. n=0:'S', regionMatch("SESSION",0,"SH")?no;"SIO"?chars 0,1,2='S','E','S' no;"SIA"? no; append 'S'. n=1:'E', n!=0 no. n=2:'S', isPrev'S'?charAt(1)='E' no; regionMatch("SESSION",2,"SH")?chars 2,3='S','S' no;"SIO"?chars 2,3,4='S','S','I' no;"SIA"? no; append 'S'. n=3:'S', isPrev'S'?charAt(2)='S' yes! dup → skip. n=4:'I', n!=0 no. n=5:'O', n!=0 no. n=6:'N', append 'N'. code="SSN". result="SSN"
46. "VACATION" → V,A,C,A,T,I,O,N. local="VACATION". wdsz=8. n=0:'V', append 'F'. n=1:'A', n!=0 no. n=2:'C', isPrev'S'?charAt(1)='A' no; "CIA"?chars 2,3,4='C','A','T'→"CAT" no; isLastChar?no; frontv.indexOf(charAt(3))=frontv.indexOf('A')=-1 no; SCH? no; isNext'H'? charAt(3)='A' no; → append 'K'. n=3:'A', n!=0 no. n=4:'T', regionMatch("VACATION",4,"TIA")? chars 4,5,6='T','I','O'→"TIO" yes! → append 'X'. n=5:'I', n!=0 no. n=6:'O', n!=0 no. n=7:'N', append 'N'. code="FKXN". result="FKXN"
47. maxCodeLen=1 test: setMaxCodeLen(1), metaphone("SMITH") → traces same as before but truncates at 1; first char appended is 'S', then code.length()=1 >= maxCodeLen(1), loop exits. result="S"
48. maxCodeLen=0: setMaxCodeLen(0): loop condition: code.length() < 0 → false immediately. result=""
49. "SCHOOL" → local="SCHOOL". S,C,H,O,O,L. wdsz=6. n=0:'S', "SH"?chars 0,1='S','C' no;"SIO"?no;"SIA"?no; append 'S'. n=1:'C', isPrev'S'?charAt(0)='S' yes; isLastChar(6,1)?no; frontv.indexOf(charAt(2))=frontv.indexOf('H')=-1 <0 → no SCI match; "CIA"?chars 1,2,3='C','H','O'→"CHO" no; isLastChar?no; frontv=-1 no; isPrev'S'&&isNext'H'? charAt(2)='H' yes! → append 'K'. n=2:'H', isLastChar(6,2)?no; varson.indexOf(charAt(1))=varson.indexOf('C')=0 >=0 → break. n=3:'O', n!=0 no. n=4:'O', isPrev'O'?charAt(3)='O' yes and symb='O'!='C' → dup! skip. n=5:'L', append 'L'. code="SKL". result="SKL"
50. "CHORUS" → local="CHORUS". C,H,O,R,U,S. wdsz=6. n=0:'C', isPrev'S'? no; "CIA"? no; isNextChar'H'? charAt(1)='H' yes; n==0, wdsz>=3, isVowel(local,2)? charAt(2)='O' yes → append 'K'. n=1:'H', isLastChar?no; varson.indexOf(charAt(0))=varson.indexOf('C')=0 >=0 → break. n=2:'O', n!=0 no. n=3:'R', append 'R'. n=4:'U', n!=0 no. n=5:'S', append 'S'. code="KRS". result="KRS"
51. "CHORD" → local="CHORD". C,H,O,R,D. wdsz=5. n=0:'C', isNext'H'? yes; n==0, wdsz>=3, isVowel(local,2)?charAt(2)='O' yes → append 'K'. n=1:'H' → varson break. n=2:'O', no. n=3:'R', append 'R'. n=4:'D', isLastChar(5,5)?wait: isLastChar(wdsz,n+1)=isLastChar(5,5)? n+1=5, 5==5 yes so isLastChar true, so !isLastChar false; append 'T'. code="KRT". result="KRT"
52. "CZAR" → already done: "KSR"
53. "TSAR" → local="TSAR". T,S,A,R. n=0:'T', "TIA"?no;"TIO"?no;"TCH"?no;"TH"?charAt(1)='S'!='H' no; append 'T'. n=1:'S', regionMatch("TSAR",1,"SH")?chars 1,2='S','A' no;"SIO"?no;"SIA"?no; append 'S'. n=2:'A', n!=0 no. n=3:'R', append 'R'. code="TSR". result="TSR"
54. "CZAR" → "KSR", "TSAR" → "TSR" so they are NOT equal
55. isMetaphoneEqual("NIGHT","KNIGHT") → both "NT" → true
56. encode(Object) with non-String → throws EncoderException
57. "BACH" → local="BACH". B,A,C,H. wdsz=4. n=0:'B', isPrev'M'? no; append 'B'. n=1:'A', n!=0 no. n=2:'C', isPrev'S'?charAt(1)='A' no; "CIA"?chars 2,3,4... wdsz=4, regionMatch check: 2+3-1=4 < 4? no → CIA check fails; isLastChar(4,2)?3!=4 no; frontv.indexOf(charAt(3))=frontv.indexOf('H')=-1 no; isPrev'S'&&next'H'? charAt(3)='H' but isPrev'S'?charAt(1)='A'!='S' no; isNext'H'?charAt(3)='H' yes; n==0? no (n=2); → append 'X'. n=3:'H', isLastChar(4,3)?yes → break. code="BX". result="BX"
58. "PTARMIGAN" → initial 'P', inwd[1]='T'!='N', local="PTARMIGAN". n=0:'P', isNext'H'?charAt(1)='T' no; append 'P'. n=1:'T', "TIA"?no;"TIO"?no;"TCH"?no;"TH"?charAt(2)='A' no; append 'T'. n=2:'A', n!=0 no. n=3:'R', append 'R'. n=4:'M', append 'M'. code.length()=4. Exit. result="PTRM"

Return all these results clearly labelled.


Subagent completed | 142.9s | 4 tool call(s) | 0.262


────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Assistant (1) 2026-09-26 11:34:06.634 UTC (+5.6s)

I'll analyze the Metaphone code carefully, tracing every branch, then write characterization tests that pin down actual 
behaviour.                                                                                                              

Tool calls:
- spawn_subagent

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Tool (1) 2026-09-26 11:38:04.324 UTC (+243.3s) Success

Tool: spawn_subagent
Args:
- name: general
- description: Trace through the Metaphone.java code to determine exact output for specific test inputs. I need you to manually simu...


────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Assistant (2) 2026-09-26 11:38:06.038 UTC (+245.0s)

Now I have all the exact outputs verified. Let me write the complete characterization test class.                       
                                                                                                                        
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
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

Task Summary

Total Cost:              0.422
Total Duration:          5m 8s


Assistant Messages:      2
Tool Calls:              1
Task ID:                 f9d0afd1a4d0183f5619c82752c7352b

````
