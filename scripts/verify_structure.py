"""
Script de verificación de la estructura del proyecto.

Verifica que todos los archivos y carpetas estén en su lugar.
"""

import os
import sys


def check_directory(path, name):
    """Verifica que un directorio exista."""
    if os.path.exists(path) and os.path.isdir(path):
        print(f"✓ {name}")
        return True
    else:
        print(f"✗ {name} - NO ENCONTRADO")
        return False


def check_file(path, name):
    """Verifica que un archivo exista."""
    if os.path.exists(path) and os.path.isfile(path):
        print(f"✓ {name}")
        return True
    else:
        print(f"✗ {name} - NO ENCONTRADO")
        return False


def main():
    """Función principal."""
    print("="*60)
    print("VERIFICACIÓN DE ESTRUCTURA DEL PROYECTO")
    print("="*60)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    
    all_ok = True
    
    # Verificar directorios principales
    print("\n1. Directorios principales:")
    dirs = [
        (os.path.join(project_root, "src"), "src/"),
        (os.path.join(project_root, "src", "strategies"), "src/strategies/"),
        (os.path.join(project_root, "src", "utils"), "src/utils/"),
        (os.path.join(project_root, "src", "config"), "src/config/"),
        (os.path.join(project_root, "scripts"), "scripts/"),
        (os.path.join(project_root, "tests"), "tests/"),
        (os.path.join(project_root, "legacy"), "legacy/"),
        (os.path.join(project_root, "data", "raw"), "data/raw/"),
        (os.path.join(project_root, "data", "processed"), "data/processed/"),
        (os.path.join(project_root, "results", "html"), "results/html/"),
        (os.path.join(project_root, "results", "csv"), "results/csv/"),
        (os.path.join(project_root, "results", "plots"), "results/plots/"),
    ]
    
    for path, name in dirs:
        all_ok &= check_directory(path, name)
    
    # Verificar archivos de estrategias
    print("\n2. Módulos de estrategias:")
    strategy_files = [
        (os.path.join(project_root, "src", "strategies", "base.py"), "base.py"),
        (os.path.join(project_root, "src", "strategies", "macd_strategies.py"), "macd_strategies.py"),
        (os.path.join(project_root, "src", "strategies", "sma_strategies.py"), "sma_strategies.py"),
        (os.path.join(project_root, "src", "strategies", "momentum_strategies.py"), "momentum_strategies.py"),
        (os.path.join(project_root, "src", "strategies", "grid_strategies.py"), "grid_strategies.py"),
        (os.path.join(project_root, "src", "strategies", "arbitrage_strategies.py"), "arbitrage_strategies.py"),
    ]
    
    for path, name in strategy_files:
        all_ok &= check_file(path, name)
    
    # Verificar archivos de utilidades
    print("\n3. Módulos de utilidades:")
    util_files = [
        (os.path.join(project_root, "src", "utils", "data_loader.py"), "data_loader.py"),
        (os.path.join(project_root, "src", "utils", "optimization.py"), "optimization.py"),
        (os.path.join(project_root, "src", "utils", "plotting.py"), "plotting.py"),
    ]
    
    for path, name in util_files:
        all_ok &= check_file(path, name)
    
    # Verificar archivos de configuración
    print("\n4. Archivos de configuración:")
    config_files = [
        (os.path.join(project_root, "src", "config", "symbols.py"), "symbols.py"),
    ]
    
    for path, name in config_files:
        all_ok &= check_file(path, name)
    
    # Verificar scripts ejecutables
    print("\n5. Scripts ejecutables:")
    script_files = [
        (os.path.join(project_root, "scripts", "run_macd_adx_ema.py"), "run_macd_adx_ema.py"),
        (os.path.join(project_root, "scripts", "run_sma_strategy.py"), "run_sma_strategy.py"),
        (os.path.join(project_root, "scripts", "run_optimization.py"), "run_optimization.py"),
    ]
    
    for path, name in script_files:
        all_ok &= check_file(path, name)
    
    # Verificar documentación
    print("\n6. Documentación:")
    doc_files = [
        (os.path.join(project_root, "README.md"), "README.md"),
        (os.path.join(project_root, "requirements.txt"), "requirements.txt"),
        (os.path.join(project_root, "setup.py"), "setup.py"),
    ]
    
    for path, name in doc_files:
        all_ok &= check_file(path, name)
    
    # Verificar archivos __init__.py
    print("\n7. Archivos __init__.py:")
    init_files = [
        (os.path.join(project_root, "src", "__init__.py"), "src/__init__.py"),
        (os.path.join(project_root, "src", "strategies", "__init__.py"), "src/strategies/__init__.py"),
        (os.path.join(project_root, "src", "utils", "__init__.py"), "src/utils/__init__.py"),
        (os.path.join(project_root, "src", "config", "__init__.py"), "src/config/__init__.py"),
        (os.path.join(project_root, "tests", "__init__.py"), "tests/__init__.py"),
    ]
    
    for path, name in init_files:
        all_ok &= check_file(path, name)
    
    # Resumen
    print("\n" + "="*60)
    if all_ok:
        print("✓ VERIFICACIÓN EXITOSA - Todos los archivos están en su lugar")
        print("\nEstructura de estrategias:")
        print("  • MACD: 4 estrategias")
        print("  • SMA: 2 estrategias")
        print("  • Momentum: 3 estrategias")
        print("  • Grid Trading: 1 estrategia")
        print("  • Arbitraje: 1 estrategia")
    else:
        print("✗ VERIFICACIÓN FALLIDA - Algunos archivos faltan")
    print("="*60)
    
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
