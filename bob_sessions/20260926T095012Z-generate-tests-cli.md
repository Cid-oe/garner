# Bob session: generate-tests

- Started: 20260926T095012Z
- Command: `bob -p <prompt>`
- Duration: 243.9s
- Bob cost: 0.533

## Prompt

````
You are writing characterization tests for a legacy Java class before it is modernized.

Goal: pin down what the code DOES today, including odd behaviour, so any change in behaviour
during modernization makes a test fail. Do not test what the comments say it should do; test
what it actually does. Where the code and its javadoc disagree, the code wins.

Requirements:
- One JUnit 5 test class named `InvoiceCalculatorCharacterizationTest` in package `com.acme.billing`.
- Use only JUnit 5 (org.junit.jupiter.api) and the JDK. No other libraries.
- Call only the public API of `InvoiceCalculator` shown below; keep test inputs deterministic.
- Cover boundaries (e.g. quantities around discount thresholds), rounding of half-cent values,
  input normalisation (whitespace, letter case, null), error cases, and date edge cases.
- Every test must pass against the code exactly as written below.
- Reply with the complete test class in a single ```java code block. Keep every line under 100 characters.

```java
package com.acme.billing;

import java.math.BigDecimal;
import java.util.Calendar;
import java.util.Date;
import java.util.Enumeration;
import java.util.GregorianCalendar;
import java.util.Hashtable;
import java.util.StringTokenizer;
import java.util.Vector;

/**
 * Invoice calculation for the ACME order desk.
 *
 * Originally written for J2SE 1.4 (2004). Finance reconciles against these
 * exact numbers every month, so do not change results without sign-off.
 *   -- rk, 2004-03-11
 *   -- jt, 2009-06-02: added staff discount, due dates
 */
public class InvoiceCalculator {

    public static final String TYPE_RETAIL = "RETAIL";
    public static final String TYPE_WHOLESALE = "WHOLESALE";
    public static final String TYPE_STAFF = "STAFF";

    /** Sales tax, applied once to the discounted subtotal. */
    private static final double TAX_RATE = 0.0825;

    /** Payment terms in days. */
    private static final int PAYMENT_TERMS_DAYS = 30;

    /** sku (String) -> unit price (Double) */
    private Hashtable priceList = new Hashtable();

    public InvoiceCalculator() {
        priceList.put("WIDGET", new Double(2.50));
        priceList.put("GADGET", new Double(12.99));
        priceList.put("GIZMO", new Double(0.125));
        priceList.put("DOOHICKEY", new Double(49.95));
    }

    public void setPrice(String sku, double price) {
        if (sku == null) {
            throw new IllegalArgumentException("sku is required");
        }
        if (price < 0) {
            throw new IllegalArgumentException("price must not be negative: " + price);
        }
        priceList.put(sku.toUpperCase(), new Double(price));
    }

    public double getPrice(String sku) {
        if (sku == null) {
            throw new IllegalArgumentException("sku is required");
        }
        Double price = (Double) priceList.get(sku.trim().toUpperCase());
        if (price == null) {
            throw new IllegalArgumentException("unknown sku: " + sku);
        }
        return price.doubleValue();
    }

    /**
     * Normalises a customer type as typed by the order desk.
     * Blank or missing means retail; unknown types are treated as retail.
     */
    public String normalizeCustomerType(String raw) {
        if (raw == null) {
            return TYPE_RETAIL;
        }
        String t = raw.trim();
        if (t.length() == 0) {
            return TYPE_RETAIL;
        }
        if (t.equalsIgnoreCase(TYPE_WHOLESALE)) {
            return TYPE_WHOLESALE;
        } else if (t.equalsIgnoreCase(TYPE_STAFF)) {
            return TYPE_STAFF;
        } else if (t.equalsIgnoreCase(TYPE_RETAIL)) {
            return TYPE_RETAIL;
        }
        return TYPE_RETAIL;
    }

    /** Discount for the customer type, as a fraction. */
    public double customerDiscountRate(String customerType) {
        String t = normalizeCustomerType(customerType);
        if (t.equals(TYPE_WHOLESALE)) {
            return 0.15;
        } else if (t.equals(TYPE_STAFF)) {
            return 0.25;
        }
        return 0.0;
    }

    /**
     * Volume discount: orders of 10 or more units get 5% off,
     * orders of 50 or more get 10% off.
     */
    public double volumeDiscountRate(int quantity) {
        if (quantity > 50) {
            return 0.10;
        }
        if (quantity > 10) {
            return 0.05;
        }
        return 0.0;
    }

    /**
     * Total for one invoice line. Customer and volume discounts do not stack:
     * the larger of the two applies. Rounded to cents.
     */
    public BigDecimal lineTotal(String sku, int quantity, String customerType) {
        if (quantity <= 0) {
            throw new IllegalArgumentException("quantity must be positive: " + quantity);
        }
        BigDecimal gross = BigDecimal.valueOf(getPrice(sku)).multiply(new BigDecimal(quantity));
        double rate = customerDiscountRate(customerType);
        double volume = volumeDiscountRate(quantity);
        if (volume > rate) {
            rate = volume;
        }
        BigDecimal net = gross.multiply(BigDecimal.ONE.subtract(BigDecimal.valueOf(rate)));
        return net.setScale(2, BigDecimal.ROUND_HALF_EVEN);
    }

    /**
     * Parses order lines in the order desk's "SKU:QTY" format.
     * Blank lines are ignored; anything else malformed is rejected.
     */
    public Vector parseLines(Vector rawLines) {
        Vector parsed = new Vector();
        for (Enumeration e = rawLines.elements(); e.hasMoreElements();) {
            String line = (String) e.nextElement();
            if (line == null || line.trim().length() == 0) {
                continue;
            }
            StringTokenizer tok = new StringTokenizer(line, ":");
            if (tok.countTokens() != 2) {
                throw new IllegalArgumentException("malformed line: " + line);
            }
            String sku = tok.nextToken().trim();
            int qty;
            try {
                qty = Integer.parseInt(tok.nextToken().trim());
            } catch (NumberFormatException nfe) {
                throw new IllegalArgumentException("bad quantity in line: " + line);
            }
            parsed.addElement(new Object[] { sku, new Integer(qty) });
        }
        return parsed;
    }

    /** Sum of line totals before tax. */
    public BigDecimal subtotal(Vector rawLines, String customerType) {
        BigDecimal sum = new BigDecimal("0.00");
        Vector lines = parseLines(rawLines);
        for (int i = 0; i < lines.size(); i++) {
            Object[] l = (Object[]) lines.elementAt(i);
            sum = sum.add(lineTotal((String) l[0], ((Integer) l[1]).intValue(), customerType));
        }
        return sum;
    }

    /** Tax on a subtotal, rounded to cents. */
    public BigDecimal tax(BigDecimal subtotal) {
        return subtotal.multiply(BigDecimal.valueOf(TAX_RATE)).setScale(2, BigDecimal.ROUND_HALF_EVEN);
    }

    /** Grand total: subtotal plus tax. Staff purchases are tax exempt. */
    public BigDecimal invoiceTotal(Vector rawLines, String customerType) {
        BigDecimal sub = subtotal(rawLines, customerType);
        if (normalizeCustomerType(customerType).equals(TYPE_STAFF)) {
            return sub;
        }
        return sub.add(tax(sub));
    }

    /**
     * Payment due date: invoice date plus payment terms. If that lands on a
     * weekend, it moves to the following Monday.
     */
    public Date dueDate(Date invoiceDate) {
        Calendar cal = new GregorianCalendar();
        cal.setTime(invoiceDate);
        cal.add(Calendar.DAY_OF_MONTH, PAYMENT_TERMS_DAYS);
        int dow = cal.get(Calendar.DAY_OF_WEEK);
        if (dow == Calendar.SATURDAY) {
            cal.add(Calendar.DAY_OF_MONTH, 2);
        } else if (dow == Calendar.SUNDAY) {
            cal.add(Calendar.DAY_OF_MONTH, 1);
        }
        return cal.getTime();
    }

    /** Plain-text invoice for the printer. */
    public String formatInvoice(Vector rawLines, String customerType) {
        StringBuffer sb = new StringBuffer();
        String type = normalizeCustomerType(customerType);
        sb.append("INVOICE (").append(type).append(")\n");
        Vector lines = parseLines(rawLines);
        for (int i = 0; i < lines.size(); i++) {
            Object[] l = (Object[]) lines.elementAt(i);
            String sku = (String) l[0];
            int qty = ((Integer) l[1]).intValue();
            sb.append(sku).append(" x").append(qty).append(" = ")
              .append(lineTotal(sku, qty, customerType)).append("\n");
        }
        BigDecimal sub = subtotal(rawLines, customerType);
        sb.append("SUBTOTAL ").append(sub).append("\n");
        if (!type.equals(TYPE_STAFF)) {
            sb.append("TAX ").append(tax(sub)).append("\n");
        }
        sb.append("TOTAL ").append(invoiceTotal(rawLines, customerType)).append("\n");
        return sb.toString();
    }
}

