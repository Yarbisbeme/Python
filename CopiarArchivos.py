import os
import shutil

# 📁 Carpeta donde están tus DTO originales
SOURCE_DIR = r"C:\Users\Eikon\OneDrive - eikon.com.do\Escritorio\EikonWebApi\EikonWebApi_20251022\EikonWebApi\EIKON.Data\DTOs"   # <-- cámbiala a tu ruta real
# 📁 Carpeta destino
DEST_DIR = os.path.join(SOURCE_DIR, "newDto")

# Crea la carpeta destino si no existe
os.makedirs(DEST_DIR, exist_ok=True)

# 🧾 Lista de DTOs a mover
dto_list = [
    "ATrhaaa000Dto", "CsrPreGenDto", "DxMenuItemDto", "DxMenuPlanoDto", "DxMnItemDto",
    "Frhaa010Dto", "Frhad010Dto", "Frhag010Dto", "Frham000Dto", "Frhan000Dto",
    "Frhap000Dto", "Frhaq000Dto", "Frhau000Dto", "Frhav000Dto", "Frhaw000Dto",
    "Frhaw010Dto", "Frhba010Dto", "Frhbb010Dto", "Frhbe010Dto", "Frhbg000Dto",
    "Frhbg010Dto", "Frhbh010Dto", "Frhbk000Dto", "Frhbp010Dto", "Frhbq010Dto",
    "Frhbs000Dto", "Frhca000Dto", "Frhcb010Dto", "Frhcc000Dto", "Frhcd000Dto",
    "Frhcd010Dto", "Frhce000Dto", "Frhch000Dto", "Frhck000Dto", "Frhcl000Dto",
    "Frhcm010Dto", "Frhcn000Dto", "Frhco000Dto", "Frhcp000Dto", "Frhcp010Dto",
    "Frhcq010Dto", "Frhcr000Dto", "Frhcr010Dto", "Frhcs010Dto", "Frhct010Dto",
    "Frhcw010Dto", "Frhdb010Dto", "Frhea000Dto", "Frhea010Dto", "Frhec010Dto",
    "Frheh010Dto", "Frhei000Dto", "Frhem000Dto", "Frheo010Dto", "Frhep010Dto",
    "Frheq000Dto", "Frher000Dto", "Frhes010Dto", "Frhet000Dto", "Frhev000Dto",
    "Frhev010Dto", "Frhew000Dto", "Frhex010Dto", "Frhey000Dto", "Frhfc010Dto",
    "Frhge000Dto", "Frhgl010Dto", "FrhgraphDto", "Frhgs010Dto", "Frhha010Dto",
    "Frhhb010Dto", "Frhhe010Dto", "Frhhp000Dto", "Frhhp010Dto", "Frhhq000Dto",
    "Frhhr010Dto", "Frhhs000Dto", "Frhhv010Dto", "Frhia010Dto", "Frhic010Dto",
    "Frhid010Dto", "Frhim010Dto", "Frhin000Dto", "Frhip010Dto", "Frhjc000Dto",
    "Frhjp010Dto", "Frhjr010Dto", "Frhjw010Dto", "Frhkd000Dto", "Frhkh000Dto",
    "Frhld010Dto", "Frhlm010Dto", "Frhlp010Dto", "Frhlq010Dto", "Frhmc010Dto",
    "Frhmp010Dto", "Frhmr010Dto", "Frhnc010Dto", "Frhne010Dto", "frhpw000Dto",
    "Frhrj010Dto", "Frhsw010Dto", "Frhte010Dto", "Krhpa000Dto", "Mrhcc000Dto",
    "Mrhco000Dto", "rptPuestosEstatusDto", "rrhel006aDto", "Test", "Trhem000Dto",
    "Trhbe000Dtocs", "Trher001Dto", "Trhfw000Dto", "Trhmd010Dto", "Trhpe000Dto",
    "Trhpo000Dto", "Trhqc000Dto", "Trhtk000Dto", "Trhtp010Dto", "Trhtw000Dto",
    "Trhwa010Dto", "usuarioDto"
]

# Extensión esperada (ajústala según tu caso)
EXTENSION = ".cs"  # o ".ts", ".cs", etc.

movidos = 0

for dto in dto_list:
    file_name = dto + EXTENSION
    source_path = os.path.join(SOURCE_DIR, file_name)
    dest_path = os.path.join(DEST_DIR, file_name)
    
    if os.path.exists(source_path):
        shutil.move(source_path, dest_path)
        movidos += 1
        print(f"✅ Movido: {file_name}")
    else:
        print(f"⚠️ No encontrado: {file_name}")

print(f"\n📦 {movidos} archivos movidos a '{DEST_DIR}'")
