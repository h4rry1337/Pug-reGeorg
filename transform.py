#!/usr/bin/env python3
"""
Transforma Neo-reGeorg para Pug-reGeorg com strings modificadas para evasão de EDR.
"""

import os
import re
import random
import string
import hashlib

# ============================================================================
# MAPEAMENTO DE SUBSTITUIÇÕES
# ============================================================================

REPLACEMENTS = {
    # Strings identificáveis principais
    "Neo-reGeorg": "Pug-reGeorg",
    "NeoReGeorg": "PugReGeorg", 
    "Neo reGeorg": "Pug reGeorg",
    "neoreg": "pugreg",
    "Neoreg": "Pugreg",
    "NeoGeorg": "PugGeorg",
    "neoGeorg": "pugGeorg",
    "neoreg_servers": "pugreg_tunnels",
    
    # Mensagem de confirmação (alterar hash)
    "NeoGeorg says, 'All seems fine'": "Service endpoint initialized successfully",
    "All seems fine": "Endpoint ready",
    
    # URLs
    "https://github.com/L-codes/Neo-reGeorg": "https://internal.corp/tools/proxy",
    "L-codes/Neo-reGeorg": "internal/proxy",
    
    # Autor
    "__author__  = 'L'": "__author__  = 'Pug'",
    
    # Nomes de classes/funções
    "NeoregReponseFormatError": "ProxyResponseFormatError",
    "askNeoGeorg": "checkEndpoint",
    "Ask NeoGeorg": "Check Endpoint",
    
    # Variáveis identificáveis
    "GeorgHello": "EndpointMsg",
    "georgHello": "endpointMsg",
    
    # Logs
    "Checking if NeoGeorg is ready": "Verifying endpoint availability",
    "NeoGeorg is ready": "Endpoint is ready",
}

# Strings para adicionar variabilidade (comentários aleatórios)
RANDOM_COMMENTS = [
    "// Configuration handler",
    "// Data processor", 
    "// Stream manager",
    "// Connection handler",
    "// Buffer controller",
]

def transform_file(filepath):
    """Transforma um arquivo aplicando substituições."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except:
        return False
    
    original_hash = hashlib.sha256(content.encode()).hexdigest()
    
    # Aplicar substituições
    for old, new in REPLACEMENTS.items():
        content = content.replace(old, new)
    
    # Adicionar salt aleatório em comentários para mudar hash
    salt = ''.join(random.choices(string.ascii_lowercase, k=8))
    
    if filepath.endswith('.py'):
        content = f"# Build: {salt}\n" + content
    elif filepath.endswith('.php'):
        content = content.replace('<?php', f'<?php\n// Build: {salt}')
    elif filepath.endswith('.jsp') or filepath.endswith('.jspx'):
        content = f'<%-- Build: {salt} --%>\n' + content
    elif filepath.endswith('.aspx'):
        content = f'<%-- Build: {salt} --%>\n' + content
    elif filepath.endswith('.ashx'):
        content = f'<%-- Build: {salt} --%>\n' + content
    elif filepath.endswith('.js'):
        content = f'// Build: {salt}\n' + content
    elif filepath.endswith('.go'):
        content = f'// Build: {salt}\n' + content
    elif filepath.endswith('.cs'):
        content = f'// Build: {salt}\n' + content
    
    new_hash = hashlib.sha256(content.encode()).hexdigest()
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return original_hash != new_hash

def main():
    root = os.path.dirname(os.path.abspath(__file__))
    
    print("=" * 60)
    print("Pug-reGeorg Transformer - EDR Evasion")
    print("=" * 60)
    
    # Arquivos para transformar
    files_to_transform = [
        'neoreg.py',
        'templates/tunnel.php',
        'templates/tunnel.jsp',
        'templates/tunnel.jspx', 
        'templates/tunnel.aspx',
        'templates/tunnel.ashx',
        'templates/tunnel.js',
        'templates/tunnel.go',
        'templates/tunnel.cs',
        'templates/NeoreGeorg.java',
    ]
    
    transformed = 0
    for relpath in files_to_transform:
        filepath = os.path.join(root, relpath)
        if os.path.exists(filepath):
            if transform_file(filepath):
                print(f"[+] Transformed: {relpath}")
                transformed += 1
            else:
                print(f"[-] No changes: {relpath}")
        else:
            print(f"[!] Not found: {relpath}")
    
    # Renomear arquivo principal
    old_main = os.path.join(root, 'neoreg.py')
    new_main = os.path.join(root, 'pugreg.py')
    if os.path.exists(old_main):
        os.rename(old_main, new_main)
        print(f"\n[+] Renamed: neoreg.py -> pugreg.py")
    
    print(f"\n[*] Transformed {transformed} files")
    print("[*] Hash signatures changed for EDR evasion")
    print("\nUsage:")
    print("  ./pugreg.py generate -k <password>")
    print("  ./pugreg.py -k <password> -u <url>")

if __name__ == '__main__':
    main()
