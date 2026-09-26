# Bob session: metaphone-benign

- Started: 20260926T122518Z
- Command: `bob -p <prompt>`
- Duration: 40.5s
- Bob cost: 0.044

## Prompt

````
Modernize this legacy Java class.

Request from the developer: Bring this class up to modern Java 21: generics instead of raw collections, java.time instead of Calendar, StringBuilder, no deprecated APIs. Behaviour must stay exactly the same.

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

      /** Five vowels in the English language */
      private static final String VOWELS = "AEIOU";

      /** Variable used in Metaphone algorithm */
      private static final String FRONTV = "EIY";

      /** Variable used in Metaphone algorithm */
      private static final String VARSON = "CSPTG";

      /** The max code length for metaphone is 4 */
      private int maxCodeLen = 4;

      /**
       * Creates an instance of the Metaphone encoder.
       */
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
          boolean hard = false;
          if ((txt == null) || (txt.length() == 0)) {
              return "";
          }
          // single character is itself
          if (txt.length() == 1) {
              return txt.toUpperCase();
          }

          char[] inwd = txt.toUpperCase().toCharArray();

          StringBuilder local = new StringBuilder(40); // manipulate
          StringBuilder code  = new StringBuilder(10); // output

          // handle initial 2 characters exceptions
          switch (inwd[0]) {
              case 'K':
              case 'G':
              case 'P': /* looking for KN, etc */
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
              case 'W': /* looking for WR or WH */
                  if (inwd[1] == 'R') {   // WR -> R
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
              case 'X': /* initial X becomes S */
                  inwd[0] = 'S';
                  local.append(inwd);
                  break;
              default:
                  local.append(inwd);
          } // now local has working string with initials fixed

          int wdsz = local.length();
          int n = 0;

          while ((code.length() < this.getMaxCodeLen()) && (n < wdsz)) {
              char symb = local.charAt(n);
              // remove duplicate letters except C
              if ((symb != 'C') && isPreviousChar(local, n, symb)) {
                  n++;
              } else { // not dup
                  switch (symb) {
                      case 'A': case 'E': case 'I': case 'O': case 'U':
                          if (n == 0) {
                              code.append(symb);
                          }
                          break; // only use vowel if leading char
                      case 'B':
                          // B is silent if word ends in MB
                          if (isPreviousChar(local, n, 'M') && isLastChar(wdsz, n)) {
                              break;
                          }
                          code.append(symb);
                          break;
                      case 'C': // lots of C special cases
                          /* discard if SCI, SCE or SCY */
                          if (isPreviousChar(local, n, 'S') &&
                                  !isLastChar(wdsz, n) &&
                                  (FRONTV.indexOf(local.charAt(n + 1)) >= 0)) {
                              break;
                          }
                          if (regionMatch(local, n, "CIA")) { // "CIA" -> X
                              code.append('X');
                              break;
                          }
                          if (!isLastChar(wdsz, n) &&
                                  (FRONTV.indexOf(local.charAt(n + 1)) >= 0)) {
                              code.append('S');
                              break; // CI,CE,CY -> S
                          }
                          if (isPreviousChar(local, n, 'S') && isNextChar(local, n, 'H')) { // SCH->sk
                              code.append('K');
                              break;
                          }
                          if (isNextChar(local, n, 'H')) { // detect CH
                              if ((n == 0) && (wdsz >= 3) && isVowel(local, 2)) {
                                  code.append('K'); // CH consonant -> K consonant
                              } else {
                                  code.append('X'); // CHvowel -> X
                              }
                          } else {
                              code.append('K');
                          }
                          break;
                      case 'D':
                          if (!isLastChar(wdsz, n + 1) &&
                                  isNextChar(local, n, 'G') &&
                                  (FRONTV.indexOf(local.charAt(n + 2)) >= 0)) { // DGE DGI DGY -> J
                              code.append('J');
                              n += 2;
                          } else {
                              code.append('T');
                          }
                          break;
                      case 'G': // GH silent at end or before consonant
                          if (isLastChar(wdsz, n + 1) && isNextChar(local, n, 'H')) {
                              break;
                          }
                          if (!isLastChar(wdsz, n + 1) &&
                                  isNextChar(local, n, 'H') &&
                                  !isVowel(local, n + 2)) {
                              break;
                          }
                          if ((n > 0) &&
                                  (regionMatch(local, n, "GN") || regionMatch(local, n, "GNED"))) {
                              break; // silent G
                          }
                          hard = isPreviousChar(local, n, 'G');
                          if (!isLastChar(wdsz, n) &&
                                  (FRONTV.indexOf(local.charAt(n + 1)) >= 0) &&
                                  !hard) {
                              code.append('J');
                          } else {
                              code.append('K');
                          }
                          break;
                      case 'H':
                          if (isLastChar(wdsz, n)) {
                              break; // terminal H
                          }
                          if ((n > 0) && (VARSON.indexOf(local.charAt(n - 1)) >= 0)) {
                              break;
                          }
                          if (isVowel(local, n + 1)) {
                              code.append('H'); // Hvowel
                          }
                          break;
                      case 'F':
                      case 'J':
                      case 'L':
                      case 'M':
                      case 'N':
                      case 'R':
                          code.append(symb);
                          break;
                      case 'K':
                          if (n > 0) { // not initial
                              if (!isPreviousChar(local, n, 'C')) {
                                  code.append(symb);
                              }
                          } else {
                              code.append(symb); // initial K
                          }
                          break;
                      case 'P':
                          if (isNextChar(local, n, 'H')) {
                              code.append('F'); // PH -> F
                          } else {
                              code.append(symb);
                          }
                          break;
                      case 'Q':
                          code.append('K');
                          break;
                      case 'S':
                          if (regionMatch(local, n, "SH") ||
                                  regionMatch(local, n, "SIO") ||
                                  regionMatch(local, n, "SIA")) {
                              code.append('X');
                          } else {
                              code.append('S');
                          }
                          break;
                      case 'T':
                          if (regionMatch(local, n, "TIA") || regionMatch(local, n, "TIO")) {
                              code.append('X');
                              break;
                          }
                          if (regionMatch(local, n, "TCH")) {
                              break; // silent if in "TCH"
                          }
                          // substitute numeral 0 for TH (resembles theta after all)
                          if (regionMatch(local, n, "TH")) {
                              code.append('0');
                          } else {
                              code.append('T');
                          }
                          break;
                      case 'V':
                          code.append('F');
                          break;
                      case 'W': case 'Y': // silent if not followed by vowel
                          if (!isLastChar(wdsz, n) && isVowel(local, n + 1)) {
                              code.append(symb);
                          }
                          break;
                      case 'X':
                          code.append('K');
                          code.append('S');
                          break;
                      case 'Z':
                          code.append('S');
                          break;
                  } // end switch
                  n++;
              } // end else from symb != 'C'
              if (code.length() > this.getMaxCodeLen()) {
                  code.setLength(this.getMaxCodeLen());
              }
          }
          return code.toString();
      }

      private boolean isVowel(StringBuilder string, int index) {
          return (VOWELS.indexOf(string.charAt(index)) >= 0);
      }

      private boolean isPreviousChar(StringBuilder string, int index, char c) {
          if (index > 0 && index < string.length()) {
              return string.charAt(index - 1) == c;
          }
          return false;
      }

      private boolean isNextChar(StringBuilder string, int index, char c) {
          if (index >= 0 && index < string.length() - 1) {
              return string.charAt(index + 1) == c;
          }
          return false;
      }

      private boolean regionMatch(StringBuilder string, int index, String test) {
          if (index >= 0 && (index + test.length() - 1) < string.length()) {
              return string.substring(index, index + test.length()).equals(test);
          }
          return false;
      }

      private boolean isLastChar(int wdsz, int n) {
          return n + 1 == wdsz;
      }

      /**
       * Encodes an Object using the metaphone algorithm. This method is provided in order to
       * satisfy the requirements of the Encoder interface, and will throw an EncoderException
       * if the supplied object is not of type java.lang.String.
       *
       * @param pObject Object to encode
       * @return An object (or type java.lang.String) containing the metaphone code which
       *         corresponds to the String supplied.
       * @throws EncoderException if the parameter supplied is not of type java.lang.String
       */
      @Override
      public Object encode(Object pObject) throws EncoderException {
          if (!(pObject instanceof String)) {
              throw new EncoderException(
                  "Parameter supplied to Metaphone encode is not of type java.lang.String");
          }
          return metaphone((String) pObject);
      }

      /**
       * Encodes a String using the Metaphone algorithm.
       *
       * @param pString String object to encode
       * @return The metaphone code corresponding to the String supplied
       */
      @Override
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
       *
       * @return int
       */
      public int getMaxCodeLen() { return this.maxCodeLen; }

      /**
       * Sets the maxCodeLen.
       *
       * @param maxCodeLen The maxCodeLen to set
       */
      public void setMaxCodeLen(int maxCodeLen) { this.maxCodeLen = maxCodeLen; }
  }
