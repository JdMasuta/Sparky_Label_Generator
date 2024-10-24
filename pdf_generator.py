from typing import List, Tuple

# Global font settings
FONT_REGULAR = 'F1'
FONT_BOLD = 'F2'
FONT_SIZE_TITLE1 = 20
FONT_SIZE_TITLE2 = 16
FONT_SIZE_BARCODE = 14

# Character width approximations (adjust based on your font)
CHAR_WIDTH_REGULAR = 0.5
CHAR_WIDTH_BOLD = 0.6

# Label dimensions
LABEL_WIDTH = 300
LABEL_HEIGHT = 160
LABEL_MARGIN_LEFT = 76
LABEL_MARGIN_BOTTOM = 4

# Barcode dimensions
BARCODE_HEIGHT = 50
BAR_WIDTH_NARROW = 1.5 # Barcode width modifier

def generate_code39(data: str) -> List[Tuple[int, int, int, int]]:
    """Generate Code 39 barcode as a list of rectangles."""
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ-. $/+%*"
    patterns = [
        "1010001110111010", "1110100010101110", "1011100010101110", "1110111000101010",
        "1010001110101110", "1110100011101010", "1011100011101010", "1010001011101110",
        "1110100010111010", "1011100010111010", "1110101000101110", "1011101000101110",
        "1110111010001010", "1010111000101110", "1110101110001010", "1011101110001010",
        "1010100011101110", "1110101000111010", "1011101000111010", "1010111000111010",
        "1110101010001110", "1011101010001110", "1110111010100010", "1010111010001110",
        "1110101110100010", "1011101110100010", "1010101110001110", "1110101011100010",
        "1011101011100010", "1010111011100010", "1110001010101110", "1000111010101110",
        "1110001110101010", "1000101110101110", "1110001011101010", "1000111011101010",
        "1000101011101110", "1110001010111010", "1000111010111010", "1000100010001010",
        "1000100010100010", "1000101000100010", "1010001000100010", "1000101110111010"
    ]
    
    rectangles = []
    x, y = 0, 0
    narrow_width = BAR_WIDTH_NARROW
    wide_width = narrow_width * 3
    height = 100

    def add_char(char):
        nonlocal x
        pattern = patterns[chars.index(char)]
        for i, bit in enumerate(pattern):
            if bit == '1':
                width = wide_width if i % 2 == 0 else narrow_width
                rectangles.append((x, y, width, height))
            x += wide_width if i % 2 == 0 else narrow_width

    # Start character
    add_char('*')

    for char in data:
        add_char(char)

    # Stop character
    add_char('*')

    return rectangles