```

````

## Bob's answer

````
Looking at the code carefully before writing the tests. Let me trace the actual behavior:

Tool calls:
- spawn_subagent

Tool (1) 2026-09-26 09:51:54.541 UTC (+101.9s) Success

Tool: spawn_subagent
Args:
- description: Analyze the following Java class and compute exact expected values for characterization tests. Trace through the code...




All computed values are confirmed. Now I have everything I need to write the complete characterization test class.

Tool calls:
- write_file

Tool (2) 2026-09-26 09:52:45.371 UTC (+152.7s) Success

Tool: write_file
Args:
- path: /tmp/bob-bridge-xiv_f1z6/InvoiceCalculatorCharacterizationTest.java
- line_count: 349
- content: package com.acme.billing;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.m...

Files changed:
  ~ file:///tmp/bob-bridge-xiv_f1z6/InvoiceCalculatorCharacterizationTest.java



Now let me verify all the arithmetic by actually running the production class + tests together:

Tool calls:
- execute_command

Tool (3) 2026-09-26 09:53:03.491 UTC (+170.8s) Success

Tool: execute_command
Args:
- command:
# Create the full directory structure and compile+run the tests
mkdir -p /tmp/acme-billing-verify/src/com/acme/billi...

Tool (4) 2026-09-26 09:53:10.162 UTC (+177.5s) Success

Tool: execute_command
Args:
- command:
# Copy the test class
cp /tmp/bob-bridge-xiv_f1z6/InvoiceCalculatorCharacterizationTest.java \
   /tmp/acme-billing-...
- timeout_seconds: 60

Tool (5) 2026-09-26 09:53:13.836 UTC (+181.2s) Success

Tool: execute_command
Args:
- command:
JUNIT_DIR=/tmp/junit5-jars
SRC=/tmp/acme-billing-verify/src
OUT=/tmp/acme-billing-verify/out
mkdir -p "$OUT"

CP="$J...

Tool (6) 2026-09-26 09:53:17.114 UTC (+184.4s) Success

Tool: execute_command
Args:
- command:
JUNIT_DIR=/tmp/junit5-jars
OUT=/tmp/acme-billing-verify/out

java -jar "$JUNIT_DIR/junit-platform-console-standalone...
- timeout_seconds: 30



61/61 tests pass. Here is the complete test class:

```java
  package com.acme.billing;

  import org.junit.jupiter.api.BeforeEach;
  import org.junit.jupiter.api.Test;

  import java.math.BigDecimal;
  import java.util.Calendar;
  import java.util.GregorianCalendar;
  import java.util.Vector;
  import java.util.Date;

  import static org.junit.jupiter.api.Assertions.*;

  /**
   * Characterization tests for {@link InvoiceCalculator}.
   *
   * These tests pin down what the code DOES today, including edge cases and
   * rounding quirks, so that any change in behaviour during modernisation causes
   * at least one test to fail. Comments note where behaviour is surprising.
   */
  class InvoiceCalculatorCharacterizationTest {

      private InvoiceCalculator calc;

      @BeforeEach
      void setUp() {
          calc = new InvoiceCalculator();
      }

      // =========================================================================
      // normalizeCustomerType
      // =========================================================================

      @Test
      void normalizeNull_returnsRetail() {
          assertEquals(InvoiceCalculator.TYPE_RETAIL, calc.normalizeCustomerType(null));
      }

      @Test
      void normalizeEmpty_returnsRetail() {
          assertEquals(InvoiceCalculator.TYPE_RETAIL, calc.normalizeCustomerType(""));
      }

      @Test
      void normalizeBlank_returnsRetail() {
          assertEquals(InvoiceCalculator.TYPE_RETAIL, calc.normalizeCustomerType("   "));
      }

      @Test
      void normalizeRetailExact_returnsRetail() {
          assertEquals(InvoiceCalculator.TYPE_RETAIL, calc.normalizeCustomerType("RETAIL"));
      }

      @Test
      void normalizeRetailLower_returnsRetail() {
          assertEquals(InvoiceCalculator.TYPE_RETAIL, calc.normalizeCustomerType("retail"));
      }

      @Test
      void normalizeWholesaleExact_returnsWholesale() {
          assertEquals(InvoiceCalculator.TYPE_WHOLESALE, calc.normalizeCustomerType("WHOLESALE"));
      }

      @Test
      void normalizeWholesaleMixedCaseWithPadding_returnsWholesale() {
          assertEquals(InvoiceCalculator.TYPE_WHOLESALE, calc.normalizeCustomerType(" Wholesale "));
      }

      @Test
      void normalizeStaffLower_returnsStaff() {
          assertEquals(InvoiceCalculator.TYPE_STAFF, calc.normalizeCustomerType("staff"));
      }

      @Test
      void normalizeUnknownString_returnsRetail() {
          // Unknown types silently fall back to RETAIL
          assertEquals(InvoiceCalculator.TYPE_RETAIL, calc.normalizeCustomerType("FOOBAR"));
      }

      // =========================================================================
      // customerDiscountRate
      // =========================================================================

      @Test
      void customerDiscountRate_retail_isZero() {
          assertEquals(0.0, calc.customerDiscountRate("RETAIL"), 0.0);
      }

      @Test
      void customerDiscountRate_null_isZeroLikeRetail() {
          // null normalises to RETAIL → 0 % discount
          assertEquals(0.0, calc.customerDiscountRate(null), 0.0);
      }

      @Test
      void customerDiscountRate_wholesale_is15Percent() {
          assertEquals(0.15, calc.customerDiscountRate("WHOLESALE"), 0.0);
      }

      @Test
      void customerDiscountRate_staff_is25Percent() {
          assertEquals(0.25, calc.customerDiscountRate("STAFF"), 0.0);
      }

      @Test
      void customerDiscountRate_unknownType_isZero() {
          assertEquals(0.0, calc.customerDiscountRate("MYSTERY"), 0.0);
      }

      // =========================================================================
      // volumeDiscountRate  (threshold is STRICTLY greater-than, not >=)
      // =========================================================================

      @Test
      void volumeDiscount_qty1_isZero() {
          assertEquals(0.0, calc.volumeDiscountRate(1), 0.0);
      }

      @Test
      void volumeDiscount_qty10_isZero() {
          // qty == 10 does NOT qualify; condition is qty > 10
          assertEquals(0.0, calc.volumeDiscountRate(10), 0.0);
      }

      @Test
      void volumeDiscount_qty11_is5Percent() {
          assertEquals(0.05, calc.volumeDiscountRate(11), 0.0);
      }

      @Test
      void volumeDiscount_qty50_is5Percent() {
          // qty == 50 does NOT qualify for the 10 % tier; condition is qty > 50
          assertEquals(0.05, calc.volumeDiscountRate(50), 0.0);
      }

      @Test
      void volumeDiscount_qty51_is10Percent() {
          assertEquals(0.10, calc.volumeDiscountRate(51), 0.0);
      }

      // =========================================================================
      // getPrice / setPrice
      // =========================================================================

      @Test
      void getPrice_knownSku_returnsPrice() {
          assertEquals(2.50, calc.getPrice("WIDGET"), 0.0);
          assertEquals(12.99, calc.getPrice("GADGET"), 0.0);
          assertEquals(0.125, calc.getPrice("GIZMO"), 0.0);
          assertEquals(49.95, calc.getPrice("DOOHICKEY"), 0.0);
      }

      @Test
      void getPrice_trims_andUppercases() {
          // getPrice trims whitespace and upper-cases before lookup
          assertEquals(2.50, calc.getPrice("  widget  "), 0.0);
      }

      @Test
      void getPrice_nullSku_throwsIllegalArgument() {
          assertThrows(IllegalArgumentException.class, () -> calc.getPrice(null));
      }

      @Test
      void getPrice_unknownSku_throwsIllegalArgument() {
          assertThrows(IllegalArgumentException.class, () -> calc.getPrice("UNKNOWN_SKU"));
      }

      @Test
      void setPrice_nullSku_throwsIllegalArgument() {
          assertThrows(IllegalArgumentException.class, () -> calc.setPrice(null, 1.0));
      }

      @Test
      void setPrice_negativePrice_throwsIllegalArgument() {
          assertThrows(IllegalArgumentException.class, () -> calc.setPrice("WIDGET", -0.01));
      }

      @Test
      void setPrice_zeroPriceIsAllowed() {
          // price == 0 satisfies "price < 0" == false, so no exception
          assertDoesNotThrow(() -> calc.setPrice("WIDGET", 0.0));
          assertEquals(0.0, calc.getPrice("WIDGET"), 0.0);
      }

      @Test
      void setPrice_uppercasesTheSku() {
          calc.setPrice("newitem", 5.00);
          assertEquals(5.00, calc.getPrice("NEWITEM"), 0.0);
      }

      // =========================================================================
      // lineTotal — basic cases
      // =========================================================================

      @Test
      void lineTotal_qty0_throwsIllegalArgument() {
          assertThrows(IllegalArgumentException.class,
                  () -> calc.lineTotal("WIDGET", 0, "RETAIL"));
      }

      @Test
      void lineTotal_negativeQty_throwsIllegalArgument() {
          assertThrows(IllegalArgumentException.class,
                  () -> calc.lineTotal("WIDGET", -1, "RETAIL"));
      }

      @Test
      void lineTotal_retail_noDiscount_roundsCorrectly() {
          // 1 × $2.50, no discount → $2.50
          assertEquals(new BigDecimal("2.50"), calc.lineTotal("WIDGET", 1, "RETAIL"));
      }

      @Test
      void lineTotal_wholesale_appliesCustomerDiscount() {
          // 1 × $12.99, 15 % off = $11.0415 → ROUND_HALF_EVEN → $11.04
          assertEquals(new BigDecimal("11.04"), calc.lineTotal("GADGET", 1, "WHOLESALE"));
      }

      @Test
      void lineTotal_staff_appliesCustomerDiscount() {
          // 1 × $2.50, 25 % off = $1.875 → ROUND_HALF_EVEN (digit before 5 is 7, odd → round up)
          // $1.875 → retained digit is 7 (odd) → 1.88
          assertEquals(new BigDecimal("1.88"), calc.lineTotal("WIDGET", 1, "STAFF"));
      }

      // =========================================================================
      // lineTotal — volume discount threshold boundary
      // =========================================================================

      @Test
      void lineTotal_qty10_noVolumeDiscount() {
          // qty == 10 falls below the > 10 threshold: no discount
          assertEquals(new BigDecimal("25.00"), calc.lineTotal("WIDGET", 10, "RETAIL"));
      }

      @Test
      void lineTotal_qty11_volumeDiscountApplied_halfEvenRoundsDown() {
          // 11 × $2.50 = $27.50; 5 % off = $26.125
          // ROUND_HALF_EVEN: retained digit 2 is even → round down to $26.12
          assertEquals(new BigDecimal("26.12"), calc.lineTotal("WIDGET", 11, "RETAIL"));
      }

      @Test
      void lineTotal_qty50_5PctVolumeDiscount() {
          // qty == 50: > 10 but NOT > 50, so 5 %
          // 50 × $2.50 = $125.00; 5 % off = $118.75
          assertEquals(new BigDecimal("118.75"), calc.lineTotal("WIDGET", 50, "RETAIL"));
      }

      @Test
      void lineTotal_qty51_10PctVolumeDiscount() {
          // qty == 51: > 50, so 10 %
          // 51 × $2.50 = $127.50; 10 % off = $114.75
          assertEquals(new BigDecimal("114.75"), calc.lineTotal("WIDGET", 51, "RETAIL"));
      }

      // =========================================================================
      // lineTotal — larger customer discount wins over volume discount
      // =========================================================================

      @Test
      void lineTotal_staff_qty51_customerDiscountBeatsVolume() {
          // STAFF = 25 %, volume(51) = 10 %. 10 % is NOT > 25 % → use 25 %
          // 51 × $2.50 = $127.50; 25 % off = $95.625
          // ROUND_HALF_EVEN: retained digit 6 (even) → round down → $95.62
          assertEquals(new BigDecimal("95.62"), calc.lineTotal("WIDGET", 51, "STAFF"));
      }

      @Test
      void lineTotal_wholesale_qty51_customerDiscountBeatsVolume() {
          // WHOLESALE = 15 %, volume(51) = 10 %. 10 % is NOT > 15 % → use 15 %
          // 51 × $2.50 = $127.50; 15 % off = $108.375
          // ROUND_HALF_EVEN: retained digit 3 (odd) → round up → $108.38
          assertEquals(new BigDecimal("108.38"), calc.lineTotal("WIDGET", 51, "WHOLESALE"));
      }

      // =========================================================================
      // lineTotal — GIZMO: price exactly $0.125, half-even rounding
      // =========================================================================

      @Test
      void lineTotal_gizmo_qty1_retail_halfEvenRoundsDown() {
          // GIZMO price = 0.125 (exact in IEEE-754); BigDecimal.valueOf(0.125) = "0.125"
          // 1 × $0.125 = $0.125; ROUND_HALF_EVEN: retained digit 2 is even → $0.12
          assertEquals(new BigDecimal("0.12"), calc.lineTotal("GIZMO", 1, "RETAIL"));
      }

      @Test
      void lineTotal_gizmo_qty2_retail() {
          // 2 × $0.125 = $0.25 (exact) → $0.25
          assertEquals(new BigDecimal("0.25"), calc.lineTotal("GIZMO", 2, "RETAIL"));
      }

      // =========================================================================
      // tax
      // =========================================================================

      @Test
      void tax_roundNumber_noRounding() {
          // $100.00 × 8.25 % = $8.25 exactly
          assertEquals(new BigDecimal("8.25"), calc.tax(new BigDecimal("100.00")));
      }

      @Test
      void tax_halfCentCase_oddDigitRoundsUp() {
          // $14.00 × 0.0825 = $1.155; retained digit 5 (odd) → round up → $1.16
          assertEquals(new BigDecimal("1.16"), calc.tax(new BigDecimal("14.00")));
      }

      @Test
      void tax_widget_singleUnit() {
          // $2.50 × 0.0825 = $0.20625; third decimal 6 > 5 → round up unconditionally → $0.21
          assertEquals(new BigDecimal("0.21"), calc.tax(new BigDecimal("2.50")));
      }

      @Test
      void tax_zero_isZero() {
          assertEquals(new BigDecimal("0.00"), calc.tax(new BigDecimal("0.00")));
      }

      // =========================================================================
      // invoiceTotal — tax applied for retail/wholesale; exempt for staff
      // =========================================================================

      @Test
      void invoiceTotal_retail_includesTax() {
          Vector lines = new Vector();
          lines.addElement("WIDGET:1");
          // subtotal = $2.50; tax = $0.21; total = $2.71
          assertEquals(new BigDecimal("2.71"), calc.invoiceTotal(lines, "RETAIL"));
      }

      @Test
      void invoiceTotal_wholesale_includesTax() {
          Vector lines = new Vector();
          lines.addElement("GADGET:1");
          // subtotal = $11.04; tax = $11.04 × 0.0825 = $0.9108 → $0.91; total = $11.95
          assertEquals(new BigDecimal("11.95"), calc.invoiceTotal(lines, "WHOLESALE"));
      }

      @Test
      void invoiceTotal_staff_isTaxExempt() {
          Vector lines = new Vector();
          lines.addElement("WIDGET:1");
          // STAFF: subtotal = $1.88, no tax added
          assertEquals(new BigDecimal("1.88"), calc.invoiceTotal(lines, "STAFF"));
      }

      @Test
      void invoiceTotal_nullCustomerType_treatedAsRetail() {
          Vector lines = new Vector();
          lines.addElement("WIDGET:1");
          // null → RETAIL → tax applies
          assertEquals(new BigDecimal("2.71"), calc.invoiceTotal(lines, null));
      }

      // =========================================================================
      // subtotal — multi-line
      // =========================================================================

      @Test
      void subtotal_multipleLines_sumsCorrectly() {
          Vector lines = new Vector();
          lines.addElement("WIDGET:1");    // $2.50
          lines.addElement("GADGET:1");   // $12.99 RETAIL, no discount → $12.99
          // sum = $15.49
          assertEquals(new BigDecimal("15.49"), calc.subtotal(lines, "RETAIL"));
      }

      @Test
      void subtotal_blankLinesIgnored() {
          Vector lines = new Vector();
          lines.addElement("WIDGET:1");
          lines.addElement("");
          lines.addElement("   ");
          lines.addElement("GADGET:1");
          assertEquals(new BigDecimal("15.49"), calc.subtotal(lines, "RETAIL"));
      }

      @Test
      void subtotal_nullElementsIgnored() {
          Vector lines = new Vector();
          lines.addElement("WIDGET:1");
          lines.addElement(null);
          lines.addElement("GADGET:1");
          assertEquals(new BigDecimal("15.49"), calc.subtotal(lines, "RETAIL"));
      }

      // =========================================================================
      // parseLines — error cases
      // =========================================================================

      @Test
      void parseLines_malformedNoColon_throws() {
          Vector lines = new Vector();
          lines.addElement("WIDGET");
          assertThrows(IllegalArgumentException.class, () -> calc.subtotal(lines, "RETAIL"));
      }

      @Test
      void parseLines_malformedTooManyColons_throws() {
          Vector lines = new Vector();
          lines.addElement("WIDGET:10:5");
          assertThrows(IllegalArgumentException.class, () -> calc.subtotal(lines, "RETAIL"));
      }

      @Test
      void parseLines_nonNumericQuantity_throws() {
          Vector lines = new Vector();
          lines.addElement("WIDGET:abc");
          assertThrows(IllegalArgumentException.class, () -> calc.subtotal(lines, "RETAIL"));
      }

      // =========================================================================
      // dueDate — weekend adjustment
      // =========================================================================

      /**
       * Build a date at midnight local time for the given year/month(1-based)/day.
       */
      private static Date localDate(int year, int month, int day) {
          Calendar c = new GregorianCalendar(year, month - 1, day, 0, 0, 0);
          c.set(Calendar.MILLISECOND, 0);
          return c.getTime();
      }

      private static int dayOfWeek(Date d) {
          Calendar c = new GregorianCalendar();
          c.setTime(d);
          return c.get(Calendar.DAY_OF_WEEK);
      }

      private static int calendarField(Date d, int field) {
          Calendar c = new GregorianCalendar();
          c.setTime(d);
          return c.get(field);
      }

      @Test
      void dueDate_plusThirtyLandsOnWeekday_noAdjustment() {
          // 2024-01-01 (Mon) + 30 = 2024-01-31 (Wed) — no adjustment
          Date due = calc.dueDate(localDate(2024, 1, 1));
          assertEquals(Calendar.WEDNESDAY, dayOfWeek(due));
          assertEquals(2024, calendarField(due, Calendar.YEAR));
          assertEquals(Calendar.JANUARY, calendarField(due, Calendar.MONTH));
          assertEquals(31, calendarField(due, Calendar.DAY_OF_MONTH));
      }

      @Test
      void dueDate_plusThirtyLandsOnSaturday_movesToMonday() {
          // 2024-01-04 (Thu) + 30 = 2024-02-03 (Sat) → pushed to 2024-02-05 (Mon)
          Date due = calc.dueDate(localDate(2024, 1, 4));
          assertEquals(Calendar.MONDAY, dayOfWeek(due));
          assertEquals(2024, calendarField(due, Calendar.YEAR));
          assertEquals(Calendar.FEBRUARY, calendarField(due, Calendar.MONTH));
          assertEquals(5, calendarField(due, Calendar.DAY_OF_MONTH));
      }

      @Test
      void dueDate_plusThirtyLandsOnSunday_movesToMonday() {
          // 2024-01-05 (Fri) + 30 = 2024-02-04 (Sun) → pushed to 2024-02-05 (Mon)
          Date due = calc.dueDate(localDate(2024, 1, 5));
          assertEquals(Calendar.MONDAY, dayOfWeek(due));
          assertEquals(2024, calendarField(due, Calendar.YEAR));
          assertEquals(Calendar.FEBRUARY, calendarField(due, Calendar.MONTH));
          assertEquals(5, calendarField(due, Calendar.DAY_OF_MONTH));
      }

      // =========================================================================
      // formatInvoice — output structure
      // =========================================================================

      @Test
      void formatInvoice_retail_containsExpectedLines() {
          Vector lines = new Vector();
          lines.addElement("WIDGET:1");
          String out = calc.formatInvoice(lines, "RETAIL");

          assertTrue(out.startsWith("INVOICE (RETAIL)\n"),
                  "Header must be 'INVOICE (RETAIL)'");
          assertTrue(out.contains("WIDGET x1 = 2.50\n"),
                  "Line item must appear with quantity and total");
          assertTrue(out.contains("SUBTOTAL 2.50\n"),
                  "SUBTOTAL line required");
          assertTrue(out.contains("TAX 0.21\n"),
                  "TAX line required for RETAIL");
          assertTrue(out.contains("TOTAL 2.71\n"),
                  "TOTAL must be subtotal + tax");
      }

      @Test
      void formatInvoice_staff_noTaxLine() {
          Vector lines = new Vector();
          lines.addElement("WIDGET:1");
          String out = calc.formatInvoice(lines, "STAFF");

          assertTrue(out.startsWith("INVOICE (STAFF)\n"));
          assertFalse(out.contains("TAX"), "Staff invoice must NOT contain a TAX line");
          assertTrue(out.contains("TOTAL 1.88\n"),
                  "TOTAL for STAFF must equal discounted subtotal with no tax");
      }

      @Test
      void formatInvoice_unknownType_normalisedToRetailInHeader() {
          Vector lines = new Vector();
          lines.addElement("WIDGET:1");
          String out = calc.formatInvoice(lines, "MYSTERY");
          assertTrue(out.startsWith("INVOICE (RETAIL)\n"),
                  "Unknown type must be normalised to RETAIL in the header");
      }

      @Test
      void formatInvoice_wholesale_headerShowsWholesale() {
          Vector lines = new Vector();
          lines.addElement("WIDGET:1");
          String out = calc.formatInvoice(lines, "wholesale");
          assertTrue(out.startsWith("INVOICE (WHOLESALE)\n"));
      }
  }
