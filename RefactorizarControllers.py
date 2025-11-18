import os
import re
from string import Template # Importante para manejar la plantilla limpiamente

# ============================================================
# CONFIGURACIÓN DE RUTAS
# ============================================================
# Asegúrate de que estas rutas existan o el script las creará si es posible
BASE_PATH = r"C:\Users\Eikon\Downloads\RefactorizacionTR\RefactorizacionTR"
MODELS_PATH = os.path.join(BASE_PATH, "ModelosTR")
CONTROLLERS_PATH = os.path.join(BASE_PATH, "Controllers")

# ============================================================
# PLANTILLA CON FORMATO string.Template (Sintaxis ${VAR})
# ============================================================
# Nota: Usamos ${VAR} para variables de Python. 
# Las llaves { } de C# se quedan normales (no hace falta ponerlas dobles).

CONTROLLER_TEMPLATE = Template(r'''using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Data.Eikon.Models;
using System.ComponentModel.DataAnnotations.Schema;
using System.ComponentModel.DataAnnotations;
using Microsoft.EntityFrameworkCore.Storage;
using Data.Eikon.DTOs;
using AutoMapper;
using EIKON.Utilities;
using Microsoft.AspNetCore.Mvc.Rendering;

namespace EIKON.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class ${MODEL}Controller : ControllerBase
    {
        private readonly EIKONDBContext _context;
        private readonly IMapper _mapper;

        public ${MODEL}Controller(EIKONDBContext  context, IMapper  mapper)
        {
            _context = context;
            _mapper = mapper;
        }

        // GET: api/${MODEL}
        [HttpGet]
        public async Task<ActionResult<IEnumerable<${MODEL}Dto>>> Get${MODEL}s()
        {
            if (_context.${MODEL}s == null)
                return NotFound();

            var list = await _context.${MODEL}s.ToListAsync();
            var dtoList = _mapper.Map<List<${MODEL}Dto>>(list);
            return Ok(dtoList);
        }

        [HttpGet("${MODEL}SelectList/{SelectedItem}")]
        public async Task<ActionResult<IEnumerable<SelectListItem>>> Get${MODEL}SelectList(string SelectedItem)
        {
            var item1 = new SelectListItem() { Value = "0", Text = "No definido" };
            var NoExiste = new List<SelectListItem> { item1 };

            if (_context.${MODEL}s == null)
                return NoExiste;

            var list = await _context.${MODEL}s
                .OrderBy(u => u.${DESCPROP})
                .Select(c => new SelectListItem
                {
                    Value = c.${CODEPROP},
                    Text = c.${DESCPROP},
                    Selected = c.${CODEPROP} == SelectedItem
                }).ToListAsync();

            if (list == null)
                return NoExiste;

            return list;
        }

        [HttpGet("${MODEL}Ref")]
        public async Task<ActionResult<IEnumerable<${MODEL}Dto>>> Get${MODEL}Ref()
        {
            var NoExiste = new List<${MODEL}Dto>();

            if (_context.${MODEL}s == null)
                return NoExiste;

            var list = await _context.${MODEL}s
                .OrderBy(u => u.${CODEPROP})
                .Select(c => new ${MODEL}Dto
                {
                    ${PREFIX}Codigo = c.${CODEPROP},
                    ${PREFIX}Descri = c.${DESCPROP},
                    IdentityColumn = c.IdentityColumn,
                    CreatedBy = c.CreatedBy,
                    CreatedOn = c.CreatedOn,
                    ChangedBy = c.ChangedBy,
                    ChangedOn = c.ChangedOn
                }).ToListAsync();

            if (list == null)
                return NoExiste;

            return list;
        }

        [HttpGet("${MODEL}PorCodigo/{codigo}")]
        public async Task<ActionResult<${MODEL}Dto>> Get${MODEL}PorCodigo(string codigo)
        {
            if (_context.${MODEL}s == null)
                return NotFound();

            var data = await _context.${MODEL}s
                .FirstOrDefaultAsync(x => x.${CODEPROP}.Contains(codigo));

            if (data == null)
                return NotFound();

            var dto = _mapper.Map<${MODEL}Dto>(data);
            return Ok(dto);
        }

        [HttpGet("${MODEL}PorDescri/{descri}")]
        public async Task<ActionResult<IEnumerable<${MODEL}Dto>>> Get${MODEL}PorDescri(string descri)
        {
            var lista = new List<${MODEL}Dto>
            {
                new ${MODEL}Dto { ${CODEPROP} = "00", ${DESCPROP} = "No hay registros" }
            };

            if (_context.${MODEL}s == null)
                return lista;

            var result = await _context.${MODEL}s
                .Where(x => x.${DESCPROP}.Contains(descri))
                .OrderBy(o => o.${DESCPROP})
                .ToListAsync();

            if (result == null)
                return lista;

            var dtoList = _mapper.Map<List<${MODEL}Dto>>(result);
            return Ok(dtoList);
        }

        [HttpPut("{codigo}")]
        public async Task<IActionResult> Put${MODEL}(string codigo, ${MODEL}Dto dto)
        {
            var entity = await _context.${MODEL}s
                .FirstOrDefaultAsync(x => x.${CODEPROP}.Contains(codigo));

            if (entity == null)
                return BadRequest();

            entity.${DESCPROP} = dto.${CODEPROP};

            _context.Entry(entity).State = EntityState.Modified;

            try
            {
                await _context.SaveChangesAsync();
            }
            catch (DbUpdateConcurrencyException)
            {
                if (!_context.${MODEL}s.Any(e => e.${CODEPROP} == codigo))
                    return NotFound();

                return Problem("Error actualizando: '${MODEL}'");
            }

            return NoContent();
        }

        [HttpPost]
        public async Task<ActionResult<${MODEL}Dto>> Post${MODEL}(${MODEL}Dto dto)
        {
            if (_context.${MODEL}s == null)
                return Problem("Entity set is null.");

            var counter = await _context.Mrhco000s
                .FirstOrDefaultAsync(x => x.Codigo.Contains("${MODEL}"));

            if (counter == null)
                return Problem("Contador no existe.");

            var sec = counter.Secuencia + 1;
            dto.${CODEPROP} = sec.ToString().PadLeft(counter.Size, '0');

            var entity = new ${MODEL}
            {
                ${CODEPROP} = dto.${CODEPROP},
                ${DESCPROP} = dto.${DESCPROP},
                CreatedBy = User.Identity.Name,
                CreatedOn = DateTime.Now,
                ChangedBy = User.Identity.Name,
                ChangedOn = DateTime.Now
            };

            try
            {
                _context.${MODEL}s.Add(entity);
                counter.Secuencia = sec;
                _context.Mrhco000s.Update(counter);
                await _context.SaveChangesAsync();
            }
            catch (Exception ex)
            {
                return Problem("Error '${MODEL}' : " + ex.Message);
            }

            return Ok(dto);
        }

        [HttpDelete("{id}")]
        public async Task<IActionResult> Delete${MODEL}(int id)
        {
            if (_context.${MODEL}s == null)
                return NotFound();

            var entity = await _context.${MODEL}s.FindAsync(id);
            if (entity == null)
                return NotFound();

            _context.${MODEL}s.Remove(entity);
            await _context.SaveChangesAsync();
            return NoContent();
        }
    }
}
''')

