import java.nio.file.*; import java.util.*;
import org.apache.commons.codec.language.Metaphone;
public class Run { public static void main(String[] a) throws Exception {
  Metaphone m = new Metaphone(); StringBuilder sb = new StringBuilder();
  for (String w : Files.readAllLines(Path.of(a[0]))) {
    String r; try { r = m.metaphone(w); } catch (Exception e) { r = "EXC:" + e.getClass().getSimpleName(); }
    sb.append(w).append('\t').append(r).append('\n'); }
  Files.writeString(Path.of(a[1]), sb.toString()); } }