```


Here is what each group of tests pins down, and why certain values are surprising:

### What the tests characterise

┌───────────────────────┬──────────────────────────────────────────────────────────────────────────────────────────────┐
│ Group                 │ Key findings pinned                                                                          │
├───────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ normalizeCustomerType │ null, "", "   " all return "RETAIL"; any unrecognised string (e.g. "FOOBAR") silently        │
│                       │ returns "RETAIL" — there is no warning or error                                              │
├───────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ customerDiscountRate  │ null input hits the normalise → RETAIL path and returns 0.0, not an exception                │
├───────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ volumeDiscountRate    │ Thresholds are strictly greater-than: qty=10 gives 0 %, qty=50 gives 5 % — the Javadoc says  │
│                       │ "10 or more" / "50 or more" but the code uses > 10 / > 50                                    │
├───────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ getPrice / setPrice   │ getPrice trims and upper-cases; setPrice only upper-cases (no trim); zero price is accepted  │
│                       │ (0.0 < 0 is false)                                                                           │
├───────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ lineTotal rounding    │ Uses ROUND_HALF_EVEN (banker's rounding): $26.125 → $26.12 (2 is even, rounds down); $1.875  │
│                       │ → $1.88 (7 is odd, rounds up); $0.125 → $0.12 (GIZMO)                                        │
├───────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ Discount selection    │ Volume discount only wins when strictly greater than the customer rate; at qty=51, STAFF (25 │
│                       │ %) beats volume (10 %), WHOLESALE (15 %) beats volume (10 %)                                 │
├───────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ tax rounding          │ $14.00 × 8.25 % = $1.155 → $1.16 (retained digit 5 is odd → rounds up); same HALF_EVEN rule  │
├───────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ invoiceTotal          │ STAFF is tax-exempt — returns subtotal only; null customer type is treated as RETAIL (tax    │
│                       │ applies)                                                                                     │
├───────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ parseLines            │ null elements in the Vector are silently skipped; blank/whitespace strings are skipped; >2   │
│                       │ colon-tokens throw; non-numeric quantity throws                                              │
├───────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ dueDate               │ Both Saturday (+2) and Sunday (+1) cases push to the following Monday; confirmed with fixed  │
│                       │ 2024 calendar dates                                                                          │
├───────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ formatInvoice         │ STAFF output has no TAX line at all; unknown customer type normalises to RETAIL in the       │
│                       │ header                                                                                       │
└───────────────────────┴──────────────────────────────────────────────────────────────────────────────────────────────┘

````

## Raw Bob output

````

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
User (1) 2026-09-26 09:50:13.099 UTC (+0.4s)

You are writing characterization tests for a legacy Java class before it is modernized.                                 
                                                                                                                        
Goal: pin down what the code DOES today, including odd behaviour, so any change in behaviour                            
during modernization makes a test fail. Do not test what the comments say it should do; test                            
what it actually does. Where the code and its javadoc disagree, the code wins.                                          
                                                                                                                        
Requirements:                                                                                                           
- One JUnit 5 test class named InvoiceCalculatorCharacterizationTest in package com.acme.billing.                       
- Use only JUnit 5 (org.junit.jupiter.api) and the JDK. No other libraries.                                             
- Call only the public API of InvoiceCalculator shown below; keep test inputs deterministic.                            
- Cover boundaries (e.g. quantities around discount thresholds), rounding of half-cent values,                          
  input normalisation (whitespace, letter case, null), error cases, and date edge cases.                                
- Every test must pass against the code exactly as written below.                                                       
- Reply with the complete test class in a single ```java code block. Keep every line under 100 characters.              
                                                                                                                        
