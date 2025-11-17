import os
import re

MODELS_PATH = r"C:\Users\Eikon\Downloads\RefactorizacionTR\RefactorizacionTR\ModelosTR"
CONTROLLERS_PATH = r"C:\Users\Eikon\Downloads\RefactorizacionTR\RefactorizacionTR\Controllers"

# ============================================================
# CONTROLADOR PLANTILLA EXACTA BASADA EN TU EJEMPLO DE Trhal000
# ============================================================

CONTROLLER_TEMPLATE = r'''
using System;
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
    public class {MODEL}Controller : ControllerBase
    {
        private readonly EIKONDBContext _context;
        private readonly IMapper _mapper;

        public {MODEL}Controller(EIKONDBContext  context, IMapper  mapper)
        {
            _context = context;
            _mapper = mapper;
        }

        // GET: api/{MODEL}
        [HttpGet]
        public async Task<ActionResult<IEnumerable<{MODEL}Dto>>> Get{MODEL}s()
        {{
            if (_context.{MODEL}s == null)
                return NotFound();

            var list = await _context.{MODEL}s.ToListAsync();
            var dtoList = _mapper.Map<List<{MODEL}Dto>>(list);
            return Ok(dtoList);
        }}

        [HttpGet("{MODEL}SelectList/{{SelectedItem}}")]
        public async Task<ActionResult<IEnumerable<SelectListItem>>> Get{MODEL}SelectList(string SelectedItem)
        {{
            var item1 = new SelectListItem() {{ Value = "0", Text = "No definido" }};
            var NoExiste = new List<SelectListItem> {{ item1 }};

            if (_context.{MODEL}s == null)
                return NoExiste;

            var list = await _context.{MODEL}s
                .OrderBy(u => u.{DESCPROP})
                .Select(c => new SelectListItem
                {{
                    Value = c.{CODEPROP},
                    Text = c.{DESCPROP},
                    Selected = c.{CODEPROP} == SelectedItem
                }}).ToListAsync();

            if (list == null)
                return NoExiste;

            return list;
        }}

        [HttpGet("{MODEL}Ref")]
        public async Task<ActionResult<IEnumerable<{MODEL}Dto>>> Get{MODEL}Ref()
        {{
            var NoExiste = new List<{MODEL}Dto>();

            if (_context.{MODEL}s == null)
                return NoExiste;

            var list = await _context.{MODEL}s
                .OrderBy(u => u.{CODEPROP})
                .Select(c => new {MODEL}Dto
                {{
                    {prefix}Codigo = c.{CODEPROP},
                    {prefix}Descri = c.{DESCPROP},
                    IdentityColumn = c.IdentityColumn,
                    CreatedBy = c.CreatedBy,
                    CreatedOn = c.CreatedOn,
                    ChangedBy = c.ChangedBy,
                    ChangedOn = c.ChangedOn
                }}).ToListAsync();

            if (list == null)
                return NoExiste;

            return list;
        }}

        [HttpGet("{MODEL}PorCodigo/{{codigo}}")]
        public async Task<ActionResult<{MODEL}Dto>> Get{MODEL}PorCodigo(string codigo)
        {{
            if (_context.{MODEL}s == null)
                return NotFound();

            var data = await _context.{MODEL}s
                .FirstOrDefaultAsync(x => x.{CODEPROP}.Contains(codigo));

            if (data == null)
                return NotFound();

            var dto = _mapper.Map<{MODEL}Dto>(data);
            return Ok(dto);
        }}

        [HttpGet("{MODEL}PorDescri/{{descri}}")]
        public async Task<ActionResult<IEnumerable<{MODEL}Dto>>> Get{MODEL}PorDescri(string descri)
        {{
            var lista = new List<{MODEL}Dto>
            {{
                new {MODEL}Dto {{ {CODEPROP} = "00", {DESCPROP} = "No hay registros" }}
            }};

            if (_context.{MODEL}s == null)
                return lista;

            var result = await _context.{MODEL}s
                .Where(x => x.{DESCPROP}.Contains(descri))
                .OrderBy(o => o.{DESCPROP})
                .ToListAsync();

            if (result == null)
                return lista;

            var dtoList = _mapper.Map<List<{MODEL}Dto>>(result);
            return Ok(dtoList);
        }}

        [HttpPut("{{codigo}}")]
        public async Task<IActionResult> Put{MODEL}(string codigo, {MODEL}Dto dto)
        {{
            var entity = await _context.{MODEL}s
                .FirstOrDefaultAsync(x => x.{CODEPROP}.Contains(codigo));

            if (entity == null)
                return BadRequest();

            entity.{DESCPROP} = dto.Descri;

            _context.Entry(entity).State = EntityState.Modified;

            try
            {{
                await _context.SaveChangesAsync();
            }}
            catch (DbUpdateConcurrencyException)
            {{
                if (!_context.{MODEL}s.Any(e => e.{CODEPROP} == codigo))
                    return NotFound();

                return Problem("Error actualizando: '{MODEL}'");
            }}

            return NoContent();
        }}

        [HttpPost]
        public async Task<ActionResult<{MODEL}Dto>> Post{MODEL}({MODEL}Dto dto)
        {{
            if (_context.{MODEL}s == null)
                return Problem("Entity set is null.");

            var counter = await _context.Mrhco000s
                .FirstOrDefaultAsync(x => x.Codigo.Contains("{MODEL}"));

            if (counter == null)
                return Problem("Contador no existe.");

            var sec = counter.Secuencia + 1;
            dto.Codigo = sec.ToString().PadLeft(counter.Size, '0');

            var entity = new {MODEL}
            {{
                {CODEPROP} = dto.Codigo,
                {DESCPROP} = dto.Descri,
                CreatedBy = User.Identity.Name,
                CreatedOn = DateTime.Now,
                ChangedBy = User.Identity.Name,
                ChangedOn = DateTime.Now
            }};

            try
            {{
                _context.{MODEL}s.Add(entity);
                counter.Secuencia = sec;
                _context.Mrhco000s.Update(counter);
                await _context.SaveChangesAsync();
            }}
            catch (Exception ex)
            {{
                return Problem("Error '{MODEL}' : " + ex.Message);
            }}

            return Ok(dto);
        }}

        [HttpDelete("{{id}}")]
        public async Task<IActionResult> Delete{MODEL}(int id)
        {{
            if (_context.{MODEL}s == null)
                return NotFound();

            var entity = await _context.{MODEL}s.FindAsync(id);
            if (entity == null)
                return NotFound();

            _context.{MODEL}s.Remove(entity);
            await _context.SaveChangesAsync();
            return NoContent();
        }}
    }}
}}
'''

