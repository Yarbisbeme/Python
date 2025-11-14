import os
import re

# === CONFIGURACIÓN ===
dtos_path = r"C:\Users\Eikon\OneDrive - eikon.com.do\Escritorio\EikonWebApi\EikonWebApi_20251022\EikonWebApi\EIKON.Data\DTOs\newDto"
controllers_path = r"C:\Users\Eikon\OneDrive - eikon.com.do\Escritorio\EikonWebApi\EikonWebApi_20251022\EikonWebApi\EIKON.Data\Controllers\NewFolder"
namespace_name = "EIKON.Controllers"
dbcontext_name = "EIKONDBContext"
contador_tabla = "Mrhco000s"

os.makedirs(controllers_path, exist_ok=True)

# === REGEX PARA PROPIEDADES PUBLICAS ===
prop_pattern = re.compile(r'public\s+([\w<>\[\]\?]+)\s+([\w]+)\s*\{\s*get;\s*set;\s*\}', re.MULTILINE)

# === FUNCIONES AUXILIARES ===
def parse_dto_properties(dto_file_path):
    text = open(dto_file_path, "r", encoding="utf-8").read()
    return prop_pattern.findall(text)

def analizar_campos_especiales(props):
    nombres_originales = [n for _, n in props]
    nombres_lower = [n.lower() for n in nombres_originales]

    def get_original(nombre_min):
        """Devuelve el nombre original respetando mayúsculas"""
        for n in nombres_originales:
            if n.lower() == nombre_min:
                return n
        return None

    result = {
        "maenume": get_original("maenume"),
        "emempresa": get_original("emempresa"),
        "maenomi": get_original("maenomi"),
        "codigo": next((n for n in nombres_originales if re.search(r"^(cod|codigo)", n, re.I)), None),
        "descripcion": next((n for n in nombres_originales if re.search(r"(descri|nombre|name|desc)", n, re.I)), None),
        "otro_nume": next(
            (n for n in nombres_originales if n.lower().endswith("nume") and n.lower() != "maenume"), None
        )
    }

    return result



def choose_code_prop(props):
    order = [r'cod', r'codigo', r'id$', r'code']
    for pat in order:
        for t, n in props:
            if re.search(pat, n, re.I):
                return n
    for t, n in props:
        if t.lower().replace("?", "") == "string":
            return n
    return props[0][1] if props else None

def choose_descri_prop(props):
    order = [r'descr', r'desc', r'nombre', r'name', r'description']
    for pat in order:
        for t, n in props:
            if re.search(pat, n, re.I):
                return n
    strings = [n for t, n in props if t.lower().replace("?", "") == "string"]
    return strings[1] if len(strings) > 1 else (strings[0] if strings else None)