```java                                                                                                                 
  package com.acme.billing;                                                                                             
                                                                                                                        
  import java.math.BigDecimal;                                                                                          
  import java.util.Calendar;                                                                                            
  import java.util.Date;                                                                                                
  import java.util.Enumeration;                                                                                         
  import java.util.GregorianCalendar;                                                                                   
  import java.util.Hashtable;                                                                                           
  import java.util.StringTokenizer;                                                                                     
  import java.util.Vector;                                                                                              
                                                                                                                        
  /**                                                                                                                   
   * Invoice calculation for the ACME order desk.                                                                       
   *                                                                                                                    
   * Originally written for J2SE 1.4 (2004). Finance reconciles against these                                           
   * exact numbers every month, so do not change results without sign-off.                                              
   *   -- rk, 2004-03-11                                                                                                
   *   -- jt, 2009-06-02: added staff discount, due dates                                                               
   */                                                                                                                   
  public class InvoiceCalculator {                                                                                      
                                                                                                                        
      public static final String TYPE_RETAIL = "RETAIL";                                                                
      public static final String TYPE_WHOLESALE = "WHOLESALE";                                                          
      public static final String TYPE_STAFF = "STAFF";                                                                  
                                                                                                                        
      /** Sales tax, applied once to the discounted subtotal. */                                                        
      private static final double TAX_RATE = 0.0825;                                                                    
                                                                                                                        
      /** Payment terms in days. */                                                                                     
      private static final int PAYMENT_TERMS_DAYS = 30;                                                                 
                                                                                                                        
      /** sku (String) -> unit price (Double) */                                                                        
      private Hashtable priceList = new Hashtable();                                                                    
                                                                                                                        
      public InvoiceCalculator() {                                                                                      
          priceList.put("WIDGET", new Double(2.50));                                                                    
          priceList.put("GADGET", new Double(12.99));                                                                   
          priceList.put("GIZMO", new Double(0.125));                                                                    
          priceList.put("DOOHICKEY", new Double(49.95));                                                                
      }                                                                                                                 
                                                                                                                        
      public void setPrice(String sku, double price) {                                                                  
          if (sku == null) {                                                                                            
              throw new IllegalArgumentException("sku is required");                                                    
          }                                                                                                             
          if (price < 0) {                                                                                              
              throw new IllegalArgumentException("price must not be negative: " + price);                               
          }                                                                                                             
          priceList.put(sku.toUpperCase(), new Double(price));                                                          
      }                                                                                                                 
                                                                                                                        
      public double getPrice(String sku) {                                                                              
          if (sku == null) {                                                                                            
              throw new IllegalArgumentException("sku is required");                                                    
          }                                                                                                             
          Double price = (Double) priceList.get(sku.trim().toUpperCase());                                              
          if (price == null) {                                                                                          
              throw new IllegalArgumentException("unknown sku: " + sku);                                                
          }                                                                                                             
          return price.doubleValue();                                                                                   
      }                                                                                                                 
                                                                                                                        
      /**                                                                                                               
       * Normalises a customer type as typed by the order desk.                                                         
       * Blank or missing means retail; unknown types are treated as retail.                                            
       */                                                                                                               
      public String normalizeCustomerType(String raw) {                                                                 
          if (raw == null) {                                                                                            
              return TYPE_RETAIL;                                                                                       
          }                                                                                                             
          String t = raw.trim();                                                                                        
          if (t.length() == 0) {                                                                                        
              return TYPE_RETAIL;                                                                                       
          }                                                                                                             
          if (t.equalsIgnoreCase(TYPE_WHOLESALE)) {                                                                     
              return TYPE_WHOLESALE;                                                                                    
          } else if (t.equalsIgnoreCase(TYPE_STAFF)) {                                                                  
              return TYPE_STAFF;                                                                                        
          } else if (t.equalsIgnoreCase(TYPE_RETAIL)) {                                                                 
              return TYPE_RETAIL;                                                                                       
          }                                                                                                             
          return TYPE_RETAIL;                                                                                           
      }                                                                                                                 
                                                                                                                        
      /** Discount for the customer type, as a fraction. */                                                             
      public double customerDiscountRate(String customerType) {                                                         
          String t = normalizeCustomerType(customerType);                                                               
          if (t.equals(TYPE_WHOLESALE)) {                                                                               
              return 0.15;                                                                                              
          } else if (t.equals(TYPE_STAFF)) {                                                                            
              return 0.25;                                                                                              
          }                                                                                                             
          return 0.0;                                                                                                   
      }                                                                                                                 
                                                                                                                        
      /**                                                                                                               
       * Volume discount: orders of 10 or more units get 5% off,                                                        
       * orders of 50 or more get 10% off.                                                                              
       */                                                                                                               
      public double volumeDiscountRate(int quantity) {                                                                  
          if (quantity > 50) {                                                                                          
              return 0.10;                                                                                              
          }                                                                                                             
          if (quantity > 10) {                                                                                          
              return 0.05;                                                                                              
          }                                                                                                             
          return 0.0;                                                                                                   
      }                                                                                                                 
                                                                                                                        
      /**                                                                                                               
       * Total for one invoice line. Customer and volume discounts do not stack:                                        
       * the larger of the two applies. Rounded to cents.                                                               
       */                                                                                                               
      public BigDecimal lineTotal(String sku, int quantity, String customerType) {                                      
          if (quantity <= 0) {                                                                                          
              throw new IllegalArgumentException("quantity must be positive: " + quantity);                             
          }                                                                                                             
          BigDecimal gross = BigDecimal.valueOf(getPrice(sku)).multiply(new BigDecimal(quantity));                      
          double rate = customerDiscountRate(customerType);                                                             
          double volume = volumeDiscountRate(quantity);                                                                 
          if (volume > rate) {                                                                                          
              rate = volume;                                                                                            
          }                                                                                                             
          BigDecimal net = gross.multiply(BigDecimal.ONE.subtract(BigDecimal.valueOf(rate)));                           
          return net.setScale(2, BigDecimal.ROUND_HALF_EVEN);                                                           
      }                                                                                                                 
                                                                                                                        
      /**                                                                                                               
       * Parses order lines in the order desk's "SKU:QTY" format.                                                       
       * Blank lines are ignored; anything else malformed is rejected.                                                  
       */                                                                                                               
      public Vector parseLines(Vector rawLines) {                                                                       
          Vector parsed = new Vector();                                                                                 
          for (Enumeration e = rawLines.elements(); e.hasMoreElements();) {                                             
              String line = (String) e.nextElement();                                                                   
              if (line == null || line.trim().length() == 0) {                                                          
                  continue;                                                                                             
              }                                                                                                         
              StringTokenizer tok = new StringTokenizer(line, ":");                                                     
              if (tok.countTokens() != 2) {                                                                             
                  throw new IllegalArgumentException("malformed line: " + line);                                        
              }                                                                                                         
              String sku = tok.nextToken().trim();                                                                      
              int qty;                                                                                                  
              try {                                                                                                     
                  qty = Integer.parseInt(tok.nextToken().trim());                                                       
              } catch (NumberFormatException nfe) {                                                                     
                  throw new IllegalArgumentException("bad quantity in line: " + line);                                  
              }                                                                                                         
              parsed.addElement(new Object[] { sku, new Integer(qty) });                                                
          }                                                                                                             
          return parsed;                                                                                                
      }                                                                                                                 
                                                                                                                        
      /** Sum of line totals before tax. */                                                                             
      public BigDecimal subtotal(Vector rawLines, String customerType) {                                                
          BigDecimal sum = new BigDecimal("0.00");                                                                      
          Vector lines = parseLines(rawLines);                                                                          
          for (int i = 0; i < lines.size(); i++) {                                                                      
              Object[] l = (Object[]) lines.elementAt(i);                                                               
              sum = sum.add(lineTotal((String) l[0], ((Integer) l[1]).intValue(), customerType));                       
          }                                                                                                             
          return sum;                                                                                                   
      }                                                                                                                 
                                                                                                                        
      /** Tax on a subtotal, rounded to cents. */                                                                       
      public BigDecimal tax(BigDecimal subtotal) {                                                                      
          return subtotal.multiply(BigDecimal.valueOf(TAX_RATE)).setScale(2, BigDecimal.ROUND_HALF_EVEN);               
      }                                                                                                                 
                                                                                                                        
      /** Grand total: subtotal plus tax. Staff purchases are tax exempt. */                                            
      public BigDecimal invoiceTotal(Vector rawLines, String customerType) {                                            
          BigDecimal sub = subtotal(rawLines, customerType);                                                            
          if (normalizeCustomerType(customerType).equals(TYPE_STAFF)) {                                                 
              return sub;                                                                                               
          }                                                                                                             
          return sub.add(tax(sub));                                                                                     
      }                                                                                                                 
                                                                                                                        
      /**                                                                                                               
       * Payment due date: invoice date plus payment terms. If that lands on a                                          
       * weekend, it moves to the following Monday.                                                                     
       */                                                                                                               
      public Date dueDate(Date invoiceDate) {                                                                           
          Calendar cal = new GregorianCalendar();                                                                       
          cal.setTime(invoiceDate);                                                                                     
          cal.add(Calendar.DAY_OF_MONTH, PAYMENT_TERMS_DAYS);                                                           
          int dow = cal.get(Calendar.DAY_OF_WEEK);                                                                      
          if (dow == Calendar.SATURDAY) {                                                                               
              cal.add(Calendar.DAY_OF_MONTH, 2);                                                                        
          } else if (dow == Calendar.SUNDAY) {                                                                          
              cal.add(Calendar.DAY_OF_MONTH, 1);                                                                        
          }                                                                                                             
          return cal.getTime();                                                                                         
      }                                                                                                                 
                                                                                                                        
      /** Plain-text invoice for the printer. */                                                                        
      public String formatInvoice(Vector rawLines, String customerType) {                                               
          StringBuffer sb = new StringBuffer();                                                                         
          String type = normalizeCustomerType(customerType);                                                            
          sb.append("INVOICE (").append(type).append(")\n");                                                            
          Vector lines = parseLines(rawLines);                                                                          
          for (int i = 0; i < lines.size(); i++) {                                                                      
              Object[] l = (Object[]) lines.elementAt(i);                                                               
              String sku = (String) l[0];                                                                               
              int qty = ((Integer) l[1]).intValue();                                                                    
              sb.append(sku).append(" x").append(qty).append(" = ")                                                     
                .append(lineTotal(sku, qty, customerType)).append("\n");                                                
          }                                                                                                             
          BigDecimal sub = subtotal(rawLines, customerType);                                                            
          sb.append("SUBTOTAL ").append(sub).append("\n");                                                              
          if (!type.equals(TYPE_STAFF)) {                                                                               
              sb.append("TAX ").append(tax(sub)).append("\n");                                                          
          }                                                                                                             
          sb.append("TOTAL ").append(invoiceTotal(rawLines, customerType)).append("\n");                                
          return sb.toString();                                                                                         
      }                                                                                                                 
  }                                                                                                                     
                                                                                                                        
```                                                                                                                     

