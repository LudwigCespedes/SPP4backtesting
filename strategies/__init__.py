from pathlib import Path
import sys

# Obtener el directorio raíz del proyecto (3 niveles arriba de este archivo)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
print(f"Project root set to: {project_root}")