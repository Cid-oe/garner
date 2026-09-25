package com.acme.billing;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.math.BigDecimal;
import java.util.Calendar;
import java.util.Date;
import java.util.GregorianCalendar;
import java.util.Vector;
import org.junit.jupiter.api.Test;

/**
 * Hand-written control tests, one per documented quirk (see QUIRKS.md).
 * Bob's generated characterization suite must catch every quirk these catch.
 */
class ControlQuirksTest {

    private final InvoiceCalculator calc = new InvoiceCalculator();

    private static Vector lines(String... raw) {
        Vector v = new Vector();
        for (String r : raw) {
            v.addElement(r);
        }
        return v;
    }

    /** Q1: rounding is banker's rounding (HALF_EVEN), not HALF_UP. */
    @Test
    void q1_roundsHalfToEven() {
        assertEquals(new BigDecimal("0.12"), calc.lineTotal("GIZMO", 1, "RETAIL"));
        assertEquals(new BigDecimal("0.82"), calc.tax(new BigDecimal("10.00")));
    }

    /** Q2: the javadoc says "10 or more", but exactly 10 units gets no volume discount. */
    @Test
    void q2_volumeDiscountStartsAboveTen() {
        assertEquals(0.0, calc.volumeDiscountRate(10));
        assertEquals(0.05, calc.volumeDiscountRate(11));
        assertEquals(0.05, calc.volumeDiscountRate(50));
        assertEquals(0.10, calc.volumeDiscountRate(51));
    }

    /** Q3: customer types are trimmed and case-insensitive; unknown means retail. */
    @Test
    void q3_customerTypeIsForgiving() {
        assertEquals("WHOLESALE", calc.normalizeCustomerType("  wholesale "));
        assertEquals("STAFF", calc.normalizeCustomerType("Staff"));
        assertEquals("RETAIL", calc.normalizeCustomerType("vip"));
        assertEquals("RETAIL", calc.normalizeCustomerType(null));
        assertEquals(new BigDecimal("21.25"), calc.lineTotal("WIDGET", 10, " wholesale"));
    }

    /** Q4: a due date that lands on a weekend moves to the following Monday. */
    @Test
    void q4_dueDateSkipsWeekends() {
        // 2026-08-28 (Friday) + 30 days = 2026-09-27 (Sunday) -> Monday 2026-09-28
        Date due = calc.dueDate(new GregorianCalendar(2026, Calendar.AUGUST, 28).getTime());
        assertEquals(new GregorianCalendar(2026, Calendar.SEPTEMBER, 28).getTime(), due);
    }

    /** Whole-invoice sanity check: staff are tax exempt, discounts do not stack. */
    @Test
    void invoiceTotalsMatchFinance() {
        Vector order = lines("WIDGET:12", "", "GADGET:1");
        assertEquals(new BigDecimal("44.91"), calc.invoiceTotal(order, "retail"));
        assertEquals(new BigDecimal("32.24"), calc.invoiceTotal(order, "STAFF"));
    }
}