Starting subagent: general
   Analyze the following Java class and compute exact expected values for characterization tests. Trace through the code logic precisely.

```java
package com.acme.billing;

import java.math.BigDecimal;
import java.util.Calendar;
import java.util.Date;
import java.util.Enumeration;
import java.util.GregorianCalendar;
import java.util.Hashtable;
import java.util.StringTokenizer;
import java.util.Vector;

public class InvoiceCalculator {
    public static final String TYPE_RETAIL = "RETAIL";
    public static final String TYPE_WHOLESALE = "WHOLESALE";
    public static final String TYPE_STAFF = "STAFF";
    private static final double TAX_RATE = 0.0825;
    private static final int PAYMENT_TERMS_DAYS = 30;
    private Hashtable priceList = new Hashtable();

    public InvoiceCalculator() {
        priceList.put("WIDGET", new Double(2.50));
        priceList.put("GADGET", new Double(12.99));
        priceList.put("GIZMO", new Double(0.125));
        priceList.put("DOOHICKEY", new Double(49.95));
    }

    public void setPrice(String sku, double price) {
        if (sku == null) throw new IllegalArgumentException("sku is required");
        if (price < 0) throw new IllegalArgumentException("price must not be negative: " + price);
        priceList.put(sku.toUpperCase(), new Double(price));
    }

    public double getPrice(String sku) {
        if (sku == null) throw new IllegalArgumentException("sku is required");
        Double price = (Double) priceList.get(sku.trim().toUpperCase());
        if (price == null) throw new IllegalArgumentException("unknown sku: " + sku);
        return price.doubleValue();
    }

    public String normalizeCustomerType(String raw) {
        if (raw == null) return TYPE_RETAIL;
        String t = raw.trim();
        if (t.length() == 0) return TYPE_RETAIL;
        if (t.equalsIgnoreCase(TYPE_WHOLESALE)) return TYPE_WHOLESALE;
        else if (t.equalsIgnoreCase(TYPE_STAFF)) return TYPE_STAFF;
        else if (t.equalsIgnoreCase(TYPE_RETAIL)) return TYPE_RETAIL;
        return TYPE_RETAIL;
    }

    public double customerDiscountRate(String customerType) {
        String t = normalizeCustomerType(customerType);
        if (t.equals(TYPE_WHOLESALE)) return 0.15;
        else if (t.equals(TYPE_STAFF)) return 0.25;
        return 0.0;
    }

    public double volumeDiscountRate(int quantity) {
        if (quantity > 50) return 0.10;
        if (quantity > 10) return 0.05;
        return 0.0;
    }

    public BigDecimal lineTotal(String sku, int quantity, String customerType) {
        if (quantity <= 0) throw new IllegalArgumentException("quantity must be positive: " + quantity);
        BigDecimal gross = BigDecimal.valueOf(getPrice(sku)).multiply(new BigDecimal(quantity));
        double rate = customerDiscountRate(customerType);
        double volume = volumeDiscountRate(quantity);
        if (volume > rate) rate = volume;
        BigDecimal net = gross.multiply(BigDecimal.ONE.subtract(BigDecimal.valueOf(rate)));
        return net.setScale(2, BigDecimal.ROUND_HALF_EVEN);
    }
    // ... rest of class
}
```

Please compute these exact values (trace the double arithmetic carefully):

1. volumeDiscountRate thresholds:
   - qty=1: 0.0
   - qty=10: 0.0 (because condition is qty > 10, not >=)
   - qty=11: 0.05
   - qty=50: 0.05 (because condition is qty > 50, not >=)
   - qty=51: 0.10

2. lineTotal for WIDGET (price=2.50):
   - qty=1, RETAIL: gross=2.50, rate=0.0, net=2.50*1.0=2.50, rounded=2.50
   - qty=10, RETAIL: gross=25.00, rate=0.0 (qty>10 is false), net=25.00, rounded=25.00
   - qty=11, RETAIL: gross=27.50, volume=0.05 > customer=0.0, net=27.50*0.95=26.125, ROUND_HALF_EVEN → 26.12 or 26.13?
     - 26.125 → the digit before 5 is 2 (even), so rounds DOWN → 26.12
   - qty=50, RETAIL: gross=125.00, volume=0.05, net=125.00*0.95=118.75, rounded=118.75
   - qty=51, RETAIL: gross=127.50, volume=0.10, net=127.50*0.90=114.75, rounded=114.75

3. GIZMO (price=0.125), qty=1, RETAIL:
   - gross = BigDecimal.valueOf(0.125) * 1 = ?
   - Note: 0.125 is exactly representable in double, so BigDecimal.valueOf(0.125) = 0.125
   - net = 0.125 * 1.0 = 0.125
   - setScale(2, ROUND_HALF_EVEN): 0.125 → digit before 5 is 2 (even) → rounds DOWN → 0.12

4. Customer discount vs volume - staff (0.25) vs volume:
   - STAFF, qty=51: customer=0.25, volume=0.10. 0.10 > 0.25 is false, so rate=0.25
   - WHOLESALE, qty=51: customer=0.15, volume=0.10. 0.10 > 0.15 is false, so rate=0.15
   - RETAIL, qty=51: customer=0.0, volume=0.10. 0.10 > 0.0, so rate=0.10

5. lineTotal GADGET (price=12.99), qty=1, WHOLESALE:
   - gross = 12.99, rate=0.15, volume=0.0
   - 0.0 > 0.15 is false, so rate=0.15
   - net = 12.99 * (1 - 0.15) = 12.99 * 0.85 = 11.0415
   - setScale(2, ROUND_HALF_EVEN): 11.0415 → look at 3rd decimal: 1, rounds down → 11.04

6. tax(BigDecimal("100.00")):
   - 100.00 * 0.0825 = 8.25 → setScale(2, ROUND_HALF_EVEN) = 8.25

7. tax rounding - find a subtotal that produces a half-cent:
   - We need subtotal * 0.0825 to end in exactly .005
   - Try subtotal = 2.50 (1 WIDGET, retail):
     - tax = 2.50 * 0.0825 = 0.20625 → setScale(2, HALF_EVEN): 3rd decimal is 6, rounds up → 0.21
   - Try subtotal that gives exactly .XX5:
     - 100/0.0825 won't give easy numbers
     - Let's try: we need X * 0.0825 = Y.ZZ5
     - 0.0825 = 33/400
     - X * 33/400 = Y.ZZ5 → X * 33 = Y.ZZ5 * 400
     - For .005: X*33 must end in 2 (since 400*0.005=2)
     - X*33 ≡ 2 (mod 10) → X ≡ 4 (mod 10) (since 3*4=12)
     - So X=4: 4*0.0825 = 0.33 (no half-cent)
     - X=14: 14*0.0825 = 1.155 → HALF_EVEN on 1.155: digit before 5 is 5 (odd) → rounds UP → 1.16
     - X=24: 24*0.0825 = 1.98 (no)
     - Hmm, let me try: need X*0.0825 to have exactly 3 decimal places ending in 5
     - X=100: 8.25 → not a half-cent issue
     - X=200/3... no, need integer
     - Actually a simpler case: GIZMO price = 0.125, which hits the half-even case directly in lineTotal

8. invoiceTotal for STAFF is tax-exempt (returns subtotal only)

