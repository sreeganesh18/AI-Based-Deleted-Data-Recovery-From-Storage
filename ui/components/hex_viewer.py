import streamlit as st

def render_hex_viewer(data, length=16, max_rows=64):
    """
    Renders a monospaced hex dump (offset, hex, ascii) with clean styling using st.html.
    
    Args:
        data (bytes): The binary data to display.
        length (int): Number of bytes per row.
        max_rows (int): Maximum number of rows to display to prevent UI lag.
    """
    if not data:
        st.info("No data available to display.")
        return

    # Truncate if too large for the viewer
    original_size = len(data)
    truncated = False
    if len(data) > length * max_rows:
        data = data[:length * max_rows]
        truncated = True

    lines = []
    for i in range(0, len(data), length):
        chunk = data[i:i + length]
        offset = f"{i:08x}"
        # Format hex values with fixed width
        hex_vals = " ".join(f"{b:02x}" for b in chunk).ljust(length * 3 - 1)
        # Format ASCII values, replacing non-printable with dots
        ascii_vals = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
        
        # Use HTML entities for special characters in ASCII view to avoid breaking the layout
        ascii_vals = ascii_vals.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        lines.append(f"<code>{offset}  {hex_vals}  |{ascii_vals}|</code>")

    if truncated:
        lines.append(f"<code>... (truncated {original_size - len(data)} more bytes)</code>")

    hex_dump = "<br>".join(lines)
    
    # Render with custom styling
    st.markdown("**Hex Viewer**")
    st.html(f"""
        <div style='
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
            background-color: #0e1117;
            color: #d1d5db;
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid #30363d;
            overflow-x: auto;
            white-space: pre;
            line-height: 1.4;
            font-size: 0.85rem;
        '>
            {hex_dump}
        </div>
    """)
