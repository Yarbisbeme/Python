import os

# Rutas de tus carpetas
path_dtos = r"C:\Users\Eikon\Downloads\Comparar\Comparar\Nueva carpeta\DTOs"
path_models = r"C:\Users\Eikon\Downloads\Comparar\Comparar\Nueva carpeta\Models"

# Obtener los nombres de archivo sin extensión
dtos = {os.path.splitext(f)[0].replace('Dto', '').lower(): f for f in os.listdir(path_dtos) if f.endswith('.cs')}
models = {os.path.splitext(f)[0].lower(): f for f in os.listdir(path_models) if f.endswith('.cs')}

# DTOs sin modelo
dtos_sin_modelo = [filename for name, filename in dtos.items() if name not in models]

# Modelos sin DTO
modelos_sin_dto = [filename for name, filename in models.items() if name not in dtos]

print(f"Total de DTOs: {len(dtos)}")
print(f"Total de Models: {len(models)}")

print(f"\nDTOs sin modelo equivalente: {len(dtos_sin_modelo)}")
for s in dtos_sin_modelo:
    print(f" - {s}")

print(f"\nModels sin DTO equivalente: {len(modelos_sin_dto)}")
for s in modelos_sin_dto:
    print(f" - {s}")