9. dueDate: 
   - A date that +30 lands on Saturday → moves to Monday (+2)
   - A date that +30 lands on Sunday → moves to Monday (+1)
   - Need to find specific dates. Let me figure out one:
     - January 1, 2024 is a Monday
     - Jan 1 + 30 = Jan 31, 2024 = Wednesday → no adjustment
     - We need a date D such that D+30 is Saturday
     - Jan 1 is Mon (dow=2), so D+30=Sat means D+30 has dow=7
     - Sat-Mon = 5 days difference in dow
     - D needs dow such that (dow-1+30) mod 7 = 5 (where Mon=0... actually Java uses 1=Sun,2=Mon,...7=Sat)
     - Let me just compute: if we want D+30 = some known Saturday
     - Saturday Jan 6, 2024: D = Dec 7, 2023
     - Saturday Feb 3, 2024: D = Jan 4, 2024 (Thursday)
     - Let's verify: Jan 4 is Thursday (Jan 1=Mon, Jan 4 = Mon+3 = Thu). Jan 4 + 30 = Feb 3.
     - Feb 3, 2024: Jan has 31 days, so Jan 4+31=Feb 4... wait
     - Jan 4 + 30 days: Jan has 31 days, so Jan 4 + 27 = Jan 31, + 3 more = Feb 3. Is Feb 3, 2024 a Saturday?
     - Jan 1=Mon, Feb 1 = 31 days later = 31 mod 7 = 3 days later = Thu. Feb 3 = Thu+2 = Sat. YES!
     - So invoiceDate=2024-01-04 → dueDate should be 2024-02-05 (Monday, +2 from Sat)
   
   - For Sunday case: need D+30=Sunday
     - Sunday Feb 4, 2024 (Feb 1=Thu, Feb 4=Sun)
     - D = Feb 4 - 30 = Jan 5, 2024 (Friday: Jan 1=Mon, Jan 5=Fri)
     - Jan 5 + 30: Jan 5+26=Jan 31, +4=Feb 4. Feb 4=Sun. YES!
     - So invoiceDate=2024-01-05 → dueDate should be 2024-02-05 (Monday, +1 from Sun)
   
   - For weekday (no adjustment): invoiceDate=2024-01-01 (Mon) + 30 = Jan 31 (Wed) → stays Jan 31

10. normalizeCustomerType:
    - null → RETAIL
    - "" → RETAIL  
    - "  " → RETAIL
    - "wholesale" → WHOLESALE
    - " Wholesale " → WHOLESALE
    - "STAFF" → STAFF
    - "unknown" → RETAIL
    - "FOOBAR" → RETAIL

11. setPrice null sku throws IllegalArgumentException
    setPrice negative price throws IllegalArgumentException
    setPrice zero price: 0 >= 0, so NOT thrown (0.0 < 0 is false), so zero price is allowed
    getPrice null throws
    getPrice unknown sku throws
    getPrice with whitespace: "  widget  ".trim().toUpperCase() = "WIDGET" → works
    lineTotal qty=0 throws
    lineTotal qty=-1 throws

12. parseLines:
    - null element in vector: skipped (null check before trim)
    - blank line: skipped
    - "WIDGET:10" → ok
    - "WIDGET" (no colon) → countTokens=1 → throws
    - "WIDGET:10:5" → countTokens=3 → throws  
    - "WIDGET:abc" → parseInt throws → wrapped in IllegalArgumentException

Please confirm all these computations and flag any that might be wrong.



Subagent completed | 63.7s | 1 tool call(s) | 0.071


────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Assistant (1) 2026-09-26 09:50:15.637 UTC (+3.0s)

Looking at the code carefully before writing the tests. Let me trace the actual behavior:                               

Tool calls:
- spawn_subagent

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Tool (1) 2026-09-26 09:51:54.541 UTC (+101.9s) Success

Tool: spawn_subagent
Args:
- description: Analyze the following Java class and compute exact expected values for characterization tests. Trace through the code...


────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Assistant (2) 2026-09-26 09:51:55.782 UTC (+103.1s)

All computed values are confirmed. Now I have everything I need to write the complete characterization test class.      

Tool calls:
- write_file

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Tool (2) 2026-09-26 09:52:45.371 UTC (+152.7s) Success

Tool: write_file
Args:
- path: /tmp/bob-bridge-xiv_f1z6/InvoiceCalculatorCharacterizationTest.java
- line_count: 349
- content: package com.acme.billing;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.m...

Files changed:
  ~ file:///tmp/bob-bridge-xiv_f1z6/InvoiceCalculatorCharacterizationTest.java

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Assistant (3) 2026-09-26 09:52:47.306 UTC (+154.6s)

Now let me verify all the arithmetic by actually running the production class + tests together:                         

Tool calls:
- execute_command

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Tool (3) 2026-09-26 09:53:03.491 UTC (+170.8s) Success

Tool: execute_command
Args:
- command: 
# Create the full directory structure and compile+run the tests
mkdir -p /tmp/acme-billing-verify/src/com/acme/billi...

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Tool (4) 2026-09-26 09:53:10.162 UTC (+177.5s) Success

Tool: execute_command
Args:
- command: 
# Copy the test class
cp /tmp/bob-bridge-xiv_f1z6/InvoiceCalculatorCharacterizationTest.java \
   /tmp/acme-billing-...
- timeout_seconds: 60

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Tool (5) 2026-09-26 09:53:13.836 UTC (+181.2s) Success

Tool: execute_command
Args:
- command: 
JUNIT_DIR=/tmp/junit5-jars
SRC=/tmp/acme-billing-verify/src
OUT=/tmp/acme-billing-verify/out
mkdir -p "$OUT"

CP="$J...

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Tool (6) 2026-09-26 09:53:17.114 UTC (+184.4s) Success

Tool: execute_command
Args:
- command: 
JUNIT_DIR=/tmp/junit5-jars
OUT=/tmp/acme-billing-verify/out

java -jar "$JUNIT_DIR/junit-platform-console-standalone...
- timeout_seconds: 30

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Assistant (4) 2026-09-26 09:53:19.924 UTC (+187.3s)

61/61 tests pass. Here is the complete test class:                                                                      
                                                                                                                        
