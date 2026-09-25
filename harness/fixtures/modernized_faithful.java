package com.acme.billing;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.DayOfWeek;
import java.time.LocalDate;
import java.time.ZoneId;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Vector;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Harness fixture, hand-written: a behaviour-preserving modernization used to
 * test the gate in mock mode. Not Bob output.
 */
public class InvoiceCalculator {

    public static final String TYPE_RETAIL = "RETAIL";
    public static final String TYPE_WHOLESALE = "WHOLESALE";
    public static final String TYPE_STAFF = "STAFF";

    private static final BigDecimal TAX_RATE = BigDecimal.valueOf(0.0825);
    private static final int PAYMENT_TERMS_DAYS = 30;

    private record Line(String sku, int quantity) {}

    private final Map<String, Double> priceList = new ConcurrentHashMap<>(Map.of(
            "WIDGET", 2.50, "GADGET", 12.99, "GIZMO", 0.125, "DOOHICKEY", 49.95));

    public void setPrice(String sku, double price) {
        if (sku == null) throw new IllegalArgumentException("sku is required");
        if (price < 0) throw new IllegalArgumentException("price must not be negative: " + price);
        priceList.put(sku.toUpperCase(Locale.ROOT), price);
    }

    public double getPrice(String sku) {
        if (sku == null) throw new IllegalArgumentException("sku is required");
        Double price = priceList.get(sku.trim().toUpperCase(Locale.ROOT));
        if (price == null) throw new IllegalArgumentException("unknown sku: " + sku);
        return price;
    }

    public String normalizeCustomerType(String raw) {
        if (raw == null || raw.isBlank()) return TYPE_RETAIL;
        String t = raw.trim();
        for (String known : List.of(TYPE_WHOLESALE, TYPE_STAFF, TYPE_RETAIL)) {
            if (t.equalsIgnoreCase(known)) return known;
        }
        return TYPE_RETAIL;
    }

    public double customerDiscountRate(String customerType) {
        return switch (normalizeCustomerType(customerType)) {
            case TYPE_WHOLESALE -> 0.15;
            case TYPE_STAFF -> 0.25;
            default -> 0.0;
        };
    }

    public double volumeDiscountRate(int quantity) {
        if (quantity > 50) return 0.10;
        if (quantity > 10) return 0.05;
        return 0.0;
    }

    public BigDecimal lineTotal(String sku, int quantity, String customerType) {
        if (quantity <= 0) throw new IllegalArgumentException("quantity must be positive: " + quantity);
        BigDecimal gross = BigDecimal.valueOf(getPrice(sku)).multiply(BigDecimal.valueOf(quantity));
        double rate = Math.max(customerDiscountRate(customerType), volumeDiscountRate(quantity));
        return gross.multiply(BigDecimal.ONE.subtract(BigDecimal.valueOf(rate))).setScale(2, RoundingMode.HALF_EVEN);
    }

    private List<Line> parse(List<String> rawLines) {
        List<Line> parsed = new ArrayList<>();
        for (String line : rawLines) {
            if (line == null || line.isBlank()) continue;
            String[] parts = java.util.Arrays.stream(line.split(":")).filter(p -> !p.isEmpty()).toArray(String[]::new);
            if (parts.length != 2) {
                throw new IllegalArgumentException("malformed line: " + line);
            }
            try {
                parsed.add(new Line(parts[0].trim(), Integer.parseInt(parts[1].trim())));
            } catch (NumberFormatException nfe) {
                throw new IllegalArgumentException("bad quantity in line: " + line);
            }
        }
        return parsed;
    }

    public Vector parseLines(Vector rawLines) {
        Vector out = new Vector();
        for (Line l : parse(new ArrayList<String>(rawLines))) out.addElement(new Object[] { l.sku(), l.quantity() });
        return out;
    }

    public BigDecimal subtotal(Vector rawLines, String customerType) {
        BigDecimal sum = new BigDecimal("0.00");
        for (Line l : parse(new ArrayList<String>(rawLines))) sum = sum.add(lineTotal(l.sku(), l.quantity(), customerType));
        return sum;
    }

    public BigDecimal tax(BigDecimal subtotal) {
        return subtotal.multiply(TAX_RATE).setScale(2, RoundingMode.HALF_EVEN);
    }

    public BigDecimal invoiceTotal(Vector rawLines, String customerType) {
        BigDecimal sub = subtotal(rawLines, customerType);
        return TYPE_STAFF.equals(normalizeCustomerType(customerType)) ? sub : sub.add(tax(sub));
    }

    public Date dueDate(Date invoiceDate) {
        ZoneId zone = ZoneId.systemDefault();
        LocalDate due = invoiceDate.toInstant().atZone(zone).toLocalDate().plusDays(PAYMENT_TERMS_DAYS);
        if (due.getDayOfWeek() == DayOfWeek.SATURDAY) due = due.plusDays(2);
        else if (due.getDayOfWeek() == DayOfWeek.SUNDAY) due = due.plusDays(1);
        return Date.from(due.atTime(invoiceDate.toInstant().atZone(zone).toLocalTime()).atZone(zone).toInstant());
    }

    public String formatInvoice(Vector rawLines, String customerType) {
        StringBuilder sb = new StringBuilder();
        String type = normalizeCustomerType(customerType);
        sb.append("INVOICE (").append(type).append(")\n");
        for (Line l : parse(new ArrayList<String>(rawLines))) {
            sb.append(l.sku()).append(" x").append(l.quantity()).append(" = ")
              .append(lineTotal(l.sku(), l.quantity(), customerType)).append("\n");
        }
        BigDecimal sub = subtotal(rawLines, customerType);
        sb.append("SUBTOTAL ").append(sub).append("\n");
        if (!type.equals(TYPE_STAFF)) sb.append("TAX ").append(tax(sub)).append("\n");
        sb.append("TOTAL ").append(invoiceTotal(rawLines, customerType)).append("\n");
        return sb.toString();
    }
}