# === FUNCION PRINCIPAL ===
def crear_controller_desde_dto(dto_filename):
    base = dto_filename.replace(".cs", "").replace("Dto", "")
    context = dto_filename.replace(".cs", "").replace("Dto", "") + "s"
    controller_name = f"{base}Controller"
    controller_file = os.path.join(controllers_path, f"{controller_name}.cs")

    dto_path = os.path.join(dtos_path, dto_filename)
    props = parse_dto_properties(dto_path)
    campos = analizar_campos_especiales(props)
    code_prop = choose_code_prop(props)
    descri_prop = choose_descri_prop(props)

    llave_nume = "Maenume" if campos["maenume"] else (campos["otro_nume"] or None)
    tiene_empresa = campos["emempresa"]
    tiene_nomina = campos["maenomi"]
    llave = "Maenume" if campos["maenume"] else (campos["otro_nume"] or code_prop or "Id")

    # ===== ESTRUCTURA BASE =====
    controller_code = f"""
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Data.Eikon.Models;
using Data.Eikon.DTOs;
using AutoMapper;
using Microsoft.AspNetCore.Mvc.Rendering;

namespace {namespace_name}
{{
    [Route("api/[controller]")]
    [ApiController]
    public class {controller_name} : ControllerBase
    {{
        private readonly {dbcontext_name} _context;
        private readonly IMapper _mapper;

        public {controller_name}({dbcontext_name} context, IMapper mapper)
        {{
            _context = context;
            _mapper = mapper;
        }}

        #region Get
        // GET: api/{base}
        [HttpGet]
        public async Task<ActionResult<IEnumerable<{base}Dto>>> Get{base}Dtos()
        {{
            if (_context.{context} == null)
            {{
                return NotFound();
            }}

            var entities = await _context.{context}.ToListAsync();
            var dtos = _mapper.Map<List<{base}Dto>>(entities);
            return Ok(dtos);
        }}
"""

    # === SELECT LIST (siempre se genera)
    select_value = "c.Maenume" if campos["maenume"] else ("c." + code_prop if code_prop else "c.Id")
    select_text = (
        f"c.{descri_prop}" if campos["descripcion"] else
        ("c.Maenume" if campos["maenume"] else ("c." + code_prop if code_prop else "c.Id"))
    )


    controller_code += f"""
        [HttpGet("SelectList/{{selectedItem?}}")]
        public async Task<ActionResult<IEnumerable<SelectListItem>>> Get{base}SelectList(string? selectedItem = null)
        {{
            var defaultItem = new SelectListItem {{ Value = "0", Text = "No definido" }};
            var noExiste = new List<SelectListItem> {{ defaultItem }};

            var myList = await _context.{context}
                .OrderBy(c => {select_text})
                .Select(c => new SelectListItem
                {{
                    Value = {select_value},
                    Text = {select_text},
                    Selected = {select_value} == selectedItem
                }})
                .ToListAsync();

            if (myList.Count == 0)
                return Ok(noExiste);

            return Ok(myList);
        }}
"""

    # === ENDPOINTS CONDICIONALES ===

    # Caso 1: Tiene Maenume + Emempresa
    if campos["maenume"] and tiene_empresa:
        controller_code += f"""
        [HttpGet("PorEmpresa/{{emempresa}}")]
        public async Task<ActionResult<IEnumerable<{base}Dto>>> Get{base}PorEmpresa(string emempresa)
        {{
            var entities = await _context.{context}
                .Where(x => x.Emempresa == emempresa)
                .ToListAsync();

            var dtos = _mapper.Map<List<{base}Dto>>(entities);
            return Ok(dtos);
        }}

        [HttpGet("PorNumeEmpresa/{{maenume}}/{{emempresa}}")]
        public async Task<ActionResult<{base}Dto>> Get{base}PorNumeEmpresa(string maenume, string emempresa)
        {{
            var entity = await _context.{context}
                .FirstOrDefaultAsync(x => x.Maenume == maenume && x.Emempresa == emempresa);

            if (entity == null)
                return NotFound();

            return Ok(_mapper.Map<{base}Dto>(entity));
        }}
"""

    # Caso 2: Tiene Maenomi → endpoint adicional
    if tiene_nomina:
        controller_code += f"""
        [HttpGet("PorNomi/{{maenomi}}")]
        public async Task<ActionResult<{base}Dto>> Get{base}PorNomi(string maenomi)
        {{
            var entity = await _context.{context}.FirstOrDefaultAsync(x => x.Maenomi == maenomi);
            if (entity == null)
                return NotFound();

            return Ok(_mapper.Map<{base}Dto>(entity));
        }}
"""

    # Caso 3: Tiene Maenume (sin empresa)
    elif campos["maenume"]:
        controller_code += f"""
        [HttpGet("PorNume/{{maenume}}")]
        public async Task<ActionResult<{base}Dto>> Get{base}PorNume(string maenume)
        {{
            var entity = await _context.{context}.FirstOrDefaultAsync(x => x.Maenume == maenume);
            if (entity == null)
                return NotFound();

            return Ok(_mapper.Map<{base}Dto>(entity));
        }}
"""

    # Caso 4: Tiene otro campo *nume
    elif campos["otro_nume"]:
        controller_code += f"""
        [HttpGet("PorNume/{{nume}}")]
        public async Task<ActionResult<{base}Dto>> Get{base}PorNume(string nume)
        {{
            var entity = await _context.{context}.FirstOrDefaultAsync(x => x.{campos["otro_nume"]} == nume);
            if (entity == null)
                return NotFound();

            return Ok(_mapper.Map<{base}Dto>(entity));
        }}
"""

    # Caso 5: Tiene código (si no hay ningún nume)
    elif campos["codigo"]:
        controller_code += f"""
        [HttpGet("PorCodigo/{{codigo}}")]
        public async Task<ActionResult<{base}Dto>> Get{base}PorCodigo(string codigo)
        {{
            var entity = await _context.{context}.FirstOrDefaultAsync(x => x.{code_prop}.Contains(codigo));
            if (entity == null)
                return NotFound();

            return Ok(_mapper.Map<{base}Dto>(entity));
        }}

"""

    # === DESCRIPCION ===
    if campos["descripcion"]:
        controller_code += f"""
        [HttpGet("PorDescri/{{descri}}")]
        public async Task<ActionResult<IEnumerable<{base}Dto>>> Get{base}PorDescri(string descri)
        {{
            var entities = await _context.{context}
                .Where(r => r.{descri_prop}.Contains(descri))
                .OrderBy(o => o.{descri_prop})
                .ToListAsync();

            var dtos = _mapper.Map<List<{base}Dto>>(entities);

            if (dtos.Count == 0)
            {{
                dtos.Add(new {base}Dto() {{ {code_prop if code_prop else 'Id'} = "00", {descri_prop} = "No hay registros" }});
            }}

            return Ok(dtos);
        }}
        
"""

    # === POST ===
    controller_code += f"""
        #endregion

        #region Post
        [HttpPost]
        public async Task<ActionResult<{base}Dto>> Post{base}Dto({base}Dto dto)
        {{
            if (_context.{context} == null)
            {{
                return Problem("Entity set '{dbcontext_name}.{base}s' is null.");
            }}

            var contador = await _context.{contador_tabla}.FirstOrDefaultAsync(x => x.Codigo.Contains("{base.upper()}"));
            if (contador == null)
            {{
                return Problem("Contador '{base}' no existe.");
            }}

            var sec = contador.Secuencia + 1;
            dto.{code_prop} = sec.ToString().PadLeft(contador.Size, '0');

            var entity = _mapper.Map<{base}>(dto);
            _context.{context}.Add(entity);

            contador.Secuencia = sec;
            _context.{contador_tabla}.Update(contador);
            await _context.SaveChangesAsync();

            var dtoResult = _mapper.Map<{base}Dto>(entity);
            return Ok(dtoResult);
        }}
        #endregion

"""
        # === PUT ===
    controller_code += f"""
    #region Put

    [HttpPut("{{codigo}}")]
        public async Task<ActionResult<{base}Dto>> Put{base}(string codigo, {base}Dto dto)
        {{
            var entity = await _context.{context}.FirstOrDefaultAsync(x => x.{llave} == codigo);
            if (entity == null)
                return NotFound();

            _mapper.Map(dto, entity);

            try
            {{
                await _context.SaveChangesAsync();
            }}
            catch (DbUpdateConcurrencyException)
            {{
                if (!{base}Exists(codigo))
                    return NotFound();
                else
                    throw;
            }}

            var dtoResult = _mapper.Map<{base}Dto>(entity);
            return Ok(dtoResult);
        }}
        #endregion
"""
    
    # === DELETE ===
    controller_code += f"""
        #region Delete
        [HttpDelete("{{codigo}}")]
        public async Task<IActionResult> Delete{base}(string codigo)
        {{
            var entity = await _context.{context}.FirstOrDefaultAsync(x => x.{llave} == codigo);
            if (entity == null)
                return NotFound();

            _context.{context}.Remove(entity);
            await _context.SaveChangesAsync();
            return NoContent();
        }}

        private bool {base}Exists(string codigo)
        {{
            return (_context.{context}?.Any(e => e.{llave} == codigo)).GetValueOrDefault();
        }}
        
        #endregion
    
        }}

"""

    # Guardar archivo
    with open(controller_file, "w", encoding="utf-8") as f:
        f.write(controller_code)

    print(f"✅ Controlador generado: {controller_name}.cs")

# === PROCESO PRINCIPAL ===
dtos = [f for f in os.listdir(dtos_path) if f.endswith(".cs")]
for dto_file in dtos:
    crear_controller_desde_dto(dto_file)

print("\n🚀 Todos los controladores han sido generados correctamente.")
