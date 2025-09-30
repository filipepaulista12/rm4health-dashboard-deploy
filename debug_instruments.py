#!/usr/bin/env python3
"""
Script para debugar os nomes dos instrumentos no REDCap
"""

from local_redcap_client import LocalREDCapClient

def debug_instruments():
    print("=== DEBUG: Instrumentos REDCap ===")
    
    client = LocalREDCapClient()
    data = client.get_data()
    
    print(f"Total de registos: {len(data)}")
    
    # Verificar valores únicos de redcap_repeat_instrument
    instruments = set()
    for record in data:
        instrument = record.get('redcap_repeat_instrument', '')
        if instrument:
            instruments.add(str(instrument))
    
    print(f"\nInstrumentos únicos encontrados ({len(instruments)}):")
    for i, instrument in enumerate(sorted(instruments)):
        print(f"{i}: '{instrument}'")
    
    # Contar registos por instrumento
    instrument_counts = {}
    for record in data:
        instrument = record.get('redcap_repeat_instrument', 'PRINCIPAL')
        instrument_counts[instrument] = instrument_counts.get(instrument, 0) + 1
    
    print(f"\nContagem por instrumento:")
    for instrument, count in sorted(instrument_counts.items()):
        print(f"'{instrument}': {count} registos")

if __name__ == "__main__":
    debug_instruments()
