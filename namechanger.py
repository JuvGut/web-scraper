import sys

def process_text(input_file, output_file):
    umlaut_map = {
        'ü': 'ue',
        'ä': 'ae',
        'ö': 'oe',
        'Ü': 'Ue',
        'Ä': 'Ae',
        'Ö': 'Oe'
    }
    
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            if 'portrait' not in line.lower():
                # Replace umlauts
                for umlaut, replacement in umlaut_map.items():
                    line = line.replace(umlaut, replacement)
                
                # Reorder name (move last word to first)
                words = line.strip().split()
                if len(words) > 1:
                    words = [words[-1]] + words[:-1]
                    line = ' '.join(words) + '\n'
                
                outfile.write(line)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Verwendung: python script.py input_file output_file")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    process_text(input_file, output_file)
    print(f"Verarbeitung abgeschlossen. Ergebnis wurde in {output_file} gespeichert.")
