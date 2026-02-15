"""
malformed_generator.py - Malformed File Generator for MaxKB Fuzzing
"""

import os
import zipfile
import io


class MalformedFileGenerator:
    def __init__(self, output_dir="malformed_files"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def _save(self, filename, content):
        path = os.path.join(self.output_dir, filename)
        if isinstance(content, bytes):
            with open(path, 'wb') as f:
                f.write(content)
        else:
            with open(path, 'w', encoding='utf-8', errors='surrogateescape') as f:
                f.write(content)
        return path

    def generate_pdf_variants(self):
        variants = []
        variants.append(self._save("pdf_01_empty.pdf", b""))
        variants.append(self._save("pdf_02_header_only.pdf", b"%PDF-1.4\n"))
        truncated = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<<"
        variants.append(self._save("pdf_03_truncated.pdf", truncated))
        large_content = b"%PDF-1.4\n" + b"A" * (5 * 1024 * 1024) + b"\n%%EOF"
        variants.append(self._save("pdf_04_large_5mb.pdf", large_content))
        null_pdf = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\n\x00\x00\x00\x00\nendobj\n%%EOF"
        variants.append(self._save("pdf_05_null_bytes.pdf", null_pdf))
        fake_pdf = b"%PXF-9.9\nThis is not a real PDF\n%%EOF"
        variants.append(self._save("pdf_06_fake_magic.pdf", fake_pdf))
        nested = b"%PDF-1.4\n"
        for i in range(1, 101):
            nested += f"{i} 0 obj\n<< /Type /Page /Parent {i+1} 0 R >>\nendobj\n".encode()
        nested += b"%%EOF"
        variants.append(self._save("pdf_07_deep_nested.pdf", nested))
        js_pdf = b"%PDF-1.4\n1 0 obj<< /Type /Catalog /OpenAction 3 0 R >>endobj\n3 0 obj<< /Type /Action /S /JavaScript /JS (app.alert('XSS')) >>endobj\n%%EOF"
        variants.append(self._save("pdf_08_javascript.pdf", js_pdf))
        return variants

    def generate_xlsx_variants(self):
        variants = []
        variants.append(self._save("xlsx_01_empty.xlsx", b""))
        variants.append(self._save("xlsx_02_bad_zip.xlsx", b"PK\x03\x04" + b"\x00" * 100))
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w') as zf:
            zf.writestr("random.txt", "This is not an Excel file")
        variants.append(self._save("xlsx_03_zip_no_excel.xlsx", buf.getvalue()))

        ct = '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="xml" ContentType="application/xml"/><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>'
        rels = '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>'
        wb = '<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheets><sheet name="Sheet1" sheetId="1" r:id="rId1" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"/></sheets></workbook>'
        wbr = '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>'

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w') as zf:
            zf.writestr("[Content_Types].xml", ct)
            zf.writestr("_rels/.rels", rels)
            zf.writestr("xl/workbook.xml", wb)
            zf.writestr("xl/_rels/workbook.xml.rels", wbr)
            zf.writestr("xl/worksheets/sheet1.xml", '<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row r="1"><c r="A1"><f>=CMD("calc")</f></c></row></sheetData></worksheet>')
        variants.append(self._save("xlsx_04_malicious_formula.xlsx", buf.getvalue()))

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w') as zf:
            zf.writestr("[Content_Types].xml", ct)
            zf.writestr("_rels/.rels", rels)
            zf.writestr("xl/workbook.xml", wb)
            zf.writestr("xl/_rels/workbook.xml.rels", wbr)
            huge = "X" * 100000
            zf.writestr("xl/worksheets/sheet1.xml", f'<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row r="1"><c r="A1" t="inlineStr"><is><t>{huge}</t></is></c></row></sheetData></worksheet>')
        variants.append(self._save("xlsx_05_huge_cell.xlsx", buf.getvalue()))
        variants.append(self._save("xlsx_06_null_bytes.xlsx", b"\x00" * 4096))
        return variants

    def generate_markdown_variants(self):
        variants = []
        deep = "\n".join([f"{'#' * min(i, 6)} Heading {i}" for i in range(1, 1001)])
        variants.append(self._save("md_01_deep_headings.md", deep))
        links = "\n".join([f"[link{i}](http://{'a'*200}.com/{i})" for i in range(5000)])
        variants.append(self._save("md_02_many_links.md", links))
        unclosed = "```python\n" * 100 + "print('hello')\n" + "text\n" * 100
        variants.append(self._save("md_03_unclosed_codeblocks.md", unclosed))
        xss_md = "# Title\n<script>alert('XSS')</script>\n![img](javascript:alert('xss'))\n[Click](javascript:alert(document.cookie))\n<img src=x onerror=alert('xss')>\n<svg onload=alert('XSS')>\n{{7*7}}\n${7*7}\n"
        variants.append(self._save("md_04_xss_injection.md", xss_md))
        special = "# Title\nParagraph with special chars\n"
        special += "Unicode: " + "".join(chr(i) for i in range(0x2600, 0x2700)) + "\n"
        variants.append(self._save("md_05_special_chars.md", special))
        table = "| C1 | C2 | C3 |\n|---|---|---|\n"
        table += "\n".join([f"| {'x'*50} | {'y'*50} | {'z'*50} |" for _ in range(10000)])
        variants.append(self._save("md_06_huge_table.md", table))
        return variants

    def generate_txt_variants(self):
        variants = []
        variants.append(self._save("txt_01_long_line.txt", "A" * (1024 * 1024)))
        mixed = b"UTF-8: Hello\n" + b"\xe4\xb8\xad\xe6\x96\x87" + b"\xff\xfe"
        variants.append(self._save("txt_02_mixed_encoding.txt", mixed))
        variants.append(self._save("txt_03_control_chars.txt", bytes(range(0, 32)) * 100))
        sql = "SELECT * FROM users WHERE 1=1;\nDROP TABLE documents;--\n' OR '1'='1'; --\n"
        variants.append(self._save("txt_04_sql_injection.txt", sql))
        return variants

    def generate_html_variants(self):
        variants = []
        variants.append(self._save("html_01_xss.html", "<html><body><script>alert('xss')</script><img src=x onerror=alert(1)></body></html>"))
        nested = "<html><body>" + "<div>" * 10000 + "X" + "</div>" * 10000 + "</body></html>"
        variants.append(self._save("html_02_deep_nested.html", nested))
        large = "<html><body>" + "<p>Paragraph</p>\n" * 50000 + "</body></html>"
        variants.append(self._save("html_03_large.html", large))
        variants.append(self._save("html_04_malicious_meta.html", '<html><head><meta http-equiv="refresh" content="0;url=javascript:alert(1)"><base href="http://evil.com/"></head><body>Normal</body></html>'))
        return variants

    def generate_docx_variants(self):
        variants = []
        variants.append(self._save("docx_01_empty.docx", b""))
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w') as zf:
            zf.writestr("word/document.xml", "<corrupted>not valid<///>")
            zf.writestr("[Content_Types].xml", "invalid")
        variants.append(self._save("docx_02_corrupted_xml.docx", buf.getvalue()))
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w') as zf:
            zf.writestr("word/document.xml", '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>&xxe;</w:t></w:r></w:p></w:body></w:document>')
            zf.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="xml" ContentType="application/xml"/><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
            zf.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        variants.append(self._save("docx_03_xxe.docx", buf.getvalue()))
        variants.append(self._save("docx_04_null.docx", b"\x00" * 2048))
        return variants

    def generate_all(self):
        all_files = {}
        print("=" * 60)
        print("MaxKB Fuzzing - Malformed File Generator")
        print("=" * 60)
        generators = {
            'pdf': self.generate_pdf_variants,
            'xlsx': self.generate_xlsx_variants,
            'markdown': self.generate_markdown_variants,
            'txt': self.generate_txt_variants,
            'html': self.generate_html_variants,
            'docx': self.generate_docx_variants,
        }
        for name, gen_func in generators.items():
            print(f"\n[*] Generating malformed {name.upper()} files...")
            all_files[name] = gen_func()
            print(f"    [OK] Generated {len(all_files[name])} variants")
        total = sum(len(v) for v in all_files.values())
        print(f"\n{'='*60}")
        print(f"[DONE] Total {total} malformed test files generated")
        print(f"    Output dir: {os.path.abspath(self.output_dir)}")
        print(f"{'='*60}")
        return all_files


if __name__ == "__main__":
    generator = MalformedFileGenerator()
    files = generator.generate_all()
    for cat, paths in files.items():
        print(f"\n{cat.upper()}:")
        for p in paths:
            print(f"  {os.path.basename(p):40s} ({os.path.getsize(p):>10,} bytes)")