```

Changes made (behaviour is identical):

┌────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────┐
│ What changed                                                       │ Why                                             │
├────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────┤
│ StringBuffer local / StringBuffer code → StringBuilder             │ StringBuilder is the modern, unsynchronized     │
│                                                                    │ replacement; same API                           │
├────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────┤
│ private String vowels/frontv/varson instance fields → private      │ They are never mutated; static final is correct │
│ static final String VOWELS/FRONTV/VARSON constants                 │ and avoids per-instance allocation              │
├────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────┤
│ All private helper method signatures updated from StringBuffer to  │ Matches the new field types                     │
│ StringBuilder                                                      │                                                 │
├────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────┤
│ java.lang.String cast kept, but instanceof java.lang.String        │ Redundant fully-qualified name removed          │
│ shortened to instanceof String                                     │                                                 │
├────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────┤
│ Added @Override on both encode overloads                           │ Explicit contract with StringEncoder; was just  │
│                                                                    │ missing                                         │
├────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────┤
│ Removed boolean matches intermediate variable in isPreviousChar /  │ Simplified to direct return; same logic         │
│ isNextChar / regionMatch                                           │                                                 │
├────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────┤
│ hard = true/false inside case 'G' collapsed into single ternary    │ Identical semantics, less noise                 │
│ assignment                                                         │                                                 │
├────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────┤
│ No java.time, no raw collections, no deprecated APIs were present  │ —                                               │
│ — nothing else to change                                           │                                                 │
└────────────────────────────────────────────────────────────────────┴─────────────────────────────────────────────────┘

````

## Raw Bob output

````

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
User (1) 2026-09-26 12:25:19.616 UTC (+0.6s)

Modernize this legacy Java class.                                                                                       
                                                                                                                        
Request from the developer: Bring this class up to modern Java 21: generics instead of raw collections, java.time       
instead of Calendar, StringBuilder, no deprecated APIs. Behaviour must stay exactly the same.                           
                                                                                                                        
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
Assistant (1) 2026-09-26 12:25:21.775 UTC (+2.7s)

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
                                                                                                                        
      /** Five vowels in the English language */                                                                        
      private static final String VOWELS = "AEIOU";                                                                     
                                                                                                                        
      /** Variable used in Metaphone algorithm */                                                                       
      private static final String FRONTV = "EIY";                                                                       
                                                                                                                        
      /** Variable used in Metaphone algorithm */                                                                       
      private static final String VARSON = "CSPTG";                                                                     
                                                                                                                        
      /** The max code length for metaphone is 4 */                                                                     
      private int maxCodeLen = 4;                                                                                       
                                                                                                                        
      /**                                                                                                               
       * Creates an instance of the Metaphone encoder.                                                                  
       */                                                                                                               
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
          boolean hard = false;                                                                                         
          if ((txt == null) || (txt.length() == 0)) {                                                                   
              return "";                                                                                                
          }                                                                                                             
          // single character is itself                                                                                 
          if (txt.length() == 1) {                                                                                      
              return txt.toUpperCase();                                                                                 
          }                                                                                                             
                                                                                                                        
          char[] inwd = txt.toUpperCase().toCharArray();                                                                
                                                                                                                        
          StringBuilder local = new StringBuilder(40); // manipulate                                                    
          StringBuilder code  = new StringBuilder(10); // output                                                        
                                                                                                                        
          // handle initial 2 characters exceptions                                                                     
          switch (inwd[0]) {                                                                                            
              case 'K':                                                                                                 
              case 'G':                                                                                                 
              case 'P': /* looking for KN, etc */                                                                       
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
              case 'W': /* looking for WR or WH */                                                                      
                  if (inwd[1] == 'R') {   // WR -> R                                                                    
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
              case 'X': /* initial X becomes S */                                                                       
                  inwd[0] = 'S';                                                                                        
                  local.append(inwd);                                                                                   
                  break;                                                                                                
              default:                                                                                                  
                  local.append(inwd);                                                                                   
          } // now local has working string with initials fixed                                                         
                                                                                                                        
          int wdsz = local.length();                                                                                    
          int n = 0;                                                                                                    
                                                                                                                        
          while ((code.length() < this.getMaxCodeLen()) && (n < wdsz)) {                                                
              char symb = local.charAt(n);                                                                              
              // remove duplicate letters except C                                                                      
              if ((symb != 'C') && isPreviousChar(local, n, symb)) {                                                    
                  n++;                                                                                                  
              } else { // not dup                                                                                       
                  switch (symb) {                                                                                       
                      case 'A': case 'E': case 'I': case 'O': case 'U':                                                 
                          if (n == 0) {                                                                                 
                              code.append(symb);                                                                        
                          }                                                                                             
                          break; // only use vowel if leading char                                                      
                      case 'B':                                                                                         
                          // B is silent if word ends in MB                                                             
                          if (isPreviousChar(local, n, 'M') && isLastChar(wdsz, n)) {                                   
                              break;                                                                                    
                          }                                                                                             
                          code.append(symb);                                                                            
                          break;                                                                                        
                      case 'C': // lots of C special cases                                                              
                          /* discard if SCI, SCE or SCY */                                                              
                          if (isPreviousChar(local, n, 'S') &&                                                          
                                  !isLastChar(wdsz, n) &&                                                               
                                  (FRONTV.indexOf(local.charAt(n + 1)) >= 0)) {                                         
                              break;                                                                                    
                          }                                                                                             
                          if (regionMatch(local, n, "CIA")) { // "CIA" -> X                                             
                              code.append('X');                                                                         
                              break;                                                                                    
                          }                                                                                             
                          if (!isLastChar(wdsz, n) &&                                                                   
                                  (FRONTV.indexOf(local.charAt(n + 1)) >= 0)) {                                         
                              code.append('S');                                                                         
                              break; // CI,CE,CY -> S                                                                   
                          }                                                                                             
                          if (isPreviousChar(local, n, 'S') && isNextChar(local, n, 'H')) { // SCH->sk                  
                              code.append('K');                                                                         
                              break;                                                                                    
                          }                                                                                             
                          if (isNextChar(local, n, 'H')) { // detect CH                                                 
                              if ((n == 0) && (wdsz >= 3) && isVowel(local, 2)) {                                       
                                  code.append('K'); // CH consonant -> K consonant                                      
                              } else {                                                                                  
                                  code.append('X'); // CHvowel -> X                                                     
                              }                                                                                         
                          } else {                                                                                      
                              code.append('K');                                                                         
                          }                                                                                             
                          break;                                                                                        
                      case 'D':                                                                                         
                          if (!isLastChar(wdsz, n + 1) &&                                                               
                                  isNextChar(local, n, 'G') &&                                                          
                                  (FRONTV.indexOf(local.charAt(n + 2)) >= 0)) { // DGE DGI DGY -> J                     
                              code.append('J');                                                                         
                              n += 2;                                                                                   
                          } else {                                                                                      
                              code.append('T');                                                                         
                          }                                                                                             
                          break;                                                                                        
                      case 'G': // GH silent at end or before consonant                                                 
                          if (isLastChar(wdsz, n + 1) && isNextChar(local, n, 'H')) {                                   
                              break;                                                                                    
                          }                                                                                             
                          if (!isLastChar(wdsz, n + 1) &&                                                               
                                  isNextChar(local, n, 'H') &&                                                          
                                  !isVowel(local, n + 2)) {                                                             
                              break;                                                                                    
                          }                                                                                             
                          if ((n > 0) &&                                                                                
                                  (regionMatch(local, n, "GN") || regionMatch(local, n, "GNED"))) {                     
                              break; // silent G                                                                        
                          }                                                                                             
                          hard = isPreviousChar(local, n, 'G');                                                         
                          if (!isLastChar(wdsz, n) &&                                                                   
                                  (FRONTV.indexOf(local.charAt(n + 1)) >= 0) &&                                         
                                  !hard) {                                                                              
                              code.append('J');                                                                         
                          } else {                                                                                      
                              code.append('K');                                                                         
                          }                                                                                             
                          break;                                                                                        
                      case 'H':                                                                                         
                          if (isLastChar(wdsz, n)) {                                                                    
                              break; // terminal H                                                                      
                          }                                                                                             
                          if ((n > 0) && (VARSON.indexOf(local.charAt(n - 1)) >= 0)) {                                  
                              break;                                                                                    
                          }                                                                                             
                          if (isVowel(local, n + 1)) {                                                                  
                              code.append('H'); // Hvowel                                                               
                          }                                                                                             
                          break;                                                                                        
                      case 'F':                                                                                         
                      case 'J':                                                                                         
                      case 'L':                                                                                         
                      case 'M':                                                                                         
                      case 'N':                                                                                         
                      case 'R':                                                                                         
                          code.append(symb);                                                                            
                          break;                                                                                        
                      case 'K':                                                                                         
                          if (n > 0) { // not initial                                                                   
                              if (!isPreviousChar(local, n, 'C')) {                                                     
                                  code.append(symb);                                                                    
                              }                                                                                         
                          } else {                                                                                      
                              code.append(symb); // initial K                                                           
                          }                                                                                             
                          break;                                                                                        
                      case 'P':                                                                                         
                          if (isNextChar(local, n, 'H')) {                                                              
                              code.append('F'); // PH -> F                                                              
                          } else {                                                                                      
                              code.append(symb);                                                                        
                          }                                                                                             
                          break;                                                                                        
                      case 'Q':                                                                                         
                          code.append('K');                                                                             
                          break;                                                                                        
                      case 'S':                                                                                         
                          if (regionMatch(local, n, "SH") ||                                                            
                                  regionMatch(local, n, "SIO") ||                                                       
                                  regionMatch(local, n, "SIA")) {                                                       
                              code.append('X');                                                                         
                          } else {                                                                                      
                              code.append('S');                                                                         
                          }                                                                                             
                          break;                                                                                        
                      case 'T':                                                                                         
                          if (regionMatch(local, n, "TIA") || regionMatch(local, n, "TIO")) {                           
                              code.append('X');                                                                         
                              break;                                                                                    
                          }                                                                                             
                          if (regionMatch(local, n, "TCH")) {                                                           
                              break; // silent if in "TCH"                                                              
                          }                                                                                             
                          // substitute numeral 0 for TH (resembles theta after all)                                    
                          if (regionMatch(local, n, "TH")) {                                                            
                              code.append('0');                                                                         
                          } else {                                                                                      
                              code.append('T');                                                                         
                          }                                                                                             
                          break;                                                                                        
                      case 'V':                                                                                         
                          code.append('F');                                                                             
                          break;                                                                                        
                      case 'W': case 'Y': // silent if not followed by vowel                                            
                          if (!isLastChar(wdsz, n) && isVowel(local, n + 1)) {                                          
                              code.append(symb);                                                                        
                          }                                                                                             
                          break;                                                                                        
                      case 'X':                                                                                         
                          code.append('K');                                                                             
                          code.append('S');                                                                             
                          break;                                                                                        
                      case 'Z':                                                                                         
                          code.append('S');                                                                             
                          break;                                                                                        
                  } // end switch                                                                                       
                  n++;                                                                                                  
              } // end else from symb != 'C'                                                                            
              if (code.length() > this.getMaxCodeLen()) {                                                               
                  code.setLength(this.getMaxCodeLen());                                                                 
              }                                                                                                         
          }                                                                                                             
          return code.toString();                                                                                       
      }                                                                                                                 
                                                                                                                        
      private boolean isVowel(StringBuilder string, int index) {                                                        
          return (VOWELS.indexOf(string.charAt(index)) >= 0);                                                           
      }                                                                                                                 
                                                                                                                        
      private boolean isPreviousChar(StringBuilder string, int index, char c) {                                         
          if (index > 0 && index < string.length()) {                                                                   
              return string.charAt(index - 1) == c;                                                                     
          }                                                                                                             
          return false;                                                                                                 
      }                                                                                                                 
                                                                                                                        
      private boolean isNextChar(StringBuilder string, int index, char c) {                                             
          if (index >= 0 && index < string.length() - 1) {                                                              
              return string.charAt(index + 1) == c;                                                                     
          }                                                                                                             
          return false;                                                                                                 
      }                                                                                                                 
                                                                                                                        
      private boolean regionMatch(StringBuilder string, int index, String test) {                                       
          if (index >= 0 && (index + test.length() - 1) < string.length()) {                                            
              return string.substring(index, index + test.length()).equals(test);                                       
          }                                                                                                             
          return false;                                                                                                 
      }                                                                                                                 
                                                                                                                        
      private boolean isLastChar(int wdsz, int n) {                                                                     
          return n + 1 == wdsz;                                                                                         
      }                                                                                                                 
                                                                                                                        
      /**                                                                                                               
       * Encodes an Object using the metaphone algorithm. This method is provided in order to                           
       * satisfy the requirements of the Encoder interface, and will throw an EncoderException                          
       * if the supplied object is not of type java.lang.String.                                                        
       *                                                                                                                
       * @param pObject Object to encode                                                                                
       * @return An object (or type java.lang.String) containing the metaphone code which                               
       *         corresponds to the String supplied.                                                                    
       * @throws EncoderException if the parameter supplied is not of type java.lang.String                             
       */                                                                                                               
      @Override                                                                                                         
      public Object encode(Object pObject) throws EncoderException {                                                    
          if (!(pObject instanceof String)) {                                                                           
              throw new EncoderException(                                                                               
                  "Parameter supplied to Metaphone encode is not of type java.lang.String");                            
          }                                                                                                             
          return metaphone((String) pObject);                                                                           
      }                                                                                                                 
                                                                                                                        
      /**                                                                                                               
       * Encodes a String using the Metaphone algorithm.                                                                
       *                                                                                                                
       * @param pString String object to encode                                                                         
       * @return The metaphone code corresponding to the String supplied                                                
       */                                                                                                               
      @Override                                                                                                         
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
       *                                                                                                                
       * @return int                                                                                                    
       */                                                                                                               
      public int getMaxCodeLen() { return this.maxCodeLen; }                                                            
                                                                                                                        
      /**                                                                                                               
       * Sets the maxCodeLen.                                                                                           
       *                                                                                                                
       * @param maxCodeLen The maxCodeLen to set                                                                        
       */                                                                                                               
      public void setMaxCodeLen(int maxCodeLen) { this.maxCodeLen = maxCodeLen; }                                       
  }                                                                                                                     
```                                                                                                                     
                                                                                                                        
