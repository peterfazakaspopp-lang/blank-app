# -*- coding: utf-8 -*-
import clr
import os

clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
from Autodesk.Revit.DB import *
from RevitServices.Persistence import DocumentManager
from System.Collections.Generic import List

doc = DocumentManager.Instance.CurrentDBDocument
view = doc.ActiveView

def get_dim(item, t, p1, p2, p3):
    for n in [p1, p2, p3]:
        for o in [item, t]:
            p = o.LookupParameter(n)
            if p and p.HasValue and p.AsDouble() > 0: return p.AsDouble()
    return 0.0

try:
    doors = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType()
    data, isolate_ids = [], List[ElementId]()
    
    for item in doors:
        try:
            owning_doc = item.Document
            t = owning_doc.GetElement(item.GetTypeId())
            if not t: continue
            
            tm = str(t.LookupParameter("Type Mark").AsString() if t.LookupParameter("Type Mark") else "")
            if "UM" not in tm.upper(): continue
            
            fam, tn = str(t.FamilyName), str(t.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString())
            wf = get_dim(item, t, "Rough Width", "Width", "Latime")
            hf = get_dim(item, t, "Rough Height", "Height", "Inaltime")
            w_mm, h_mm = round(wf * 304.8, 0), round(hf * 304.8, 0)
            
            cwp = item.LookupParameter("Clear Width") or t.LookupParameter("Clear Width")
            chp = item.LookupParameter("Clear Height") or t.LookupParameter("Clear Height")
            cw = round(cwp.AsDouble() * 0.3048, 2) if cwp else round(wf * 0.3048, 2)
            ch = round(chp.AsDouble() * 0.3048, 2) if chp else round(hf * 0.3048, 2)
            
            sd = str(item.LookupParameter("AS_sens-deschidere").AsString() if item.LookupParameter("AS_sens-deschidere") else "N/A")
            fr_p = item.LookupParameter("Fire Rating") or t.LookupParameter("Fire Rating")
            fr = str(fr_p.AsString()) if fr_p and fr_p.HasValue else "N/A"
            
            lvl = owning_doc.GetElement(item.LevelId)
            ln = str(lvl.Name) if lvl else "N/A"
            gp = str(item.LookupParameter("AS_grosime-perete").AsValueString() if item.LookupParameter("AS_grosime-perete") else "N/A")
            
            rm_f = str(item.LookupParameter("AS_LINKED-FROM").AsString() if item.LookupParameter("AS_LINKED-FROM") else "N/A")
            rm_t = str(item.LookupParameter("AS_LINKED-TO").AsString() if item.LookupParameter("AS_LINKED-TO") else "N/A")
            
            wt = "BA"
            if hasattr(item, "Host") and item.Host:
                hw = owning_doc.GetElement(item.Host.GetTypeId())
                if hw and hw.LookupParameter("Type Mark") and hw.LookupParameter("Type Mark").HasValue:
                    wt = str(hw.LookupParameter("Type Mark").AsString()).strip() or "BA"
                    
            bz_p = item.LookupParameter("AS_bronze-C34") or item.LookupParameter("AS_bronz-C34") or t.LookupParameter("AS_bronz-C34")
            bz = "-"
            if bz_p and bz_p.HasValue:
                v_str = str(bz_p.AsValueString() or bz_p.AsString()).lower()
                if "yes" in v_str or "da" in v_str or "1" in v_str: bz = rm_f
                
            ft_ral_p = item.LookupParameter("FT RAL") or t.LookupParameter("FT RAL")
            ft_ral = str(ft_ral_p.AsString() or ft_ral_p.AsValueString()) if ft_ral_p and ft_ral_p.HasValue else "N/A"
                
            flags = []
            for p in ["AS_Bara_anti-panica", "AS_control-acces", "AS_yala-masterkey", "Deschidere automata in caz de incendiu", "Inchidere automata in caz de incendiu"]:
                param = item.LookupParameter(p) or t.LookupParameter(p)
                val = "✗"
                if param and param.HasValue:
                    v = str(param.AsValueString()).lower()
                    if "yes" in v or "da" in v or param.AsInteger() == 1 or "1" in v: val = "✓"
                flags.append(val)
                
            cluj_p = item.LookupParameter("CLUJ_Part") or t.LookupParameter("CLUJ_Part")
            cluj_val = str(cluj_p.AsString()) if cluj_p and cluj_p.HasValue else "N/A"
            
            # --- READ EXISTING MARK DIRECTLY FROM REVIT ---
            mark_p = item.LookupParameter("AS_door-mark")
            existing_mark = str(mark_p.AsString()) if mark_p and mark_p.HasValue else "UNMARKED"
                
            if owning_doc.IsLinked == False: isolate_ids.Add(item.Id)
            
            data.append({'elem': item, 'fam': fam, 'w_mm': w_mm, 'h_mm': h_mm, 'tn': tn, 'sd': sd, 'cw': cw, 'ch': ch, 'fr': fr, 'ln': ln, 'flags': flags, 'gp': gp, 'wt': wt, 'rm_f': rm_f, 'rm_t': rm_t, 'bz': bz, 'tm': tm, 'cluj': cluj_val, 'ft_ral': ft_ral, 'mark': existing_mark})
        except: continue

    if len(data) > 0:
        headers = ["Family", "TIP", "INDICATIV USA", "SENS DESCHIDERE", "L (m)", "H (m)", "REZISTENTA FOC", "NIVEL", "FT RAL", "TOTAL", "BA", "CA", "YM", "MDA", "ER", "GROS. PERETE", "TIP PERETE", "AS_LINKED-FROM", "AS_LINKED-TO", "FÎ RAL: C34", "CLUJ_Part"]
        matrix = [headers]
        
        for d in data:
            f = d['flags']
            matrix.append([
                str(d['fam']), str(d['tn']), str(d['mark']), str(d['sd']), str(d['cw']), str(d['ch']), str(d['fr']), 
                str(d['ln']), str(d['ft_ral']), "1", str(f[0]), str(f[1]), str(f[2]), str(f[3]), str(f[4]), 
                str(d['gp']), str(d['wt']), str(d['rm_f']), str(d['rm_t']), str(d['bz']), str(d['cluj'])
            ])
            
        output_dir = r"D:\PROIECTE\ASX\Tablouri tamplarie"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        file_path = os.path.join(output_dir, "PLOT_MASTER.tsv")
        
        with open(file_path, "w", encoding="utf-8-sig") as f:
            for row in matrix:
                f.write("\t".join([str(cell).replace("\n", " ") for cell in row]) + "\n")
                
        OUT = "Successfully exported " + str(len(data)) + " doors with existing Revit marks to: " + file_path
    else: 
        OUT = "Error: No doors matching filters found."
except Exception as ex:
    import traceback
    OUT = "Error: " + str(ex) + "\n" + traceback.format_exc()
