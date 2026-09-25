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
