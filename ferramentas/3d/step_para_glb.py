# -*- coding: utf-8 -*-
"""STEP (montagem, com nomes e cores das peças) -> glTF binário (.glb) em metros.

A malha sai do sólido do CAD (OpenCascade), com flecha máxima configurável: a geometria
é a do desenho, só triangulada. Os nomes das peças (ex.: E-0004-V3) seguem para o .glb,
para os materiais serem escolhidos por peça no Blender.

Uso: python step_para_glb.py entrada.step saida.glb [flecha_mm=0.03] [angulo_rad=0.15]
"""
import sys, time
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString, TCollection_AsciiString
from OCP.XCAFApp import XCAFApp_Application
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.collections import Sequence_TDF_Label as TDF_LabelSequence
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.RWGltf import RWGltf_CafWriter
from OCP.RWMesh import RWMesh_CoordinateSystem
from OCP.collections import IndexedDataMap_TCollection_AsciiString_TCollection_AsciiString as InfoArquivo
from OCP.Message import Message_ProgressRange
from OCP.IFSelect import IFSelect_RetDone

src, dst = sys.argv[1], sys.argv[2]
flecha = float(sys.argv[3]) if len(sys.argv) > 3 else 0.03
angulo = float(sys.argv[4]) if len(sys.argv) > 4 else 0.15

t0 = time.time()
app = XCAFApp_Application.GetApplication_s()
doc = TDocStd_Document(TCollection_ExtendedString("MDTV-XCAF"))
app.InitDocument(doc)
rd = STEPCAFControl_Reader()
rd.SetColorMode(True); rd.SetNameMode(True); rd.SetLayerMode(True)
if rd.ReadFile(src) != IFSelect_RetDone:
    sys.exit('não consegui ler ' + src)
rd.Transfer(doc, Message_ProgressRange())
st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
livres = TDF_LabelSequence(); st.GetFreeShapes(livres)
for i in range(1, livres.Length() + 1):
    BRepMesh_IncrementalMesh(st.GetShape_s(livres.Value(i)), flecha, False, angulo, True)
t1 = time.time()
w = RWGltf_CafWriter(TCollection_AsciiString(dst), True)
conv = w.ChangeCoordinateSystemConverter()
conv.SetInputLengthUnit(0.001)                                   # CAD em mm -> glTF em m
conv.SetInputCoordinateSystem(RWMesh_CoordinateSystem.RWMesh_CoordinateSystem_Zup)
ok = w.Perform(doc, InfoArquivo(), Message_ProgressRange())
print('OK' if ok else 'FALHOU', dst, 'leitura+malha %.1fs, escrita %.1fs, %d formas livres' % (t1 - t0, time.time() - t1, livres.Length()))