```java                                                                                                                 
  package com.acme.billing;                                                                                             
                                                                                                                        
  import org.junit.jupiter.api.BeforeEach;                                                                              
  import org.junit.jupiter.api.Test;                                                                                    
                                                                                                                        
  import java.math.BigDecimal;                                                                                          
  import java.util.Calendar;                                                                                            
  import java.util.GregorianCalendar;                                                                                   
  import java.util.Vector;                                                                                              
  import java.util.Date;                                                                                                
                                                                                                                        
  import static org.junit.jupiter.api.Assertions.*;                                                                     
                                                                                                                        
  /**                                                                                                                   
   * Characterization tests for {@link InvoiceCalculator}.                                                              
   *                                                                                                                    
   * These tests pin down what the code DOES today, including edge cases and                                            
   * rounding quirks, so that any change in behaviour during modernisation causes                                       
   * at least one test to fail. Comments note where behaviour is surprising.                                            
   */                                                                                                                   
  class InvoiceCalculatorCharacterizationTest {                                                                         
                                                                                                                        
      private InvoiceCalculator calc;                                                                                   
                                                                                                                        
      @BeforeEach                                                                                                       
      void setUp() {                                                                                                    
          calc = new InvoiceCalculator();                                                                               
      }                                                                                                                 
                                                                                                                        
      // =========================================================================                                      
      // normalizeCustomerType                                                                                          
      // =========================================================================                                      
                                                                                                                        
      @Test                                                                                                             
      void normalizeNull_returnsRetail() {                                                                              
          assertEquals(InvoiceCalculator.TYPE_RETAIL, calc.normalizeCustomerType(null));                                
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void normalizeEmpty_returnsRetail() {                                                                             
          assertEquals(InvoiceCalculator.TYPE_RETAIL, calc.normalizeCustomerType(""));                                  
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void normalizeBlank_returnsRetail() {                                                                             
          assertEquals(InvoiceCalculator.TYPE_RETAIL, calc.normalizeCustomerType("   "));                               
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void normalizeRetailExact_returnsRetail() {                                                                       
          assertEquals(InvoiceCalculator.TYPE_RETAIL, calc.normalizeCustomerType("RETAIL"));                            
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void normalizeRetailLower_returnsRetail() {                                                                       
          assertEquals(InvoiceCalculator.TYPE_RETAIL, calc.normalizeCustomerType("retail"));                            
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void normalizeWholesaleExact_returnsWholesale() {                                                                 
          assertEquals(InvoiceCalculator.TYPE_WHOLESALE, calc.normalizeCustomerType("WHOLESALE"));                      
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void normalizeWholesaleMixedCaseWithPadding_returnsWholesale() {                                                  
          assertEquals(InvoiceCalculator.TYPE_WHOLESALE, calc.normalizeCustomerType(" Wholesale "));                    
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void normalizeStaffLower_returnsStaff() {                                                                         
          assertEquals(InvoiceCalculator.TYPE_STAFF, calc.normalizeCustomerType("staff"));                              
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void normalizeUnknownString_returnsRetail() {                                                                     
          // Unknown types silently fall back to RETAIL                                                                 
          assertEquals(InvoiceCalculator.TYPE_RETAIL, calc.normalizeCustomerType("FOOBAR"));                            
      }                                                                                                                 
                                                                                                                        
      // =========================================================================                                      
      // customerDiscountRate                                                                                           
      // =========================================================================                                      
                                                                                                                        
      @Test                                                                                                             
      void customerDiscountRate_retail_isZero() {                                                                       
          assertEquals(0.0, calc.customerDiscountRate("RETAIL"), 0.0);                                                  
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void customerDiscountRate_null_isZeroLikeRetail() {                                                               
          // null normalises to RETAIL → 0 % discount                                                                   
          assertEquals(0.0, calc.customerDiscountRate(null), 0.0);                                                      
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void customerDiscountRate_wholesale_is15Percent() {                                                               
          assertEquals(0.15, calc.customerDiscountRate("WHOLESALE"), 0.0);                                              
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void customerDiscountRate_staff_is25Percent() {                                                                   
          assertEquals(0.25, calc.customerDiscountRate("STAFF"), 0.0);                                                  
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void customerDiscountRate_unknownType_isZero() {                                                                  
          assertEquals(0.0, calc.customerDiscountRate("MYSTERY"), 0.0);                                                 
      }                                                                                                                 
                                                                                                                        
      // =========================================================================                                      
      // volumeDiscountRate  (threshold is STRICTLY greater-than, not >=)                                               
      // =========================================================================                                      
                                                                                                                        
      @Test                                                                                                             
      void volumeDiscount_qty1_isZero() {                                                                               
          assertEquals(0.0, calc.volumeDiscountRate(1), 0.0);                                                           
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void volumeDiscount_qty10_isZero() {                                                                              
          // qty == 10 does NOT qualify; condition is qty > 10                                                          
          assertEquals(0.0, calc.volumeDiscountRate(10), 0.0);                                                          
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void volumeDiscount_qty11_is5Percent() {                                                                          
          assertEquals(0.05, calc.volumeDiscountRate(11), 0.0);                                                         
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void volumeDiscount_qty50_is5Percent() {                                                                          
          // qty == 50 does NOT qualify for the 10 % tier; condition is qty > 50                                        
          assertEquals(0.05, calc.volumeDiscountRate(50), 0.0);                                                         
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void volumeDiscount_qty51_is10Percent() {                                                                         
          assertEquals(0.10, calc.volumeDiscountRate(51), 0.0);                                                         
      }                                                                                                                 
                                                                                                                        
      // =========================================================================                                      
      // getPrice / setPrice                                                                                            
      // =========================================================================                                      
                                                                                                                        
      @Test                                                                                                             
      void getPrice_knownSku_returnsPrice() {                                                                           
          assertEquals(2.50, calc.getPrice("WIDGET"), 0.0);                                                             
          assertEquals(12.99, calc.getPrice("GADGET"), 0.0);                                                            
          assertEquals(0.125, calc.getPrice("GIZMO"), 0.0);                                                             
          assertEquals(49.95, calc.getPrice("DOOHICKEY"), 0.0);                                                         
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void getPrice_trims_andUppercases() {                                                                             
          // getPrice trims whitespace and upper-cases before lookup                                                    
          assertEquals(2.50, calc.getPrice("  widget  "), 0.0);                                                         
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void getPrice_nullSku_throwsIllegalArgument() {                                                                   
          assertThrows(IllegalArgumentException.class, () -> calc.getPrice(null));                                      
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void getPrice_unknownSku_throwsIllegalArgument() {                                                                
          assertThrows(IllegalArgumentException.class, () -> calc.getPrice("UNKNOWN_SKU"));                             
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void setPrice_nullSku_throwsIllegalArgument() {                                                                   
          assertThrows(IllegalArgumentException.class, () -> calc.setPrice(null, 1.0));                                 
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void setPrice_negativePrice_throwsIllegalArgument() {                                                             
          assertThrows(IllegalArgumentException.class, () -> calc.setPrice("WIDGET", -0.01));                           
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void setPrice_zeroPriceIsAllowed() {                                                                              
          // price == 0 satisfies "price < 0" == false, so no exception                                                 
          assertDoesNotThrow(() -> calc.setPrice("WIDGET", 0.0));                                                       
          assertEquals(0.0, calc.getPrice("WIDGET"), 0.0);                                                              
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void setPrice_uppercasesTheSku() {                                                                                
          calc.setPrice("newitem", 5.00);                                                                               
          assertEquals(5.00, calc.getPrice("NEWITEM"), 0.0);                                                            
      }                                                                                                                 
                                                                                                                        
      // =========================================================================                                      
      // lineTotal — basic cases                                                                                        
      // =========================================================================                                      
                                                                                                                        
      @Test                                                                                                             
      void lineTotal_qty0_throwsIllegalArgument() {                                                                     
          assertThrows(IllegalArgumentException.class,                                                                  
                  () -> calc.lineTotal("WIDGET", 0, "RETAIL"));                                                         
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void lineTotal_negativeQty_throwsIllegalArgument() {                                                              
          assertThrows(IllegalArgumentException.class,                                                                  
                  () -> calc.lineTotal("WIDGET", -1, "RETAIL"));                                                        
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void lineTotal_retail_noDiscount_roundsCorrectly() {                                                              
          // 1 × $2.50, no discount → $2.50                                                                             
          assertEquals(new BigDecimal("2.50"), calc.lineTotal("WIDGET", 1, "RETAIL"));                                  
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void lineTotal_wholesale_appliesCustomerDiscount() {                                                              
          // 1 × $12.99, 15 % off = $11.0415 → ROUND_HALF_EVEN → $11.04                                                 
          assertEquals(new BigDecimal("11.04"), calc.lineTotal("GADGET", 1, "WHOLESALE"));                              
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void lineTotal_staff_appliesCustomerDiscount() {                                                                  
          // 1 × $2.50, 25 % off = $1.875 → ROUND_HALF_EVEN (digit before 5 is 7, odd → round up)                       
          // $1.875 → retained digit is 7 (odd) → 1.88                                                                  
          assertEquals(new BigDecimal("1.88"), calc.lineTotal("WIDGET", 1, "STAFF"));                                   
      }                                                                                                                 
                                                                                                                        
      // =========================================================================                                      
      // lineTotal — volume discount threshold boundary                                                                 
      // =========================================================================                                      
                                                                                                                        
      @Test                                                                                                             
      void lineTotal_qty10_noVolumeDiscount() {                                                                         
          // qty == 10 falls below the > 10 threshold: no discount                                                      
          assertEquals(new BigDecimal("25.00"), calc.lineTotal("WIDGET", 10, "RETAIL"));                                
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void lineTotal_qty11_volumeDiscountApplied_halfEvenRoundsDown() {                                                 
          // 11 × $2.50 = $27.50; 5 % off = $26.125                                                                     
          // ROUND_HALF_EVEN: retained digit 2 is even → round down to $26.12                                           
          assertEquals(new BigDecimal("26.12"), calc.lineTotal("WIDGET", 11, "RETAIL"));                                
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void lineTotal_qty50_5PctVolumeDiscount() {                                                                       
          // qty == 50: > 10 but NOT > 50, so 5 %                                                                       
          // 50 × $2.50 = $125.00; 5 % off = $118.75                                                                    
          assertEquals(new BigDecimal("118.75"), calc.lineTotal("WIDGET", 50, "RETAIL"));                               
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void lineTotal_qty51_10PctVolumeDiscount() {                                                                      
          // qty == 51: > 50, so 10 %                                                                                   
          // 51 × $2.50 = $127.50; 10 % off = $114.75                                                                   
          assertEquals(new BigDecimal("114.75"), calc.lineTotal("WIDGET", 51, "RETAIL"));                               
      }                                                                                                                 
                                                                                                                        
      // =========================================================================                                      
      // lineTotal — larger customer discount wins over volume discount                                                 
      // =========================================================================                                      
                                                                                                                        
      @Test                                                                                                             
      void lineTotal_staff_qty51_customerDiscountBeatsVolume() {                                                        
          // STAFF = 25 %, volume(51) = 10 %. 10 % is NOT > 25 % → use 25 %                                             
          // 51 × $2.50 = $127.50; 25 % off = $95.625                                                                   
          // ROUND_HALF_EVEN: retained digit 6 (even) → round down → $95.62                                             
          assertEquals(new BigDecimal("95.62"), calc.lineTotal("WIDGET", 51, "STAFF"));                                 
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void lineTotal_wholesale_qty51_customerDiscountBeatsVolume() {                                                    
          // WHOLESALE = 15 %, volume(51) = 10 %. 10 % is NOT > 15 % → use 15 %                                         
          // 51 × $2.50 = $127.50; 15 % off = $108.375                                                                  
          // ROUND_HALF_EVEN: retained digit 3 (odd) → round up → $108.38                                               
          assertEquals(new BigDecimal("108.38"), calc.lineTotal("WIDGET", 51, "WHOLESALE"));                            
      }                                                                                                                 
                                                                                                                        
      // =========================================================================                                      
      // lineTotal — GIZMO: price exactly $0.125, half-even rounding                                                    
      // =========================================================================                                      
                                                                                                                        
      @Test                                                                                                             
      void lineTotal_gizmo_qty1_retail_halfEvenRoundsDown() {                                                           
          // GIZMO price = 0.125 (exact in IEEE-754); BigDecimal.valueOf(0.125) = "0.125"                               
          // 1 × $0.125 = $0.125; ROUND_HALF_EVEN: retained digit 2 is even → $0.12                                     
          assertEquals(new BigDecimal("0.12"), calc.lineTotal("GIZMO", 1, "RETAIL"));                                   
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void lineTotal_gizmo_qty2_retail() {                                                                              
          // 2 × $0.125 = $0.25 (exact) → $0.25                                                                         
          assertEquals(new BigDecimal("0.25"), calc.lineTotal("GIZMO", 2, "RETAIL"));                                   
      }                                                                                                                 
                                                                                                                        
      // =========================================================================                                      
      // tax                                                                                                            
      // =========================================================================                                      
                                                                                                                        
      @Test                                                                                                             
      void tax_roundNumber_noRounding() {                                                                               
          // $100.00 × 8.25 % = $8.25 exactly                                                                           
          assertEquals(new BigDecimal("8.25"), calc.tax(new BigDecimal("100.00")));                                     
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void tax_halfCentCase_oddDigitRoundsUp() {                                                                        
          // $14.00 × 0.0825 = $1.155; retained digit 5 (odd) → round up → $1.16                                        
          assertEquals(new BigDecimal("1.16"), calc.tax(new BigDecimal("14.00")));                                      
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void tax_widget_singleUnit() {                                                                                    
          // $2.50 × 0.0825 = $0.20625; third decimal 6 > 5 → round up unconditionally → $0.21                          
          assertEquals(new BigDecimal("0.21"), calc.tax(new BigDecimal("2.50")));                                       
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void tax_zero_isZero() {                                                                                          
          assertEquals(new BigDecimal("0.00"), calc.tax(new BigDecimal("0.00")));                                       
      }                                                                                                                 
                                                                                                                        
      // =========================================================================                                      
      // invoiceTotal — tax applied for retail/wholesale; exempt for staff                                              
      // =========================================================================                                      
                                                                                                                        
      @Test                                                                                                             
      void invoiceTotal_retail_includesTax() {                                                                          
          Vector lines = new Vector();                                                                                  
          lines.addElement("WIDGET:1");                                                                                 
          // subtotal = $2.50; tax = $0.21; total = $2.71                                                               
          assertEquals(new BigDecimal("2.71"), calc.invoiceTotal(lines, "RETAIL"));                                     
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void invoiceTotal_wholesale_includesTax() {                                                                       
          Vector lines = new Vector();                                                                                  
          lines.addElement("GADGET:1");                                                                                 
          // subtotal = $11.04; tax = $11.04 × 0.0825 = $0.9108 → $0.91; total = $11.95                                 
          assertEquals(new BigDecimal("11.95"), calc.invoiceTotal(lines, "WHOLESALE"));                                 
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void invoiceTotal_staff_isTaxExempt() {                                                                           
          Vector lines = new Vector();                                                                                  
          lines.addElement("WIDGET:1");                                                                                 
          // STAFF: subtotal = $1.88, no tax added                                                                      
          assertEquals(new BigDecimal("1.88"), calc.invoiceTotal(lines, "STAFF"));                                      
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void invoiceTotal_nullCustomerType_treatedAsRetail() {                                                            
          Vector lines = new Vector();                                                                                  
          lines.addElement("WIDGET:1");                                                                                 
          // null → RETAIL → tax applies                                                                                
          assertEquals(new BigDecimal("2.71"), calc.invoiceTotal(lines, null));                                         
      }                                                                                                                 
                                                                                                                        
      // =========================================================================                                      
      // subtotal — multi-line                                                                                          
      // =========================================================================                                      
                                                                                                                        
      @Test                                                                                                             
      void subtotal_multipleLines_sumsCorrectly() {                                                                     
          Vector lines = new Vector();                                                                                  
          lines.addElement("WIDGET:1");    // $2.50                                                                     
          lines.addElement("GADGET:1");   // $12.99 RETAIL, no discount → $12.99                                        
          // sum = $15.49                                                                                               
          assertEquals(new BigDecimal("15.49"), calc.subtotal(lines, "RETAIL"));                                        
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void subtotal_blankLinesIgnored() {                                                                               
          Vector lines = new Vector();                                                                                  
          lines.addElement("WIDGET:1");                                                                                 
          lines.addElement("");                                                                                         
          lines.addElement("   ");                                                                                      
          lines.addElement("GADGET:1");                                                                                 
          assertEquals(new BigDecimal("15.49"), calc.subtotal(lines, "RETAIL"));                                        
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void subtotal_nullElementsIgnored() {                                                                             
          Vector lines = new Vector();                                                                                  
          lines.addElement("WIDGET:1");                                                                                 
          lines.addElement(null);                                                                                       
          lines.addElement("GADGET:1");                                                                                 
          assertEquals(new BigDecimal("15.49"), calc.subtotal(lines, "RETAIL"));                                        
      }                                                                                                                 
                                                                                                                        
      // =========================================================================                                      
      // parseLines — error cases                                                                                       
      // =========================================================================                                      
                                                                                                                        
      @Test                                                                                                             
      void parseLines_malformedNoColon_throws() {                                                                       
          Vector lines = new Vector();                                                                                  
          lines.addElement("WIDGET");                                                                                   
          assertThrows(IllegalArgumentException.class, () -> calc.subtotal(lines, "RETAIL"));                           
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void parseLines_malformedTooManyColons_throws() {                                                                 
          Vector lines = new Vector();                                                                                  
          lines.addElement("WIDGET:10:5");                                                                              
          assertThrows(IllegalArgumentException.class, () -> calc.subtotal(lines, "RETAIL"));                           
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void parseLines_nonNumericQuantity_throws() {                                                                     
          Vector lines = new Vector();                                                                                  
          lines.addElement("WIDGET:abc");                                                                               
          assertThrows(IllegalArgumentException.class, () -> calc.subtotal(lines, "RETAIL"));                           
      }                                                                                                                 
                                                                                                                        
      // =========================================================================                                      
      // dueDate — weekend adjustment                                                                                   
      // =========================================================================                                      
                                                                                                                        
      /**                                                                                                               
       * Build a date at midnight local time for the given year/month(1-based)/day.                                     
       */                                                                                                               
      private static Date localDate(int year, int month, int day) {                                                     
          Calendar c = new GregorianCalendar(year, month - 1, day, 0, 0, 0);                                            
          c.set(Calendar.MILLISECOND, 0);                                                                               
          return c.getTime();                                                                                           
      }                                                                                                                 
                                                                                                                        
      private static int dayOfWeek(Date d) {                                                                            
          Calendar c = new GregorianCalendar();                                                                         
          c.setTime(d);                                                                                                 
          return c.get(Calendar.DAY_OF_WEEK);                                                                           
      }                                                                                                                 
                                                                                                                        
      private static int calendarField(Date d, int field) {                                                             
          Calendar c = new GregorianCalendar();                                                                         
          c.setTime(d);                                                                                                 
          return c.get(field);                                                                                          
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void dueDate_plusThirtyLandsOnWeekday_noAdjustment() {                                                            
          // 2024-01-01 (Mon) + 30 = 2024-01-31 (Wed) — no adjustment                                                   
          Date due = calc.dueDate(localDate(2024, 1, 1));                                                               
          assertEquals(Calendar.WEDNESDAY, dayOfWeek(due));                                                             
          assertEquals(2024, calendarField(due, Calendar.YEAR));                                                        
          assertEquals(Calendar.JANUARY, calendarField(due, Calendar.MONTH));                                           
          assertEquals(31, calendarField(due, Calendar.DAY_OF_MONTH));                                                  
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void dueDate_plusThirtyLandsOnSaturday_movesToMonday() {                                                          
          // 2024-01-04 (Thu) + 30 = 2024-02-03 (Sat) → pushed to 2024-02-05 (Mon)                                      
          Date due = calc.dueDate(localDate(2024, 1, 4));                                                               
          assertEquals(Calendar.MONDAY, dayOfWeek(due));                                                                
          assertEquals(2024, calendarField(due, Calendar.YEAR));                                                        
          assertEquals(Calendar.FEBRUARY, calendarField(due, Calendar.MONTH));                                          
          assertEquals(5, calendarField(due, Calendar.DAY_OF_MONTH));                                                   
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void dueDate_plusThirtyLandsOnSunday_movesToMonday() {                                                            
          // 2024-01-05 (Fri) + 30 = 2024-02-04 (Sun) → pushed to 2024-02-05 (Mon)                                      
          Date due = calc.dueDate(localDate(2024, 1, 5));                                                               
          assertEquals(Calendar.MONDAY, dayOfWeek(due));                                                                
          assertEquals(2024, calendarField(due, Calendar.YEAR));                                                        
          assertEquals(Calendar.FEBRUARY, calendarField(due, Calendar.MONTH));                                          
          assertEquals(5, calendarField(due, Calendar.DAY_OF_MONTH));                                                   
      }                                                                                                                 
                                                                                                                        
      // =========================================================================                                      
      // formatInvoice — output structure                                                                               
      // =========================================================================                                      
                                                                                                                        
      @Test                                                                                                             
      void formatInvoice_retail_containsExpectedLines() {                                                               
          Vector lines = new Vector();                                                                                  
          lines.addElement("WIDGET:1");                                                                                 
          String out = calc.formatInvoice(lines, "RETAIL");                                                             
                                                                                                                        
          assertTrue(out.startsWith("INVOICE (RETAIL)\n"),                                                              
                  "Header must be 'INVOICE (RETAIL)'");                                                                 
          assertTrue(out.contains("WIDGET x1 = 2.50\n"),                                                                
                  "Line item must appear with quantity and total");                                                     
          assertTrue(out.contains("SUBTOTAL 2.50\n"),                                                                   
                  "SUBTOTAL line required");                                                                            
          assertTrue(out.contains("TAX 0.21\n"),                                                                        
                  "TAX line required for RETAIL");                                                                      
          assertTrue(out.contains("TOTAL 2.71\n"),                                                                      
                  "TOTAL must be subtotal + tax");                                                                      
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void formatInvoice_staff_noTaxLine() {                                                                            
          Vector lines = new Vector();                                                                                  
          lines.addElement("WIDGET:1");                                                                                 
          String out = calc.formatInvoice(lines, "STAFF");                                                              
                                                                                                                        
          assertTrue(out.startsWith("INVOICE (STAFF)\n"));                                                              
          assertFalse(out.contains("TAX"), "Staff invoice must NOT contain a TAX line");                                
          assertTrue(out.contains("TOTAL 1.88\n"),                                                                      
                  "TOTAL for STAFF must equal discounted subtotal with no tax");                                        
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void formatInvoice_unknownType_normalisedToRetailInHeader() {                                                     
          Vector lines = new Vector();                                                                                  
          lines.addElement("WIDGET:1");                                                                                 
          String out = calc.formatInvoice(lines, "MYSTERY");                                                            
          assertTrue(out.startsWith("INVOICE (RETAIL)\n"),                                                              
                  "Unknown type must be normalised to RETAIL in the header");                                           
      }                                                                                                                 
                                                                                                                        
      @Test                                                                                                             
      void formatInvoice_wholesale_headerShowsWholesale() {                                                             
          Vector lines = new Vector();                                                                                  
          lines.addElement("WIDGET:1");                                                                                 
          String out = calc.formatInvoice(lines, "wholesale");                                                          
          assertTrue(out.startsWith("INVOICE (WHOLESALE)\n"));                                                          
      }                                                                                                                 
  }                                                                                                                     
```                                                                                                                     
                                                                                                                        