def create_pdf(items: List[dict]) -> bytes:
    """Create a PDF with improved label formatting, precisely centered content, and cutting guide, supporting multiple pages."""
    def escape_pdf_string(s):
        return s.replace('(', '\\(').replace(')', '\\)')

    def get_string_width(s, font_size, font_type):
        char_width = CHAR_WIDTH_BOLD if font_type == FONT_BOLD else CHAR_WIDTH_REGULAR
        return len(s) * char_width * font_size

    pdf_content = [
        '%PDF-1.4',
        '1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj'
    ]

    pages = []
    page_count = (len(items) + 3) // 4  # Calculate total number of pages

    for page in range(page_count):
        content = ['BT']
        for i in range(4):
            item_index = page * 4 + i
            if item_index >= len(items):
                break

            item = items[item_index]
            y_bottom = 792 - (i * 198 + 180)  # Bottom of the label
            y_top = y_bottom + LABEL_HEIGHT   # Top of the label
            
            # Draw main border
            content.extend([
                '2 w',  # Set line width to 2
                '0.8 0.8 0.8 RG',  # Set stroke color to light gray
                f'{LABEL_MARGIN_LEFT} {y_bottom+LABEL_MARGIN_BOTTOM} {LABEL_WIDTH} {LABEL_HEIGHT} re S',  # Draw rectangle
            ])
            
            # Draw secondary dashed border for cutting guide
            content.extend([
                '[4 4] 0 d',  # Set dash pattern
                '1 w',  # Set line width to 1
                '0 0 0 RG',  # Set stroke color to black
                f'{LABEL_MARGIN_LEFT-10} {y_bottom-6} {LABEL_WIDTH+20} {LABEL_HEIGHT+20} re S',  # Draw rectangle
                '[] 0 d'  # Reset dash pattern
            ])
            
            # Center of the label
            center_x = LABEL_MARGIN_LEFT + (LABEL_WIDTH / 2)
            
            # Title 1 (larger font, centered)
            title1_width = get_string_width(item["title1"], FONT_SIZE_TITLE1, FONT_BOLD)
            title1_start = center_x - (title1_width / 2)
            content.extend([
                f'/{FONT_BOLD} {FONT_SIZE_TITLE1} Tf',  # Bold font
                '0 0 0 rg',  # Black color
                f'1 0 0 1 {title1_start} {y_top-30} Tm',
                f'({escape_pdf_string(item["title1"])}) Tj'
            ])
            
            # Title 2 (smaller font, centered)
            title2_width = get_string_width(item["title2"], FONT_SIZE_TITLE2, FONT_REGULAR)
            title2_start = center_x - (title2_width / 2)
            content.extend([
                f'/{FONT_REGULAR} {FONT_SIZE_TITLE2} Tf',  # Regular font
                f'1 0 0 1 {title2_start} {y_top-55} Tm',
                f'({escape_pdf_string(item["title2"])}) Tj'
            ])
            
            # Generate and draw barcode (centered)
            barcode = generate_code39(item['barcode'])
            content.append('0 G')  # Set fill color to black
            barcode_total_width = sum(rect[2] for rect in barcode) * 0.5
            barcode_start_x = center_x - (barcode_total_width / 2) - 50
            barcode_start_y = y_bottom + (LABEL_HEIGHT - BARCODE_HEIGHT) / 3  # Bottom third vertically
            for rect in barcode:
                x, _, width, height = rect
                content.append(f'{barcode_start_x + x*0.5} {barcode_start_y} {width*0.5} {BARCODE_HEIGHT} re f')
            
            # Barcode number (centered)
            barcode_text = "*" + item["barcode"] + "*"
            barcode_text_width = get_string_width(barcode_text, FONT_SIZE_BARCODE, FONT_REGULAR)
            barcode_text_start = center_x - (barcode_text_width / 2)
            content.extend([
                f'/{FONT_REGULAR} {FONT_SIZE_BARCODE} Tf',  # Regular font
                f'1 0 0 1 {barcode_text_start} {y_bottom+20} Tm',
                f'({escape_pdf_string(barcode_text)}) Tj'
            ])

        content.append('ET')
        pages.append('\n'.join(content))

    # Add page objects
    for i in range(page_count):
        pdf_content.append(f'{3+i*2} 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents {4+i*2} 0 R/Resources<</Font<</F1 {3+page_count*2} 0 R/F2 {4+page_count*2} 0 R>>>>>>endobj')
        pdf_content.append(f'{4+i*2} 0 obj<</Length {5+i*2} 0 R>>stream\n{pages[i]}\nendstream\nendobj')
        pdf_content.append(f'{5+i*2} 0 obj\n{len(pages[i])}\nendobj')

    # Add Pages object
    pdf_content.insert(2, f'2 0 obj<</Type/Pages/Kids[{" ".join([f"{3+i*2} 0 R" for i in range(page_count)])}]/Count {page_count}>>endobj')

    # Add font objects
    pdf_content.extend([
        f'{3+page_count*2} 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj',
        f'{4+page_count*2} 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica-Bold>>endobj',
    ])

    # Create xref
    xref_start = len('\n'.join(pdf_content)) + 1
    pdf_content.append('xref')
    pdf_content.append(f'0 {5+page_count*2}')
    pdf_content.append('0000000000 65535 f ')
    
    offset = 0
    for i in range(1, 5+page_count*2):
        offset += len(pdf_content[i-1]) + 1  # +1 for newline
        pdf_content.append(f'{offset:010} 00000 n ')

    # Trailer
    pdf_content.extend([
        f'trailer<</Size {5+page_count*2}/Root 1 0 R>>',
        'startxref',
        str(xref_start),
        '%%EOF'
    ])

    return '\n'.join(pdf_content).encode()
