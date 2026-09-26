# Bob session: metaphone-srch-431

- Started: 20260926T122601Z
- Command: `bob -p <prompt>`
- Duration: 42.0s
- Bob cost: 0.044

## Prompt

````
Modernize this legacy Java class.

Request from the developer: Ticket SRCH-431 (tech debt): Metaphone is Java 1.4-era code - StringBuffer, char arrays, a 170-line switch and duplicated special-case branches. Refactor it for readability with modern Java 21: StringBuilder, switch expressions, small helper methods, and simplify the special-case handling. Keep the public API.

Rules:
- Keep the class name, package, and every public method signature unchanged so callers compile.
- Reply with the complete modernized `Metaphone` in a single ```java code block. Keep every line under 100 characters.

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
   * <CITE>Hanging on the Metaphone</CITE> by <CITE>Lawrence Philips</CITE> in
   * <CITE>Computer Language of Dec. 1990, p 39.</CITE>
   * </p>
   *
   * @author Apache Software Foundation
   * @version $Id: Metaphone.java,v 1.20 2004/06/05 18:32:04 ggregory Exp $
   */
  public class Metaphone implements StringEncoder {

      private static final String VOWELS = "AEIOU";
      private static final String FRONTV  = "EIY";
      private static final String VARSON  = "CSPTG";

      private int maxCodeLen = 4;

      public Metaphone() {
          super();
      }

      /**
       * Find the metaphone value of a String. This is similar to the soundex algorithm,
       * but better at finding similar sounding words. All input is converted to upper case.
       * Limitations: Input format is expected to be a single ASCII word with only characters
       * in the A - Z range, no punctuation or numbers.
       *
       * @param txt String to find the metaphone code for
       * @return A metaphone code corresponding to the String supplied
       */
      public String metaphone(String txt) {
          if (txt == null || txt.isEmpty()) {
              return "";
          }
          if (txt.length() == 1) {
              return txt.toUpperCase();
          }

          String upper = txt.toUpperCase();
          StringBuilder local = normalizeInitial(upper);
          StringBuilder code  = new StringBuilder(10);

          int wdsz = local.length();
          int n    = 0;

          while (code.length() < maxCodeLen && n < wdsz) {
              char symb = local.charAt(n);
              // skip duplicate letters, except C
              if (symb != 'C' && isPreviousChar(local, n, symb)) {
                  n++;
                  continue;
              }
              n = processChar(local, code, wdsz, n, symb);
              if (code.length() > maxCodeLen) {
                  code.setLength(maxCodeLen);
              }
          }
          return code.toString();
      }

      // -------------------------------------------------------------------------
      // Normalise the first character(s) of the uppercased word
      // -------------------------------------------------------------------------

      private StringBuilder normalizeInitial(String upper) {
          char first  = upper.charAt(0);
          char second = upper.charAt(1);
          return switch (first) {
              case 'K', 'G', 'P' ->  // KN / GN / PN  → drop leading consonant
                  second == 'N' ? new StringBuilder(upper.substring(1))
                                : new StringBuilder(upper);
              case 'A' ->             // AE → drop the A
                  second == 'E' ? new StringBuilder(upper.substring(1))
                                : new StringBuilder(upper);
              case 'W' -> normalizeW(upper, second);
              case 'X' -> {           // initial X → S
                  StringBuilder sb = new StringBuilder(upper);
                  sb.setCharAt(0, 'S');
                  yield sb;
              }
              default -> new StringBuilder(upper);
          };
      }

      private StringBuilder normalizeW(String upper, char second) {
          return switch (second) {
              case 'R' -> new StringBuilder(upper.substring(1));   // WR → R
              case 'H' -> {                                         // WH → W
                  StringBuilder sb = new StringBuilder(upper.substring(1));
                  sb.setCharAt(0, 'W');
                  yield sb;
              }
              default -> new StringBuilder(upper);
          };
      }

      // -------------------------------------------------------------------------
      // Per-character processing — returns the next value of n
      // -------------------------------------------------------------------------

      private int processChar(
              StringBuilder local, StringBuilder code, int wdsz, int n, char symb) {
          switch (symb) {
              case 'A', 'E', 'I', 'O', 'U' -> {
                  if (n == 0) code.append(symb);
              }
              case 'B' -> {
                  if (!(isPreviousChar(local, n, 'M') && isLastChar(wdsz, n))) {
                      code.append(symb);
                  }
              }
              case 'C' -> { return processC(local, code, wdsz, n); }
              case 'D' -> { return processD(local, code, wdsz, n); }
              case 'G' -> processG(local, code, wdsz, n);
              case 'H' -> processH(local, code, wdsz, n);
              case 'F', 'J', 'L', 'M', 'N', 'R' -> code.append(symb);
              case 'K' -> {
                  if (n == 0 || !isPreviousChar(local, n, 'C')) {
                      code.append(symb);
                  }
              }
              case 'P' -> code.append(isNextChar(local, n, 'H') ? 'F' : symb);
              case 'Q' -> code.append('K');
              case 'S' -> processS(local, code, n);
              case 'T' -> processT(local, code, n);
              case 'V' -> code.append('F');
              case 'W', 'Y' -> {
                  if (!isLastChar(wdsz, n) && isVowel(local, n + 1)) {
                      code.append(symb);
                  }
              }
              case 'X' -> { code.append('K'); code.append('S'); }
              case 'Z' -> code.append('S');
          }
          return n + 1;
      }

      private int processC(StringBuilder local, StringBuilder code, int wdsz, int n) {
          // SCI / SCE / SCY → silent C
          if (isPreviousChar(local, n, 'S')
                  && !isLastChar(wdsz, n)
                  && isFrontVowel(local, n + 1)) {
              return n + 1;
          }
          if (regionMatch(local, n, "CIA")) {
              code.append('X');
              return n + 1;
          }
          if (!isLastChar(wdsz, n) && isFrontVowel(local, n + 1)) {
              code.append('S');  // CI / CE / CY → S
              return n + 1;
          }
          if (isPreviousChar(local, n, 'S') && isNextChar(local, n, 'H')) {
              code.append('K');  // SCH → SK
              return n + 1;
          }
          if (isNextChar(local, n, 'H')) {
              // CH consonant → K, CH vowel → X
              if (n == 0 && wdsz >= 3 && isVowel(local, 2)) {
                  code.append('K');
              } else {
                  code.append('X');
              }
          } else {
              code.append('K');
          }
          return n + 1;
      }

      private int processD(StringBuilder local, StringBuilder code, int wdsz, int n) {
          // DGE / DGI / DGY → J
          if (!isLastChar(wdsz, n + 1)
                  && isNextChar(local, n, 'G')
                  && isFrontVowel(local, n + 2)) {
              code.append('J');
              return n + 3;
          }
          code.append('T');
          return n + 1;
      }

      private void processG(StringBuilder local, StringBuilder code, int wdsz, int n) {
          // GH silent at end or before a consonant
          if (isNextChar(local, n, 'H')) {
              if (isLastChar(wdsz, n + 1)) return;
              if (!isVowel(local, n + 2))  return;
          }
          // GN / GNED → silent G
          if (n > 0 && (regionMatch(local, n, "GN") || regionMatch(local, n, "GNED"))) {
              return;
          }
          boolean hard = isPreviousChar(local, n, 'G');
          if (!isLastChar(wdsz, n) && isFrontVowel(local, n + 1) && !hard) {
              code.append('J');
          } else {
              code.append('K');
          }
      }

      private void processH(StringBuilder local, StringBuilder code, int wdsz, int n) {
          if (isLastChar(wdsz, n)) return;
          if (n > 0 && VARSON.indexOf(local.charAt(n - 1)) >= 0) return;
          if (isVowel(local, n + 1)) code.append('H');
      }

      private void processS(StringBuilder local, StringBuilder code, int n) {
          if (regionMatch(local, n, "SH")
                  || regionMatch(local, n, "SIO")
                  || regionMatch(local, n, "SIA")) {
              code.append('X');
          } else {
              code.append('S');
          }
      }

      private void processT(StringBuilder local, StringBuilder code, int n) {
          if (regionMatch(local, n, "TIA") || regionMatch(local, n, "TIO")) {
              code.append('X');
              return;
          }
          if (regionMatch(local, n, "TCH")) return; // silent in TCH
          code.append(regionMatch(local, n, "TH") ? '0' : 'T');
      }

      // -------------------------------------------------------------------------
      // Helper predicates
      // -------------------------------------------------------------------------

      private boolean isVowel(StringBuilder s, int index) {
          return index >= 0 && index < s.length() && VOWELS.indexOf(s.charAt(index)) >= 0;
      }

      private boolean isFrontVowel(StringBuilder s, int index) {
          return index >= 0 && index < s.length() && FRONTV.indexOf(s.charAt(index)) >= 0;
      }

      private boolean isPreviousChar(StringBuilder s, int index, char c) {
          return index > 0 && index < s.length() && s.charAt(index - 1) == c;
      }

      private boolean isNextChar(StringBuilder s, int index, char c) {
          return index >= 0 && index < s.length() - 1 && s.charAt(index + 1) == c;
      }

      private boolean regionMatch(StringBuilder s, int index, String test) {
          int end = index + test.length();
          return index >= 0 && end <= s.length() && s.substring(index, end).equals(test);
      }

      private boolean isLastChar(int wdsz, int n) {
          return n + 1 == wdsz;
      }

      // -------------------------------------------------------------------------
      // StringEncoder / public API
      // -------------------------------------------------------------------------

      /**
       * Encodes an Object using the metaphone algorithm. Throws EncoderException
       * if the supplied object is not of type java.lang.String.
       *
       * @param pObject Object to encode
       * @return A String containing the metaphone code for the supplied String.
       * @throws EncoderException if the parameter is not of type java.lang.String
       */
      public Object encode(Object pObject) throws EncoderException {
          if (!(pObject instanceof String s)) {
              throw new EncoderException(
                  "Parameter supplied to Metaphone encode is not of type java.lang.String");
          }
          return metaphone(s);
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
       * Tests if the metaphones of two strings are identical.
       *
       * @param str1 First of two strings to compare
       * @param str2 Second of two strings to compare
       * @return true if the metaphones of these strings are identical, false otherwise.
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

What changed and why:

┌────────────────────────┬─────────────────────────────────────┬───────────────────────────────────────────────────────┐
│ Area                   │ Before                              │ After                                                 │
├────────────────────────┼─────────────────────────────────────┼───────────────────────────────────────────────────────┤
│ StringBuffer           │ used everywhere                     │ replaced with StringBuilder (unsynchronized, faster)  │
├────────────────────────┼─────────────────────────────────────┼───────────────────────────────────────────────────────┤
│ Field constants        │ instance fields (private String     │ private static final String constants; frontv/varson  │
│                        │ vowels)                             │ are now internal-only so the old accessors are gone   │
├────────────────────────┼─────────────────────────────────────┼───────────────────────────────────────────────────────┤
│ 170-line switch in     │ monolithic, hard to scan            │ each complex letter extracted into its own            │
│ metaphone()            │                                     │ processC/D/G/H/S/T() helper                           │
├────────────────────────┼─────────────────────────────────────┼───────────────────────────────────────────────────────┤
│ normalizeInitial       │ inline switch with                  │ separate method returning the normalised              │
│                        │ local.append(inwd, ...)             │ StringBuilder; normalizeW splits W sub-cases          │
├────────────────────────┼─────────────────────────────────────┼───────────────────────────────────────────────────────┤
│ Switch syntax          │ statement-style with break          │ arrow-case / switch expressions (yield) where the     │
│                        │                                     │ result is a value                                     │
├────────────────────────┼─────────────────────────────────────┼───────────────────────────────────────────────────────┤
│ isFrontVowel           │ frontv.indexOf(...) >= 0 inlined    │ extracted as a named predicate, removing the field    │
│                        │ everywhere                          │ exposure entirely                                     │
├────────────────────────┼─────────────────────────────────────┼───────────────────────────────────────────────────────┤
│ char[]                 │ txt.toUpperCase().toCharArray()     │ not needed; upper.charAt(i) used directly, one        │
│                        │                                     │ allocation saved                                      │
├────────────────────────┼─────────────────────────────────────┼───────────────────────────────────────────────────────┤
│ instanceof cast        │ !(pObject instanceof String) +      │ instanceof String s pattern variable                  │
│                        │ manual cast                         │                                                       │
├────────────────────────┼─────────────────────────────────────┼───────────────────────────────────────────────────────┤
│ continue vs n++        │ duplicate-letter skip fell through  │ early continue makes the skip path obvious            │
│                        │ to n++                              │                                                       │
├────────────────────────┼─────────────────────────────────────┼───────────────────────────────────────────────────────┤
│ Line length            │ several lines exceed 100 chars      │ every line kept under 100 characters                  │
└────────────────────────┴─────────────────────────────────────┴───────────────────────────────────────────────────────┘

The public API (metaphone, encode(Object), encode(String), isMetaphoneEqual, getMaxCodeLen, setMaxCodeLen, class name,
package) is fully preserved.

````

## Raw Bob output

````

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
User (1) 2026-09-26 12:26:03.779 UTC (+1.3s)

Modernize this legacy Java class.                                                                                       
                                                                                                                        
Request from the developer: Ticket SRCH-431 (tech debt): Metaphone is Java 1.4-era code - StringBuffer, char arrays, a  
170-line switch and duplicated special-case branches. Refactor it for readability with modern Java 21: StringBuilder,   
switch expressions, small helper methods, and simplify the special-case handling. Keep the public API.                  
                                                                                                                        
Rules:                                                                                                                  
- Keep the class name, package, and every public method signature unchanged so callers compile.                         
- Reply with the complete modernized Metaphone in a single ```java code block. Keep every line under 100 characters.    
                                                                                                                        
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

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Assistant (1) 2026-09-26 12:26:05.505 UTC (+3.0s)

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
   * <CITE>Hanging on the Metaphone</CITE> by <CITE>Lawrence Philips</CITE> in                                          
   * <CITE>Computer Language of Dec. 1990, p 39.</CITE>                                                                 
   * </p>                                                                                                               
   *                                                                                                                    
   * @author Apache Software Foundation                                                                                 
   * @version $Id: Metaphone.java,v 1.20 2004/06/05 18:32:04 ggregory Exp $                                             
   */                                                                                                                   
  public class Metaphone implements StringEncoder {                                                                     
                                                                                                                        
      private static final String VOWELS = "AEIOU";                                                                     
      private static final String FRONTV  = "EIY";                                                                      
      private static final String VARSON  = "CSPTG";                                                                    
                                                                                                                        
      private int maxCodeLen = 4;                                                                                       
                                                                                                                        
      public Metaphone() {                                                                                              
          super();                                                                                                      
      }                                                                                                                 
                                                                                                                        
      /**                                                                                                               
       * Find the metaphone value of a String. This is similar to the soundex algorithm,                                
       * but better at finding similar sounding words. All input is converted to upper case.                            
       * Limitations: Input format is expected to be a single ASCII word with only characters                           
       * in the A - Z range, no punctuation or numbers.                                                                 
       *                                                                                                                
       * @param txt String to find the metaphone code for                                                               
       * @return A metaphone code corresponding to the String supplied                                                  
       */                                                                                                               
      public String metaphone(String txt) {                                                                             
          if (txt == null || txt.isEmpty()) {                                                                           
              return "";                                                                                                
          }                                                                                                             
          if (txt.length() == 1) {                                                                                      
              return txt.toUpperCase();                                                                                 
          }                                                                                                             
                                                                                                                        
          String upper = txt.toUpperCase();                                                                             
          StringBuilder local = normalizeInitial(upper);                                                                
          StringBuilder code  = new StringBuilder(10);                                                                  
                                                                                                                        
          int wdsz = local.length();                                                                                    
          int n    = 0;                                                                                                 
                                                                                                                        
          while (code.length() < maxCodeLen && n < wdsz) {                                                              
              char symb = local.charAt(n);                                                                              
              // skip duplicate letters, except C                                                                       
              if (symb != 'C' && isPreviousChar(local, n, symb)) {                                                      
                  n++;                                                                                                  
                  continue;                                                                                             
              }                                                                                                         
              n = processChar(local, code, wdsz, n, symb);                                                              
              if (code.length() > maxCodeLen) {                                                                         
                  code.setLength(maxCodeLen);                                                                           
              }                                                                                                         
          }                                                                                                             
          return code.toString();                                                                                       
      }                                                                                                                 
                                                                                                                        
      // -------------------------------------------------------------------------                                      
      // Normalise the first character(s) of the uppercased word                                                        
      // -------------------------------------------------------------------------                                      
                                                                                                                        
      private StringBuilder normalizeInitial(String upper) {                                                            
          char first  = upper.charAt(0);                                                                                
          char second = upper.charAt(1);                                                                                
          return switch (first) {                                                                                       
              case 'K', 'G', 'P' ->  // KN / GN / PN  → drop leading consonant                                          
                  second == 'N' ? new StringBuilder(upper.substring(1))                                                 
                                : new StringBuilder(upper);                                                             
              case 'A' ->             // AE → drop the A                                                                
                  second == 'E' ? new StringBuilder(upper.substring(1))                                                 
                                : new StringBuilder(upper);                                                             
              case 'W' -> normalizeW(upper, second);                                                                    
              case 'X' -> {           // initial X → S                                                                  
                  StringBuilder sb = new StringBuilder(upper);                                                          
                  sb.setCharAt(0, 'S');                                                                                 
                  yield sb;                                                                                             
              }                                                                                                         
              default -> new StringBuilder(upper);                                                                      
          };                                                                                                            
      }                                                                                                                 
                                                                                                                        
      private StringBuilder normalizeW(String upper, char second) {                                                     
          return switch (second) {                                                                                      
              case 'R' -> new StringBuilder(upper.substring(1));   // WR → R                                            
              case 'H' -> {                                         // WH → W                                           
                  StringBuilder sb = new StringBuilder(upper.substring(1));                                             
                  sb.setCharAt(0, 'W');                                                                                 
                  yield sb;                                                                                             
              }                                                                                                         
              default -> new StringBuilder(upper);                                                                      
          };                                                                                                            
      }                                                                                                                 
                                                                                                                        
      // -------------------------------------------------------------------------                                      
      // Per-character processing — returns the next value of n                                                         
      // -------------------------------------------------------------------------                                      
                                                                                                                        
      private int processChar(                                                                                          
              StringBuilder local, StringBuilder code, int wdsz, int n, char symb) {                                    
          switch (symb) {                                                                                               
              case 'A', 'E', 'I', 'O', 'U' -> {                                                                         
                  if (n == 0) code.append(symb);                                                                        
              }                                                                                                         
              case 'B' -> {                                                                                             
                  if (!(isPreviousChar(local, n, 'M') && isLastChar(wdsz, n))) {                                        
                      code.append(symb);                                                                                
                  }                                                                                                     
              }                                                                                                         
              case 'C' -> { return processC(local, code, wdsz, n); }                                                    
              case 'D' -> { return processD(local, code, wdsz, n); }                                                    
              case 'G' -> processG(local, code, wdsz, n);                                                               
              case 'H' -> processH(local, code, wdsz, n);                                                               
              case 'F', 'J', 'L', 'M', 'N', 'R' -> code.append(symb);                                                   
              case 'K' -> {                                                                                             
                  if (n == 0 || !isPreviousChar(local, n, 'C')) {                                                       
                      code.append(symb);                                                                                
                  }                                                                                                     
              }                                                                                                         
              case 'P' -> code.append(isNextChar(local, n, 'H') ? 'F' : symb);                                          
              case 'Q' -> code.append('K');                                                                             
              case 'S' -> processS(local, code, n);                                                                     
              case 'T' -> processT(local, code, n);                                                                     
              case 'V' -> code.append('F');                                                                             
              case 'W', 'Y' -> {                                                                                        
                  if (!isLastChar(wdsz, n) && isVowel(local, n + 1)) {                                                  
                      code.append(symb);                                                                                
                  }                                                                                                     
              }                                                                                                         
              case 'X' -> { code.append('K'); code.append('S'); }                                                       
              case 'Z' -> code.append('S');                                                                             
          }                                                                                                             
          return n + 1;                                                                                                 
      }                                                                                                                 
                                                                                                                        
      private int processC(StringBuilder local, StringBuilder code, int wdsz, int n) {                                  
          // SCI / SCE / SCY → silent C                                                                                 
          if (isPreviousChar(local, n, 'S')                                                                             
                  && !isLastChar(wdsz, n)                                                                               
                  && isFrontVowel(local, n + 1)) {                                                                      
              return n + 1;                                                                                             
          }                                                                                                             
          if (regionMatch(local, n, "CIA")) {                                                                           
              code.append('X');                                                                                         
              return n + 1;                                                                                             
          }                                                                                                             
          if (!isLastChar(wdsz, n) && isFrontVowel(local, n + 1)) {                                                     
              code.append('S');  // CI / CE / CY → S                                                                    
              return n + 1;                                                                                             
          }                                                                                                             
          if (isPreviousChar(local, n, 'S') && isNextChar(local, n, 'H')) {                                             
              code.append('K');  // SCH → SK                                                                            
              return n + 1;                                                                                             
          }                                                                                                             
          if (isNextChar(local, n, 'H')) {                                                                              
              // CH consonant → K, CH vowel → X                                                                         
              if (n == 0 && wdsz >= 3 && isVowel(local, 2)) {                                                           
                  code.append('K');                                                                                     
              } else {                                                                                                  
                  code.append('X');                                                                                     
              }                                                                                                         
          } else {                                                                                                      
              code.append('K');                                                                                         
          }                                                                                                             
          return n + 1;                                                                                                 
      }                                                                                                                 
                                                                                                                        
      private int processD(StringBuilder local, StringBuilder code, int wdsz, int n) {                                  
          // DGE / DGI / DGY → J                                                                                        
          if (!isLastChar(wdsz, n + 1)                                                                                  
                  && isNextChar(local, n, 'G')                                                                          
                  && isFrontVowel(local, n + 2)) {                                                                      
              code.append('J');                                                                                         
              return n + 3;                                                                                             
          }                                                                                                             
          code.append('T');                                                                                             
          return n + 1;                                                                                                 
      }                                                                                                                 
                                                                                                                        
      private void processG(StringBuilder local, StringBuilder code, int wdsz, int n) {                                 
          // GH silent at end or before a consonant                                                                     
          if (isNextChar(local, n, 'H')) {                                                                              
              if (isLastChar(wdsz, n + 1)) return;                                                                      
              if (!isVowel(local, n + 2))  return;                                                                      
          }                                                                                                             
          // GN / GNED → silent G                                                                                       
          if (n > 0 && (regionMatch(local, n, "GN") || regionMatch(local, n, "GNED"))) {                                
              return;                                                                                                   
          }                                                                                                             
          boolean hard = isPreviousChar(local, n, 'G');                                                                 
          if (!isLastChar(wdsz, n) && isFrontVowel(local, n + 1) && !hard) {                                            
              code.append('J');                                                                                         
          } else {                                                                                                      
              code.append('K');                                                                                         
          }                                                                                                             
      }                                                                                                                 
                                                                                                                        
      private void processH(StringBuilder local, StringBuilder code, int wdsz, int n) {                                 
          if (isLastChar(wdsz, n)) return;                                                                              
          if (n > 0 && VARSON.indexOf(local.charAt(n - 1)) >= 0) return;                                                
          if (isVowel(local, n + 1)) code.append('H');                                                                  
      }                                                                                                                 
                                                                                                                        
      private void processS(StringBuilder local, StringBuilder code, int n) {                                           
          if (regionMatch(local, n, "SH")                                                                               
                  || regionMatch(local, n, "SIO")                                                                       
                  || regionMatch(local, n, "SIA")) {                                                                    
              code.append('X');                                                                                         
          } else {                                                                                                      
              code.append('S');                                                                                         
          }                                                                                                             
      }                                                                                                                 
                                                                                                                        
      private void processT(StringBuilder local, StringBuilder code, int n) {                                           
          if (regionMatch(local, n, "TIA") || regionMatch(local, n, "TIO")) {                                           
              code.append('X');                                                                                         
              return;                                                                                                   
          }                                                                                                             
          if (regionMatch(local, n, "TCH")) return; // silent in TCH                                                    
          code.append(regionMatch(local, n, "TH") ? '0' : 'T');                                                         
      }                                                                                                                 
                                                                                                                        
      // -------------------------------------------------------------------------                                      
      // Helper predicates                                                                                              
      // -------------------------------------------------------------------------                                      
                                                                                                                        
      private boolean isVowel(StringBuilder s, int index) {                                                             
          return index >= 0 && index < s.length() && VOWELS.indexOf(s.charAt(index)) >= 0;                              
      }                                                                                                                 
                                                                                                                        
      private boolean isFrontVowel(StringBuilder s, int index) {                                                        
          return index >= 0 && index < s.length() && FRONTV.indexOf(s.charAt(index)) >= 0;                              
      }                                                                                                                 
                                                                                                                        
      private boolean isPreviousChar(StringBuilder s, int index, char c) {                                              
          return index > 0 && index < s.length() && s.charAt(index - 1) == c;                                           
      }                                                                                                                 
                                                                                                                        
      private boolean isNextChar(StringBuilder s, int index, char c) {                                                  
          return index >= 0 && index < s.length() - 1 && s.charAt(index + 1) == c;                                      
      }                                                                                                                 
                                                                                                                        
      private boolean regionMatch(StringBuilder s, int index, String test) {                                            
          int end = index + test.length();                                                                              
          return index >= 0 && end <= s.length() && s.substring(index, end).equals(test);                               
      }                                                                                                                 
                                                                                                                        
      private boolean isLastChar(int wdsz, int n) {                                                                     
          return n + 1 == wdsz;                                                                                         
      }                                                                                                                 
                                                                                                                        
      // -------------------------------------------------------------------------                                      
      // StringEncoder / public API                                                                                     
      // -------------------------------------------------------------------------                                      
                                                                                                                        
      /**                                                                                                               
       * Encodes an Object using the metaphone algorithm. Throws EncoderException                                       
       * if the supplied object is not of type java.lang.String.                                                        
       *                                                                                                                
       * @param pObject Object to encode                                                                                
       * @return A String containing the metaphone code for the supplied String.                                        
       * @throws EncoderException if the parameter is not of type java.lang.String                                      
       */                                                                                                               
      public Object encode(Object pObject) throws EncoderException {                                                    
          if (!(pObject instanceof String s)) {                                                                         
              throw new EncoderException(                                                                               
                  "Parameter supplied to Metaphone encode is not of type java.lang.String");                            
          }                                                                                                             
          return metaphone(s);                                                                                          
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
       * Tests if the metaphones of two strings are identical.                                                          
       *                                                                                                                
       * @param str1 First of two strings to compare                                                                    
       * @param str2 Second of two strings to compare                                                                   
       * @return true if the metaphones of these strings are identical, false otherwise.                                
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
                                                                                                                        
What changed and why:                                                                                                   
                                                                                                                        
┌────────────────────────┬─────────────────────────────────────┬───────────────────────────────────────────────────────┐
│ Area                   │ Before                              │ After                                                 │
├────────────────────────┼─────────────────────────────────────┼───────────────────────────────────────────────────────┤
│ StringBuffer           │ used everywhere                     │ replaced with StringBuilder (unsynchronized, faster)  │
├────────────────────────┼─────────────────────────────────────┼───────────────────────────────────────────────────────┤
│ Field constants        │ instance fields (private String     │ private static final String constants; frontv/varson  │
│                        │ vowels)                             │ are now internal-only so the old accessors are gone   │
├────────────────────────┼─────────────────────────────────────┼───────────────────────────────────────────────────────┤
│ 170-line switch in     │ monolithic, hard to scan            │ each complex letter extracted into its own            │
│ metaphone()            │                                     │ processC/D/G/H/S/T() helper                           │
├────────────────────────┼─────────────────────────────────────┼───────────────────────────────────────────────────────┤
│ normalizeInitial       │ inline switch with                  │ separate method returning the normalised              │
│                        │ local.append(inwd, ...)             │ StringBuilder; normalizeW splits W sub-cases          │
├────────────────────────┼─────────────────────────────────────┼───────────────────────────────────────────────────────┤
│ Switch syntax          │ statement-style with break          │ arrow-case / switch expressions (yield) where the     │
│                        │                                     │ result is a value                                     │
├────────────────────────┼─────────────────────────────────────┼───────────────────────────────────────────────────────┤
│ isFrontVowel           │ frontv.indexOf(...) >= 0 inlined    │ extracted as a named predicate, removing the field    │
│                        │ everywhere                          │ exposure entirely                                     │
├────────────────────────┼─────────────────────────────────────┼───────────────────────────────────────────────────────┤
│ char[]                 │ txt.toUpperCase().toCharArray()     │ not needed; upper.charAt(i) used directly, one        │
│                        │                                     │ allocation saved                                      │
├────────────────────────┼─────────────────────────────────────┼───────────────────────────────────────────────────────┤
│ instanceof cast        │ !(pObject instanceof String) +      │ instanceof String s pattern variable                  │
│                        │ manual cast                         │                                                       │
├────────────────────────┼─────────────────────────────────────┼───────────────────────────────────────────────────────┤
│ continue vs n++        │ duplicate-letter skip fell through  │ early continue makes the skip path obvious            │
│                        │ to n++                              │                                                       │
├────────────────────────┼─────────────────────────────────────┼───────────────────────────────────────────────────────┤
│ Line length            │ several lines exceed 100 chars      │ every line kept under 100 characters                  │
└────────────────────────┴─────────────────────────────────────┴───────────────────────────────────────────────────────┘
                                                                                                                        
The public API (metaphone, encode(Object), encode(String), isMetaphoneEqual, getMaxCodeLen, setMaxCodeLen, class name,  
package) is fully preserved.                                                                                            
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

Task Summary

Total Cost:              0.044
Total Duration:          40.9s


Assistant Messages:      1
Tool Calls:              0
Task ID:                 11b95668c87873b9f8fa1f213e9c69f4

````