# ============================================================
# DETECTAR MODELOS VÁLIDOS (prefijo + 7 campos mínimos)
# ============================================================

def find_valid_models():

    valid = []

    for file in os.listdir(MODELS_PATH):

        if not file.endswith(".cs"):
            continue

        path = os.path.join(MODELS_PATH, file)
        content = open(path, "r", encoding="utf-8").read()

        class_match = re.search(r"class\s+(\w+)", content)
        if not class_match:
            continue

        model = class_match.group(1)

        prefix_match = re.search(r"public\s+\w+\s+(\w{2})Codigo\b", content)
        if not prefix_match:
            continue

        prefix = prefix_match.group(1)

        required = [
            f"{prefix}Codigo",
            f"{prefix}Descri",
            "IdentityColumn",
            "CreatedBy",
            "CreatedOn",
            "ChangedBy",
            "ChangedOn",
        ]

        ok = True
        for field in required:
            if not re.search(rf"\b{field}\b", content):
                ok = False
                break

        if ok:
            valid.append((model, prefix))

    return valid

# ============================================================
# GENERAR CONTROLADOR REEMPLAZANDO VARIABLES EN LA PLANTILLA
# ============================================================

def create_controller(model, prefix):

    codeprop = f"{prefix}Codigo"
    descprop = f"{prefix}Descri"

    controller_code = CONTROLLER_TEMPLATE.replace("{MODEL}", model)
    controller_code = controller_code.replace("{CODEPROP}", codeprop)
    controller_code = controller_code.replace("{DESCPROP}", descprop)

    file_path = os.path.join(CONTROLLERS_PATH, f"{model}Controller.cs")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(controller_code)

    print(f"✔ Controlador generado: {model}Controller.cs")


# ============================================================
# EJECUCIÓN PRINCIPAL
# ============================================================

print("\n🔍 Analizando modelos...\n")
valid_models = find_valid_models()

if not valid_models:
    print("❌ No se encontraron modelos válidos.")
else:
    print("📌 Modelos detectados:")
    for m, p in valid_models:
        print(f"   ✔ {m} (prefijo: {p})")

    print("\n🛠 Generando controladores...\n")

    for m, p in valid_models:
        create_controller(m, p)

    print("\n🎉 FINALIZADO: Controladores creados y reemplazados.\n")
