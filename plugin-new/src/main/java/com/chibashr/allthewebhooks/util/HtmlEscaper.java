package com.chibashr.allthewebhooks.util;

public final class HtmlEscaper {
    private HtmlEscaper() {
    }

    public static String escape(String input) {
        if (input == null) {
            return "";
        }
        StringBuilder builder = new StringBuilder();
        for (char c : input.toCharArray()) {
            switch (c) {
                case '&':
                    builder.append("&amp;");
                    break;
                case '<':
                    builder.append("&lt;");
                    break;
                case '>':
                    builder.append("&gt;");
                    break;
                case '"':
                    builder.append("&quot;");
                    break;
                case '\'':
                    builder.append("&#39;");
                    break;
                default:
                    builder.append(c);
                    break;
            }
        }
        return builder.toString();
    }
}