# ============================================================
# FUNCIONES
# ============================================================

def ensure_directories():
    """Crea el directorio de controladores si no existe."""
    if not os.path.exists(CONTROLLERS_PATH):
        os.makedirs(CONTROLLERS_PATH)
        print(f"📁 Directorio creado: {CONTROLLERS_PATH}")

def find_valid_models():
    """Analiza los archivos .cs buscando la estructura requerida."""
    if not os.path.exists(MODELS_PATH):
        print(f"❌ Error: La ruta de modelos no existe: {MODELS_PATH}")
        return []

    valid = []
    
    print(f"📂 Escaneando: {MODELS_PATH} ...")

    for file in os.listdir(MODELS_PATH):
        if not file.endswith(".cs"):
            continue

        path = os.path.join(MODELS_PATH, file)
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"⚠️ No se pudo leer {file}: {e}")
            continue

        # 1. Buscar nombre de la clase
        class_match = re.search(r"class\s+(\w+)", content)
        if not class_match:
            continue
        model_name = class_match.group(1)

        # 2. Buscar prefijo (Ej: public string TrCodigo)
        # Buscamos una propiedad que termine en 'Codigo' y tenga exactamente 2 letras antes
        prefix_match = re.search(r"public\s+\w+\s+(\w{2})Codigo\b", content)
        if not prefix_match:
            # Opcional: avisar si tiene clase pero no prefijo
            # print(f"   🔸 {model_name} ignorado (No se encontró patrón XxCodigo)")
            continue
            
        prefix = prefix_match.group(1)

        # 3. Validar campos obligatorios de auditoría y base
        required_fields = [
            f"{prefix}Codigo",
            f"{prefix}Descri",
            "IdentityColumn",
            "CreatedBy",
            "CreatedOn",
            "ChangedBy",
            "ChangedOn",
        ]

        # Verificamos que TODOS los campos existan en el contenido
        missing_fields = [field for field in required_fields if not re.search(rf"\b{field}\b", content)]
        
        if not missing_fields:
            valid.append((model_name, prefix))
        else:
            print(f"   ⚠️ {model_name} incompleto. Faltan: {missing_fields}")

    return valid

def create_controller(model, prefix):
    """Genera el archivo Controller usando la plantilla segura."""
    
    codeprop = f"{prefix}Codigo"
    descprop = f"{prefix}Descri"

    # Usamos substitute para reemplazar las variables ${VAR}
    # Esto ignora las llaves { } normales de C#
    controller_code = CONTROLLER_TEMPLATE.substitute(
        MODEL=model,
        CODEPROP=codeprop,
        DESCPROP=descprop,
        PREFIX=prefix  # Agregamos el prefijo que faltaba
    )

    file_path = os.path.join(CONTROLLERS_PATH, f"{model}Controller.cs")

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(controller_code)
        print(f"   ✔ Generado: {model}Controller.cs")
    except Exception as e:
        print(f"   ❌ Error escribiendo {model}: {e}")

# ============================================================
# EJECUCIÓN PRINCIPAL
# ============================================================

if __name__ == "__main__":
    print("\n🚀 INICIANDO GENERADOR DE CONTROLADORES\n")
    
    ensure_directories()
    
    valid_models = find_valid_models()

    if not valid_models:
        print("\n❌ No se encontraron modelos válidos para procesar.")
    else:
        print(f"\n📌 Se detectaron {len(valid_models)} modelos válidos.\n")
        
        print("🛠  Generando archivos...\n")
        for m, p in valid_models:
            create_controller(m, p)

        print("\n🎉 PROCESO FINALIZADO CON ÉXITO.\n")