import os
import re

# Rutas de las carpetas
models_path = r'C:\Users\Eikon\OneDrive - eikon.com.do\Escritorio\EikonWebApi_20251022\EikonWebApi_20251022\EikonWebApi\EIKON.Data\Models'
dtos_path = r'C:\Users\Eikon\OneDrive - eikon.com.do\Escritorio\EikonWebApi_20251022\EikonWebApi_20251022\EikonWebApi\EIKON.Data\DTOs'

# Crear la carpeta dtocreado si no existe
if not os.path.exists(dtos_path):
    os.makedirs(dtos_path)

# Listar archivos .cs
models = [f for f in os.listdir(models_path) if f.endswith('.cs')]
dtos = [f for f in os.listdir(dtos_path) if f.endswith('.cs')]

# Expresión regular para detectar propiedades públicas
property_pattern = re.compile(r'public\s+([\w<>\[\]?]+)\s+([\w]+)\s*\{\s*get;\s*set;\s*\}')

def extract_properties(model_file_path):
    """Extrae propiedades públicas y aplica inicializaciones especiales"""
    dto_properties = []
    with open(model_file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            match = property_pattern.match(line)
            if match:
                type_name, prop_name = match.groups()
                type_lower = type_name.lower().replace("?", "")
                name_lower = prop_name.lower()

                # === Reglas especiales ===

                # Omitir propiedades tipo timestamp o con "timestamp" en el nombre
                if type_lower == "timestamp" or "timestamp" in name_lower:
                    continue

                # IdentityColumn
                if prop_name == "IdentityColumn":
                    prop_line = (
                        "        [Key]\n"
                        "        [DatabaseGenerated(DatabaseGeneratedOption.Identity)]\n"
                        "        public int IdentityColumn { get; set; } = 0;"
                    )

                # DateTime
                elif type_lower == "datetime":
                    prop_line = f"        public {type_name} {prop_name} {{ get; set; }} = new DateTime(1900, 01, 01);"

                # Enteros, Decimales y flotantes
                elif type_lower in ["int", "int32", "long", "short", "decimal", "double", "float"]:
                    prop_line = f"        public {type_name} {prop_name} {{ get; set; }} = 0;"

                # Strings
                elif type_lower == "string":
                    prop_line = f"        public string {prop_name} {{ get; set; }} = string.Empty;"

                # Resto de propiedades
                else:
                    prop_line = f"        public {type_name} {prop_name} {{ get; set; }}"

                dto_properties.append(prop_line)
    return dto_properties


def create_dto(model_file):
    """Crea el archivo DTO basado en el modelo"""
    model_name = model_file[:-3]
    dto_name = f"{model_name}Dto"
    dto_file_path = os.path.join(dtos_path, f"{dto_name}.cs")
    
    model_file_path = os.path.join(models_path, model_file)
    properties = extract_properties(model_file_path)
    
    # Contenido del DTO
    content = f"""using System;
    using System.ComponentModel.DataAnnotations;
    using System.ComponentModel.DataAnnotations.Schema;

   namespace Data.Eikon.DTOs
    {{
        public class {dto_name}
        {{
    """
    for prop in properties:
        content += prop + "\n"
    
    content += "    }\n}"
    
    # Guardar el archivo
    with open(dto_file_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"✅ DTO creado: {dto_file_path}")

# Crear DTOs para modelos que no los tienen en dtocreado
for model_file in models:
    expected_dto = f"{model_file[:-3]}Dto.cs"
    if expected_dto not in dtos:
        create_dto(model_file)

print("\n🚀 Proceso completado exitosamente.")