Changes made (behaviour is identical):                                                                                  
                                                                                                                        
┌────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────┐
│ What changed                                                       │ Why                                             │
├────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────┤
│ StringBuffer local / StringBuffer code → StringBuilder             │ StringBuilder is the modern, unsynchronized     │
│                                                                    │ replacement; same API                           │
├────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────┤
│ private String vowels/frontv/varson instance fields → private      │ They are never mutated; static final is correct │
│ static final String VOWELS/FRONTV/VARSON constants                 │ and avoids per-instance allocation              │
├────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────┤
│ All private helper method signatures updated from StringBuffer to  │ Matches the new field types                     │
│ StringBuilder                                                      │                                                 │
├────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────┤
│ java.lang.String cast kept, but instanceof java.lang.String        │ Redundant fully-qualified name removed          │
│ shortened to instanceof String                                     │                                                 │
├────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────┤
│ Added @Override on both encode overloads                           │ Explicit contract with StringEncoder; was just  │
│                                                                    │ missing                                         │
├────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────┤
│ Removed boolean matches intermediate variable in isPreviousChar /  │ Simplified to direct return; same logic         │
│ isNextChar / regionMatch                                           │                                                 │
├────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────┤
│ hard = true/false inside case 'G' collapsed into single ternary    │ Identical semantics, less noise                 │
│ assignment                                                         │                                                 │
├────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────┤
│ No java.time, no raw collections, no deprecated APIs were present  │ —                                               │
│ — nothing else to change                                           │                                                 │
└────────────────────────────────────────────────────────────────────┴─────────────────────────────────────────────────┘
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

Task Summary

Total Cost:              0.044
Total Duration:          39.3s


Assistant Messages:      1
Tool Calls:              0
Task ID:                 c87f1d070f039336b41e58ff5dc25ee8

````
