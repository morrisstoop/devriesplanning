#!/usr/bin/env python3
"""
split_devries.py — Splits het grote index.html bestand in losse bestanden.

GEBRUIK:
1. Zet dit script in dezelfde map als je index.html
2. Run: python3 split_devries.py
3. Upload de gegenereerde bestanden naar GitHub

Output:
  - index.html     (structuur + CSS, laadt de JS bestanden)
  - data.js        (alle data arrays: R, NL, CAT_DATA, PC_LOOKUP, PLAN_DATA etc.)
  - heatmap.js     (heatmap + dagplanner logica - eerste <script> blok)
  - weekplanner.js (weekplanner + gantt logica - tweede <script> blok)
"""

import re
import os

INPUT_FILE = "index.html"

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"FOUT: {INPUT_FILE} niet gevonden in huidige map!")
        print(f"Zorg dat dit script in dezelfde map staat als je index.html")
        return
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        html = f.read()
    
    print(f"Origineel bestand: {len(html):,} characters ({len(html)//1024} KB)")
    
    # Vind alle <script> blokken
    script_pattern = re.compile(r'<script>(.*?)</script>', re.DOTALL)
    scripts = script_pattern.findall(html)
    
    print(f"Gevonden: {len(scripts)} script blokken")
    
    if len(scripts) < 1:
        print("FOUT: Geen script blokken gevonden!")
        return
    
    # === DATA EXTRACTIE uit script 1 ===
    script1 = scripts[0]
    
    # Zoek alle grote data declaraties
    data_vars = []
    data_patterns = [
        (r'const HW\s*=\s*\{[^}]+\};', 'HW'),
        (r'const R\s*=\s*\[.*?\];', 'R'),
        (r'const NL\s*=\s*\[.*?\];', 'NL'),
        (r'const IJSSELMEER\s*=\s*\[.*?\];', 'IJSSELMEER'),
        (r'const OA_LOCS\s*=\s*\[.*?\];', 'OA_LOCS'),
        (r'const PC_LOOKUP\s*=\s*\[.*?\];', 'PC_LOOKUP'),
        (r'const CAT_COLORS\s*=\s*\{.*?\};', 'CAT_COLORS'),
        (r'const CAT_BE\s*=\s*\{[^;]+\};', 'CAT_BE'),
        (r'const CAT_DATA\s*=\s*\{.*?\};', 'CAT_DATA'),
        (r'const DC\s*=\s*\{[^}]+\};', 'DC'),
        (r'const DI\s*=\s*\{[^}]+\};', 'DI'),
        (r'const CENTER\s*=\s*\{[^}]+\};', 'CENTER'),
        (r'const MIN_Z\s*=.*?;', 'MIN_Z'),
        (r'const DP_NORMTIJDEN\s*=\s*\{[^;]+\};', 'DP_NORMTIJDEN'),
        (r'const MAT_PRIJS\s*=\s*\{[^;]+\};', 'MAT_PRIJS'),
    ]
    
    data_content = "// =============================================\n"
    data_content += "// DATA.JS — De Vries Isolatietechniek\n"
    data_content += "// Auto-gegenereerd door split_devries.py\n"
    data_content += "// =============================================\n\n"
    
    remaining_script1 = script1
    
    for pattern, name in data_patterns:
        match = re.search(pattern, script1, re.DOTALL)
        if match:
            data_content += match.group(0) + "\n\n"
            remaining_script1 = remaining_script1.replace(match.group(0), f'// [MOVED TO data.js: {name}]')
            print(f"  Extracted: {name} ({len(match.group(0)):,} chars)")
        else:
            print(f"  WARNING: {name} niet gevonden")
    
    # Clean remaining script 1 (remove the [MOVED] comments for cleanliness)
    heatmap_lines = []
    for line in remaining_script1.split('\n'):
        if '// [MOVED TO data.js:' not in line:
            heatmap_lines.append(line)
    heatmap_content = '\n'.join(heatmap_lines)
    
    # Remove excessive blank lines
    while '\n\n\n' in heatmap_content:
        heatmap_content = heatmap_content.replace('\n\n\n', '\n\n')
    
    heatmap_content = "// =============================================\n" + \
                      "// HEATMAP.JS — Kaart, sidebar, dagplanner\n" + \
                      "// Auto-gegenereerd door split_devries.py\n" + \
                      "// =============================================\n\n" + \
                      heatmap_content.strip() + "\n"
    
    # === SCRIPT 2: WEEKPLANNER ===
    weekplanner_content = ""
    if len(scripts) >= 2:
        weekplanner_content = "// =============================================\n" + \
                              "// WEEKPLANNER.JS — Weekplanner & Gantt\n" + \
                              "// Auto-gegenereerd door split_devries.py\n" + \
                              "// =============================================\n\n"
        
        script2 = scripts[1]
        
        # Extract PLAN_DATA from script 2
        plan_match = re.search(r'const PLAN_DATA\s*=\s*\[.*?\];', script2, re.DOTALL)
        if plan_match:
            data_content += "\n" + plan_match.group(0) + "\n"
            script2 = script2.replace(plan_match.group(0), '// [PLAN_DATA moved to data.js]')
            print(f"  Extracted: PLAN_DATA ({len(plan_match.group(0)):,} chars)")
        
        # Clean script2
        wp_lines = [l for l in script2.split('\n') if '// [PLAN_DATA moved to data.js]' not in l]
        weekplanner_content += '\n'.join(wp_lines).strip() + "\n"
    
    # === NIEUWE INDEX.HTML ===
    # Vervang script blokken met externe referenties
    new_html = html
    
    # Vervang eerste script blok
    first_script = f'<script>{scripts[0]}</script>'
    new_html = new_html.replace(first_script, 
        '<script src="data.js"></script>\n<script src="heatmap.js"></script>')
    
    # Vervang tweede script blok (als aanwezig)
    if len(scripts) >= 2:
        second_script = f'<script>{scripts[1]}</script>'
        new_html = new_html.replace(second_script, 
            '<script src="weekplanner.js"></script>')
    
    # === SCHRIJF BESTANDEN ===
    files = {
        'index_new.html': new_html,
        'data.js': data_content,
        'heatmap.js': heatmap_content,
    }
    if weekplanner_content:
        files['weekplanner.js'] = weekplanner_content
    
    print("\n=== OUTPUT ===")
    total = 0
    for fname, content in files.items():
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(content)
        size = len(content)
        total += size
        print(f"  {fname}: {size:,} chars ({size//1024} KB)")
    
    print(f"\n  Totaal: {total:,} chars ({total//1024} KB)")
    print(f"  Origineel: {len(html):,} chars ({len(html)//1024} KB)")
    print(f"\n✅ Klaar! Upload deze bestanden naar GitHub:")
    print(f"   1. Hernoem index_new.html → index.html")
    print(f"   2. Upload data.js, heatmap.js, weekplanner.js")
    print(f"   3. Test lokaal door index_new.html in browser te openen")

if __name__ == '__main__':
    main()