────────────────────────────────────────────────────────────────────────────────                                        
                                                                                                                        
Here is what each group of tests pins down, and why certain values are surprising:                                      
                                                                                                                        
### What the tests characterise                                                                                         
                                                                                                                        
┌───────────────────────┬──────────────────────────────────────────────────────────────────────────────────────────────┐
│ Group                 │ Key findings pinned                                                                          │
├───────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ normalizeCustomerType │ null, "", "   " all return "RETAIL"; any unrecognised string (e.g. "FOOBAR") silently        │
│                       │ returns "RETAIL" — there is no warning or error                                              │
├───────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ customerDiscountRate  │ null input hits the normalise → RETAIL path and returns 0.0, not an exception                │
├───────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ volumeDiscountRate    │ Thresholds are strictly greater-than: qty=10 gives 0 %, qty=50 gives 5 % — the Javadoc says  │
│                       │ "10 or more" / "50 or more" but the code uses > 10 / > 50                                    │
├───────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ getPrice / setPrice   │ getPrice trims and upper-cases; setPrice only upper-cases (no trim); zero price is accepted  │
│                       │ (0.0 < 0 is false)                                                                           │
├───────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ lineTotal rounding    │ Uses ROUND_HALF_EVEN (banker's rounding): $26.125 → $26.12 (2 is even, rounds down); $1.875  │
│                       │ → $1.88 (7 is odd, rounds up); $0.125 → $0.12 (GIZMO)                                        │
├───────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ Discount selection    │ Volume discount only wins when strictly greater than the customer rate; at qty=51, STAFF (25 │
│                       │ %) beats volume (10 %), WHOLESALE (15 %) beats volume (10 %)                                 │
├───────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ tax rounding          │ $14.00 × 8.25 % = $1.155 → $1.16 (retained digit 5 is odd → rounds up); same HALF_EVEN rule  │
├───────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ invoiceTotal          │ STAFF is tax-exempt — returns subtotal only; null customer type is treated as RETAIL (tax    │
│                       │ applies)                                                                                     │
├───────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ parseLines            │ null elements in the Vector are silently skipped; blank/whitespace strings are skipped; >2   │
│                       │ colon-tokens throw; non-numeric quantity throws                                              │
├───────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ dueDate               │ Both Saturday (+2) and Sunday (+1) cases push to the following Monday; confirmed with fixed  │
│                       │ 2024 calendar dates                                                                          │
├───────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ formatInvoice         │ STAFF output has no TAX line at all; unknown customer type normalises to RETAIL in the       │
│                       │ header                                                                                       │
└───────────────────────┴──────────────────────────────────────────────────────────────────────────────────────────────┘
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

Task Summary

Total Cost:              0.533
Total Duration:          4m 3s


Assistant Messages:      4
Tool Calls:              6
Task ID:                 6e4d92a016b8435380e8f1142ab417d2

````
